# Copyright (c) Facebook, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import collections
import logging
import os
import pprint
import threading
import time
import timeit
import traceback
import typing

os.environ["OMP_NUM_THREADS"] = "1"  # Necessary for multithreading.
import torch
from torch import multiprocessing as mp
from torch import nn
from torch.nn import functional as F
from core import file_writer
from core import vtrace
#from core.models import Net
from core.ResnetModel import ResNet as Net
from core import environment
from core import prof



import atari_wrappers

from concurrent import futures
import pickle
import grpc
from grpc.experimental import aio
import asyncio
from utils import rpcenv_pb2,rpcenv_pb2_grpc


# yapf: disable
parser = argparse.ArgumentParser(description="PyTorch Scalable Agent")

parser.add_argument("--env", type=str, default="PongNoFrameskip-v4",
                    help="Gym environment.")
parser.add_argument("--mode", default="train",
                    choices=["train", "test", "test_render"],
                    help="Training or test mode.")
parser.add_argument("--xpid", default=None,
                    help="Experiment id (default: None).")

# Training settings.
parser.add_argument("--disable_checkpoint", action="store_true",
                    help="Disable saving checkpoint.")
parser.add_argument("--savedir", default="~/coknight_logs",
                    help="Root dir where experiment data will be saved.")
parser.add_argument("--num_actors", default=4, type=int, metavar="N",
                    help="Number of actors (default: 4).")
parser.add_argument("--total_steps", default=100000, type=int, metavar="T",
                    help="Total environment steps to train for.")
parser.add_argument("--batch_size", default=8, type=int, metavar="B",
                    help="Learner batch size.")
parser.add_argument("--unroll_length", default=80, type=int, metavar="T",
                    help="The unroll length (time dimension).")
parser.add_argument("--num_buffers", default=None, type=int,
                    metavar="N", help="Number of shared-memory buffers.")
parser.add_argument("--num_learner_threads", "--num_threads", default=1, type=int,
                    metavar="N", help="Number learner threads.")
parser.add_argument("--disable_cuda", action="store_true",
                    help="Disable CUDA.")
parser.add_argument("--use_lstm", action="store_true",
                    help="Use LSTM in agent model.")

# Loss settings.
parser.add_argument("--entropy_cost", default=0.0006,
                    type=float, help="Entropy cost/multiplier.")
parser.add_argument("--baseline_cost", default=0.5,
                    type=float, help="Baseline cost/multiplier.")
parser.add_argument("--discounting", default=0.99,
                    type=float, help="Discounting factor.")
parser.add_argument("--reward_clipping", default="abs_one",
                    choices=["abs_one", "none"],
                    help="Reward clipping.")

# Optimizer settings.
parser.add_argument("--learning_rate", default=0.00048,
                    type=float, metavar="LR", help="Learning rate.")
parser.add_argument("--alpha", default=0.99, type=float,
                    help="RMSProp smoothing constant.")
parser.add_argument("--momentum", default=0, type=float,
                    help="RMSProp momentum.")
parser.add_argument("--epsilon", default=0.01, type=float,
                    help="RMSProp epsilon.")
parser.add_argument("--grad_norm_clipping", default=40.0, type=float,
                    help="Global gradient norm clip.")


parser.add_argument("--remark", default="logs", type=str,
                    help="Global gradient norm clip.")
# yapf: enable


logging.basicConfig(
    format=(
        "[%(levelname)s:%(process)d %(module)s:%(lineno)d %(asctime)s] " "%(message)s"
    ),
    level=0,
)

Buffers = typing.Dict[str, typing.List[torch.Tensor]]

buffers = {}

actor_model = None

learner_model = None

free_queue = None

full_queue = None

def compute_baseline_loss(advantages):
    return 0.5 * torch.sum(advantages ** 2)


def compute_entropy_loss(logits):
    """Return the entropy loss, i.e., the negative entropy of the policy."""
    policy = F.softmax(logits, dim=-1)
    log_policy = F.log_softmax(logits, dim=-1)
    return torch.sum(policy * log_policy)


def compute_policy_gradient_loss(logits, actions, advantages):
    cross_entropy = F.nll_loss(
        F.log_softmax(torch.flatten(logits, 0, 1), dim=-1),
        target=torch.flatten(actions, 0, 1),
        reduction="none",
    )
    cross_entropy = cross_entropy.view_as(advantages)
    return torch.sum(cross_entropy * advantages.detach())


def get_batch(
    flags,
    free_queue: mp.SimpleQueue,
    full_queue: mp.SimpleQueue,
    buffers: Buffers,
    initial_agent_state_buffers,
    timings,
    lock=threading.Lock(),
):
    with lock:
        timings.time("lock")
        indices = [full_queue.get() for _ in range(flags.batch_size)]
        timings.time("dequeue")
    batch = {
        key: torch.stack([buffers[key][m] for m in indices], dim=1) for key in buffers
    }
    initial_agent_state = (
        torch.cat(ts, dim=1)
        for ts in zip(*[initial_agent_state_buffers[m] for m in indices])
    )
    timings.time("batch")
    for m in indices:
        free_queue.put(m)
    timings.time("enqueue")
    batch = {k: t.to(device=flags.device, non_blocking=True) for k, t in batch.items()}
    initial_agent_state = tuple(
        t.to(device=flags.device, non_blocking=True) for t in initial_agent_state
    )
    timings.time("device")
    return batch, initial_agent_state


def learn(
    flags,
    model,
    batch,
    initial_agent_state,
    optimizer,
    scheduler,
    lock=threading.Lock(),  # noqa: B008
):
    """Performs a learning (optimization) step."""
    with lock:

        #model.train()

        learner_outputs, unused_state = model(batch, initial_agent_state)

        # Take final value function slice for bootstrapping.
        bootstrap_value = learner_outputs["baseline"][-1]

        # Move from obs[t] -> action[t] to action[t] -> obs[t].
        batch = {key: tensor[1:] for key, tensor in batch.items()}
        learner_outputs = {key: tensor[:-1] for key, tensor in learner_outputs.items()}

        rewards = batch["reward"]
        if flags.reward_clipping == "abs_one":
            clipped_rewards = torch.clamp(rewards, -1, 1)
        elif flags.reward_clipping == "none":
            clipped_rewards = rewards

        discounts = (~batch["done"]).float() * flags.discounting

        vtrace_returns = vtrace.from_logits(
            behavior_policy_logits=batch["policy_logits"],
            target_policy_logits=learner_outputs["policy_logits"],
            actions=batch["action"],
            discounts=discounts,
            rewards=clipped_rewards,
            values=learner_outputs["baseline"],
            bootstrap_value=bootstrap_value,
        )

        pg_loss = compute_policy_gradient_loss(
            learner_outputs["policy_logits"],
            batch["action"],
            vtrace_returns.pg_advantages,
        )
        baseline_loss = flags.baseline_cost * compute_baseline_loss(
            vtrace_returns.vs - learner_outputs["baseline"]
        )
        entropy_loss = flags.entropy_cost * compute_entropy_loss(
            learner_outputs["policy_logits"]
        )

        total_loss = pg_loss + baseline_loss + entropy_loss

        episode_returns = batch["episode_return"][batch["done"]]
        stats = {
            "episode_returns": tuple(episode_returns.cpu().numpy()),
            "mean_episode_return": torch.mean(episode_returns).item(),
            "total_loss": total_loss.item(),
            "pg_loss": pg_loss.item(),
            "baseline_loss": baseline_loss.item(),
            "entropy_loss": entropy_loss.item(),
        }

        optimizer.zero_grad()
        total_loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), flags.grad_norm_clipping)
        optimizer.step()
        scheduler.step()

        global actor_model
        actor_model.load_state_dict(model.state_dict())
        return stats

def create_buffers(flags, obs_shape, num_actions) -> Buffers:
    T = flags.unroll_length
    specs = dict(
        frame=dict(size=(T + 1, *obs_shape), dtype=torch.uint8),
        reward=dict(size=(T + 1,), dtype=torch.float32),
        done=dict(size=(T + 1,), dtype=torch.bool),
        episode_return=dict(size=(T + 1,), dtype=torch.float32),
        episode_step=dict(size=(T + 1,), dtype=torch.int32),
        policy_logits=dict(size=(T + 1, num_actions), dtype=torch.float32),
        baseline=dict(size=(T + 1,), dtype=torch.float32),
        last_action=dict(size=(T + 1,), dtype=torch.int64),
        action=dict(size=(T + 1,), dtype=torch.int64),
    )
    global buffers
    buffers = {key: [] for key in specs}
    for _ in range(flags.num_buffers):
        for key in buffers:
            ## torch.empty may result in a Bug on vtrace calculate because random values are of out of bound
            #buffers[key].append(torch.empty(**specs[key]).share_memory_())
            buffers[key].append(torch.zeros(**specs[key]).share_memory_())
    return buffers

def update_buffers(flags, updated_datas):
    global free_queue
    global full_queue
    index = free_queue.get()
    T = flags.unroll_length
    b_size = len(buffers["frame"])
    for key in buffers.keys():
        if(b_size >= T):
            buffers[key].pop(0)
        buffers[key].append(updated_datas[key][0])
    #logging.info("# updated episode !")
    full_queue.put(index)
    return buffers

def train(flags):  # pylint: disable=too-many-branches, too-many-statements
    if flags.xpid is None:
        flags.xpid = "coknight-%s-%s" % (flags.remark,time.strftime("%Y%m%d-%H%M%S"))
    plogger = file_writer.FileWriter(
        xpid=flags.xpid, xp_args=flags.__dict__, rootdir=flags.savedir
    )
    checkpointpath = os.path.expandvars(
        os.path.expanduser("%s/%s/%s" % (flags.savedir, flags.xpid, "model.tar"))
    )

    if flags.num_buffers is None:  # Set sensible default for num_buffers.
        flags.num_buffers = max(2 * flags.num_actors, flags.batch_size)
    if flags.num_actors >= flags.num_buffers:
        raise ValueError("num_buffers should be larger than num_actors")
    if flags.num_buffers < flags.batch_size:
        raise ValueError("num_buffers should be larger than batch_size")

    T = flags.unroll_length
    B = flags.batch_size

    flags.device = None
    if not flags.disable_cuda and torch.cuda.is_available():
        logging.info("Using CUDA.")
        flags.device = torch.device("cuda")
    else:
        logging.info("Not using CUDA.")
        flags.device = torch.device("cpu")

    env = create_env(flags)

    global actor_model
    actor_model = Net(env.observation_space.shape, env.action_space.n)
    buffers = create_buffers(flags, env.observation_space.shape, actor_model.num_actions)

    # Add initial RNN state.
    initial_agent_state_buffers = []
    for _ in range(flags.num_buffers):
        state = actor_model.initial_state(batch_size=1)
        for t in state:
            t.share_memory_()
        initial_agent_state_buffers.append(state)

    global free_queue
    global full_queue
    ctx = mp.get_context("fork")
    free_queue = ctx.SimpleQueue()
    full_queue = ctx.SimpleQueue()


    global learner_model
    learner_model = Net(
            env.observation_space.shape, env.action_space.n
    ).to(device=flags.device)

    optimizer = torch.optim.RMSprop(
        learner_model.parameters(),
        lr=flags.learning_rate,
        momentum=flags.momentum,
        eps=flags.epsilon,
        alpha=flags.alpha,
    )

    def lr_lambda(epoch):
        return 1 - min(epoch * T * B, flags.total_steps) / flags.total_steps

    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    logger = logging.getLogger("logfile")
    stat_keys = [
        "total_loss",
        "mean_episode_return",
        "pg_loss",
        "baseline_loss",
        "entropy_loss",
    ]
    logger.info("# Step\t%s", "\t".join(stat_keys))

    step, stats = 0, {}

    def batch_and_learn(i, lock=threading.Lock()):
        """Thread target for the learning process."""
        nonlocal step, stats
        timings = prof.Timings()
        while step < flags.total_steps:
            timings.reset()
            batch, agent_state = get_batch(
                flags,
                free_queue,
                full_queue,
                buffers,
                initial_agent_state_buffers,
                timings,
            )
            stats = learn(
                flags, learner_model, batch, agent_state, optimizer, scheduler
            )
            timings.time("learn")
            with lock:
                to_log = dict(step=step)
                to_log.update({k: stats[k] for k in stat_keys})
                plogger.log(to_log)
                step += T * B

        if i == 0:
            logging.info("Batch and learn: %s", timings.summary())

    for m in range(flags.num_buffers):
        free_queue.put(m)

    threads = []
    for i in range(flags.num_learner_threads):
        thread = threading.Thread(
            target=batch_and_learn, name="batch-and-learn-%d" % i, args=(i,)
        )
        thread.start()
        threads.append(thread)

    def checkpoint():
        if flags.disable_checkpoint:
            return
        logging.info("Saving checkpoint to %s", checkpointpath)
        torch.save(
            {
                "model_state_dict": actor_model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "scheduler_state_dict": scheduler.state_dict(),
                "flags": vars(flags),
            },
            checkpointpath,
        )

    timer = timeit.default_timer
    try:
        last_checkpoint_time = timer()
        while step < flags.total_steps:
            start_step = step
            start_time = timer()
            time.sleep(10)

            if timer() - last_checkpoint_time > 10 * 60:  # Save every 10 min.
                checkpoint()
                last_checkpoint_time = timer()

            sps = (step - start_step) / (timer() - start_time)
            if stats.get("episode_returns", None):
                mean_return = (
                    "Return per episode: %.1f. " % stats["mean_episode_return"]
                )
            else:
                mean_return = ""
            total_loss = stats.get("total_loss", float("inf"))
            logging.info(
                "Steps %i @ %.1f SPS. Loss %f. %sStats:\n%s",
                step,
                sps,
                total_loss,
                mean_return,
                pprint.pformat(stats),
            )
    except KeyboardInterrupt:
        return  # Try joining actors then quit.
    else:
        for thread in threads:
            thread.join()
        logging.info("Learning finished after %d steps.", step)
    finally:
        for _ in range(flags.num_actors):
            free_queue.put(None)
 

    checkpoint()
    plogger.close()

'''
grpc implement
'''
class ActorInferenceRpc(rpcenv_pb2_grpc.RPCActorInferenceServicer):
    def StreamingInference(self, request, context):
        with torch.no_grad():
            global learner_model
            #learner_model.eval()
            (s_dict, core_state) = learner_model(pickle.loads(request.inter_tensors).cuda(),
                                    pickle.loads(request.agent_state),
                                    request.cut_layer,
                                    LearnerInferenceMode = True,
                                    T=request.T, B=request.B,
                                    reward=pickle.loads(request.reward).cuda())
            for k,v in s_dict.items():
                s_dict[k] = v.cpu()
            core_state = list(map(lambda x:x.cpu(),core_state))
            outputs = (s_dict,core_state)
            return rpcenv_pb2.Action(agent_output_state = pickle.dumps(outputs))

class ActorUpdateModelRPC(rpcenv_pb2_grpc.RPCModelUpdateServicer):
    def StreamingModelUpdate(self, request, context):
        global actor_model
        return rpcenv_pb2.Model(parameters = pickle.dumps(actor_model.state_dict()))

class ActorUploadTrajectoryRPC(rpcenv_pb2_grpc.UploadTrajectoryServicer):
    def TrajectoryUpload(self, request, context):
        update_buffers(flags, pickle.loads(request.datas))
        return rpcenv_pb2.Uploaded(ack = "ok")

async def serve():
    server = aio.server(futures.ThreadPoolExecutor(max_workers=48), options=[
        ('grpc.max_send_message_length', 1024 * 1024 * 1024),
        ('grpc.max_receive_message_length', 1024 * 1024 * 1024)])

    rpcenv_pb2_grpc.add_RPCActorInferenceServicer_to_server(ActorInferenceRpc(), server)
    rpcenv_pb2_grpc.add_RPCModelUpdateServicer_to_server(ActorUpdateModelRPC(), server)
    rpcenv_pb2_grpc.add_UploadTrajectoryServicer_to_server(ActorUploadTrajectoryRPC(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    try:
        await server.wait_for_termination()
        
    except KeyboardInterrupt:
        await server.stop(None)


def create_env(flags):
    return atari_wrappers.wrap_pytorch(
        atari_wrappers.wrap_deepmind(
            atari_wrappers.make_atari(flags.env),
            clip_rewards=False,
            frame_stack=True,
            scale=False,
        )
    )

def run_train(flags):

    if flags.mode == "train":
        train(flags)
    else:
        test(flags)
    ## wait for initial
    time.sleep(3)

def main(flags):

    thread = threading.Thread(target = run_train, args=(flags,))
    thread.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([serve()]))
    loop.close()

if __name__ == "__main__":
    flags = parser.parse_args()
    main(flags)
