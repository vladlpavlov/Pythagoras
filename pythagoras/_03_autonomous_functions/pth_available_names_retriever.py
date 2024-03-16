import sys
from typing import Any


def retrieve_objs_available_inside_autonomous_functions() -> dict[str,Any]:
    """Names available inside autonomous functions without explicit import.

   """
    result = dict(
        pth = sys.modules['pythagoras']
        , post_event = sys.modules['pythagoras'].post_event
        , print_event = sys.modules['pythagoras'].print_event
        )
    return result