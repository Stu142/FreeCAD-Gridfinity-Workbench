"""A module to interact with the user."""

# ruff: noqa: F403, F405

from __future__ import annotations

import math

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWidgets import *


class GridDialog(QDialog):
    """A dialog with togglable grid cells."""

    def __init__(self, n: int, m: int, offset: int, spacing: int) -> None:
        """Create the dialog object."""
        super().__init__()
        self.n = n
        self.m = m
        self.offset = offset
        self.spacing = spacing

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.label = QLabel()
        self.pixmap = QPixmap(QSize(2 * offset + (n - 1) * spacing, 2 * offset + (m - 1) * spacing))

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        self.grid_layout = [[False] * m for _ in range(n)]

    def _to_canvas_point(self, point: QPoint) -> QPoint:
        return self.spacing * point + QPoint(self.offset, self.offset)

    def _recompute(self) -> None:
        self.pixmap.fill(self.palette().color(QPalette.Window))

        painter = QPainter(self.pixmap)
        for i in range(self.n):
            for j in range(self.m):
                if self.grid_layout[i][j]:
                    painter.fillRect(
                        QRect(
                            self._to_canvas_point(QPoint(i, j)),
                            self._to_canvas_point(QPoint(i + 1, j + 1)),
                        ),
                        self.palette().highlight(),
                    )
        pen = QPen()
        pen.setWidth(4)
        pen.setColor(self.palette().color(QPalette.Text))
        painter.setPen(pen)
        for i in range(self.n):
            for j in range(self.m):
                painter.drawPoint(self._to_canvas_point(QPoint(i, j)))
        painter.end()

        self.label.setPixmap(self.pixmap)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self._is_good())

    def _is_good(self) -> bool:
        cell_count = 0
        starting_cell = None
        for i in range(self.n):
            for j in range(self.m):
                if self.grid_layout[i][j]:
                    cell_count += 1
                    starting_cell = (i, j)
        if cell_count == 0:
            return False
        visited = set()

        def dfs(i: int, j: int) -> None:
            if (
                (i, j) in visited
                or i < 0
                or j < 0
                or i >= self.n
                or j >= self.m
                or not self.grid_layout[i][j]
            ):
                return
            visited.add((i, j))
            dfs(i + 1, j)
            dfs(i - 1, j)
            dfs(i, j + 1)
            dfs(i, j - 1)

        dfs(*starting_cell)
        return cell_count == len(visited)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: ARG002, D102, N802
        self._recompute()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: D102, N802
        origin_pos = QPointF(self.offset + self.label.x(), self.offset + self.label.y())
        pos = (event.localPos() - origin_pos) / self.spacing
        self.grid_layout[math.floor(pos.x())][math.floor(pos.y())] ^= True
        self._recompute()


def get_custom_shape() -> list[list[bool]] | None:
    """Get a custom shape from the user. Returns None if the user aborted the operation."""
    dialog = GridDialog(10, 10, 40, 50)
    if not dialog.exec():
        return None
    return dialog.grid_layout
