# libraries
import json

from laplace_log import log


def json_style(d: dict | list, json_cls=None) -> str:
    '''Return a JSON string of a dictionary or list.'''
    try:
        return json.dumps(d, indent=4, sort_keys=True, default=str, cls=json_cls)
    except Exception as e:
        log.error(f"Error: {e}\n"
                  "Going back for string config.")
        return str(d)  # fallback if object is not JSON serializable