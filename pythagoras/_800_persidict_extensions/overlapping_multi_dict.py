from persidict import PersiDict
from pythagoras._010_basic_portals.exceptions import NotAllowedError

# TODO: move this class to persidict package?

class OverlappingMultiDict:
    """A class that holds several PersiDict objects with different fyle_type-s.

    The class is designed to be used as a container for several PersiDict objects
    that have different file_type-s. All inner PersiDict objects
    have the same dir_name attribute. Each inner PersiDict object is accessible
    as an attribute of the OverlappingMultiDict object.
    The attribute name is the same as the file_type
    of the inner PersiDict object.

    OverlappingMultiDict allows to store several PersiDict objects
    in a single object, which can be useful for managing multiple types of data
    in a single file directory or in an s3 bucket.

    """
    def __init__(self, dict_type:type, dir_name:str, **subdicts_params):
        assert issubclass(dict_type, PersiDict)
        for subdict_name in subdicts_params:
            assert isinstance(subdicts_params[subdict_name], dict)
            self.__dict__[subdict_name] = dict_type(
                **subdicts_params[subdict_name]
                ,file_type=subdict_name
                ,dir_name=dir_name)

        def __getstate__(self):
            raise NotAllowedError("This object should never be pickled")

        def __setstate__(self, state):
            raise NotAllowedError("This object should never be pickled")