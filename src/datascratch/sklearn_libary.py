import sklearn
from .draggable_parameter import BANNED_PARAMETERS
import inspect

class SubLibary():
    def __init__(self , function_calls , library_name):
        self.function_calls = function_calls
        self.library_name = library_name            

    def get_sklearn_parameters(sklearn_model_function_call):
        raw = inspect.signature(sklearn_model_function_call).parameters.items()
        full_list = []
        for item in raw:
            if item[0] not in BANNED_PARAMETERS:
                full_list.append(
                    (item[0] , item[1].default)
                )
        return full_list
    

    