import sys
from PySide6.QtWidgets import (
    QPushButton,
    QLayout,
    QApplication,
    QMainWindow,
    QSizePolicy,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
    QColorDialog,
)
from PySide6.QtGui import QColor, QImage, QPixmap, QPalette
from PySide6.QtCore import Qt


class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class ColoredButton(QPushButton):
    def update_bg(self, color: str):
        self.setStyleSheet(
            f"background-color: {color}; border: 1px solid black;; border-radius: 5px;"
        )

    def open_color_dialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.update_bg(color.name())


class RightLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        # align right and center
        self.setAlignment(Qt.AlignRight | Qt.AlignCenter)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout(central_widget)
        topbar_layout = QHBoxLayout()
        # make the topbar_layout elements align to the left
        topbar_layout.setAlignment(Qt.AlignRight)
        layout.addLayout(topbar_layout)

        # Create the top bar widgets
        aspect_label = RightLabel("Aspect Ratio:")
        self.aspect_edit = QLineEdit(aspect_label)
        self.aspect_edit.setFixedWidth(60)
        self.aspect_edit.setParent(aspect_label)

        width_label = RightLabel("Width:")
        # fix width_label width
        width_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # width_label.setFixedWidth(60)
        self.width_edit = QLineEdit()
        self.width_edit.setFixedWidth(60)

        height_label = RightLabel("Height:")
        self.height_edit = QLineEdit()
        self.height_edit.setFixedWidth(60)

        self.bg_color_button = ColoredButton("Background color")
        self.bg_transparent_button = QPushButton("make Background transparent")

        self.resize_button = QPushButton("Apply")

        # Create an image label to display the image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        # self.image_label.setFixedSize(600, 400)

        # Add the top bar widgets and the image label to the layout
        topbar_layout.addWidget(aspect_label)
        topbar_layout.addWidget(self.aspect_edit)
        topbar_layout.addWidget(width_label)
        topbar_layout.addWidget(self.width_edit)
        topbar_layout.addWidget(height_label)
        topbar_layout.addWidget(self.height_edit)
        topbar_layout.addWidget(self.bg_color_button)
        topbar_layout.addWidget(self.bg_transparent_button)

        topbar_layout.addWidget(self.resize_button)
        # why is it the `layout` and not `topbar_layout` that needs to be fixedsize?
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.addWidget(self.image_label)

        # Connect the color dialog button signal to the slot
        self.bg_color_button.clicked.connect(self.bg_color_button.open_color_dialog)
        self.bg_transparent_button.clicked.connect(self.make_bg_transparent)

    def make_bg_transparent(self):
        self.bg_color_button.update_bg("transparent")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
