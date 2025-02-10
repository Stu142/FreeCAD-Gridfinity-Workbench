"""A module to interact with the user."""

# ruff: noqa: F403, F405

from __future__ import annotations

import math

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWidgets import *


class GridDialog(QDialog):
    """A dialog with togglable grid cells."""

    def __init__(self, x: int, y: int, offset: int, spacing: int) -> None:
        """Create the dialog object."""
        super().__init__()
        self.x = x
        self.y = y
        self.offset = offset
        self.spacing = spacing

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.label = QLabel()
        self.pixmap = QPixmap(QSize(2 * offset + x * spacing, 2 * offset + y * spacing))

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        self.grid_layout = [[False] * y for _ in range(x)]

        self.origin_pos = QPoint(
            self.offset,
            self.offset + self.y * self.spacing,
        )

    def _to_canvas_point(self, point: QPoint) -> QPoint:
        point.setY(-point.y())
        return self.origin_pos + self.spacing * point

    def _from_mouse_pos(self, point: QPoint) -> QPointF:
        relative_pos = point - (self.origin_pos + self.label.pos())
        return QPointF(relative_pos.x(), -relative_pos.y()) / self.spacing

    def _recompute(self) -> None:
        self.pixmap.fill(self.palette().color(QPalette.Window))

        painter = QPainter(self.pixmap)
        for x in range(self.x):
            for y in range(self.y):
                if self.grid_layout[x][y]:
                    painter.fillRect(
                        QRect(
                            self._to_canvas_point(QPoint(x, y + 1)),
                            self._to_canvas_point(QPoint(x + 1, y)),
                        ),
                        self.palette().highlight(),
                    )
        pen = QPen()
        pen.setWidth(4)
        pen.setColor(self.palette().color(QPalette.Text))
        painter.setPen(pen)
        for x in range(self.x + 1):
            for y in range(self.y + 1):
                painter.drawPoint(self._to_canvas_point(QPoint(x, y)))
        painter.end()

        self.label.setPixmap(self.pixmap)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self._is_good())

    def _is_good(self) -> bool:
        cell_count = 0
        starting_cell = None
        for x in range(self.x):
            for y in range(self.y):
                if self.grid_layout[x][y]:
                    cell_count += 1
                    starting_cell = (x, y)
        if cell_count == 0:
            return False

        visited = set()

        def dfs(x: int, y: int) -> None:
            if (
                (x, y) in visited
                or x < 0
                or y < 0
                or x >= self.x
                or y >= self.y
                or not self.grid_layout[x][y]
            ):
                return
            visited.add((x, y))
            dfs(x + 1, y)
            dfs(x - 1, y)
            dfs(x, y + 1)
            dfs(x, y - 1)

        dfs(*starting_cell)
        return cell_count == len(visited)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: ARG002, D102, N802
        self._recompute()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: D102, N802
        pos = self._from_mouse_pos(event.localPos())
        self.grid_layout[math.floor(pos.x())][math.floor(pos.y())] ^= True
        self._recompute()


def get_custom_shape() -> list[list[bool]] | None:
    """Get a custom shape from the user. Returns None if the user aborted the operation."""
    dialog = GridDialog(10, 10, 40, 50)
    if not dialog.exec():
        return None
    return dialog.grid_layout
