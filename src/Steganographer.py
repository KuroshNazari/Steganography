from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QMessageBox, QScrollArea, QHBoxLayout,
                             QTextEdit)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QTextOption
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from datetime import datetime
import skimage.io
import sys
import os

from encoder import encode, decode


def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and PyInstaller """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = "."
    return os.path.join(base_path, relative_path)

icon_path = resource_path("icon.ico")


# Thread class for performing encoding in background
class EncodeWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)     

    def __init__(self, picture, text, password):
        super().__init__()
        self.picture = picture
        self.text = text
        self.password = password

    def run(self):
        try:
            # Encoding text into image using encode function from encoder module 
            img = skimage.io.imread(self.picture)
            result = encode(img=img, string=self.text, password=self.password if self.password else None)
            now = datetime.now().strftime("_%Y%m%d-%H%M%S")
            save_path = self.picture.rsplit('.', 1)[0] + now + '_encoded.png'
            skimage.io.imsave(save_path, result)
            self.finished.emit(save_path)
        except Exception as e:
            self.error.emit(str(e))


# Main application window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Setup main window properties
        self.setWindowTitle("Steganographer")
        self.setFixedWidth(300)
        self.setWindowIcon(QIcon(icon_path))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Encode tab
        self.encode_tab = QWidget()
        self.tabs.addTab(self.encode_tab, "Encode")
        self.init_encoding_tab()

        # Decode tab
        self.decode_tab = QWidget()
        self.tabs.addTab(self.decode_tab, "Decode")
        self.init_decoding_tab()

        # Results Tab
        self.results_tab = QWidget()
        self.tabs.addTab(self.results_tab, "Results")
        self.results_label = QLabel("Results will be displayed here.")
        layout = QVBoxLayout()
        layout.addWidget(self.results_label)
        self.results_tab.setLayout(layout)
        self.tabs.setTabEnabled(2, False)

        # About Tab
        self.about_tab = QWidget()
        self.tabs.addTab(self.about_tab, "About")
        self.init_about_tab()
        
        # Add a footer for the copyright notice
        self.add_footer()


    # Initialize the Encode tab
    def init_encoding_tab(self):
        layout = QVBoxLayout()

        # Picture upload section
        self.label_pic_enc = QLabel("No picture selected.")
        self.label_pic_enc.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_pic_enc)

        btn_upload_pic_enc = QPushButton("Upload Picture")
        btn_upload_pic_enc.clicked.connect(self.upload_picture_enc)
        layout.addWidget(btn_upload_pic_enc)

        # Text input section
        self.text_enc = QTextEdit()
        self.text_enc.setWordWrapMode(QTextOption.WordWrap)  # Enable word wrap
        self.text_enc.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Enable vertical scrolling if needed
        self.text_enc.setPlaceholderText("Enter Text")
        layout.addWidget(self.text_enc)

        label = QLabel("* Use encryption for Persian characters")
        label.setStyleSheet("font-size: 10px; color: blue;")
        layout.addWidget(label)

        # Password input section
        self.password_enc = QLineEdit()
        self.password_enc.setEchoMode(QLineEdit.Password)
        self.password_enc.setPlaceholderText("Password (Optional)")
        layout.addWidget(self.password_enc)

        # Submit button
        self.btn_submit_dec = QPushButton("Encode")
        self.btn_submit_dec.clicked.connect(self.encoding_tab_function)
        layout.addWidget(self.btn_submit_dec)

        self.encode_tab.setLayout(layout)


    # Initialize the Decode tab
    def init_decoding_tab(self):
        layout = QVBoxLayout()

        # Picture upload section
        self.label_pic_dec = QLabel("No picture selected.")
        self.label_pic_dec.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_pic_dec)

        btn_upload_pic_dec = QPushButton("Upload Picture")
        btn_upload_pic_dec.clicked.connect(self.upload_picture_dec)
        layout.addWidget(btn_upload_pic_dec)

        # Password input section
        self.password_dec = QLineEdit()
        self.password_dec.setEchoMode(QLineEdit.Password)
        self.password_dec.setPlaceholderText("Password")
        layout.addWidget(self.password_dec)
    
        # Submit button
        self.btn_submit_dec = QPushButton("Decode")
        self.btn_submit_dec.clicked.connect(self.decoding_tab_function)
        layout.addWidget(self.btn_submit_dec)

        self.decode_tab.setLayout(layout)


    # Initialize the About tab content
    def init_about_tab(self):
        layout = QVBoxLayout()
      
        about_app_label = QLabel("About App")
        about_app_label.setAlignment(Qt.AlignCenter)
        about_app_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 0; margin-bottom: 0px;")
        layout.addWidget(about_app_label)

        app_info = QLabel(
            "Name: Steganographer\n"
            "Version: 1.0.0\n"
            "Release Date: 12/18/2024\n"
            "Powerd By: PyQt5\n"
            "Developed By: Kourosh Nazari\n"
        )
        app_info.setAlignment(Qt.AlignCenter)
        app_info.setStyleSheet("font-size: 14px; padding: 5px; margin-bottom: 0;")
        app_info.setWordWrap(True)
        layout.addWidget(app_info)
      
        about_label = QLabel("About the Developer")
        about_label.setAlignment(Qt.AlignCenter)
        about_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 0; margin-bottom: 0px;")
        layout.addWidget(about_label)

        developer_info = QLabel(
            "Name: Kourosh Nazari\n"
            "Email: k.nazari1381@gmail.com\n"
            "Github Username: KuroshNazari\n"
            "Telegram Username: KuroshNazari\n"
        )
        developer_info.setAlignment(Qt.AlignCenter)
        developer_info.setStyleSheet("QLabel {font-size: 14px; padding: 5px; margin-bottom: 70px;}")
        developer_info.setWordWrap(True)
        layout.addWidget(developer_info)

        self.about_tab.setLayout(layout)

    # Add footer for copyright and version information
    def add_footer(self):
        footer = QWidget()
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer.setLayout(footer_layout)

        copyright_label = QLabel("© 2024 Steganographer. All rights reserved.\n Version: 1.0.0")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #fff; font-size: 10px;")
        footer_layout.addWidget(copyright_label)

        self.main_layout.addWidget(footer)


    # Handle picture upload for encoding
    def upload_picture_enc(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Picture", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.label_pic_enc.setPixmap(QPixmap(file_name).scaled(200, 200, Qt.KeepAspectRatio))
            self.picture_path1 = file_name


    # Handle picture upload for decoding
    def upload_picture_dec(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Picture", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.label_pic_dec.setPixmap(QPixmap(file_name).scaled(200, 200, Qt.KeepAspectRatio))
            self.picture_path2 = file_name


    # Perform the encoding process
    def encoding_tab_function(self):
        picture = getattr(self, 'picture_path1', None)
        password = self.password_enc.text()
        text = self.text_enc.toPlainText()
        # text = text.encode("utf-8").decode("utf-8")

        if not picture or not text:
            QMessageBox.warning(self, "Input Error", "Picture and text are required for encoding.")
            return

        # Initialize and start the worker thread
        self.worker = EncodeWorker(picture, text, password)
        self.worker.finished.connect(self.on_encode_finished)
        self.worker.error.connect(self.on_encode_error)
        self.worker.start()


    # Perform the decoding process
    def decoding_tab_function(self):
        picture = getattr(self, 'picture_path2', None)
        password = self.password_dec.text()

        if not picture:
            QMessageBox.warning(self, "Input Error", "Picture is required for decoding.")
            return

        try:
            img = skimage.io.imread(picture)
            result = decode(img=img, password=password if password else None)
            self.display_results(result)
        except Exception as e:
            QMessageBox.warning(self, "Decoding Error", str(e))


    # Handle the successful encoding process
    def on_encode_finished(self, save_path):
        QMessageBox.information(self, "Encoding Results", f"Image saved at:\n{save_path}")


    # Handle errors during the encoding process
    def on_encode_error(self, error_message):
        QMessageBox.warning(self, "Encoding Error", error_message)


    # Display the decoding results
    def display_results(self, results):

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        self.results_label.setText(results)
        scroll_layout.addWidget(self.results_label)
        scroll_widget.setLayout(scroll_layout)

        scroll_area.setWidget(scroll_widget)

        # scrollable area
        layout = self.results_tab.layout()
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)
        layout.addWidget(scroll_area)

        self.save_button = QPushButton("Save Results as Text File")
        self.save_button.clicked.connect(lambda: self.save_results_to_file(results))
        layout.addWidget(self.save_button)

        self.tabs.setTabEnabled(2, True)
        self.tabs.setCurrentIndex(2)


    # Save the results to a text file
    def save_results_to_file(self, results):
        save_file, _ = QFileDialog.getSaveFileName(self, "Save Results As", "results.txt", "Text Files (*.txt)")
        if save_file:
            try:
                with open(save_file, "w", encoding="utf-8") as file:
                    file.write(results)
                QMessageBox.information(self, "Save Success", f"Results saved to {save_file}")
            except Exception as e:
                QMessageBox.warning(self, "Save Error", str(e))



if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set the application font
    custom_font = QFont("Arial", 10)
    custom_font.setBold(False)
    app.setFont(custom_font)
    app.setWindowIcon(QIcon(icon_path))

    # Define application stylesheet
    style = """

        QWidget {
            background-color: #8d99ae;
            font-family: 'Arial font';
        }

        QPushButton {
            background: #2b2d42;
            border: none;
            padding: 10px;
            border-radius: 5px;
            color: #fff;
        }

        QLineEdit {
            background: #edf2f4;
            border: none;
            padding: 10px;
            border-radius: 5px;
            color: #000;
        }

        QTabWidget::pane {
            border: none;
            background: #8d99ae;
        } 

        QTabBar::tab {
            background: #8d99ae;
            padding: 15px;
        } 

        QTabBar::tab:selected { 
            background: #2b2d42;
            color: #fff;
        }

        QScrollBar:vertical {
            border: none;
            background: #edf2f4;
            width: 12px;
            margin: 0px 0px 0px 0px;
        }

        QScrollBar::handle:vertical {
            background: #2b2d42;
            min-height: 20px;
            border-radius: 5px;
        }

        QScrollBar::add-line:vertical {
            background: none;
            height: 0px;
        }

        QScrollBar::sub-line:vertical {
            background: none;
            height: 0px;
        }

        QScrollBar:horizontal {
            border: none;
            background: #edf2f4;
            height: 12px;
            margin: 0px 0px 0px 0px;
        }

        QScrollBar::handle:horizontal {
            background: #2b2d42;
            min-width: 20px;
            border-radius: 5px;
        }

        QScrollBar::add-line:horizontal {
            background: none;
            width: 0px;
        }

        QScrollBar::sub-line:horizontal {
            background: none;
            width: 0px;
        }


    """
    app.setStyleSheet(style)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
