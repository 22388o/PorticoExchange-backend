# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mpay.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nmpay.proto\x12\x04mpay\"\x10\n\x0eGetInfoRequest\"\"\n\x0fGetInfoResponse\x12\x0f\n\x07version\x18\x01 \x01(\t\"\x98\x01\n\x10GetRoutesRequest\x12\x18\n\x0b\x64\x65stination\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x18\n\x0bmin_success\x18\x02 \x01(\x02H\x01\x88\x01\x01\x12\x1c\n\x0fmin_success_ema\x18\x03 \x01(\x02H\x02\x88\x01\x01\x42\x0e\n\x0c_destinationB\x0e\n\x0c_min_successB\x12\n\x10_min_success_ema\"\xa0\x02\n\x11GetRoutesResponse\x12\x33\n\x06routes\x18\x01 \x03(\x0b\x32#.mpay.GetRoutesResponse.RoutesEntry\x1a\x86\x01\n\x06Routes\x12\x34\n\x06routes\x18\x02 \x03(\x0b\x32$.mpay.GetRoutesResponse.Routes.Route\x1a\x46\n\x05Route\x12\r\n\x05route\x18\x01 \x03(\t\x12\x14\n\x0csuccess_rate\x18\x02 \x01(\x01\x12\x18\n\x10success_rate_ema\x18\x03 \x01(\x01\x1aM\n\x0bRoutesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12-\n\x05value\x18\x02 \x01(\x0b\x32\x1e.mpay.GetRoutesResponse.Routes:\x02\x38\x01\"M\n\x13ListPaymentsRequest\x12\x10\n\x06\x62olt11\x18\x01 \x01(\tH\x00\x12\x16\n\x0cpayment_hash\x18\x02 \x01(\tH\x00\x42\x0c\n\nidentifier\"\xd2\x03\n\x14ListPaymentsResponse\x12\x34\n\x08payments\x18\x01 \x03(\x0b\x32\".mpay.ListPaymentsResponse.Payment\x1a\x83\x03\n\x07Payment\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x13\n\x0b\x64\x65stination\x18\x02 \x01(\t\x12\x14\n\x0cpayment_hash\x18\x03 \x01(\t\x12\x0e\n\x06\x61mount\x18\x04 \x01(\x04\x12\n\n\x02ok\x18\x05 \x01(\x08\x12<\n\x08\x61ttempts\x18\x06 \x03(\x0b\x32*.mpay.ListPaymentsResponse.Payment.Attempt\x12\x12\n\ncreated_at\x18\x07 \x01(\x04\x1a\xd2\x01\n\x07\x41ttempt\x12\n\n\x02id\x18\x01 \x01(\x04\x12\n\n\x02ok\x18\x02 \x01(\x08\x12\x0c\n\x04time\x18\x03 \x01(\x04\x12<\n\x04hops\x18\x04 \x03(\x0b\x32..mpay.ListPaymentsResponse.Payment.Attempt.Hop\x12\x12\n\ncreated_at\x18\x05 \x01(\x04\x1aO\n\x03Hop\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04node\x18\x02 \x01(\t\x12\x0f\n\x07\x63hannel\x18\x03 \x01(\t\x12\x11\n\tdirection\x18\x04 \x01(\x04\x12\n\n\x02ok\x18\x05 \x01(\x08\"\x9c\x01\n\nPayRequest\x12\x0e\n\x06\x62olt11\x18\x01 \x01(\t\x12\x19\n\x0cmax_fee_msat\x18\x02 \x01(\x04H\x00\x88\x01\x01\x12\x1c\n\x0f\x65xempt_fee_msat\x18\x03 \x01(\x04H\x01\x88\x01\x01\x12\x14\n\x07timeout\x18\x04 \x01(\x04H\x02\x88\x01\x01\x42\x0f\n\r_max_fee_msatB\x12\n\x10_exempt_fee_msatB\n\n\x08_timeout\"]\n\x0bPayResponse\x12\x14\n\x0cpayment_hash\x18\x01 \x01(\t\x12\x18\n\x10payment_preimage\x18\x02 \x01(\t\x12\x10\n\x08\x66\x65\x65_msat\x18\x03 \x01(\x04\x12\x0c\n\x04time\x18\x04 \x01(\x04\"\x18\n\x16ResetPathMemoryRequest\"K\n\x17ResetPathMemoryResponse\x12\x10\n\x08payments\x18\x01 \x01(\x04\x12\x10\n\x08\x61ttempts\x18\x02 \x01(\x04\x12\x0c\n\x04hops\x18\x03 \x01(\x04\x32\xc9\x02\n\x04Mpay\x12\x38\n\x07GetInfo\x12\x14.mpay.GetInfoRequest\x1a\x15.mpay.GetInfoResponse\"\x00\x12>\n\tGetRoutes\x12\x16.mpay.GetRoutesRequest\x1a\x17.mpay.GetRoutesResponse\"\x00\x12G\n\x0cListPayments\x12\x19.mpay.ListPaymentsRequest\x1a\x1a.mpay.ListPaymentsResponse\"\x00\x12,\n\x03Pay\x12\x10.mpay.PayRequest\x1a\x11.mpay.PayResponse\"\x00\x12P\n\x0fResetPathMemory\x12\x1c.mpay.ResetPathMemoryRequest\x1a\x1d.mpay.ResetPathMemoryResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mpay_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _GETROUTESRESPONSE_ROUTESENTRY._options = None
  _GETROUTESRESPONSE_ROUTESENTRY._serialized_options = b'8\001'
  _globals['_GETINFOREQUEST']._serialized_start=20
  _globals['_GETINFOREQUEST']._serialized_end=36
  _globals['_GETINFORESPONSE']._serialized_start=38
  _globals['_GETINFORESPONSE']._serialized_end=72
  _globals['_GETROUTESREQUEST']._serialized_start=75
  _globals['_GETROUTESREQUEST']._serialized_end=227
  _globals['_GETROUTESRESPONSE']._serialized_start=230
  _globals['_GETROUTESRESPONSE']._serialized_end=518
  _globals['_GETROUTESRESPONSE_ROUTES']._serialized_start=305
  _globals['_GETROUTESRESPONSE_ROUTES']._serialized_end=439
  _globals['_GETROUTESRESPONSE_ROUTES_ROUTE']._serialized_start=369
  _globals['_GETROUTESRESPONSE_ROUTES_ROUTE']._serialized_end=439
  _globals['_GETROUTESRESPONSE_ROUTESENTRY']._serialized_start=441
  _globals['_GETROUTESRESPONSE_ROUTESENTRY']._serialized_end=518
  _globals['_LISTPAYMENTSREQUEST']._serialized_start=520
  _globals['_LISTPAYMENTSREQUEST']._serialized_end=597
  _globals['_LISTPAYMENTSRESPONSE']._serialized_start=600
  _globals['_LISTPAYMENTSRESPONSE']._serialized_end=1066
  _globals['_LISTPAYMENTSRESPONSE_PAYMENT']._serialized_start=679
  _globals['_LISTPAYMENTSRESPONSE_PAYMENT']._serialized_end=1066
  _globals['_LISTPAYMENTSRESPONSE_PAYMENT_ATTEMPT']._serialized_start=856
  _globals['_LISTPAYMENTSRESPONSE_PAYMENT_ATTEMPT']._serialized_end=1066
  _globals['_LISTPAYMENTSRESPONSE_PAYMENT_ATTEMPT_HOP']._serialized_start=987
  _globals['_LISTPAYMENTSRESPONSE_PAYMENT_ATTEMPT_HOP']._serialized_end=1066
  _globals['_PAYREQUEST']._serialized_start=1069
  _globals['_PAYREQUEST']._serialized_end=1225
  _globals['_PAYRESPONSE']._serialized_start=1227
  _globals['_PAYRESPONSE']._serialized_end=1320
  _globals['_RESETPATHMEMORYREQUEST']._serialized_start=1322
  _globals['_RESETPATHMEMORYREQUEST']._serialized_end=1346
  _globals['_RESETPATHMEMORYRESPONSE']._serialized_start=1348
  _globals['_RESETPATHMEMORYRESPONSE']._serialized_end=1423
  _globals['_MPAY']._serialized_start=1426
  _globals['_MPAY']._serialized_end=1755
# @@protoc_insertion_point(module_scope)
