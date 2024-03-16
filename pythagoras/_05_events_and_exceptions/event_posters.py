
from pythagoras._01_foundational_objects.hash_and_random_signatures import (
    get_random_signature)
from pythagoras._05_events_and_exceptions.type_retrievers import (
    retrieve_IdempotentFnExecutionContext_class)
from pythagoras._05_events_and_exceptions.find_in_callstack import (
    find_local_var_in_callstack)
from pythagoras._05_events_and_exceptions.global_event_loggers import (
    register_event_globally)

import pythagoras as pth


def get_current_function_execution_context():
    all_context_objects = find_local_var_in_callstack(name_to_find="_pth_ec"
        , class_to_find=retrieve_IdempotentFnExecutionContext_class())
    if len(all_context_objects) > 0:
        return all_context_objects[0]
    else:
        return None


class EventPosterFactory:
    def __init__(self, enable_printing: bool = False):
        self.enable_printing = enable_printing


    def __getitem__(self, item):
        return EventPoster(
            event_type = item, enable_printing = self.enable_printing)

    def __call__(self, *args, **kwargs):
        event_poster =  EventPoster(
            event_type = None, enable_printing = self.enable_printing)
        return event_poster(*args, **kwargs)

class EventPoster:
    def __init__(self, event_type: str|None, enable_printing: bool = False):
        assert isinstance(event_type, (str, type(None)))
        assert isinstance(enable_printing, bool)
        self.event_type = event_type
        self.enable_printing = enable_printing

    def __call__(self,*args, **kwargs) -> None:
        assert pth.is_correctly_initialized(), (
            "The Pythagoras package has not been correctly initialized.")
        fe_context = get_current_function_execution_context()
        if fe_context is not None:
            fe_context.register_event(
                self.event_type, *args, **kwargs)
        else:
            event_id = get_random_signature()
            if self.event_type is not None:
                kwargs["event_type"] = self.event_type
                event_id = self.event_type + "_" + event_id
            register_event_globally(event_id, *args, **kwargs, )

        if self.enable_printing:
            print("\n" + 15*"~" + " EVENT WAS POSTED " + 15*"~")
            if self.event_type is not None:
                print(f"Event type: {self.event_type}")
            if len(args) > 0:
                print(f"Event message: ", *args)
            if len(kwargs) > 0:
                print(f"Event parameters:")
                for k in kwargs:
                    print(f"\t{k}: {kwargs[k]}")


post_event = EventPosterFactory(enable_printing = False)
print_event = EventPosterFactory(enable_printing = True)

