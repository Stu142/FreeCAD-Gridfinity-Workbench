from PySide.QtWidgets import *
from PySide.QtGui import *
from PySide.QtCore import *

n = 20
m = 20
offset = 40
spacing = 25

class MyWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.pixmap = QPixmap(QSize(2 * offset + (n-1) * spacing, 2 * offset + (m-1) * spacing))

        self.pen_unselected = QPen()
        self.pen_unselected.setWidth(3)
        self.pen_selected = QPen()
        self.pen_selected.setWidth(4)
        self.pen_selected.setColor(Qt.blue)
        self.pen_finished = QPen()

        self.clear()
        self.label.setPixmap(self.pixmap)

        self.path = []

    def to_canvas_point(self, point: QPoint) -> QPoint:
        return spacing * point + QPoint(offset, offset)

    def clear(self):
        self.pixmap.fill(Qt.white)
        with QPainter(self.pixmap) as painter:
            painter.setPen(self.pen_unselected)
            for i in range(n):
                for j in range(m):
                    painter.drawPoint(self.to_canvas_point(QPoint(i, j)))

    def mousePressEvent(self, event):
        pos = ((event.position() - QPointF(offset + self.label.x(), offset + self.label.y())) / spacing).toPoint()

        if not self.path:
            with QPainter(self.pixmap) as painter:
                painter.setPen(self.pen_selected)
                painter.drawPoint(self.to_canvas_point(pos))
            self.label.setPixmap(self.pixmap)
            self.path.append(pos)
        else:
            last_point = self.path[-1]
            diff = pos - last_point

            if diff == QPoint(0, 0):
                print("clicked the same point, ignoring")
                return

            if abs(diff.x()) >= abs(diff.y()):
                diff.setY(0)
            else:
                diff.setX(0)
            new_point = last_point + diff

            with QPainter(self.pixmap) as painter:
                painter.setPen(self.pen_selected)
                painter.drawLine(self.to_canvas_point(last_point), self.to_canvas_point(new_point))
            self.label.setPixmap(self.pixmap)

            self.path.append(new_point)

            if self.path[0] == new_point:
                self.close()

def get_custom_shape():
    dialog = MyWindow()
    dialog.exec_()
    res = [p.toTuple() for p in dialog.path]
    return res
