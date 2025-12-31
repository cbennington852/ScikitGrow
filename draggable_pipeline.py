from draggable import Draggable , DraggableData
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
import PyQt5.QtWidgets as QtW
from PyQt5.QtGui import QDrag , QIcon , QPixmap , QCursor , QColor , QPolygon, QPen, QBrush, QIcon, QPainter
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from column_pipeline import DraggableColumn , ColumnsSection
from list_of_acceptable_sklearn_functions import SklearnAcceptableFunctions
from colors_and_appearance import AppAppearance

class GUILibarySubmodule(QtW.QGroupBox):
    def __init__(self , sublibary , render_type = "", hex_value = "",  **kwargs):
        super().__init__(**kwargs)
        self.layout = QVBoxLayout(self)
        self.setAcceptDrops(True)
        self.sublibary = sublibary
        self.setTitle(self.sublibary.library_name)
        if len(self.sublibary.function_calls) == 0:
            self.deleteLater()
        for sklearn in self.sublibary.function_calls:
            self.layout.addWidget(Draggable(
                name=str(sklearn.__name__),
                sklearn_function=sklearn,
                render_type=render_type,
                hex_color=hex_value
            ))
        
    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        e.accept()
        
    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        from_parent = widget.parentWidget()
        to_parent = self
        if isinstance(from_parent , GUILibarySubmodule) and isinstance(to_parent , GUILibarySubmodule):
            e.accept()
        elif isinstance(from_parent , PipelineSection) and isinstance(to_parent , GUILibarySubmodule):
            e.accept()
            from_parent.layout().removeWidget(widget)
            if from_parent.is_holding:
                from_parent.is_holding = False
            # tell previous parent to resize?
            from_parent.my_parent.resize_based_on_children()
            widget.deleteLater()


class PipelineSection(QtW.QGroupBox):
    """
    This only holds one thing. 
    """

    BASE_MINIMUM_HEIGHT = 80

    def __init__(self , accepting_function, title, my_parent , max_num_models = 100,  **kwargs):
        super().__init__( **kwargs)
        self.my_title = title
        self.setTitle(title)
        self.my_parent = my_parent
        self.max_num_models = max_num_models
        self.accepting_function = accepting_function
        self.setAcceptDrops(True)
        self.setMinimumHeight(PipelineSection.BASE_MINIMUM_HEIGHT)
        self.my_layout = QVBoxLayout()
        self.my_layout.setContentsMargins(ColumnsSection.width_from_start_mouth_to_left_side - 2 , 0 , 0 , 0)
        self.my_layout.setSpacing(0);  
        self.model_hovering = False
        self.is_holding = False
        self.setLayout(self.my_layout)

    def get_pipeline_objects(self):
        resulting_models = []
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , Draggable):
                parameters_as_dict = dict(child.data.parameters)
                curr = child.data.sklearn_function(**parameters_as_dict)
                resulting_models.append(curr)
        return resulting_models

    def pipeline_section_from_data( accepting_function, title, my_parent , data : list[DraggableData] , max_num_models):
        new_pipe = PipelineSection(
            accepting_function=accepting_function,
            title=title,
            my_parent=my_parent,
            max_num_models=max_num_models
        )
        for drag_data in data:
            # Make a new draggable.
            new_drag = Draggable.new_draggable_from_data(drag_data)
            print("New draggable" , new_drag)
            new_pipe.my_layout.addWidget(new_drag)
            print(new_drag)
            # add it to this.
        return new_pipe

    def get_data(self) -> list[DraggableData]:
        lst_data = []
        for model in self.get_models():
            lst_data.append(model.data)
        return lst_data

    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if isinstance(widget , Draggable):
            print("TEST" , widget.render_type , self.accepting_function(widget.data.sklearn_function) , self.accepting_function)
            if self.accepting_function(widget.data.sklearn_function):
                e.accept()        
                self.model_hovering = True
                self.repaint()
                
        else:
            e.ignore()

    def dragLeaveEvent(self, event):
        self.model_hovering = False

        # Check to see if this is empty, and change the is_holding status.
        self.is_holding = False 
        for child in self.findChildren(QtW.QWidget):
            self.is_holding = True
            break

        # Repaint the module
        self.repaint()
        event.accept() # Accept the leave event

    def get_num_models(self):
        return len(self.get_models())
    
    def get_models(self) -> list[Draggable]:
        res_models = []
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , Draggable):
                res_models.append(child)
        return res_models
    
    def paintEvent(self, e):
        if self.my_title == "Validator":
            if self.is_holding == True:
                painter = QPainter(self)
                painter.setPen(QColor(AppAppearance.PIPELINE_TITLE_COLOR))
                painter.drawText( 0 , 15 , self.my_title)
            else:
                painter = QPainter(self)
                # Writing the name of the thing.
                painter.setPen(QColor(AppAppearance.PIPELINE_TITLE_COLOR))
                painter.drawText( 0 , 15 , self.my_title)
                if self.model_hovering == True:
                    painter.setBrush(QColor(AppAppearance.PIPELINE_HOVER_COLOR))
                else:
                    painter.setBrush(QColor(AppAppearance.PIPELINE_NOT_HOVER_COLOR))

                left_right_margin = 10
                top_bottom_margin = 20
                painter.setPen(QColor(AppAppearance.PIPELINE_HOLDER_BORDER_COLOR))
                
                # tunable parameters
                height_block = self.height() - top_bottom_margin*2
                width_triangle = Draggable.POINTY_TRIANGLE_WIDTH
                width_center_block = self.width() - left_right_margin*2 - left_right_margin - width_triangle*2
                triangle_mid_y_axis = int(height_block / 2) + top_bottom_margin
                
                pointy_block = QPolygon([
                    QPoint(left_right_margin , triangle_mid_y_axis), # end of left point.
                    QPoint(width_triangle + left_right_margin, top_bottom_margin), # Top Left corner of triangle / box
                    QPoint(width_center_block + width_triangle  , top_bottom_margin), # Top Right corner of triangle / box
                    QPoint(width_center_block + 2*width_triangle , triangle_mid_y_axis), # end of right point.
                    QPoint(width_center_block + width_triangle , height_block + top_bottom_margin),
                    QPoint(width_triangle + left_right_margin , height_block + top_bottom_margin),
                ])

                painter.drawPolygon(pointy_block)

        elif self.my_title == "Models":
            if self.is_holding == True:
                painter = QPainter(self)
                painter.setPen(QColor(AppAppearance.PIPELINE_TITLE_COLOR))
                painter.drawText( 0 , 15 , self.my_title)
            else:
                painter = QPainter(self)
                # Writing the name of the thing.
                painter.setPen(QColor(AppAppearance.PIPELINE_TITLE_COLOR))
                painter.drawText( 0 , 15 , self.my_title)
                if self.model_hovering == True:
                    painter.setBrush(QColor(AppAppearance.PIPELINE_HOVER_COLOR))
                else:
                    painter.setBrush(QColor(AppAppearance.PIPELINE_NOT_HOVER_COLOR))
                painter.setPen(QColor(AppAppearance.PIPELINE_HOLDER_BORDER_COLOR))

                left_right_margin = 10
                top_bottom_margin = 20
                width_rect = self.width() - left_right_margin*2
                height_rect = self.height() - top_bottom_margin*2
                corner_radius = 15
                round_rect_y = top_bottom_margin
                round_rect_x = int(self.width() / 2) - int(width_rect/2)
                painter.drawRoundedRect(
                    round_rect_x, 
                    round_rect_y, 
                    width_rect,
                    height_rect,
                    corner_radius,
                    corner_radius
                )
        elif self.my_title == 'Preprocessors':
            painter = QPainter(self)
            
            if self.model_hovering == True:
                painter.fillRect(self.rect(), QColor(AppAppearance.PIPELINE_HOVER_COLOR))
            else:
                painter.fillRect(self.rect(), QColor(AppAppearance.PIPELINE_NOT_HOVER_COLOR))


            painter.setPen(QColor(AppAppearance.PIPELINE_HOLDER_BORDER_COLOR))
            painter.setBrush(QColor(AppAppearance.PIPELINE_PREPROCESSOR_BACKGROUND_COLOR))
            # Top level calculations
            width = self.width()
            height = self.height()
        

            # Top level input Calculations
            starting_x = 0
            starting_y = 0
            right_of_bevel_width = max(width - Draggable.left_of_bevel_width + 5,120)
            
            top_of_left_bevel_x = starting_x + Draggable.left_of_bevel_width 
            bottom_right_of_top_bevel_x = top_of_left_bevel_x + Draggable.bevel_slant_width + Draggable.bevel_width
            far_right_corner_x = bottom_right_of_top_bevel_x + Draggable.bevel_slant_width + right_of_bevel_width
            start_second_bevel = bottom_right_of_top_bevel_x + Draggable.bevel_slant_width + Draggable.space_in_between_two_bevels
            left_margin = 10

            space_in_between_two_bevels = Draggable.space_in_between_two_bevels

            #space_needed_for_mouth = height - ColumnsSection.height_between_top_mouth_and_top_bar*2
            space_needed_for_mouth = max(self.get_num_models() * DraggableColumn.block_height , DraggableColumn.block_height)

            second_bevel_x_offset = 40 + space_in_between_two_bevels
            # where to start the bevel from the left. 
            holder_block = QPolygon([
                    QPoint( 0 , 0),             # Left Top corner
                    QPoint(width , 0),          # Right Top corner
                    QPoint(width , ColumnsSection.height_between_top_mouth_and_top_bar),

                    QPoint(second_bevel_x_offset + ColumnsSection.bevel_left_start + ColumnsSection.width_from_start_mouth_to_left_side, ColumnsSection.height_between_top_mouth_and_top_bar), # right start bevel.
                    # Bottom right of bevel
                    QPoint(
                        second_bevel_x_offset + ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth
                        ),
                    # Bottom left of bevel
                    QPoint(
                        second_bevel_x_offset + ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth
                        ),
                    QPoint(
                        second_bevel_x_offset + ColumnsSection.bevel_left_start - (DraggableColumn.bevel_slant_width*2) - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar 
                        ),

                    # right top of mouth
                    QPoint(ColumnsSection.bevel_left_start + ColumnsSection.width_from_start_mouth_to_left_side, ColumnsSection.height_between_top_mouth_and_top_bar), # right start bevel.
                    # Bottom right of bevel
                    QPoint(
                        ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth
                        ),
                    # Bottom left of bevel
                    QPoint(
                        ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth
                        ),
                    QPoint(
                        ColumnsSection.bevel_left_start - (DraggableColumn.bevel_slant_width*2) - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar 
                        ),

                    # left top of mouth
                    QPoint(ColumnsSection.width_from_start_mouth_to_left_side , ColumnsSection.height_between_top_mouth_and_top_bar),
                    # Bottom of the mouth
                    QPoint(ColumnsSection.width_from_start_mouth_to_left_side , ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth),

                    QPoint(
                        ColumnsSection.bevel_left_start - (DraggableColumn.bevel_slant_width*2) - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth
                        ),
                    QPoint(
                        ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth + space_needed_for_mouth
                        ),
                    QPoint(
                        ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth + space_needed_for_mouth
                        ),
                    QPoint(
                        ColumnsSection.bevel_left_start + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth
                        ), # right start bevel.


                    QPoint(
                        second_bevel_x_offset + ColumnsSection.bevel_left_start - (DraggableColumn.bevel_slant_width*2) - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth
                        ),
                    QPoint(
                        second_bevel_x_offset + ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width - DraggableColumn.bevel_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth + space_needed_for_mouth
                        ),
                    # Bottom right of bevel
                    QPoint(
                        second_bevel_x_offset + ColumnsSection.bevel_left_start - DraggableColumn.bevel_slant_width + ColumnsSection.width_from_start_mouth_to_left_side, 
                        ColumnsSection.height_between_top_mouth_and_top_bar + DraggableColumn.bevel_depth + space_needed_for_mouth
                        ),
                    # Bottom left of bevel
                    QPoint(second_bevel_x_offset + ColumnsSection.bevel_left_start + ColumnsSection.width_from_start_mouth_to_left_side, 
                           ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth), # right start bevel.
                    
                    
                    
                
                    QPoint(width , ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth),

                    QPoint(width , height),     # Right Bottom corner
                    QPoint(0 , height)          # Left Bottom corner
                ])

            painter.drawPolygon(holder_block)
            # Render title
            painter.setPen(QColor(AppAppearance.PIPELINE_TITLE_COLOR))
            painter.drawText(15 , 20, self.my_title)

            # 5 putting all of the children inside of each other
            # 5.1 gather list of children
            lst_of_children = []
            for i in range(0 , self.my_layout.count()):
                if isinstance(self.my_layout.itemAt(i) , QtW.QWidgetItem):
                    temp_widget = self.my_layout.itemAt(i).widget()
                    lst_of_children.append(temp_widget)
            # 5.2 If more than one, move the bottoms inside of the ones on top of it.
            if len(lst_of_children) > 1:
                first_child = lst_of_children[0]
                for i in range(1 , len(lst_of_children)):
                    tmp  = lst_of_children[i]
                    new_x = first_child.geometry().topLeft().x()
                    new_y = first_child.geometry().topLeft().y() + i*Draggable.block_height
                    tmp.move(new_x , new_y)
            
        else:
            return super().paintEvent(e)

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        from_parent = widget.parentWidget()
        to_parent = self
        def check_is_correct_type():
            if not isinstance(widget , Draggable):
                e.ignore()
                return
        # remove the spacer ,and readadd to bottom.
        def remove_all_spacers():
            for i in range(0 , self.my_layout.count()):
                if isinstance(self.my_layout.itemAt(i) , QtW.QSpacerItem): 
                    temp_widget = self.my_layout.itemAt(i)
                    self.my_layout.removeItem(temp_widget)
                    del temp_widget
        
        def if_limit_remove_all_other_widgets():
            if (self.get_num_models() == self.max_num_models):
                # Remove one the children from this
                for child in self.findChildren(QtW.QWidget):
                    if isinstance(child , Draggable) and child != widget:
                        child.deleteLater()
            else:
                e.accept()
            
        check_is_correct_type()
        remove_all_spacers()
        if_limit_remove_all_other_widgets()
        # Handle replacement with parent module. If applicable
        if isinstance(from_parent , GUILibarySubmodule) and isinstance(to_parent , PipelineSection):
            self.my_layout.addWidget(widget.copy_self())
        else:
            # accept
            # Add the dang widget
            self.my_layout.addWidget(widget)
        # Accepts
        e.accept()
        # update is holding.
        self.is_holding = True            
        # tell the parent to resize.
        self.my_parent.resize_based_on_children()
        # add space to end of the layout to make it all squished to top.
        self.my_layout.addStretch()
        # Remove hovering attribute.
        self.model_hovering=False        
        # Re-render the group box
        self.repaint()

class PipelineData():
    def __init__(
            self ,
              pipeline_name : str,
              preprocessor_section : list[DraggableData],
              model_pipeline  : list[DraggableData],
              validator : list[DraggableData],
              x_pos : int,
              y_pos : int,
              ):
        # get_models -> data
        self.pipeline_name = pipeline_name
        self.preprocessor_section = preprocessor_section
        self.model_pipeline = model_pipeline
        self.validator = validator
        self.x_pos = x_pos,
        self.y_pos = y_pos

class Pipeline(QtW.QMdiSubWindow):
    all_pipelines = []

    BASE_PIPELINE_WIDTH = 400
    BASE_PIPELINE_HEIGHT = 400
    SECTION_PREPROCCESSOR_TITLE="Preprocessors"
    SECTION_MODEL_TITLE="Models"
    SECTION_VALIDATOR_TITLE="Validator"
    ###############################################
    # List of Filter / Accepting Functions
    ###############################################

    CLASSIFIER_FILTER = lambda x : x in SklearnAcceptableFunctions.CLASSIFIERS
    PREPROCESSOR_FILTER = lambda x : x in SklearnAcceptableFunctions.PREPROCESSORS
    REGRESSOR_FILTER = lambda x : x in SklearnAcceptableFunctions.REGRESSORS
    VALIDATOR_FILTER = lambda x : x in SklearnAcceptableFunctions.VALIDATORS
    MODEL_FILTER = lambda x : x in SklearnAcceptableFunctions.MODELS


    def __init__(self, my_parent, GUI_parent ,  **kwargs):
        super().__init__(GUI_parent, **kwargs)
        my_layout = QVBoxLayout()
        self.main_thing = QtW.QWidget()
        self.my_parent = my_parent
        self.setStyleSheet(f"background-color:{AppAppearance.PIPELINE_BACKGROUND_COLOR}")
        self.main_thing.setLayout(my_layout)
        self.setFixedSize(Pipeline.BASE_PIPELINE_WIDTH , Pipeline.BASE_PIPELINE_HEIGHT)
        self.name_pipeline = QtW.QLineEdit()
        self.name_pipeline.setText(f"pipeline {1 + len(self.my_parent.pipelines)}")
        self.preproccessor_pipe = PipelineSection(
            title=Pipeline.SECTION_PREPROCCESSOR_TITLE,
            accepting_function=Pipeline.PREPROCESSOR_FILTER,
            my_parent=self

        )
        self.model_pipe = PipelineSection(
            title=Pipeline.SECTION_MODEL_TITLE,
            accepting_function=Pipeline.MODEL_FILTER,
            my_parent=self,
            max_num_models=1
        )
        self.validator = PipelineSection(
            title=Pipeline.SECTION_VALIDATOR_TITLE,
            accepting_function=Pipeline.VALIDATOR_FILTER,
            my_parent=self,
            max_num_models=1
        )
        # set mimumum heights
        my_layout.addWidget(self.name_pipeline)
        my_layout.addWidget(self.preproccessor_pipe)
        my_layout.addWidget(self.model_pipe)
        my_layout.addWidget(self.validator)
        self.setWidget(self.main_thing)

    def get_pipeline_data(self) -> PipelineData:
        pipeline_data = PipelineData(
            pipeline_name=self.name_pipeline.text(),
            preprocessor_section=self.preproccessor_pipe.get_data(),
            model_pipeline=self.model_pipe.get_data(),
            validator=self.validator.get_data(),
            x_pos=self.pos().x(),
            y_pos=self.pos().y()
        )
        return pipeline_data

    def pipeline_from_data(GUI_parent , my_parent, data : PipelineData):
        # THIS RETURNS A PIPELINE
        new_pipeline = Pipeline(
            my_parent=my_parent,
            GUI_parent=GUI_parent
        )
        new_pipeline.validator = PipelineSection.pipeline_section_from_data(
            accepting_function=Pipeline.VALIDATOR_FILTER,
            title=Pipeline.SECTION_VALIDATOR_TITLE,
            my_parent=new_pipeline,
            data=data.validator,
            max_num_models=1
        )
        new_pipeline.model_pipe = PipelineSection.pipeline_section_from_data(
            accepting_function=Pipeline.MODEL_FILTER,
            title=Pipeline.SECTION_MODEL_TITLE,
            my_parent=new_pipeline,
            data=data.model_pipeline,
            max_num_models=1
        )
        new_pipeline.preproccessor_pipe = PipelineSection.pipeline_section_from_data(
            accepting_function=Pipeline.PREPROCESSOR_FILTER,
            title=Pipeline.SECTION_PREPROCCESSOR_TITLE,
            my_parent=new_pipeline,
            data=data.preprocessor_section,
            max_num_models=None
        )
        # Remove old layout
        new_pipeline.main_thing.deleteLater()
        # make new layout. 
        main_thing = QWidget()
        my_layout = QtW.QVBoxLayout()
        my_layout.addWidget(new_pipeline.preproccessor_pipe)        
        my_layout.addWidget(new_pipeline.model_pipe)
        my_layout.addWidget(new_pipeline.validator)
        main_thing.setLayout(my_layout)
        new_pipeline.setWidget(main_thing)
        print("Model form pipeline" , new_pipeline.model_pipe.get_models())
        new_pipeline.name_pipeline.setText(data.pipeline_name)
        print(data.x_pos , data.y_pos, type(data.x_pos) , type(data.y_pos))
        if isinstance(data.x_pos , tuple):
            data.x_pos = data.x_pos[0]
        if isinstance(data.y_pos , tuple):
            data.y_pos = data.y_pos[0]
        print(new_pipeline)
        new_pipeline.move(data.x_pos , data.y_pos)
        new_pipeline.resize_based_on_children()
        return new_pipeline
        
            
    def get_name_pipeline(self) -> str:
        return self.name_pipeline.text
    
    def resize_based_on_children(self):
        # get the number of pre-proccessors and their height, default to zero if one or below. 
        pre_proccessor_height = max((self.preproccessor_pipe.get_num_models()-1) * Draggable.BASE_HEIGHT , 0)
        # Resize the pipeline based on the children size n_stuff.
        self.setFixedHeight(Pipeline.BASE_PIPELINE_HEIGHT + pre_proccessor_height)
    

    def closeEvent(self, event):
        for x in range(0 , len(self.my_parent.pipelines)):
            if self.my_parent.pipelines[x] == self:
                del self.my_parent.pipelines[x]
                self.deleteLater()
                super(QtW.QMdiSubWindow, self).closeEvent(event)
                return
