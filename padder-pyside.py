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
from PySide6.QtGui import QColor, QImage, QPixmap, QPalette
from PySide6.QtCore import Qt
from PIL import Image, ImageOps


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
            print(e)
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
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

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
        self.image.setFixedSize(600, 400)
        self.image.setStyleSheet(
            f"border: 1px solid black; border-radius: 5px;"
        )

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
        layout.addWidget(self.error_label)
        layout.addWidget(self.image_button)
        layout.addWidget(self.image)

        # Connect the color dialog button signal to the slot
        self.bg_color_button.clicked.connect(self.bg_color_button.open_color_dialog)
        self.bg_transparent_button.clicked.connect(self.make_bg_transparent)
        # Connect the image label to `load_image` method
        self.image_button.clicked.connect(self.load_image)
        self.resize_button.clicked.connect(self.resize_image)

    @catch_error
    def make_bg_transparent(self):
        self.bg_color_button.update_bg("transparent")

    @catch_error
    # load image from file and display it in the image label
    def load_image(self):
        # open system finder
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        image = QPixmap(filename)
        self.original_image_pil = Image.open(filename)
        self.image.setPixmap(image)
        # set label size to image size
        self.image.setFixedSize(image.size())
        # set placeholder for width and height edit
        self.width_edit.setPlaceholderText(str(image.width()))
        self.height_edit.setPlaceholderText(str(image.height()))
        # set placeholder for aspect ratio edit
        self.aspect_edit.setPlaceholderText(f"{(image.width() / image.height()):.3f}")

    @catch_error
    def resize_image(self):
        # get width and height from edit
        width = to_int(self.width_edit.text())
        height = to_int(self.height_edit.text())
        # get aspect ratio from edit
        aspect_ratio = to_float(self.aspect_edit.text())
        if aspect_ratio:
            # if width and height is set, ignore aspect ratio
            if width and height:
                raise ValueError(
                    "Can't set both width and height if aspect ratio is set"
                )
            TODO
        if not width and not height:
            raise ValueError("Must set width and height")

        color = self.bg_color_button.color or "transparent"
        print("padding color", color)
        self.resized_pil_image = resize_with_padding(
            self.original_image_pil, width, height, color
        )
        # set image to label
        new_pixmap = pil_to_pixmap(self.resized_pil_image)
        self.image.setPixmap(new_pixmap)
        self.image.setFixedSize(new_pixmap.size())


    # set pixmap to label
    def set_pixmap(self, pixmap: QPixmap):
        self.image.setPixmap(pixmap)
        self.image.setFixedSize(pixmap.size())
        # set placeholder for width and height edit
        self.width_edit.setPlaceholderText(str(image.width()))
        self.height_edit.setPlaceholderText(str(image.height()))
        # set placeholder for aspect ratio edit
        self.aspect_edit.setPlaceholderText(f"{(image.width() / image.height()):.3f}")


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


# convert QPIXMAP to PIL image
# def qimage_to_pil(image: QImage):
#     image = image.convertToFormat(QImage.Format_RGBA8888)
#     width = image.width()
#     height = image.height()
#     ptr = image.bits()
#     ptr.setsize(image.byteCount())
#     arr = bytearray(ptr)
#     return Image.frombuffer("RGBA", (width, height), arr, "raw", "RGBA", 0, 1)


# convert PIL image to QPIXMAP
def pil_to_pixmap(image: Image):
    width, height = image.size
    data = image.tobytes("raw", "RGBA")
    qimage = QImage(data, width, height, QImage.Format_RGBA8888)
    # qimage to qpixmap
    pixmap = QPixmap.fromImage(qimage)
    return pixmap


def resize_with_padding(img, width, height, color):
    img.thumbnail((width, height))
    delta_width = width - img.size[0]
    delta_height = height - img.size[1]
    pad_width = delta_width // 2
    pad_height = delta_height // 2
    padding = (
        pad_width,
        pad_height,
        int(delta_width - pad_width),
        delta_height - pad_height,
    )
    # expand with color
    print("expand")
    return ImageOps.expand(img, padding, fill=None)


# Make it so all images have 1.33 aspect ratios
def normalise_img(path):
    desired_aspect_ratio = 1.33
    old = Image.open(path)
    width, height = old.size
    current_asp = width / height
    if abs(current_asp - desired_aspect_ratio) < 0.01:
        return old  # Good enough
    return resize_with_padding(old, int(width * desired_aspect_ratio), int(width))


if __name__ == "__main__":
    print("#" * 80)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
