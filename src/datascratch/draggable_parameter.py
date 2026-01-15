import PyQt5.QtWidgets as QtW

# This is an abstract class BTW.
class Parameter(QtW.QWidget):
    """
    Abstract class to handle parameter fields.

    Args:
        QtW (_type_): _description_
    """
    def __init__(self):
        pass

    def text():
        pass

# QSpinBox for int's
# QDoubleSpinBox for doubles

class SingleLineParameter(QtW.QLineEdit):
    def __init__(self , name , value,  **kwargs):
        super().__init__(**kwargs) 
        self.setText(str(value))

class IntSingleLine(QtW.QSpinBox):
    def __init__(self , name , value,  **kwargs):
        super().__init__(**kwargs)
        max_value = 2147483647 # this is the 32-bit int max for signed ints
        self.setMinimum(-max_value) # Or use a very small number like -1e9
        self.setMaximum(max_value) 
        self.setValue(value)

    def text(self):
        return str(super().text())

class FloatSingleLine(QtW.QDoubleSpinBox):
    def __init__(self , name , value,  **kwargs):
        super().__init__(**kwargs)
        self.setMinimum(float('-inf')) # Or use a very small number like -1e9
        self.setMaximum(float('inf')) 
        self.setValue(value)

    def text(self):
        return str(super().text())

class BooleanSingleLine(QtW.QCheckBox):
    def __init__(self , name , value,  **kwargs):
        super().__init__(**kwargs)
        self.setChecked(value)

    def text(self):
        return str(self.isChecked())
    

BANNED_PARAMETERS = {
    # Some parameters don't need to be changed.
    # Example: Verbose, which prints stuff out to the console, can be hidden from the user.
    'n_jobs',
    'verbose',
    'warm_start',
    'dtype'
}


def parameter_filter(name : str , value) -> Parameter:
    """
    Args:
        name (str): _description_
        value (_type_): _description_

    Returns:
        Parameter: _description_
    """
    try:
        if type(value) is int:
            return IntSingleLine(name , value)
        elif type(value) is float:
            return FloatSingleLine(name, value)
        elif type(value) is bool:
            return BooleanSingleLine(name , value)
        else:
            return SingleLineParameter(name , value)
    except:
        return SingleLineParameter(name , value)