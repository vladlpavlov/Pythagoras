
from pythagoras._01_foundational_objects.hash_and_random_signatures import (
    get_random_signature)
from pythagoras._05_events_and_exceptions.type_retrievers import (
    retrieve_FunctionExecutionContext_class)
from pythagoras._05_events_and_exceptions.find_in_callstack import \
    find_local_var_in_callstack
from pythagoras._05_events_and_exceptions.global_event_loggers import (
    register_event_globally)

import pythagoras as pth


def get_current_function_execution_context():
    all_context_objects = find_local_var_in_callstack(name_to_find="_pth_ec"
        , class_to_find=retrieve_FunctionExecutionContext_class())
    if len(all_context_objects) > 0:
        return all_context_objects[0]
    else:
        return None


class EventPosterFactory:
    def __init__(self):
        pass

    def __getitem__(self, item):
        return EventPoster(event_type = item)

    def __call__(self, **kwargs):
        return EventPoster(event_type = None)(**kwargs)

class EventPoster:
    def __init__(self, event_type: str|None):
        assert isinstance(event_type, (str, type(None)))
        self.event_type = event_type

    def __call__(self,**kwargs) -> None:
        assert pth.is_correctly_initialized(), (
            "The Pythagoras package has not been correctly initialized.")
        context = get_current_function_execution_context()
        if context is not None:
            context.register_event(event_type = self.event_type, **kwargs)
        else:
            if self.event_type is not None:
                kwargs["event_type"] = self.event_type
                event_id = self.event_type + "_" + get_random_signature()
            else:
                event_id = get_random_signature()
            register_event_globally(**kwargs, event_id = event_id)

post_event = EventPosterFactory()

