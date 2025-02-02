import math

from PySide.QtWidgets import *
from PySide.QtGui import *
from PySide.QtCore import *

n = 10
m = 10
offset = 40
spacing = 50

class GridDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.label = QLabel()
        self.pixmap = QPixmap(QSize(2 * offset + (n-1) * spacing, 2 * offset + (m-1) * spacing))

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        self.grid_layout = [[False]*m for _ in range(n)]

    def to_canvas_point(self, point: QPoint) -> QPoint:
        return spacing * point + QPoint(offset, offset)

    def recompute(self) -> None:
        self.pixmap.fill(self.palette().color(QPalette.Window))
        with QPainter(self.pixmap) as painter:
            for i in range(n):
                for j in range(m):
                    if self.grid_layout[i][j]:
                        painter.fillRect(
                            QRect(
                                self.to_canvas_point(QPoint(i, j)),
                                self.to_canvas_point(QPoint(i+1, j+1)),
                            ),
                            self.palette().highlight()
                        )
            pen = QPen()
            pen.setWidth(4)
            pen.setColor(self.palette().color(QPalette.Text))
            painter.setPen(pen)
            for i in range(n):
                for j in range(m):
                    painter.drawPoint(self.to_canvas_point(QPoint(i, j)))
        self.label.setPixmap(self.pixmap)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.is_good())

    def is_good(self) -> bool:
        remaining_cells = 0
        starting_cell = None
        for i in range(n):
            for j in range(m):
                if self.grid_layout[i][j]:
                    remaining_cells += 1
                    starting_cell = (i,j)
        if remaining_cells == 0:
            return False
        visited = set()
        def dfs(i, j):
            nonlocal remaining_cells
            if (i, j) in visited or i < 0 or j < 0 or i >= n or j >= m or not self.grid_layout[i][j]:
                return
            visited.add((i, j))
            dfs(i+1, j)
            dfs(i-1, j)
            dfs(i, j+1)
            dfs(i, j-1)
            remaining_cells -= 1
        dfs(*starting_cell)
        return remaining_cells == 0

    def showEvent(self, event) -> None:
        self.recompute()

    def mousePressEvent(self, event) -> None:
        pos = ((event.position() - QPointF(offset + self.label.x(), offset + self.label.y())) / spacing)
        self.grid_layout[math.floor(pos.x())][math.floor(pos.y())] ^= True
        self.recompute()

class WireDialog(QDialog):
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
    dialog = GridDialog()
    if not dialog.exec():
        return None
    return dialog.grid_layout
