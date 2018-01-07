from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt # the QT namespace
import sys
import util
import core

PRINTABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
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
        
    def setBinaryData(self, data):
        self.centralWidget().setData(data)
    
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            QtGui.QApplication.quit()
            return
        super(MainWindow, self).keyPressEvent(e)
    
    def onOpen(self):
        pass
    
class QHexWidget(QtGui.QAbstractScrollArea):
    
    def __init__(self):      
        super(QHexWidget, self).__init__()
        self.data = None
        # hex area
        self.hexGridWidth = 30
        self.hexGridHeight = 30
        self.hexColumnCount = 0x10
        # header area
        #   common
        self.headerBgColor = QtGui.QColor(128, 128, 128)
        #   row header area
        self.rowHeaderWidth = 80
        # ascii area
        self.splitterWidth = 10
        self.asciiAreaWidth = 128
        
        self.initUI()
        
    def initUI(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.verticalScrollBar().valueChanged.connect(self.onSliderValueChanged)
        
    def setData(self, data):
        self.data = data
        self.onDataChanged()
        
    def getLineCount(self):
        if self.data is None:
            return 0
        size = self.data.size
        if size % self.hexColumnCount == 0:
            return size / self.hexColumnCount
        else:
            return size // self.hexColumnCount + 1
    
    def getVisibleLineCount(self):
        return self.getRowHeaderHeight() // self.hexGridHeight
    
    def onDataChanged(self):
        self.verticalScrollBar().setRange(0, self.getLineCount() - 1)
        self.verticalScrollBar().setPageStep(self.getVisibleLineCount())
        
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self.viewport())
        self.drawWidget(qp)
        qp.end()
      
    def getTotalWidth(self):
        total = 0
        total += self.rowHeaderWidth
        total += self.hexGridWidth * self.hexColumnCount
        total += self.splitterWidth
        total += self.asciiAreaWidth
        return total
    
    def getColumnHeaderWidth(self):
        return self.getTotalWidth() - self.rowHeaderWidth
    
    def getColumnHeaderHeight(self):
        return self.hexGridHeight
    
    def getColumnHeaderRect(self):
        return QtCore.QRect(self.getRowHeaderWidth(), 0, self.getColumnHeaderWidth(),
                            self.getColumnHeaderHeight())
    
    def getColumnHeaderBgColor(self):
        return self.headerBgColor
    
    def getRowHeaderWidth(self):
        return self.rowHeaderWidth
    
    def getRowHeaderHeight(self):
        height = self.viewport().size().height() - self.getColumnHeaderHeight()
        return height
    
    def getRowHeaderRect(self):
        return QtCore.QRect(0, self.getColumnHeaderHeight(), self.getRowHeaderWidth(),
                            self.getRowHeaderHeight())
    
    def getRowHeaderBgColor(self):
        return self.headerBgColor
    
    def getHeaderBgColor(self):
        return self.headerBgColor
    
    def getBeginOffset(self):
        if not self.verticalScrollBar().isVisible():
            return 0
        lineNo = self.verticalScrollBar().value()
        offset = lineNo * self.hexColumnCount
        return offset
    
    def getAsciiAreaRect(self):
        rect = self.getColumnHeaderRect()
        return QtCore.QRect(rect.right() - self.asciiAreaWidth, rect.bottom(),
                            self.asciiAreaWidth, self.getRowHeaderHeight())
        
    def drawWidget(self, qp):
        # header
        #   top left corner
        qp.fillRect(0, 0, self.rowHeaderWidth, self.getColumnHeaderHeight(),
                    self.getHeaderBgColor())
        #   column
        #       bg
        qp.fillRect(self.getColumnHeaderRect(), self.getColumnHeaderBgColor())
        #       offset
        x = self.getColumnHeaderRect().x()
        y = self.getColumnHeaderRect().y()
        for i in xrange(self.hexColumnCount):
            qp.drawText(QtCore.QPointF(x, y + self.hexGridHeight), "%X" % (i % 16))
            x += self.hexGridWidth
        #   row
        #       bg
        qp.fillRect(self.getRowHeaderRect(), self.getRowHeaderBgColor())
        #       offset
        x = 0
        y = self.getColumnHeaderHeight()
        offset = self.getBeginOffset()
        for i in xrange(self.getVisibleLineCount()):
            qp.drawText(QtCore.QPointF(x, y + self.hexGridHeight), "%08X" % offset)
            y += self.hexGridHeight
            offset += self.hexColumnCount
        # hex values
        if self.data is None:
            return
        self.data.seek(self.getBeginOffset())
        bytedata = self.data.get_raw(self.getVisibleLineCount() * self.hexColumnCount)
        values = map(ord, bytedata)
        y = self.getColumnHeaderHeight()
        for i in xrange(self.getVisibleLineCount()):
            x = self.getRowHeaderWidth()
            for j in xrange(self.hexColumnCount):
                v = values[i * self.hexColumnCount + j]
                qp.drawText(QtCore.QPointF(x, y + self.hexGridHeight), "%02X" % v)
                x += self.hexGridWidth
            y += self.hexGridHeight

        # ascii value
        #   splitter
        rect = self.getAsciiAreaRect()
        # splitter
        qp.drawLine(rect.left() + self.splitterWidth * 0.5, 0,
                    rect.left() + self.splitterWidth * 0.5, rect.bottom())
        x = rect.x() + self.splitterWidth
        y = rect.y()
        for i in xrange(self.getVisibleLineCount()):
            s = bytedata[i * self.hexColumnCount: (i + 1) * self.hexColumnCount]
            s = "".join(map(lambda ch: ch if ch in PRINTABLE else ".", s))
            qp.drawText(QtCore.QPointF(x, y + self.hexGridHeight), s)
            y += self.hexGridHeight
        
    def maximumViewportSize(self):
        return QSize(
            self.viewport.size().width(),
            self.getColumHeaderHeight() + self.getLineCount() * self.hexGridHeight
        )
    
    def onSliderValueChanged(self, newValue):
        self.viewport().update()

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
