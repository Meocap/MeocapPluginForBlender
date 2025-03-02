# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: tracker.proto
# Protobuf Python Version: 5.28.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    2,
    '',
    'tracker.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from .algebra import f32_pb2 as algebra_dot_f32__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rtracker.proto\x12\x07tracker\x1a\x11\x61lgebra.f32.proto\"\x87\x01\n\rTrackerReport\x12\x1e\n\x03rot\x18\x01 \x01(\x0b\x32\x11.algebra.f32.Quat\x12 \n\x05\x61\x63\x63\x65l\x18\x02 \x01(\x0b\x32\x11.algebra.f32.Vec3\x12\x11\n\ttimestamp\x18\x03 \x01(\x04\x12\x10\n\x08\x61\x63\x63uracy\x18\x04 \x01(\x02\x12\x0f\n\x07\x62\x61ttery\x18\x05 \x01(\x02\"\xb9\x05\n\x12\x42odyTrackerReports\x12.\n\x0eleft_lower_arm\x18\x01 \x01(\x0b\x32\x16.tracker.TrackerReport\x12/\n\x0fright_lower_arm\x18\x02 \x01(\x0b\x32\x16.tracker.TrackerReport\x12.\n\x0eleft_lower_leg\x18\x03 \x01(\x0b\x32\x16.tracker.TrackerReport\x12/\n\x0fright_lower_leg\x18\x04 \x01(\x0b\x32\x16.tracker.TrackerReport\x12$\n\x04head\x18\x05 \x01(\x0b\x32\x16.tracker.TrackerReport\x12$\n\x04hips\x18\x06 \x01(\x0b\x32\x16.tracker.TrackerReport\x12.\n\x0eleft_upper_arm\x18\x07 \x01(\x0b\x32\x16.tracker.TrackerReport\x12/\n\x0fright_upper_arm\x18\x08 \x01(\x0b\x32\x16.tracker.TrackerReport\x12.\n\x0eleft_upper_leg\x18\t \x01(\x0b\x32\x16.tracker.TrackerReport\x12/\n\x0fright_upper_leg\x18\n \x01(\x0b\x32\x16.tracker.TrackerReport\x12%\n\x05\x63hest\x18\x0b \x01(\x0b\x32\x16.tracker.TrackerReport\x12)\n\tleft_hand\x18\x0c \x01(\x0b\x32\x16.tracker.TrackerReport\x12*\n\nright_hand\x18\r \x01(\x0b\x32\x16.tracker.TrackerReport\x12)\n\tleft_foot\x18\x0e \x01(\x0b\x32\x16.tracker.TrackerReport\x12*\n\nright_foot\x18\x0f \x01(\x0b\x32\x16.tracker.TrackerReport*\xfb\x01\n\x0cTrackerIndex\x12\x10\n\x0cLeftLowerArm\x10\x00\x12\x11\n\rRightLowerArm\x10\x01\x12\x10\n\x0cLeftLowerLeg\x10\x02\x12\x11\n\rRightLowerLeg\x10\x03\x12\x08\n\x04Head\x10\x04\x12\x08\n\x04Hips\x10\x05\x12\x10\n\x0cLeftUpperArm\x10\x06\x12\x11\n\rRightUpperArm\x10\x07\x12\x10\n\x0cLeftUpperLeg\x10\x08\x12\x11\n\rRightUpperLeg\x10\t\x12\t\n\x05\x43hest\x10\n\x12\x0c\n\x08LeftHand\x10\x0b\x12\r\n\tRightHand\x10\x0c\x12\x0c\n\x08LeftFoot\x10\r\x12\r\n\tRightFoot\x10\x0e\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tracker_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_TRACKERINDEX']._serialized_start=884
  _globals['_TRACKERINDEX']._serialized_end=1135
  _globals['_TRACKERREPORT']._serialized_start=46
  _globals['_TRACKERREPORT']._serialized_end=181
  _globals['_BODYTRACKERREPORTS']._serialized_start=184
  _globals['_BODYTRACKERREPORTS']._serialized_end=881
# @@protoc_insertion_point(module_scope)
