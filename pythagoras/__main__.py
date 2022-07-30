import sys

from pythagoras.p_cloud import SharedStorage_P2P_Cloud, PFuncOutputAddress, PValueAddress, PFunctionCallSignature

if sys.argv[1] == SharedStorage_P2P_Cloud.__name__:
    assert len(sys.argv) == 5

    base_dir = sys.argv[2]
    address_prefix = sys.argv[3]
    address_hash_id = sys.argv[4]

    target_address = PFuncOutputAddress.from_strings(
            prefix = address_prefix
            , hash_id = address_hash_id
            , check_value_store = False)

    cloud = SharedStorage_P2P_Cloud(
        base_dir = base_dir
        , restore_from = target_address)

    func_call_signature_addr = PValueAddress.from_strings(
        prefix=address_prefix
        , hash_id=address_hash_id)

    func_call_signature = func_call_signature_addr.get()
    assert isinstance(func_call_signature, PFunctionCallSignature)
    func_name = func_call_signature.__name__
    func_arguments = func_call_signature.args_addr.get()

    cloud.sync_local_inprocess_function_call(func_name, func_arguments)
