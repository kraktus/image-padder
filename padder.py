from __future__ import annotations

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
    QFileDialog,
)
import traceback
from PySide6.QtGui import QColor, QImage, QPixmap, QPalette
from PySide6.QtCore import Qt
from PIL import Image, ImageOps
from pathlib import Path
import subprocess


class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class ColoredButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.color = None

    def update_bg(self, color: str):
        if color == "transparent":
            self.color = None  # PIL store transparent color as `None`
        else:
            self.color = color
        self.setStyleSheet(
            f"background-color: {color}; border: 1px solid black; border-radius: 5px;"
        )

    def open_color_dialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.update_bg(color.name())


# decorator to catch exceptions and display them
def catch_error(func):
    def wrapper(window: MainWindow, *args, **kwargs):
        try:
            func(window, *args, **kwargs)
        except Exception as e:
            traceback.print_exception(e)
            window.error_label.setText(str(e))

    return wrapper


class RightLabel(QLabel):
    def __init__(self, text: str):
        super().__init__(text)
        # align right and center
        self.setAlignment(Qt.AlignRight | Qt.AlignCenter)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resized_pil_image = None

        self.setWindowTitle(f"Image Padder, commit: {get_git_revision_short_hash()}")
        # self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout(central_widget)
        topbar_layout = QHBoxLayout()
        self.topbar_layout = topbar_layout
        # make the topbar_layout elements align to the left
        topbar_layout.setAlignment(Qt.AlignRight)
        layout.addLayout(topbar_layout)

        # Create the top bar widgets
        aspect_label = RightLabel("Aspect Ratio:")
        self.aspect_edit = QLineEdit(aspect_label)
        self.aspect_edit.setFixedWidth(60)
        self.aspect_edit.setParent(aspect_label)

        width_label = RightLabel("Width:")
        # fix width_label width, useful(?)
        width_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.width_edit = QLineEdit()
        self.width_edit.setFixedWidth(60)

        height_label = RightLabel("Height:")
        self.height_edit = QLineEdit()
        self.height_edit.setFixedWidth(60)

        self.bg_color_button = ColoredButton("Background color")
        self.bg_transparent_button = QPushButton("make Background transparent")

        self.resize_button = QPushButton("Apply")

        self.save_button = QPushButton("Save")

        # error label
        self.error_label = QLabel()
        # set error label to red
        self.error_label.setStyleSheet("color: red")
        # set error height to 33
        self.error_label.setFixedHeight(33)
        # allow easy copy paste
        self.error_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Create image upload button
        self.image_button = QPushButton("Upload image")
        self.image = QLabel()
        self.image.setFixedSize(600, 600)
        self.image.setStyleSheet(f"border: 1px solid black; border-radius: 5px;")

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
        topbar_layout.addWidget(self.save_button)
        # why is it the `layout` and not `topbar_layout` that needs to be fixedsize?
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.addWidget(self.error_label)
        layout.addWidget(self.image_button)
        layout.addWidget(self.image)

        # Connect the color dialog button signal to the slot
        self.bg_color_button.clicked.connect(self.bg_color_button.open_color_dialog)
        self.bg_transparent_button.clicked.connect(self.make_bg_transparent)
        # test image
        self.load_image("mandrill.jpg")
        self.image_button.clicked.connect(self.prompt_load_image)
        self.resize_button.clicked.connect(self.resize_image)
        self.save_button.clicked.connect(self.save_image)

    @catch_error
    def make_bg_transparent(self):
        self.bg_color_button.update_bg("transparent")

    @catch_error
    # load image from file and display it in the image label
    def prompt_load_image(self):
        # open system finder
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        self.load_image(filename)

    @catch_error
    def load_image(self, filename):
        image = QPixmap(filename)
        self.original_image_pil = Image.open(filename).convert("RGBA")
        self.original_image_pil.filename = filename
        self.image.setPixmap(image.scaled(self.image.size(), Qt.KeepAspectRatio))
        # set placeholder for width and height edit
        self.original_width = image.width()
        self.width_edit.setPlaceholderText(str(image.width()))
        self.original_height = image.height()
        self.height_edit.setPlaceholderText(str(image.height()))
        # set placeholder for aspect ratio edit
        self.original_aspect_ratio = image.width() / image.height()
        self.aspect_edit.setPlaceholderText(f"{self.original_aspect_ratio:.3f}")

    @catch_error
    def resize_image(self):
        # get width and height from edit
        width = to_int(self.width_edit.text())
        height = to_int(self.height_edit.text())
        # get aspect ratio from edit
        aspect_ratio = to_float(self.aspect_edit.text())
        if aspect_ratio:
            if width and height:
                raise ValueError(
                    "Can't set both width and height if aspect ratio is set"
                )
            width, height = compute_new_size(
                self.original_aspect_ratio,
                self.original_width,
                self.original_height,
                aspect_ratio,
            )
        if not width and not height:
            raise ValueError("Must set width and height")

        color = self.bg_color_button.color
        print("padding color", color)
        self.resized_pil_image = resize_with_padding(
            self.original_image_pil, width, height, color
        )

        # set image to label
        new_pixmap = pil_to_pixmap(self.resized_pil_image).scaled(
            self.image.size(), Qt.KeepAspectRatio
        )
        self.image.setPixmap(new_pixmap)

    @catch_error
    def save_image(self):
        # default saved filename is `<original_name>_padded.<extension>`
        filename_path = Path(self.original_image_pil.filename)
        stem = filename_path.stem
        suffix = filename_path.suffix

        # open system finder, only allow to save in same format as original
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Image", f"{stem}_padded", f"Image Files (*.{suffix})"
        )
        # save with keep if jpeg, best otherwise
        if self.resized_pil_image is None:
            raise ValueError("Must resize image before saving")
        # change so it works for all formats
        self.resized_pil_image.save(filename, quality="keep")


# faillible convert to int
def to_int(s):
    try:
        return int(s)
    except ValueError:
        return None


# faillible convert to float
def to_float(s):
    try:
        return float(s)
    except ValueError:
        return None


# convert PIL image to QPIXMAP
def pil_to_pixmap(image: Image):
    width, height = image.size
    data = image.tobytes("raw", "RGBA")
    qimage = QImage(data, width, height, QImage.Format_RGBA8888)
    # qimage to qpixmap
    pixmap = QPixmap.fromImage(qimage)
    return pixmap


# aspect ratio to new width, height, only growing
def compute_new_size(old_aspect, width, height, new_aspect):
    if new_aspect > old_aspect:
        new_width = int(width * (new_aspect / old_aspect))
        new_height = height
    else:
        new_height = int(height * (old_aspect / new_aspect))
        new_width = width
    return new_width, new_height


def resize_with_padding(original_img, width, height, color):
    delta_width = width - original_img.size[0]
    delta_height = height - original_img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (
        pad_width,
        pad_height,
        int(delta_width - pad_width),
        delta_height - pad_height,
    )
    expanded = ImageOps.expand(original_img.copy(), padding, fill=color)
    return expanded


# https://stackoverflow.com/a/21901260/20374403
def get_git_revision_short_hash() -> str:
    return (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .decode("ascii")
        .strip()
    )


if __name__ == "__main__":
    print("#" * 80)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
