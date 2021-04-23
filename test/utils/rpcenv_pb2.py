# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: rpcenv.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='rpcenv.proto',
  package='rpcenv',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0crpcenv.proto\x12\x06rpcenv\"\x18\n\x06\x41\x63tion\x12\x0e\n\x06\x61\x63tion\x18\x01 \x01(\x05\"z\n\x04Step\x12\x13\n\x0bobservation\x18\x01 \x01(\x0c\x12\x0e\n\x06reward\x18\x02 \x01(\x02\x12\x0c\n\x04\x64one\x18\x03 \x01(\x08\x12\x14\n\x0c\x65pisode_step\x18\x04 \x01(\x05\x12\x16\n\x0e\x65pisode_return\x18\x05 \x01(\x02\x12\x11\n\tcut_layer\x18\x06 \x01(\x05\"\x18\n\x04Pull\x12\x10\n\x08\x61\x63tor_id\x18\x01 \x01(\x05\"\x1b\n\x05Model\x12\x12\n\nparameters\x18\x01 \x01(\x0c\";\n\nTrajectory\x12\x10\n\x08\x61\x63tor_id\x18\x01 \x01(\x05\x12\x1b\n\x05\x64\x61tas\x18\x02 \x03(\x0b\x32\x0c.rpcenv.Step\"\x17\n\x08Uploaded\x12\x0b\n\x03\x61\x63k\x18\x01 \x01(\t2I\n\x11RPCActorInference\x12\x34\n\x12StreamingInference\x12\x0c.rpcenv.Step\x1a\x0e.rpcenv.Action\"\x00\x32G\n\x0eRPCModelUpdate\x12\x35\n\x14StreamingModelUpdate\x12\x0c.rpcenv.Pull\x1a\r.rpcenv.Model\"\x00\x32N\n\x10UploadTrajectory\x12:\n\x10TrajectoryUpload\x12\x12.rpcenv.Trajectory\x1a\x10.rpcenv.Uploaded\"\x00\x62\x06proto3'
)




_ACTION = _descriptor.Descriptor(
  name='Action',
  full_name='rpcenv.Action',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='action', full_name='rpcenv.Action.action', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=24,
  serialized_end=48,
)


_STEP = _descriptor.Descriptor(
  name='Step',
  full_name='rpcenv.Step',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='observation', full_name='rpcenv.Step.observation', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='reward', full_name='rpcenv.Step.reward', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='done', full_name='rpcenv.Step.done', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='episode_step', full_name='rpcenv.Step.episode_step', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='episode_return', full_name='rpcenv.Step.episode_return', index=4,
      number=5, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='cut_layer', full_name='rpcenv.Step.cut_layer', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=50,
  serialized_end=172,
)


_PULL = _descriptor.Descriptor(
  name='Pull',
  full_name='rpcenv.Pull',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='actor_id', full_name='rpcenv.Pull.actor_id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=174,
  serialized_end=198,
)


_MODEL = _descriptor.Descriptor(
  name='Model',
  full_name='rpcenv.Model',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='parameters', full_name='rpcenv.Model.parameters', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=200,
  serialized_end=227,
)


_TRAJECTORY = _descriptor.Descriptor(
  name='Trajectory',
  full_name='rpcenv.Trajectory',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='actor_id', full_name='rpcenv.Trajectory.actor_id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='datas', full_name='rpcenv.Trajectory.datas', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=229,
  serialized_end=288,
)


_UPLOADED = _descriptor.Descriptor(
  name='Uploaded',
  full_name='rpcenv.Uploaded',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='ack', full_name='rpcenv.Uploaded.ack', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=290,
  serialized_end=313,
)

_TRAJECTORY.fields_by_name['datas'].message_type = _STEP
DESCRIPTOR.message_types_by_name['Action'] = _ACTION
DESCRIPTOR.message_types_by_name['Step'] = _STEP
DESCRIPTOR.message_types_by_name['Pull'] = _PULL
DESCRIPTOR.message_types_by_name['Model'] = _MODEL
DESCRIPTOR.message_types_by_name['Trajectory'] = _TRAJECTORY
DESCRIPTOR.message_types_by_name['Uploaded'] = _UPLOADED
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Action = _reflection.GeneratedProtocolMessageType('Action', (_message.Message,), {
  'DESCRIPTOR' : _ACTION,
  '__module__' : 'rpcenv_pb2'
  # @@protoc_insertion_point(class_scope:rpcenv.Action)
  })
_sym_db.RegisterMessage(Action)

Step = _reflection.GeneratedProtocolMessageType('Step', (_message.Message,), {
  'DESCRIPTOR' : _STEP,
  '__module__' : 'rpcenv_pb2'
  # @@protoc_insertion_point(class_scope:rpcenv.Step)
  })
_sym_db.RegisterMessage(Step)

Pull = _reflection.GeneratedProtocolMessageType('Pull', (_message.Message,), {
  'DESCRIPTOR' : _PULL,
  '__module__' : 'rpcenv_pb2'
  # @@protoc_insertion_point(class_scope:rpcenv.Pull)
  })
_sym_db.RegisterMessage(Pull)

Model = _reflection.GeneratedProtocolMessageType('Model', (_message.Message,), {
  'DESCRIPTOR' : _MODEL,
  '__module__' : 'rpcenv_pb2'
  # @@protoc_insertion_point(class_scope:rpcenv.Model)
  })
_sym_db.RegisterMessage(Model)

Trajectory = _reflection.GeneratedProtocolMessageType('Trajectory', (_message.Message,), {
  'DESCRIPTOR' : _TRAJECTORY,
  '__module__' : 'rpcenv_pb2'
  # @@protoc_insertion_point(class_scope:rpcenv.Trajectory)
  })
_sym_db.RegisterMessage(Trajectory)

Uploaded = _reflection.GeneratedProtocolMessageType('Uploaded', (_message.Message,), {
  'DESCRIPTOR' : _UPLOADED,
  '__module__' : 'rpcenv_pb2'
  # @@protoc_insertion_point(class_scope:rpcenv.Uploaded)
  })
_sym_db.RegisterMessage(Uploaded)



_RPCACTORINFERENCE = _descriptor.ServiceDescriptor(
  name='RPCActorInference',
  full_name='rpcenv.RPCActorInference',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=315,
  serialized_end=388,
  methods=[
  _descriptor.MethodDescriptor(
    name='StreamingInference',
    full_name='rpcenv.RPCActorInference.StreamingInference',
    index=0,
    containing_service=None,
    input_type=_STEP,
    output_type=_ACTION,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_RPCACTORINFERENCE)

DESCRIPTOR.services_by_name['RPCActorInference'] = _RPCACTORINFERENCE


_RPCMODELUPDATE = _descriptor.ServiceDescriptor(
  name='RPCModelUpdate',
  full_name='rpcenv.RPCModelUpdate',
  file=DESCRIPTOR,
  index=1,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=390,
  serialized_end=461,
  methods=[
  _descriptor.MethodDescriptor(
    name='StreamingModelUpdate',
    full_name='rpcenv.RPCModelUpdate.StreamingModelUpdate',
    index=0,
    containing_service=None,
    input_type=_PULL,
    output_type=_MODEL,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_RPCMODELUPDATE)

DESCRIPTOR.services_by_name['RPCModelUpdate'] = _RPCMODELUPDATE


_UPLOADTRAJECTORY = _descriptor.ServiceDescriptor(
  name='UploadTrajectory',
  full_name='rpcenv.UploadTrajectory',
  file=DESCRIPTOR,
  index=2,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=463,
  serialized_end=541,
  methods=[
  _descriptor.MethodDescriptor(
    name='TrajectoryUpload',
    full_name='rpcenv.UploadTrajectory.TrajectoryUpload',
    index=0,
    containing_service=None,
    input_type=_TRAJECTORY,
    output_type=_UPLOADED,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_UPLOADTRAJECTORY)

DESCRIPTOR.services_by_name['UploadTrajectory'] = _UPLOADTRAJECTORY

# @@protoc_insertion_point(module_scope)
