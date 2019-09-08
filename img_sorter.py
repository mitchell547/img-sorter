from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFileDialog
import os
import shutil
from functools import partial

IMG_FORMATS = (".jpg", ".jpeg", ".png")
IMG_VIEW_SIZE = (640, 480)
MINIMAL_SIZE_POLICY = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

def _build_path(folders, filename):
    return "./{}/{}".format(folders, filename)

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
                        
        self.resize(*IMG_VIEW_SIZE)
        short_dir_name = os.path.basename(os.getcwd())
        self.setWindowTitle("Image Sorter" + " (.../{})".format(short_dir_name))
        
        self._paths_btns = set()

        # Get images in current folder
        #files = [s.encode("utf-8") for s in os.listdir()]
        self.imageIteratorInit()
        
        # Init image view        
        self._name_label = QtWidgets.QLabel(self)
        self._name_label.setAlignment(Qt.AlignCenter)    
        
        self._img_label = QtWidgets.QLabel(self)
        self._img_label.setAlignment(Qt.AlignCenter) 
        self.onNextClick()
        
        # Init buttons
        # (upper layout)
        change_dir_btn = QtWidgets.QPushButton('Change dir...', self)
        change_dir_btn.setSizePolicy(MINIMAL_SIZE_POLICY)
        change_dir_btn.clicked.connect(self.onDirChange)
        
        upper_btn_layout = QtWidgets.QHBoxLayout()
        upper_btn_layout.setAlignment(Qt.AlignLeft)        
        upper_btn_layout.addWidget(change_dir_btn)        
        
        # (lower layout)
        self._path_line = QtWidgets.QLineEdit(self)
        self._path_line.setPlaceholderText("Relative or absolute path")
        
        move_btn = QtWidgets.QPushButton('MOVE FILE', self)
        move_btn.clicked.connect(self.onMoveClick)
        next_btn = QtWidgets.QPushButton('NEXT >>', self)
        next_btn.clicked.connect(self.onNextClick)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(move_btn)
        btn_layout.addWidget(next_btn)
        
        self._path_btns_lyt = QtWidgets.QHBoxLayout()
        self._path_btns_lyt.setAlignment(Qt.AlignLeft)
        
        # Init layouts
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(upper_btn_layout)
        
        vlayout.addWidget(self._name_label)
        vlayout.addWidget(self._img_label)
        
        vlayout.addWidget(self._path_line)
        vlayout.addLayout(btn_layout)
        
        vlayout.addLayout(self._path_btns_lyt)
        
        wdg = QtWidgets.QWidget()
        wdg.setLayout(vlayout)
        
        self.setCentralWidget(wdg)
    
    def imageIteratorInit(self):
        files = os.listdir()
        self._images = list(filter(lambda s: s.endswith(IMG_FORMATS), files))
        self._img_iter = iter(self._images)
    
    def onMoveClick(self, checked, arg_path=None):        
        new_path = self._path_line.text()
        
        if not (new_path and new_path.strip()):
            QtWidgets.QMessageBox.warning(self, 'Error', 'File path is empty')
            return 
        if not os.path.exists(_build_path(new_path, "")):
            QtWidgets.QMessageBox.warning(self, 'Error', 'No such directory')
            return 
            
        if arg_path != None:
            new_path = arg_path
        
        if not new_path in self._paths_btns:        
            new_btn = QtWidgets.QPushButton(new_path, self)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            new_btn.setSizePolicy(sizePolicy)
            new_btn.clicked.connect(lambda: self.onMoveClick(False, new_path))
            self._path_btns_lyt.addWidget(new_btn)
            self._paths_btns.add(new_path)
        
        newname = self._cur_img_name
        while os.path.exists(_build_path(new_path, newname)):
            base, extension = os.path.splitext(newname)
            newname = base + '(2)' + extension
        shutil.copy2(self._cur_img_name, _build_path(new_path, newname))
        os.remove(self._cur_img_name)
        print("moved with name " + newname)
        self.onNextClick()
    
    def onNextClick(self):
        try:
            img = next(self._img_iter)
            self._cur_img_name = img
            pixmap = QtGui.QPixmap(img).scaled(*IMG_VIEW_SIZE, QtCore.Qt.KeepAspectRatio)
            self._img_label.setPixmap(pixmap)
            self._name_label.setText(img)
        except StopIteration:
            self._img_label.setText("No More Images!")
            self._name_label.setText("")
        
    def onDirChange(self):
        new_dir = str(QFileDialog.getExistingDirectory(self, "Select Working Directory"))
        os.chdir(new_dir)
        self.setWindowTitle("Image Sorter" + " (.../{})".format(os.path.basename(new_dir)))
        self.imageIteratorInit()
        self.onNextClick()
    

if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
        