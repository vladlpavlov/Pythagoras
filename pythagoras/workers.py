""" Classes and functions that enable stand-alone and subprocess workers.
"""
import sys

from pythagoras.p_cloud import PValueAddress

from pythagoras.p_cloud import KwArgsDict

from pythagoras.p_cloud import PFuncOutputAddress, P_Cloud_Implementation, SharedStorage_P2P_Cloud, \
    PFunctionCallSignature, PCloudizedFunctionSnapshot



def oneoff_subprocess_sharedstorage_worker():
    """Implementation of an entry point for running ane instance of a function.

    """
    assert len(sys.argv)==4
    base_dir = sys.argv[1]
    address_prefix = sys.argv[2]
    address_hash_id = sys.argv[3]

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



