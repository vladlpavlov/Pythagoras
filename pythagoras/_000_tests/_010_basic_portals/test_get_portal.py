from pythagoras import BasicPortal, _PortalTester

def test_portal_nested(tmpdir):

    with _PortalTester():

        portal = BasicPortal(tmpdir)
        portal2 = BasicPortal(tmpdir)
        portal3 = BasicPortal(tmpdir)

        with portal:
            assert BasicPortal.get_portal() == portal
            assert BasicPortal.get_portal(portal3) == portal3
            with portal2:
                assert BasicPortal.get_portal() == portal2
                assert BasicPortal.get_portal(portal3) == portal3
                portal4 = BasicPortal(tmpdir)
                with portal3:
                    assert BasicPortal.get_portal() == portal3
                    assert BasicPortal.get_portal(portal2) == portal2
                    with portal2:
                        assert BasicPortal.get_portal() == portal2
                        assert BasicPortal.get_portal(portal) == portal
                    assert BasicPortal.get_portal() == portal3
                assert BasicPortal.get_portal(portal2) == portal2
                assert BasicPortal.get_portal() == portal2
                assert BasicPortal.get_portal(portal3) == portal3
            assert BasicPortal.get_portal() == portal