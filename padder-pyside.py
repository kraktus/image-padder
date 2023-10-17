import sys
from PySide6.QtWidgets import QPushButton, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QSlider, QColorDialog
from PySide6.QtGui import QColor, QImage, QPixmap, QPalette
from PySide6.QtCore import Qt

class Color(QWidget):

    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

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
        topbar_layout.setAlignment(Qt.AlignLeft)
        layout.addLayout(topbar_layout)

        # Create the top bar widgets
        aspect_label = QLabel("Aspect Ratio:")
        self.aspect_edit = QLineEdit()
        self.aspect_edit.setFixedWidth(60)

        width_label = QLabel("Width:")
        self.width_edit = QLineEdit()
        self.width_edit.setFixedWidth(60)

        height_label = QLabel("Height:")
        self.height_edit = QLineEdit()
        self.height_edit.setFixedWidth(60)

        self.color_dialog_button = QPushButton("Color Chooser")

        # Create an image label to display the image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(600, 400)

        # Add the top bar widgets and the image label to the layout
        topbar_layout.addWidget(aspect_label)
        topbar_layout.addWidget(self.aspect_edit)
        topbar_layout.addWidget(width_label)
        topbar_layout.addWidget(self.width_edit)
        topbar_layout.addWidget(height_label)
        topbar_layout.addWidget(self.height_edit)
        topbar_layout.addWidget(self.color_dialog_button)
        layout.addWidget(self.image_label)

        # Connect the color dialog button signal to the slot
        self.color_dialog_button.clicked.connect(self.open_color_dialog)

    def open_color_dialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.image_label.setStyleSheet("background-color: %s" % color.name())

    def update_image(self):
        aspect = float(self.aspect_edit.text())
        width = int(self.width_edit.text())
        height = int(self.height_edit.text())

        # Create an image with the specified width, height, and aspect ratio
        image = QImage(width, height, QImage.Format_RGB32)
        image.fill(Qt.white)

        painter = QPainter(image)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawRect(0, 0, width * aspect, height)

        # Scale the image to fit the label's size
        scaled_image = image.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio)

        # Convert the image to QPixmap and set it as the label's pixmap
        pixmap = QPixmap.fromImage(scaled_image)
        self.image_label.setPixmap(pixmap)

        painter.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())