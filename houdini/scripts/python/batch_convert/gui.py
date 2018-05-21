import hou
import converters
import batch_convert

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

class MainGui(QtWidgets.QWidget):
    """
    A class specifying graphical user interface of the tool
    """
    def __init__(self, parent=None):
        super(MainGui, self).__init__(parent)
        
        self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        self.setProperty("houdiniStyle", True)
        
        self.setWindowTitle("Batch texture conversion")
        self.setMinimumSize(400, 450)

        self.input_formats_list = batch_convert.input_formats
        self.output_formats_list = batch_convert.output_formats_dict.keys()

        # create layouts
        main_layout = QtWidgets.QVBoxLayout()
        folder_layout = QtWidgets.QHBoxLayout()
        form_layout = QtWidgets.QFormLayout()
        bottom_buttons = QtWidgets.QHBoxLayout()

        # Create widgets
        file_label = QtWidgets.QLabel("Select a folder with textures for conversion")

        self.folder_path = QtWidgets.QLineEdit()
        folder_button = hou.qt.createFileChooserButton() # this is H specific
        folder_button.setFileChooserFilter(hou.fileType.Directory)
        folder_button.setFileChooserMode(hou.fileChooserMode.Read)
        folder_button.setFileChooserTitle("Select a folder with textures for conversion")
        folder_button.setFileChooserStartDirectory( hou.expandString("$JOB") )

        self.input_formats = QtWidgets.QListWidget()
        self.input_formats.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.input_formats.addItems(self.input_formats_list)
        self.input_formats.setFixedHeight( self.input_formats.sizeHintForRow(0) * (self.input_formats.count()+2) )
        for i in range( self.input_formats.count() ):
            self.input_formats.setCurrentRow(i, QtCore.QItemSelectionModel.SelectionFlag.Select)
        
        #self.output_format = QtWidgets.QComboBox()
        self.output_format = hou.qt.createComboBox() # this is H specific
        self.output_format.addItems(self.output_formats_list)
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setFormat("%p % done (%v / %m textures)")
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.progress_text = QtWidgets.QLabel()
        self.progress_text.setAlignment( QtCore.Qt.AlignCenter )
        self.progress_text.setText( self.progress_bar.text() )

        self.button_convert = QtWidgets.QPushButton("Convert")
        button_cancel = QtWidgets.QPushButton("Cancel")
        
        # Create assign widgets and layouts
        main_layout.addWidget(file_label)
        
        folder_layout.addWidget(self.folder_path)
        folder_layout.addWidget(folder_button)
        
        form_layout.addRow("Input Formats", self.input_formats)
        form_layout.addRow("Output Format", self.output_format)
        
        bottom_buttons.addStretch(1)
        bottom_buttons.addWidget(self.button_convert)
        bottom_buttons.addWidget(button_cancel)

        main_layout.addLayout(folder_layout)
        main_layout.addLayout(form_layout)
        main_layout.addStretch(3)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.progress_text)        
        main_layout.addStretch(1)        
        main_layout.addLayout(bottom_buttons)

        # Set dialog main_layout
        self.setLayout(main_layout)
        
        # center the window
        my_dimensions = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        my_dimensions.moveCenter(centerPoint)
        self.move(my_dimensions.topLeft())

        # Add button signalsprint "convert"
        folder_button.fileSelected.connect(self.applyFolderPath)
        self.progress_bar.valueChanged.connect(self.updateProgressText)
        self.button_convert.clicked.connect(self.convert)
        button_cancel.clicked.connect(self.cancel)  

    @QtCore.Slot(str)
    def applyFolderPath(self, path):
        path = hou.expandString(path)
        self.folder_path.setText(path)

    @QtCore.Slot()
    def incProgressBar(self):
        val = self.progress_bar.value()
        val = val + 1
        self.progress_bar.setValue(val)

    @QtCore.Slot(int)
    def updateProgressText(self):
        self.progress_text.setText( self.progress_bar.text() )

    def convert(self):
        """
        starts batch conversion
        """
        input_formats = self.input_formats.selectedItems()
        input_formats = [str( item.text() ) for item in input_formats]

        output_format_func = self.output_format.currentText()
        output_format_func = batch_convert.output_formats_dict[output_format_func]
        
        root_path = self.folder_path.text()
        
        batch_convert.batchConvert(ui_obj=self, input_formats=input_formats, output_format_func=output_format_func, root_path=root_path)
        
    def cancel(self):
        """
        cancel button
        """
        self.close()


def confirm_dialog(tex_count):
    """
    displays a confirmation dialog (with info about amount of found textures) for starting texture conversion process
    """
    font = QtGui.QFont()
    font.setBold( True )

    dialog = QtWidgets.QMessageBox()
    dialog.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
    dialog.setProperty("houdiniStyle", True)
    dialog.setFont(font)

    dialog.setIcon(QtWidgets.QMessageBox.Information)
    dialog.setWindowTitle("Proceed?")
    dialog.setText("{} textures found, proceed?".format(tex_count))

    dialog.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
    dialog.setDefaultButton(QtWidgets.QMessageBox.Yes)
    ret = dialog.exec_()
    
    if ret == dialog.Ok:
        return True
    else:
        return False