import sys
import pytesseract
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import Image
import cv2,os
import numpy as np 
import datetime

# Jika tesseract tidak di PATH, set manual:
pytesseract.pytesseract.tesseract_cmd = r"E:\Data\Tesseract_ORC\tesseract.exe"

# arahkan ke folder tessdata
os.environ["TESSDATA_PREFIX"] = r"E:\Data\Tesseract_ORC\tessdata"
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class OCRApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR with Tesseract")
        self.resize(900, 600)

        self.image_label = QtWidgets.QLabel("No image loaded")
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setMinimumSize(640, 480)

        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(False)

        # Buttons
        btn_open = QtWidgets.QPushButton("Open Image")
        btn_open.clicked.connect(self.open_image)

        btn_ocr = QtWidgets.QPushButton("Run OCR")
        btn_ocr.clicked.connect(self.run_ocr)

        btn_save = QtWidgets.QPushButton("Save Text")
        btn_save.clicked.connect(self.save_text)

        # Layouts
        left_v = QtWidgets.QVBoxLayout()
        left_v.addWidget(self.image_label)
        left_v.addWidget(btn_open)
        left_v.addWidget(btn_ocr)
        left_v.addWidget(btn_save)

        right_v = QtWidgets.QVBoxLayout()
        right_v.addWidget(QtWidgets.QLabel("Recognized Text:"))
        right_v.addWidget(self.text_edit)

        main_h = QtWidgets.QHBoxLayout(self)
        main_h.addLayout(left_v, 2)
        main_h.addLayout(right_v, 3)

        # State
        self.current_image = None

    def open_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open image", "", 
                                                       "Image files (*.png *.jpg *.jpeg *.bmp *.tif)")
        if not path:
            return
        img_bgr = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img_bgr is None:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to open image.")
            return
        self.current_image = img_bgr
        self.display_image(img_bgr)

    def display_image(self, bgr_img):
        rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_image = QtGui.QImage(rgb.data, w, h, ch*w, QtGui.QImage.Format_RGB888)
        scaled = qt_image.scaled(self.image_label.width(), self.image_label.height(), 
                                 QtCore.Qt.KeepAspectRatio)
        self.image_label.setPixmap(QtGui.QPixmap.fromImage(scaled))

    def run_ocr(self):
        if self.current_image is None:
            QtWidgets.QMessageBox.warning(self, "Warning", "No image loaded.")
            return
        rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        text = pytesseract.image_to_string(pil_img, lang="eng")  # ganti "ind" untuk bahasa Indonesia
        self.text_edit.setText(text)

    def save_text(self):
        text = self.text_edit.toPlainText()
        if not text.strip():
            QtWidgets.QMessageBox.information(self, "Info", "No text to save.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Text", 
                                                        f"ocr_result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                                        "Text files (*.txt)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        QtWidgets.QMessageBox.information(self, "Saved", f"Text saved to:\n{path}")

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = OCRApp()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
