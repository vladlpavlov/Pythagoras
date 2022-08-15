from time import sleep

import pytest

from pythagoras import SharedStorage_P2P_Cloud, P_Cloud_Implementation
from pythagoras.p_cloud import post_log_entry
import pythagoras


def test_unattributed_logging(tmpdir):
    cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir)
    event_log = cloud.event_log
    crash_history = cloud.crash_history
    event = "TEST"
    post_log_entry(event)
    post_log_entry(event, name_prefix="DEMO")
    post_log_entry(event)
    post_log_entry(event,category="exception")
    unattributed_events = event_log.get_subdict("unattributed")
    unattributed_errors = crash_history.get_subdict("unattributed")
    assert len(unattributed_errors) == 1
    assert len(unattributed_events) == 3
    for k in unattributed_events:
        assert unattributed_events[k] == event

    P_Cloud_Implementation._reset()

N = 4

def sample_function(i:int):
    for j in range(N):
        post_log_entry(f"Message # {j}")


def test_logging_from_cloudfunction(tmpdir):
    cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir,
           persist_config_init=dict(p_idempotency_checks=0))
    event_log = cloud.event_log

    assert len(event_log) == 0

    global sample_function
    sample_function = cloud.cloudize_function(sample_function)

    for i in range(N):
        sample_function(i=i)
    assert len(event_log) == N*N

    for i in range(N):
        sample_function(i=i)
    assert len(event_log) == N*N

    cloud.persistent_config_params["p_idempotency_checks"]=1.0

    for i in range(N):
        sample_function(i=i)
    assert len(event_log) == 2*N*N

    P_Cloud_Implementation._reset()


def another_sample_function(i:int):
    for j in range(3):
        pythagoras.post_log_entry(f"Message # {j}")
def test_logging_from_cloudfunction_subprt(tmpdir):

    cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir
        ,persist_config_init=dict(p_idempotency_checks=0))

    event_log = cloud.event_log

    assert len(event_log) == 0

    global another_sample_function
    another_sample_function = cloud.cloudize_function(another_sample_function)

    another_sample_function._sync_subprocess_v(i=1)

    assert len(event_log) == 3

    P_Cloud_Implementation._reset()


def sample_function_N_3(i:int):
    pythagoras.post_log_entry(f"Message right before an exception")
    return i/0
def test_exceptiions_from_cloudfunction(tmpdir):

    cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir
        ,persist_config_init=dict(p_idempotency_checks=0))

    event_log = cloud.event_log
    crash_history = cloud.crash_history

    assert len(event_log) == 0
    assert len(crash_history) == 0

    global another_sample_function
    another_sample_function = cloud.cloudize_function(sample_function_N_3)

    with pytest.raises(BaseException):
        another_sample_function._sync_inprocess_v(i=1000)

    assert len(event_log) == 1
    assert len(crash_history) == 1

    P_Cloud_Implementation._reset()



def sample_function_N_4(i: int):
    pythagoras.post_log_entry(f"Message right before an exception i={i}")
    return i / 0


def test_exceptiions_from_cloudfunction_sp(tmpdir):

    cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir
            , persist_config_init=dict(p_idempotency_checks=0))

    event_log = cloud.event_log
    crash_history = cloud.crash_history

    assert len(event_log) == 0
    assert len(crash_history) == 0

    global another_sample_function
    another_sample_function = cloud.cloudize_function(sample_function_N_4)

    for j in range(3):
        with pytest.raises(BaseException):
            another_sample_function._sync_subprocess_v(i=1000+j)

    assert len(event_log) == 3
    assert len(another_sample_function._fsnapshot_event_log) == 3
    assert len(another_sample_function._fname_event_log) == 3

    assert len(crash_history) >= 6
    assert len(another_sample_function._fsnapshot_crash_history) == 6
    assert len(another_sample_function._fname_crash_history) == 6

    P_Cloud_Implementation._reset()


def sample_function_N_5(i: int):
    pythagoras.post_log_entry(f"Message right before an exception")
    return i / 0

def test_exceptiions_from_cloudfunction_asp(tmpdir):

    cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir
            , persist_config_init=dict(p_idempotency_checks=0))

    event_log = cloud.event_log
    crash_history = cloud.crash_history

    assert len(event_log) == 0
    assert len(crash_history) == 0

    global another_sample_function
    another_sample_function = cloud.cloudize_function(sample_function_N_5)

    addr = None

    for j in range(3):
        addr = another_sample_function._async_subprocess_a(i=1000+j)
        sleep(15)
        assert len(addr.fo_crash_history) == 1
        assert len(addr.fo_event_log) == 1

    assert len(another_sample_function._fsnapshot_crash_history) == 3
    assert len(another_sample_function._fname_crash_history) == 3
    assert len(another_sample_function._fsnapshot_event_log) == 3
    assert len(another_sample_function._fname_event_log) == 3

    assert len(event_log) == 3
    assert len(crash_history) >= 6

    P_Cloud_Implementation._reset()