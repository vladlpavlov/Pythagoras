from persidict import PersiDict

class MultiPersiDict:
    """ TODO: move this class to persidict package."""
    def __init__(self, dict_type:type, dir_name:str, **subdicts_params):
        assert issubclass(dict_type, PersiDict)
        for subdict_name in subdicts_params:
            assert isinstance(subdicts_params[subdict_name], dict)
            self.__dict__[subdict_name] = dict_type(
                **subdicts_params[subdict_name]
                ,file_type=subdict_name
                ,dir_name=dir_name)

        def __getstate__(self):
            assert False, "This object should never be pickled"

        def __setstate__(self, state):
            assert False, "This object should never be pickled"