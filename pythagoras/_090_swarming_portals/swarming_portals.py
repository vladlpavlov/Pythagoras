from __future__ import annotations

import atexit
import os
from copy import deepcopy
from time import sleep
import random

import pandas as pd
from persidict import FileDirDict

from pythagoras import BasicPortal, build_execution_environment_summary
from pythagoras._010_basic_portals.foundation import _runtime
from pythagoras._820_strings_signatures_converters.random_signatures import get_random_signature
from pythagoras._800_persidict_extensions.overlapping_multi_dict import (
    OverlappingMultiDict)
from pythagoras._070_pure_functions.pure_core_classes import (
    PureCodePortal, PureFnExecutionResultAddr)
# from pythagoras._090_swarming_portals.clean_runtime_id import clean_runtime_id
from pythagoras._820_strings_signatures_converters.node_signatures import get_node_signature

from multiprocessing import get_context

from pythagoras._810_output_manipulators.output_suppressor import (
    OutputSuppressor)


class SwarmingPortal(PureCodePortal):
    compute_nodes: OverlappingMultiDict | None

    def __init__(self, base_dir:str
                 , dict_type:type = FileDirDict
                 , default_island_name:str = "Samos"
                 , p_consistency_checks:float|None = None
                 , n_background_workers:int|None = 3
                 , runtime_id:str|None = None
                 ):
        super().__init__(base_dir = base_dir
                         ,dict_type = dict_type
                         ,default_island_name = default_island_name
                         , p_consistency_checks=p_consistency_checks)
        n_background_workers = int(n_background_workers)
        assert n_background_workers >= 0
        self.n_background_workers = n_background_workers

        compute_nodes_dir = os.path.join(base_dir, "compute_nodes")
        compute_nodes = OverlappingMultiDict(
            dict_type=dict_type
            , dir_name=compute_nodes_dir
            , pkl=dict(digest_len=0, immutable_items=False)
            , json=dict(digest_len=0, immutable_items=False)
        )
        self.compute_nodes = compute_nodes

        if runtime_id is None:
            self.node_id = get_node_signature()
            runtime_id = get_random_signature()
            self.runtime_id = runtime_id
            address = [self.node_id, "runtime_id"]
            self.compute_nodes.pkl[address] = runtime_id
            # for portal in self.get_noncurrent_portals():
            #     portal.compute_nodes.pkl[address] = runtime_id

            if len(BasicPortal.all_portals) == 1:
                atexit.register(_clean_runtime_id)

            summary = build_execution_environment_summary()
            address = [self.node_id, "execution_environment"]
            self.compute_nodes.json[address] = summary
            # for portal in self.get_noncurrent_portals():
            #     portal.compute_nodes.json[address] = summary
        else:
            self.runtime_id = runtime_id

        for n in range(n_background_workers):
            self._launch_background_worker()


    def get_params(self) -> dict:
        """Get the portal's configuration parameters"""
        params = super().get_params()
        params["n_background_workers"]=self.n_background_workers
        params["runtime_id"]=self.runtime_id
        return params

    def describe(self) -> pd.DataFrame:
        """Get a DataFrame describing the portal's current state"""
        all_params = [super().describe()]
        all_params.append(_runtime(
            "Background workers"
            , self.n_background_workers))

        result = pd.concat(all_params)
        result.reset_index(drop=True, inplace=True)
        return result


    def parent_runtime_is_live(self):
        node_id = get_node_signature()
        address = [node_id, "runtime_id"]
        runtime_id = self.runtime_id
        with self:
            try:
                if runtime_id == self.compute_nodes.pkl[address]:
                    return True
            except:
                pass
        # for portal in BasicPortal.all_portals.values():
        #     try:
        #         with portal:
        #             if runtime_id == portal.compute_nodes.pkl[address]:
        #                 return True
        #     except:
        #         pass
        return False


    def _launch_background_worker(self):
        """Launch one background worker process."""
        init_params = deepcopy(self.get_params())
        init_params["n_background_workers"] = 0
        ctx = get_context("spawn")
        p = ctx.Process(target=_background_worker, kwargs=init_params)
        p.start()
        return p


    def _clear(self):
        address = [self.node_id, "runtime_id"]
        self.compute_nodes.pkl.delete_if_exists(address)
        self.compute_nodes = None
        super()._clear()


    @classmethod
    def _clear_all(cls):
        super()._clear_all()


    @classmethod
    def get_portal(cls, suggested_portal: PureCodePortal | None = None
                   ) -> SwarmingPortal:
        return BasicPortal.get_portal(suggested_portal)


    @classmethod
    def get_current_portal(cls) -> SwarmingPortal | None:
        """Get the current (default) portal object"""
        return BasicPortal._current_portal(expected_class=cls)


    @classmethod
    def get_noncurrent_portals(cls) -> list[SwarmingPortal]:
        return BasicPortal._noncurrent_portals(expected_class=cls)


    @classmethod
    def get_active_portals(cls) -> list[SwarmingPortal]:
        return BasicPortal._active_portals(expected_class=cls)

    def _randomly_delay_execution(self
            , p:float = 0.5
            , min_delay:float = 0.2 
            , max_delay:float = 1.2
            ) -> None:
        """Randomly delay execution by a given probability."""
        if self.entropy_infuser.uniform(0, 1) < p:
            delay = self.entropy_infuser.uniform(min_delay, max_delay)
            sleep(delay)

def _background_worker(**portal_init_params):
    """Background worker that keeps processing random execution requests."""
    portal_init_params["n_background_workers"] = 0
    with SwarmingPortal(**portal_init_params) as portal:
        portal._randomly_delay_execution(p=1)
        ctx = get_context("spawn")
        with OutputSuppressor():
            while True:
                if not portal.parent_runtime_is_live():
                    return
                p = ctx.Process(
                    target=_process_random_execution_request
                    , kwargs=portal_init_params)
                p.start()
                p.join()
                portal._randomly_delay_execution()


def _process_random_execution_request(**portal_init_params):
    """Process one random execution request."""
    portal_init_params["n_background_workers"] = 0
    with SwarmingPortal(**portal_init_params) as portal:
        max_addresses_to_consider = random.randint(200, 5000)
        # TODO: are 200 and 5000 good values for max_addresses_to_consider?
        with OutputSuppressor():
            candidate_addresses = []
            while len(candidate_addresses) == 0:
                if not portal.parent_runtime_is_live():
                    return
                for addr in portal.execution_requests:
                    new_address = PureFnExecutionResultAddr.from_strings(
                        prefix=addr[0], hash_value=addr[1]
                        , assert_readiness=False) # How does it handle portals?
                    if not new_address.needs_execution:
                        continue
                    if not new_address.can_be_executed:
                        continue
                    candidate_addresses.append(new_address)
                    if len(candidate_addresses) > max_addresses_to_consider:
                        break
                if len(candidate_addresses) == 0:
                    portal._randomly_delay_execution(p=1)
            random_address = portal.entropy_infuser.choice(candidate_addresses)
            random_address.execute()


def _clean_runtime_id():
    """ Clean runtime id.

    This function is called at the end of the program execution.
    It deletes the runtime_id record from all portals.
    """
    node_id = get_node_signature()
    address = [node_id, "runtime_id"]
    for portal_id in BasicPortal.all_portals:
        try:
            portal = BasicPortal.all_portals[portal_id]
            with portal:
                portal.compute_nodes.pkl.delete_if_exists(address)
        except:
            pass