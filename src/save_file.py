from .GUI_libary_and_pipeline_mother import PipelineData , ColumnsWindowData
import pandas as pd

class SaveFile():
    def __init__(self , pipelines_data : list[PipelineData] , dataframe : pd.DataFrame , columns_data : ColumnsWindowData):
        # Check types.
        self.pipelines_data = pipelines_data
        self.dataframe = dataframe
        self.columns_data = columns_data

class SaveFileException(Exception):
    def __init__(self, *args):
        super().__init__(*args)