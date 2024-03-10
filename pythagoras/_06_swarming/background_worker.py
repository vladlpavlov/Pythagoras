from time import sleep
from copy import deepcopy
from multiprocessing import get_context

from pythagoras._06_swarming.output_suppressor import OutputSuppressor
import pythagoras as pth



def parent_runtime_is_live():
    node_id = pth.get_node_signature()
    try:
        if pth.runtime_id == pth.execution_nodes[node_id,"runtime_id"]:
            return True
        else:
            return False
    except:
        return False


def process_random_execution_request(pth_init_params:dict):
    pth_init_params["n_background_workers"] = 0
    pth.initialize(**pth_init_params)

    with OutputSuppressor():

        candidate_addresses = []
        while len(candidate_addresses) == 0:
            random_delay = pth.entropy_infuser.uniform(0.5, 1.5)
            sleep(random_delay)
            if not parent_runtime_is_live():
                return
            for seq in pth.operational_hub.binary:
                new_addresses = pth.FunctionExecutionResultAddress.from_strings(
                    prefix=seq[0], hash_value=seq[1], assert_readiness=False)
                if not new_addresses.needs_execution:
                    continue
                if not new_addresses.can_be_executed:
                    continue

                candidate_addresses.append(new_addresses)
                if len(candidate_addresses) > 256: #TODO: randomize this
                    break

        random_address = pth.entropy_infuser.choice(candidate_addresses)
        random_address.execute()


def background_worker(pth_init_params:dict):
    pth_init_params["n_background_workers"] = 0
    pth.initialize(**pth_init_params)
    subpr_kwargs = dict(pth_init_params=pth_init_params)

    ctx = get_context("spawn")

    with OutputSuppressor():
        while True:
            random_delay = pth.entropy_infuser.uniform(0.1, 0.5)
            sleep(random_delay)
            if not parent_runtime_is_live():
                return
            p = ctx.Process(
                target=process_random_execution_request
                , kwargs=subpr_kwargs)
            p.start()
            p.join()



def launch_background_worker(pth_init_params:dict | None = None):
    if pth_init_params is None:
        pth_init_params = deepcopy(pth.initialization_parameters)

    pth_init_params["n_background_workers"] = 0
    pth_init_params["runtime_id"] = pth.runtime_id

    ctx = get_context("spawn")

    subpr_kwargs = dict(
        pth_init_params = pth_init_params)
    p = ctx.Process(target=background_worker, kwargs=subpr_kwargs)
    p.start()
    return p