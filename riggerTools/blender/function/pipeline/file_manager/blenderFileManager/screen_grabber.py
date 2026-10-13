import sys
import os

try:
    from PySide2 import QtWidgets, QtGui, QtCore
except ImportError:
    try:
        from PySide6 import QtWidgets, QtGui, QtCore
    except ImportError:
        pass

class ScreenCaptureDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ScreenCaptureDialog, self).__init__(parent)
        
        # Make the dialog completely frameless and full screen, staying on top
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | 
            QtCore.Qt.WindowStaysOnTopHint | 
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.Tool
        )
        
        # Grab the primary screen
        app = QtWidgets.QApplication.instance()
        screen = app.primaryScreen()
        self.screenshot = screen.grabWindow(0)
        self.screen_geometry = screen.geometry()
        
        self.setGeometry(self.screen_geometry)
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        
        # Crop variables
        self.start_pos = None
        self.end_pos = None
        self.is_cropping = False
        self.cropped_pixmap = None
        
        # Set focus policy to receive key events
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus()
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        
        # Draw the original full screen screenshot
        painter.drawPixmap(0, 0, self.screenshot)
        
        # Draw semi-transparent black overlay
        overlay_color = QtGui.QColor(0, 0, 0, 100)  # 100 is transparency (out of 255)
        painter.fillRect(self.rect(), overlay_color)
        
        # If cropping is active or a crop area exists, redraw the clear area
        if self.start_pos and self.end_pos:
            rect = QtCore.QRect(self.start_pos, self.end_pos).normalized()
            if rect.width() > 0 and rect.height() > 0:
                # Draw the original screenshot back over the selection area (so it is bright/clear)
                painter.drawPixmap(rect, self.screenshot, rect)
                
                # Draw a nice dashed orange border around the crop area
                # Using #d29a2e (the premium orange matching the file manager dark theme)
                pen = QtGui.QPen(QtGui.QColor(210, 154, 46), 2, QtCore.Qt.DashLine)
                painter.setPen(pen)
                painter.drawRect(rect)
                
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.is_cropping = True
            self.update()
            
    def mouseMoveEvent(self, event):
        if self.is_cropping:
            # Constrain selection to a square (1:1 aspect ratio)
            dx = event.pos().x() - self.start_pos.x()
            dy = event.pos().y() - self.start_pos.y()
            
            size = max(abs(dx), abs(dy))
            
            end_x = self.start_pos.x() + (size if dx >= 0 else -size)
            end_y = self.start_pos.y() + (size if dy >= 0 else -size)
            
            self.end_pos = QtCore.QPoint(end_x, end_y)
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.is_cropping:
            dx = event.pos().x() - self.start_pos.x()
            dy = event.pos().y() - self.start_pos.y()
            
            size = max(abs(dx), abs(dy))
            
            end_x = self.start_pos.x() + (size if dx >= 0 else -size)
            end_y = self.start_pos.y() + (size if dy >= 0 else -size)
            
            self.end_pos = QtCore.QPoint(end_x, end_y)
            self.is_cropping = False
            
            rect = QtCore.QRect(self.start_pos, self.end_pos).normalized()
            if rect.width() > 10 and rect.height() > 10:
                # Crop the pixmap
                self.cropped_pixmap = self.screenshot.copy(rect)
                self.accept()
            else:
                self.start_pos = None
                self.end_pos = None
                self.update()
                
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.reject()
        else:
            super(ScreenCaptureDialog, self).keyPressEvent(event)
            
    def get_cropped_pixmap(self):
        return self.cropped_pixmap
