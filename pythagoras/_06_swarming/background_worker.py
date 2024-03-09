from time import sleep
from copy import deepcopy
import os, sys
from multiprocessing import Process

from pythagoras._99_misc_utils.output_suppressor import OutputSuppressor
import pythagoras as pth


def process_random_execution_request(pth_init_params:dict):
    pth_init_params["n_background_workers"] = 0
    pth.initialize(**pth_init_params)

    with OutputSuppressor():

        candidate_addresses = []
        while len(candidate_addresses) == 0:
            random_delay = pth.entropy_infuser.uniform(0.5, 1.5)
            sleep(random_delay)
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

    with OutputSuppressor():
        while True:
            random_delay = pth.entropy_infuser.uniform(0.1, 0.5)
            sleep(random_delay)
            p = Process(
                target=process_random_execution_request
                , kwargs=subpr_kwargs)
            p.start()
            p.join()



def launch_background_worker(pth_init_params:dict | None = None):
    if pth_init_params is None:
        pth_init_params = deepcopy(pth.initialization_parameters)

    pth_init_params["n_background_workers"] = 0

    subpr_kwargs = dict(
        pth_init_params = pth_init_params)
    p = Process(target=background_worker, kwargs=subpr_kwargs)
    p.start()
    return p