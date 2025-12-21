from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QPushButton, QMessageBox, QWidget, QVBoxLayout, QLabel
from sklearn_libary import SubLibary
import PyQt5.QtWidgets as QtW
from PyQt5.QtCore import  QPoint
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag , QIcon , QPixmap , QCursor , QColor , QPolygon, QPen, QBrush, QIcon, QPainter
import PyQt5.QtCore as QtCore 
from draggable import Draggable , DraggableColumn
from sklearn.base import is_regressor, is_classifier
import sklearn

class GUILibary(QtW.QTabWidget):

    ###############################################
    # List of Filter / Accepting Functions
    ###############################################
    def model_filter(x):
        try:
            return is_classifier(x) or is_regressor(x)
        except:
            return False
    def regression_filter(x):
        try:
            return is_regressor(x)
        except:
            return False
    def classification_filter(x):
        try:
            return is_classifier(x)
        except:
            return False
    CLASSIFIER_FILTER = classification_filter
    PREPROCESSOR_FILTER = lambda x : hasattr(x, 'fit') and hasattr(x, 'transform') and (not hasattr(x , 'predict'))
    REGRESSOR_FILTER = regression_filter
    VALIDATOR_FILTER = lambda x : getattr(x, 'split', None) is not None and callable(getattr(x, 'split', None))
    MODEL_FILTER = model_filter





    def __init__(self , dataframe,  **kwargs):
        super().__init__(**kwargs)
        self.dataframe = dataframe
        sklearn_models = [
            (sklearn.linear_model,"#8F0177" , Draggable.BUBBLE),
            (sklearn.ensemble,"#360185" , Draggable.BUBBLE),
            (sklearn.neural_network, "#38008C", Draggable.BUBBLE)
            (sklearn.preprocessing, "#301CA0" ,Draggable.INTERLOCK_RIGHT),
            (sklearn.tree ,"#DE1A58" , Draggable.BUBBLE),
            (sklearn.model_selection , "#235622" , Draggable.POINTY)
        ]

        # Styling
        self.setTabPosition(QtW.QTabWidget.West)


        self.curr_index = 0
        def addModule(name , filter):    
            regressor_box = QtW.QWidget()
            regressor_layout = QtW.QVBoxLayout()
            regressor_box.setLayout(regressor_layout)
            for subsection , hex_color , render_type in sklearn_models:
                curr = GUILibarySubmodule(
                        sublibary=SubLibary.get_public_methods(
                            library=subsection,

                            filter_function=filter
                        ),
                        render_type=render_type,
                        hex_value=hex_color
                    )
                regressor_layout.addWidget(curr)
            scroll_regressor = QtW.QScrollArea()
            scroll_regressor.setWidget(regressor_box)
            scroll_regressor.setWidgetResizable(True)
            if isinstance(name , QIcon):
                self.addTab(scroll_regressor , "")
                self.setTabIcon(self.curr_index , name)
                self.setIconSize(QtCore.QSize(90 , 90))
            else:
                self.addTab(scroll_regressor , name)
            self.curr_index += 1
        

        addModule(QIcon(":/images/reggessor_icon.svg") , GUILibary.REGRESSOR_FILTER)
        addModule(QIcon(":/images/classification_icon.svg") , GUILibary.CLASSIFIER_FILTER)
        addModule(QIcon(":/images/preproccessor_icon.svg") , GUILibary.PREPROCESSOR_FILTER)
        addModule(QIcon(":/images/validators_icon.svg") , GUILibary.VALIDATOR_FILTER)


        self.addTab(self.cols_tab() ,"")
        self.setTabIcon(self.curr_index , QIcon(":/images/columns_icon.svg"))

        curr_index = 0



    def cols_tab(self):
        cols = ColumnsSubmodule(self.dataframe.columns.to_list())
        scroll = QtW.QScrollArea()
        scroll.setWidget(cols)
        scroll.setWidgetResizable(True)
        return scroll


class ColumnsSubmodule(QtW.QWidget):
    def __init__(self , lst_cols , **kwargs):
        super().__init__(**kwargs)
        self.layout = QVBoxLayout(self)
        self.setAcceptDrops(True)
        self.lst_cols = lst_cols
        for col in self.lst_cols:
            new_widget = DraggableColumn(col)
            self.layout.addWidget(new_widget)
    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        e.accept()
        
    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        from_parent = widget.parentWidget()
        to_parent = self
        if isinstance(from_parent , ColumnsSubmodule) and isinstance(to_parent , ColumnsSubmodule):
            e.accept()
        elif isinstance(from_parent , ColumnsSection) and isinstance(to_parent , ColumnsSubmodule):
            e.accept()
            from_parent.layout().removeWidget(widget)
            widget.deleteLater()

class GUILibarySubmodule(QtW.QGroupBox):
    def __init__(self , sublibary : SubLibary , render_type = "", hex_value = "",  **kwargs):
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
            widget.deleteLater()

class ColumnsSection(QtW.QGroupBox):
    def __init__(self , title, my_parent , max_num_cols = 100, **kwargs):
        super().__init__( **kwargs)
        self.my_title = title
        self.my_parent = my_parent
        self.max_num_cols = max_num_cols
        self.resize(200 , 90)
        self.hovering = False
        self.setAcceptDrops(True)
        self.my_layout = QVBoxLayout()
        self.setStyleSheet("")
        self.my_layout.setContentsMargins(ColumnsSection.width_from_start_mouth_to_left_side - 2 , 0 , 0 , 0)
        self.my_layout.setSpacing(0);  
        self.setLayout(self.my_layout)
        self.setTitle(self.my_title)
        self.my_layout.addStretch()


    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if isinstance(widget , DraggableColumn):
            e.accept()
            self.hovering=True        
            self.repaint()
        else:
            e.ignore()

    def dragLeaveEvent(self, e):
        self.hovering = False
        self.repaint()
        e.accept() 
    
    def get_num_cols(self):
        num = 0
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , DraggableColumn):
                num += 1
        return num
    
    def get_cols(self) -> list[DraggableColumn]:
        res_cols = []
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , DraggableColumn):
                res_cols.append(child)
        return res_cols
    
    bevel_left_start = DraggableColumn.bevel_width + DraggableColumn.bevel_slant_width*2 + DraggableColumn.left_of_bevel_width
    bottom_right_of_top_bevel_x = bevel_left_start + DraggableColumn.bevel_slant_width + DraggableColumn.bevel_width
    width_from_start_mouth_to_left_side = 10
    height_between_top_mouth_and_top_bar = 30
    
    def paintEvent(self, event):
        painter = QPainter(self)
        

        painter.setPen(QColor("#040404"))
        painter.setBrush(QColor("#B5B3B3"))

        if self.hovering == True:
            painter.fillRect(self.rect(), QColor("lightgray"))

        # Top level calculations
        width = self.width()
        height = self.height()

        #space_needed_for_mouth = height - ColumnsSection.height_between_top_mouth_and_top_bar*2
        space_needed_for_mouth = max(self.get_num_cols() * DraggableColumn.block_height , DraggableColumn.block_height )

        # where to start the bevel from the left. 
        holder_block = QPolygon([
            QPoint( 0 , 0),             # Left Top corner
            QPoint(width , 0),          # Right Top corner

            # right top of mouth
            QPoint(width , ColumnsSection.height_between_top_mouth_and_top_bar),

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
            
           
            QPoint(width , ColumnsSection.height_between_top_mouth_and_top_bar + space_needed_for_mouth),

            QPoint(width , height),     # Right Bottom corner
            QPoint(0 , height)          # Left Bottom corner
        ])

        painter.drawPolygon(holder_block)
        painter.setPen(QColor(Qt.black))
        painter.drawText(15 , 20 ,f"{self.my_title}")

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
                new_y = first_child.geometry().topLeft().y() + i*DraggableColumn.block_height
                tmp.move(new_x , new_y)
        

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        # remove the spacer ,and readadd to bottom.
        for i in range(0 , self.my_layout.count()):
            if isinstance(self.my_layout.itemAt(i) , QtW.QSpacerItem): 
                temp_widget = self.my_layout.itemAt(i)
                self.my_layout.removeItem(temp_widget)
                del temp_widget
        
        if (self.get_num_cols() == self.max_num_cols):
            # Remove one the children from this
            for child in self.findChildren(QtW.QWidget):
                if isinstance(child , DraggableColumn) and child != widget:
                    e.accept()
                    self.my_layout.addWidget(widget)
                    child.deleteLater()
                    return
        # we can see the previous parent
        from_parent = widget.parentWidget()
        to_parent = self
        self.my_layout.addWidget(widget)
        if not isinstance(widget , DraggableColumn):
            e.ignore()
            return
        if isinstance(from_parent , ColumnsSubmodule) and isinstance(to_parent , ColumnsSection):
            e.accept()
            self.my_parent.resize_based_on_children()
            # Below adds a new widget copy of draggable to the library
            from_parent.layout.insertWidget(from_parent.layout.indexOf(widget) , widget.copy_self())
        elif isinstance(from_parent , ColumnsSection) and isinstance(to_parent , ColumnsSection):
            e.accept()
            self.my_parent.resize_based_on_children()


        self.my_layout.addStretch()
        self.hovering=False        
        self.repaint()

         # for the not first widgets, take their positons and offset by the bevel height 

#class PreProccessorPipelineSection(QtW.QGroupBox):

class PipelineSection(QtW.QGroupBox):
    """
    This only holds one thing. 
    """
    def __init__(self , accepting_function, title, max_num_models = 100,  **kwargs):
        super().__init__( **kwargs)
        self.my_title = title
        self.setTitle(title)
        self.max_num_models = max_num_models
        self.accepting_function = accepting_function
        self.setAcceptDrops(True)
        self.my_layout = QVBoxLayout()
        self.model_hovering = False
        self.is_holding = False
        self.setLayout(self.my_layout)

    def get_pipeline_objects(self):
        resulting_models = []
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , Draggable):
                parameters_as_dict = dict(child.parameters)
                curr = child.sklearn_function(**parameters_as_dict)
                resulting_models.append(curr)
        return resulting_models

    def dragEnterEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if isinstance(widget , Draggable):
            if self.accepting_function(widget.sklearn_function):
                e.accept()        
                self.model_hovering = True
                self.repaint()
                
        else:
            e.ignore()

    def dragLeaveEvent(self, event):
        self.model_hovering = False
        self.repaint()
        event.accept() # Accept the leave event

    def get_num_models(self):
        num = 0
        for child in self.findChildren(QtW.QWidget):
            if isinstance(child , Draggable):
                num += 1
        return num
    
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
                painter.setPen(QColor("#040404"))
                painter.drawText( 0 , 15 , self.my_title)
            else:
                painter = QPainter(self)
                # Writing the name of the thing.
                painter.setPen(QColor("#040404"))
                painter.drawText( 0 , 15 , self.my_title)
                if self.model_hovering == True:
                    painter.setBrush(QColor("#787878"))
                else:
                    painter.setBrush(QColor("#DFDFDF"))

                left_right_margin = 10
                top_bottom_margin = 20
                
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
                painter.setPen(QColor("#040404"))
                painter.drawText( 0 , 15 , self.my_title)
            else:
                painter = QPainter(self)
                # Writing the name of the thing.
                painter.setPen(QColor("#040404"))
                painter.drawText( 0 , 15 , self.my_title)
                if self.model_hovering == True:
                    painter.setBrush(QColor("#787878"))
                else:
                    painter.setBrush(QColor("#DFDFDF"))

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
        else:
            return super().paintEvent(e)

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()
        if (self.get_num_models() == self.max_num_models):
            # Remove one the children from this
            for child in self.findChildren(QtW.QWidget):
                if isinstance(child , Draggable) and child != widget:
                    e.accept()
                    self.my_layout.addWidget(widget)
                    child.deleteLater()
                    return
        # we can see the previous parent
        from_parent = widget.parentWidget()
        to_parent = self
        self.my_layout.addWidget(widget)
        if not isinstance(widget , Draggable):
            e.ignore()
            return
        # Sudo code:
            # Libary -> Libary
                # No replacement, only accept
            # Libary -> Pipeline
                # Yes replacement
            # Pipeline -> Libary
                # No replacement, only accept
            # Pipeline -> Pipeline
                # only accept
        if isinstance(from_parent , GUILibarySubmodule) and isinstance(to_parent , PipelineSection):
            e.accept()
            # Below adds a new widget copy of draggable to the library
            from_parent.layout.insertWidget(from_parent.layout.indexOf(widget) , widget.copy_self())
        elif isinstance(from_parent , PipelineSection) and isinstance(to_parent , PipelineSection):
            e.accept()
        self.is_holding = True

class Pipeline(QtW.QMdiSubWindow):
    all_pipelines = []

    def __init__(self, my_parent, GUI_parent ,  **kwargs):
        super().__init__(GUI_parent, **kwargs)
        my_layout = QVBoxLayout()
        main_thing = QtW.QWidget()
        self.my_parent = my_parent
        main_thing.setLayout(my_layout)
        self.resize(400 , 400)
        self.name_pipeline = QtW.QLineEdit()
        self.name_pipeline.setText(f"pipeline {1 + len(self.my_parent.pipelines)}")
        self.preproccessor_pipe = PipelineSection(
            title="Preproccessors",
            accepting_function=GUILibary.PREPROCESSOR_FILTER

        )
        self.model_pipe = PipelineSection(
            title="Models",
            accepting_function=GUILibary.MODEL_FILTER,
            max_num_models=1
        )
        self.validator = PipelineSection(
            title="Validator",
            # Makes sure this is a validator by checking if it has a 'split' function which is required.
            accepting_function=GUILibary.VALIDATOR_FILTER,
            max_num_models=1
        )
        my_layout.addWidget(self.name_pipeline)
        my_layout.addWidget(self.preproccessor_pipe)
        my_layout.addWidget(self.model_pipe)
        my_layout.addWidget(self.validator)
        self.setWidget(main_thing)

    def get_name_pipeline(self) -> str:
        return self.name_pipeline.text

    def closeEvent(self, event):
        for x in range(0 , len(self.my_parent.pipelines)):
            if self.my_parent.pipelines[x] == self:
                del self.my_parent.pipelines[x]
                self.deleteLater()
                super(QtW.QMdiSubWindow, self).closeEvent(event)
                return




class PipelineMother(QtW.QMainWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setWindowFlags(Qt.WindowType.Widget)
        self.pipelines = []
        self.train_models = None

        toolbar = QtW.QToolBar()
        self.main_thing = QtW.QMdiArea()
        self.main_thing.setWindowIcon(QIcon(":/images/Mini_Logo_Alantis_Learn_book.svg"))
        my_layout = QtW.QVBoxLayout()
        self.main_thing.setLayout(my_layout)
        self.add_pipeline_button = QtW.QPushButton("Add Pipeline")
        self.add_pipeline_button.setFixedSize(150 ,60)
        self.add_pipeline_button.setIcon(QIcon(":/images/add_pipeline.svg"))
        self.add_pipeline_button.clicked.connect(self.add_pipeline)
        toolbar.addWidget(self.add_pipeline_button)
        self.setCentralWidget(self.main_thing)
        self.addToolBar(toolbar)

        self.add_pipeline()

        self.render_x_y_train_sub_window()

    def render_x_y_train_sub_window(self):
        sub_window = ColumnsMDIWindow(self.main_thing)
        self.x_columns = sub_window.x_columns
        self.y_columns = sub_window.y_columns
        self.train_models = sub_window.train_models
      

    def add_pipeline(self):
        new_pipeline = Pipeline(self , self.main_thing)
        new_pipeline.move(30 , 30)
        new_pipeline.show()
        self.pipelines.append(new_pipeline)


class ColumnsMDIWindow(QtW.QMdiSubWindow):
    STARTING_HEIGHT = 300
    STARTING_WIDTH = 400
    def __init__(self, parent , **kwargs):
        super().__init__(parent, **kwargs)
        self.setFixedSize(ColumnsMDIWindow.STARTING_WIDTH , ColumnsMDIWindow.STARTING_HEIGHT)
        main_widget = QtW.QWidget()
        mayo = QtW.QVBoxLayout()
        main_widget.setLayout(mayo)
        self.setWidget(main_widget)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint , False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint , False)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        self.train_models = QtW.QPushButton(
            "Train Models"
        )
        play_icon = self.style().standardIcon(QtW.QStyle.SP_MediaPlay)
        
        # Set the icon on the button
        self.train_models.setIcon(play_icon)


        self.x_columns = ColumnsSection(
            "X axis",
            my_parent=self,
            max_num_cols=400
        )
        self.y_columns = ColumnsSection(
            "Y axis",
            my_parent=self,
            max_num_cols=1
        )

        mayo.addWidget(self.train_models)
        mayo.addWidget(self.x_columns)
        mayo.addWidget(self.y_columns)
        self.show()

    def closeEvent(self, event):
        event.ignore()
    
    def resize_based_on_children(self):
        print(f"Before height : {self.height()}")
        button_and_extra_height = self.train_models.height() + 55
        num_x_cols_recommended_height = self.x_columns.get_num_cols() * DraggableColumn.block_height + ColumnsSection.height_between_top_mouth_and_top_bar*2
        num_y_cols_recommended_height = self.y_columns.get_num_cols() * DraggableColumn.block_height + ColumnsSection.height_between_top_mouth_and_top_bar*2
        purposed_height = num_x_cols_recommended_height + num_y_cols_recommended_height + button_and_extra_height
        print(f"Purposed height {purposed_height}")
        self.setFixedHeight(max(purposed_height, ColumnsMDIWindow.STARTING_HEIGHT))
        print(f"After height {self.height()}")