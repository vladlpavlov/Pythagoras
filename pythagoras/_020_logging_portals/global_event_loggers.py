#
# def get_active_portals() -> list[DataPortal]:
#     active_portals = {}
#     active_portals[id(pth.default_portal)] = pth.default_portal
#     for portal in DataPortal.portals_stack:
#         active_portals[id(portal)] = portal
#     result = list(active_portals.values())
#     return result

#
# def register_exception_globally(exception_id = None, **kwargs):
#     path = current_date_gmt_string()
#     exc_type, exc_value, trace_back = sys.exc_info()
#     if exception_id is None:
#         exception_id = exc_type.__name__ + "_" + get_random_signature()
#     full_path = [path, exception_id]
#
#     for portal in DataPortal.active_portals():
#         portal.crash_history[full_path] = add_execution_environment_summary(
#             exc_value=exc_value, **kwargs)
#
#
# def register_event_globally(event_id, *args, **kwargs):
#     path = current_date_gmt_string()
#     if event_id is None:
#         event_id = get_random_signature()
#     full_path = [path, event_id]
#
#     for portal in DataPortal.active_portals():
#         portal.event_log[full_path] = add_execution_environment_summary(
#             *args,**kwargs)
