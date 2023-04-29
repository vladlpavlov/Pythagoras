import os
import platform
from getpass import getuser
import socket

from pythagoras import uuid8andhalf

def test_uuid8andhalf():
    all_uuids = []
    for i in range(10_000):
        new_uuid = uuid8andhalf()
        assert isinstance(new_uuid, str)
        assert str(getuser()) in new_uuid
        assert str(os.getpid() ) in new_uuid
        assert str(socket.gethostname() ) in new_uuid
        assert str(platform.platform()) in new_uuid
        assert str( ) in new_uuid
        all_uuids += [new_uuid]
    assert len(all_uuids) == len(set(all_uuids))
