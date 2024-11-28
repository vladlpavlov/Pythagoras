from typing import Optional

from .foundation import BasicPortal


class PortalAwareClass:
    """A base class for objects that need to access a portal.

    The class enables functionality for storing and restoring its objects.
    When a portal-aware object is pickled, the portal data is not saved,
    and the object is pickled as if it were a regular object.
    When the object is unpickled, the portal is restored to the current portal.
    The "current" portal is the innermost portal
    in the stack of portal "with" statements. It means that
    a portal-aware object can only be unpickled from within a portal context.
    """

    _portal: BasicPortal|None

    def __init__(self, portal:Optional[BasicPortal]=None):
        self._portal = BasicPortal.get_portal(portal)


    @property
    def portal(self) -> BasicPortal:
        if not hasattr(self,"_portal") or self._portal is None:
            self.capture_portal()
        return self._portal


    def capture_portal(self):
        """Capture the current portal.

        This method is supposed to be called from within .__setstate__()
        """
        assert (not hasattr(self, "_portal")) or self._portal is None
        self._portal = BasicPortal._current_portal()

    def __getstate__(self):
        """This method is called when the object is pickled.

        Make sure NOT to include portal info the object's state
        while pickling it.
        """
        raise NotImplementedError(
            "PortalAwareClass objects must have custom __getstate__() method")


    def __setstate__(self, state):
        """This method is called when the object is unpickled.

        Portal information was not include into the object's state
        when it was pickled. Make sure to set the portal info
        when the object is unpickled by setting the portal to the current one.
        Use .capture_portal() method from within .__setstate__() achieve this.
        """
        raise NotImplementedError(
            "PortalAwareClass objects must have custom __setstate__() method")

    def __copy__(self):
        result = self.__new__(type(self))
        result.__setstate__(self.__getstate__())
        return result