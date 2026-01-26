from PyQt5.QtCore import QSettings



class DataScratchSettings():

    _settings = None

    # Keys
    RECENT_FILES_KEY = "recent_files_key"

    def getSettings() -> QSettings:
        if DataScratchSettings._settings == None:
            DataScratchSettings._settings = QSettings("DataScratchGitHub" , "DataScratch")
            return DataScratchSettings._settings
        else:
            return DataScratchSettings._settings