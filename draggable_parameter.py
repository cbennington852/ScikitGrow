import PyQt5.QtWidgets as QtW

# This is an abstract class BTW.
class Parameter(QtW.QWidget):
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
        self.setValue(value)

    def text(self):
        return str(super().text())

class FloatSingleLine(QtW.QDoubleSpinBox):
    def __init__(self , name , value,  **kwargs):
        super().__init__(**kwargs)
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
    'n_jobs',
    'verbose'
}


def parameter_filter(name : str , value) -> Parameter:
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