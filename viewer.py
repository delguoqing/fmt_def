# -*- coding: utf8 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt # the QT namespace
import sys
import util
import core
from .qhexwidget import QHexWidget

COLUMN_NAME = 0
COLUMN_OFFSET = 1
COLUMN_VALUE = 2
COLUMN_TYPE = 3

COLUMN_DEF = {
    COLUMN_NAME: {
        "titleText": "Name",
        "method": "getDisplayName",
    },
    COLUMN_OFFSET: {
        "titleText": "Offset",
        "method": "getFormatedOffset",
    },
    COLUMN_VALUE: {
        "titleText": "Value",
        "method": "getFormatedValue",
    },
    COLUMN_TYPE: {
        "titleText": "Type",
        "method": "getTypeName",
    },                
}

class CustomModel(QtCore.QAbstractItemModel):
    def __init__(self, root, columns):
        QtCore.QAbstractItemModel.__init__(self)
        self._root = root
        self._columns = columns

    def rowCount(self, in_index):
        if in_index.isValid():
            return in_index.internalPointer().getChildCount()
        return self._root.getChildCount()

    def index(self, in_row, in_column, in_parent=None):
        if not in_parent or not in_parent.isValid():
            parent = self._root
        else:
            parent = in_parent.internalPointer()

        if not QtCore.QAbstractItemModel.hasIndex(self, in_row, in_column, in_parent):
            return QtCore.QModelIndex()

        if parent.getChildCount() > 0:
            child = parent.getChild(in_row)
            return QtCore.QAbstractItemModel.createIndex(self, in_row, in_column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, in_index):
        if in_index.isValid():
            p = in_index.internalPointer().getParent()
            if p:
                return QtCore.QAbstractItemModel.createIndex(self, p.getSiblingIndex(), 0, p)
        return QtCore.QModelIndex()

    def columnCount(self, in_index):
        return len(self._columns)

    def data(self, in_index, role):
        if not in_index.isValid():
            return None
        node = in_index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            logicColumn = self._columns[in_index.column()]
            methodName = COLUMN_DEF[logicColumn]["method"]
            method = getattr(node, methodName)
            return method()
        return None
    
    # for horizontal headers, the section corresponds to the column number
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                logicalColumn = self._columns[section]
                return COLUMN_DEF[logicalColumn]["titleText"]
    
class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, parent=None, flags=0):
        super(MainWindow, self).__init__(parent=parent, flags=Qt.WindowFlags(flags))
        self.hierachy = None
        self.initUI()
        
    def initUI(self):
        self.createMenus()
        self.statusBar()    # forces status bar to be created
        self.setCentralWidget(QHexWidget())
        self.showMaximized()
        
    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        
        openAct = QtGui.QAction("&Open...", self)
        openAct.triggered.connect(self.onOpen)
        fileMenu.addAction(openAct)
            
    def addHierachyView(self, view):
        dockWidget = QtGui.QDockWidget("Hierarchy", self)
        dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dockWidget.setWidget(view)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockWidget)
        self.hierarchy = view
        view.clicked.connect(self.onHierachyViewItemClicked)
        
    def setBinaryData(self, data):
        self.centralWidget().setData(data)

    def onHierachyViewItemClicked(self, index):
        node = index.internalPointer()
        offset = node.getOffset()
        self.centralWidget().setCursorPostionAndScroll(offset)
        
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            QtGui.QApplication.quit()
            return
        super(MainWindow, self).keyPressEvent(e)
    
    def onOpen(self):
        pass

def view_format(format, binary_data):
    app = QtGui.QApplication(sys.argv)
    
    mainWindow = MainWindow()
    
    # create hierachy view
    v = QtGui.QTreeView()
    model = CustomModel(format, [COLUMN_NAME, COLUMN_OFFSET, COLUMN_TYPE, COLUMN_VALUE])
    v.setModel(model)
    mainWindow.addHierachyView(v)
    mainWindow.setBinaryData(binary_data)

    sys.exit(app.exec_())

def view_file(filepath, fmt_def):
    format = fmt_def.getFormat()

    f = open(filepath, "rb")
    getter = util.get_getter(f, "<")
    format.read(getter, core.ReadContext(0, "<"))

    getter.seek(0)
    view_format(format, getter)
    
    f.close()

if __name__ == "__main__":
    from .nier2 import wmb_fmt
    view_file(sys.argv[1], wmb_fmt)
