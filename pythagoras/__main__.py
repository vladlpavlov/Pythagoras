import sys

from pythagoras.p_cloud import SharedStorage_P2P_Cloud, PFuncOutputAddress, PValueAddress, PFunctionCallSignature, \
    KwArgsDict

if sys.argv[1] == SharedStorage_P2P_Cloud.__name__:
    assert len(sys.argv) == 6

    base_dir = sys.argv[2]
    address_prefix = sys.argv[3]
    address_descriptor = sys.argv[4]
    address_hash_value = sys.argv[5]

    target_address = PFuncOutputAddress.from_strings(
            prefix = address_prefix
            , descriptor = address_descriptor
            , hash_value = address_hash_value
            , check_value_store = False)

    cloud = SharedStorage_P2P_Cloud(
        base_dir = base_dir
        , restore_from = target_address)

    cloud.sync_local_inprocess_function_call(target_address)
