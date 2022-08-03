from pythagoras import SharedStorage_P2P_Cloud, P_Cloud_Implementation
from pythagoras.p_cloud import _log_a_record


def test_unattributed_logging(tmpdir):
    cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir)
    event_log = cloud.event_log
    crash_history = cloud.crash_history
    event = "TEST"
    _log_a_record(event)
    _log_a_record(event)
    _log_a_record(event)
    _log_a_record(event,"exception")
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
        _log_a_record(f"Message # {j}")


def test_logging_from_cloudfunction(tmpdir):
    cloud = SharedStorage_P2P_Cloud(base_dir=tmpdir)
    event_log = cloud.event_log

    global sample_function
    sample_function = cloud.publish(sample_function)

    for i in range(N):
        sample_function(i=i)
    assert len(event_log) == N*N

    for i in range(N):
        sample_function(i=i)
    assert len(event_log) == N*N

    P_Cloud_Implementation._reset()