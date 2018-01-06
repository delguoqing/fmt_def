from PyQt4 import QtCore, QtGui
import sys
import util
import core

class CustomModel(QtCore.QAbstractItemModel):
    def __init__(self, root):
        QtCore.QAbstractItemModel.__init__(self)
        self._root = root

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
        return 1

    def data(self, in_index, role):
        if not in_index.isValid():
            return None
        node = in_index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.getDisplayName()
        return None

def view_format(format):
    app = QtGui.QApplication(sys.argv)
    v = QtGui.QTreeView()
    v.setModel(CustomModel(format))
    v.show()
    sys.exit(app.exec_())

def view_file(filepath, fmt_def):
    format = fmt_def.getFormat()

    f = open(filepath, "rb")
    getter = util.get_getter(f, "<")
    format.read(getter, core.ReadContext(0, "<"))
    f.close()

    view_format(format)

if __name__ == "__main__":
    from .nier2 import wmb_fmt
    view_file(sys.argv[1], wmb_fmt)
