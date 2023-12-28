import sys

from pythagoras.OLD_p_cloud import SharedStorage_P2P_Cloud, PFuncOutputAddress, PValueAddress, PFunctionCallSignature, \
    KwArgsDict, post_log_entry

if sys.argv[1] == SharedStorage_P2P_Cloud.__name__:
    assert len(sys.argv) == 6

    base_dir = sys.argv[2]
    address_prefix = sys.argv[3]
    address_descriptor = sys.argv[4]
    address_hash_value = sys.argv[5]

    # post_log_entry() attributes posted events to an address, stored
    # in a variable named __fo_addr__ in one of callstack frames
    __fo_addr__ = PFuncOutputAddress.from_strings(
            prefix = address_prefix
            , descriptor = address_descriptor
            , hash_value = address_hash_value
            , check_value_store = False)

    cloud = SharedStorage_P2P_Cloud(
        base_dir = base_dir
        , restore_from = __fo_addr__)

    try:
        cloud.sync_local_inprocess_function_call(__fo_addr__)
    except BaseException as exc:
        post_log_entry(exc)
        raise
