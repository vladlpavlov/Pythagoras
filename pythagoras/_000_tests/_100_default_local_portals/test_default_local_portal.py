from pythagoras import DefaultLocalPortal, BasicPortal, SwarmingPortal, _PortalTester
import tempfile
from unittest.mock import patch
from pathlib import Path
import pytest
import pythagoras as pth

@pytest.fixture
def mock_path_home():
    """Fixture to mock pathlib.Path.home to use a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_home:
        with patch("pathlib.Path.home", return_value=Path(temp_home)):
            yield Path(temp_home)

def test_default_local_portal(mock_path_home):
    with _PortalTester():
        DefaultLocalPortal._clear_all()
        portal_1 = DefaultLocalPortal()
        portal_2 = DefaultLocalPortal()
        portal_3 = DefaultLocalPortal()
        assert len(BasicPortal.all_portals) == 1

        assert ".pythagoras" in portal_1.base_dir
        assert ".default_portal" in portal_2.base_dir
        homepath = Path("~").expanduser()
        assert str(mock_path_home) in portal_3.base_dir

        assert isinstance(portal_1, SwarmingPortal)
        DefaultLocalPortal._clear_all()

def f():
    return 42

def test_work_with_no_portal(mock_path_home):
    with _PortalTester():
        DefaultLocalPortal._clear_all()
        assert len(BasicPortal.all_portals) == 0
        f_pure = pth.pure()(f)
        f_result = f_pure()
        assert f_result == 42
        assert len(BasicPortal.all_portals) == 1
        portal = DefaultLocalPortal()
        assert len(portal.execution_requests) == 0
        assert len(portal.execution_results) == 1
        assert len(portal.known_functions["Samos"]) == 1
        DefaultLocalPortal._clear_all()

