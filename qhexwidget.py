# -*- coding: utf8 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt # the QT namespace

PRINTABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '

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
        self.headerBgColor = Qt.lightGray
        #   row header area
        self.rowHeaderWidth = 100
        self.splitterWidth = 8
        # ascii area
        self.asciiAreaWidth = 164
        # cursor
        # we need to render cursor in hexArea and asciiArea at the same time!
        self.cursorPos = -1  # use offset as cursor position
        self.cursorRect = None
        self.cursorRectSize = QtCore.QSize(20, 23)
        self.cursorBlinkState = 0
        self.cursorRectAscii = None
        self.holdBlinkStateCounter = 0
        
        self.timerBlink = QtCore.QTimer(self)
        self.timerBlink.timeout.connect(self.onTimerBlinkTimeout)
        
        self.commonTextOption = QtGui.QTextOption(Qt.AlignCenter)
        self.commonFont = QtGui.QFont("Consolas", 12)

        self.beginOffset = 0
        self.pageValue = None
        self.pageValueBeginOffset = None
        
        self.initUI()
        
    def initUI(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.verticalScrollBar().valueChanged.connect(self.onSliderValueChanged)
        
        self.setCursorPosition(0)
        self.timerBlink.start(500)
                
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
    
    def getPageValues(self):
        if self.pageValue is None or self.pageValueBeginOffset != self.beginOffset:
            if self.data is None:
                return []
            self.data.seek(self.getBeginOffset())
            bytedata = self.data.get_raw(self.getVisibleLineCount() * self.hexColumnCount)
            values = map(ord, bytedata)
            self.pageValue = values
            self.pageValueBeginOffset = self.beginOffset
        return self.pageValue
    
    def onDataChanged(self):
        linePerPage = self.getVisibleLineCount()
        self.verticalScrollBar().setRange(0, self.getLineCount() - linePerPage)
        self.verticalScrollBar().setPageStep(linePerPage)
      
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
        return self.beginOffset
    
    def getAsciiAreaRect(self):
        rect = self.getColumnHeaderRect()
        return QtCore.QRect(rect.right() - self.asciiAreaWidth,
                            rect.bottom(), self.asciiAreaWidth,
                            self.getRowHeaderHeight())
        
    def drawWidget(self, qp):
        # 用于绘制文本的通用QTextOption，文本需要被绘制在矩形区域的中央
        # 本来Qt中应该传入QAlignment对象，但是pyqt的文档说可以使用QAlignmentFlag是等价的
        txtOption = self.commonTextOption
        qp.setFont(self.commonFont)
        
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
            qp.drawText(QtCore.QRectF(x, y, self.hexGridWidth, self.getColumnHeaderHeight()),
                        "%X" % (i % 16), txtOption)
            x += self.hexGridWidth
        #   row
        #       bg
        qp.fillRect(self.getRowHeaderRect(), self.getRowHeaderBgColor())
        #       offset
        x = 0
        y = self.getColumnHeaderHeight()
        offset = self.getBeginOffset()
        for i in xrange(self.getVisibleLineCount()):
            qp.drawText(QtCore.QRectF(x, y, self.getRowHeaderWidth(), self.hexGridHeight),
                        "%08X" % offset, txtOption)
            y += self.hexGridHeight
            offset += self.hexColumnCount
        # hex values
        values = self.getPageValues()
        self.drawHexArea(qp, values, txtOption)
        # ascii value
        #   splitter
        rect = self.getAsciiAreaRect()
        qp.drawLine(rect.left() - self.splitterWidth, 0, rect.left() - self.splitterWidth,
                    rect.bottom())
        x = rect.x()
        y = rect.y()
        for i in xrange(self.getVisibleLineCount()):
            v = values[i * self.hexColumnCount: (i + 1) * self.hexColumnCount]
            s = "".join(map(lambda ch: chr(ch) if chr(ch) in PRINTABLE else ".", v))
            qp.drawText(QtCore.QRectF(x, y, rect.width(), self.hexGridHeight), s,
                        QtGui.QTextOption(Qt.AlignLeft | Qt.AlignVCenter))
            y += self.hexGridHeight
        
    def drawHexArea(self, qp, values, textOption=None):
        if textOption is None:
            textOption = self.commonTextOption
        qp.setFont(self.commonFont)
        y = self.getColumnHeaderHeight()
        
        rowCount = len(values) / self.hexColumnCount
        if len(values) % self.hexColumnCount == 0:
            lastRowColumnCount = self.hexColumnCount
        else:
            rowCount = rowCount + 1
            lastRowColumnCount = len(values) % self.hexColumnCount
        for i in xrange(rowCount):
            x = self.getRowHeaderWidth()
            if i == rowCount - 1:
                columnCount = lastRowColumnCount
            else:
                columnCount = self.hexColumnCount
            for j in xrange(columnCount):
                v = values[i * self.hexColumnCount + j]
                qp.drawText(QtCore.QRectF(x, y, self.hexGridWidth, self.hexGridHeight),
                            "%02X" % v, textOption)
                x += self.hexGridWidth
            y += self.hexGridHeight
            
    def drawHexValue(self, qp, value, x, y, textOption=None):
        if textOption is None:
            textOption = self.commonTextOption
        qp.setFont(self.commonFont)
        qp.drawText(QtCore.QRectF(x, y, self.hexGridWidth, self.hexGridHeight),
                    "%02X" % value, textOption)
    
    def drawHexValueAtOffset(self, qp, offset, textOption=None):
        value = self.data.get("B", offset=offset)
        rect = self.getHexGridRect(offset)
        return self.drawHexValue(qp, value, rect.x(), rect.y(), textOption=textOption)
                
    def isCursorVisible(self):
        cursorVisible = (self.data is not None and 0 <= self.cursorPos < self.data.size \
                         and self.isHexGridInViewport(self.cursorPos))
        return cursorVisible
    
    def drawCursor(self, qp):
        if not self.isCursorVisible():
            return
        # fill cursor rect
        if self.cursorBlinkState == 0:
            color = self.viewport().palette().color(QtGui.QPalette.Base)
            textColor = self.viewport().palette().color(QtGui.QPalette.WindowText)
        else:
            color = self.viewport().palette().color(QtGui.QPalette.WindowText)
            textColor = self.viewport().palette().color(QtGui.QPalette.Base)
        rect = QtCore.QRect()
        rect.setSize(self.cursorRectSize)
        rect.moveCenter(self.cursorRect.center())
        qp.fillRect(rect, color)
        # draw text on top
        pen = qp.pen()
        qp.setPen(textColor)
        self.drawHexValueAtOffset(qp, self.cursorPos, self.commonTextOption)
        qp.setPen(pen)
        
    def drawCursorAscii(self, qp):
        if not self.isCursorVisible():
            return
        qp.fillRect(self.cursorRectAscii,
                    self.viewport().palette().color(QtGui.QPalette.Base))
        row, col = self.getLocalRowColumn(self.cursorPos)
        v = self.getPageValues()[row * self.hexColumnCount: (row + 1) * self.hexColumnCount]
        s = "".join(map(lambda ch: chr(ch) if chr(ch) in PRINTABLE else ".", v))
        # set background for cursor character    
        metrics = QtGui.QFontMetrics(qp.font())
        color = Qt.lightGray
        rect = QtCore.QRect(self.cursorRectAscii.left() + metrics.averageCharWidth() * col,
                            self.cursorRectAscii.top(),
                            metrics.averageCharWidth(), self.cursorRectAscii.height())
        qp.fillRect(rect, color)
        # redraw all text
        qp.drawText(QtCore.QRectF(self.cursorRectAscii), s,
                    QtGui.QTextOption(Qt.AlignLeft | Qt.AlignVCenter))
        
        
    def maximumViewportSize(self):
        return QSize(
            self.viewport.size().width(),
            self.getColumHeaderHeight() + self.getLineCount() * self.hexGridHeight
        )
    
    def getHexGridRect(self, offset):
        row, column = self.getLocalRowColumn(offset)
        x = self.getRowHeaderWidth() + self.hexGridWidth * column
        y = self.getColumnHeaderHeight() + self.hexGridHeight * row
        return QtCore.QRect(x, y, self.hexGridWidth, self.hexGridHeight)
    
    def getAsciiLineRect(self, offset):
        row, _ = self.getLocalRowColumn(offset)
        asciiAreaRect = self.getAsciiAreaRect()
        left = asciiAreaRect.left()
        hexGridRect = self.getHexGridRect(offset)
        top = hexGridRect.top()
        return QtCore.QRect(left, top, asciiAreaRect.width(), hexGridRect.height())
        
    def onSliderValueChanged(self, newValue):
        self.beginOffset = newValue * self.hexColumnCount
        self.viewport().update()
        self.setCursorPosition(self.cursorPos)
        
    def onTimerBlinkTimeout(self):
        if self.holdBlinkStateCounter > 0:
            self.holdBlinkStateCounter -= 1
            return
        self.cursorBlinkState = 1 - self.cursorBlinkState
        self.updateCursor()
        
    def holdBlinkState(self, state, counter=1):
        self.cursorBlinkState = state
        self.holdBlinkStateCounter = counter
        
    def updateCursor(self):
        if self.isCursorVisible():
            self.viewport().update(self.cursorRect)
            self.viewport().update(self.cursorRectAscii)
            
    def scrollTo(self, offset):
        newLineNo = min(max(0, offset / self.hexColumnCount), self.getLineCount())
        self.verticalScrollBar().setValue(newLineNo)
        
    def getLocalRowColumn(self, offset):
        beginOffset = self.getBeginOffset()
        relOffset = offset - beginOffset
        
        row = relOffset / self.hexColumnCount
        column = relOffset % self.hexColumnCount
        return row, column
    
    def isHexGridInViewport(self, offset):
        row, column = self.getLocalRowColumn(offset)
        return 0 <= row < self.getVisibleLineCount()
            
    def setCursorPosition(self, position):
        position = max(0, position)
        if self.data is not None:
            position = min(position, self.data.size)
            
        # redraw old cursor rect
        self.cursorBlinkState = 0
        self.updateCursor()
        
        # draw new cursor rect if visible
        self.cursorPos = position
        self.cursorRect = self.getHexGridRect(position)
        
        # cursor area for ascii data
        self.cursorRectAscii = self.getAsciiLineRect(position)
        
        if self.isCursorVisible():
            self.holdBlinkState(1, 1)
            self.updateCursor()
            
    def setCursorPostionAndScroll(self, position):
        oldPosition = self.cursorPos
        oldRelLine, _ = self.getLocalRowColumn(oldPosition)
        self.setCursorPosition(position)
        if self.isCursorVisible():
            return
        newRelLine, _ = self.getLocalRowColumn(self.cursorPos)
        
        self.scrollTo(self.beginOffset + (newRelLine - oldRelLine) * self.hexColumnCount)
        
    def positionToHexGrid(self, x, y):
        grid0Rect = self.getHexGridRect(0)
        x -= grid0Rect.left()
        if x < 0:
            return -1
        y -= grid0Rect.top()
        if y < 0:
            return -1
        row = y / grid0Rect.height()
        column = x / grid0Rect.width()
        return row * self.hexColumnCount + column
    
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self.viewport())
        if e.rect() == self.cursorRect:
            self.drawCursor(qp)
        if e.rect() == self.cursorRectAscii:
            self.drawCursorAscii(qp)
        else:
            self.drawWidget(qp)    
            self.drawCursor(qp)
            self.drawCursorAscii(qp)
        qp.end()
        
    def keyPressEvent(self, e):
        if e.matches(QtGui.QKeySequence.MoveToNextChar):
            self.setCursorPostionAndScroll(self.cursorPos + 1)
        elif e.matches(QtGui.QKeySequence.MoveToPreviousChar):
            self.setCursorPostionAndScroll(self.cursorPos - 1)        
        elif e.matches(QtGui.QKeySequence.MoveToPreviousChar):
            self.setCursorPostionAndScroll(self.cursorPos - 1)
        elif e.matches(QtGui.QKeySequence.MoveToEndOfLine):
            line = self.cursorPos / self.hexColumnCount
            self.setCursorPostionAndScroll(self.hexColumnCount * (line + 1) - 1)
        elif e.matches(QtGui.QKeySequence.MoveToStartOfLine):
            line = self.cursorPos / self.hexColumnCount
            self.setCursorPostionAndScroll(self.hexColumnCount * line)
        elif e.matches(QtGui.QKeySequence.MoveToPreviousLine):
            self.setCursorPostionAndScroll(self.cursorPos - self.hexColumnCount)
        elif e.matches(QtGui.QKeySequence.MoveToNextLine):
            self.setCursorPostionAndScroll(self.cursorPos + self.hexColumnCount)
        elif e.matches(QtGui.QKeySequence.MoveToNextPage):
            self.setCursorPostionAndScroll(self.cursorPos + self.hexColumnCount * self.getVisibleLineCount())
        elif e.matches(QtGui.QKeySequence.MoveToPreviousPage):
            self.setCursorPostionAndScroll(self.cursorPos - self.hexColumnCount * self.getVisibleLineCount())
        elif e.matches(QtGui.QKeySequence.MoveToEndOfDocument):
            if self.data is not None:
                self.setCursorPostionAndScroll(self.data.size - 1)
        elif e.matches(QtGui.QKeySequence.MoveToStartOfDocument):
            if self.data is not None:
                self.setCursorPostionAndScroll(0)
        else:
            return super(QHexWidget, self).keyPressEvent(e)
        
    def mousePressEvent(self, e):
        offset = self.positionToHexGrid(e.pos().x(), e.pos().y())
        if offset >= 0:
            self.setCursorPosition(offset)
            