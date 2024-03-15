import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QComboBox, QPushButton, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal

class SerialReadThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, port_name, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self.serial_port = None
        self.is_running = False

    def run(self):
        try:
            self.serial_port = serial.Serial(self.port_name, 9600)
            self.is_running = True
            while self.is_running and self.serial_port.is_open:
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:
                    self.data_received.emit(data)
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            if self.serial_port:
                self.serial_port.close()

    def stop(self):
        self.is_running = False

class SerialDataLogger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.serial_thread = None
        self.file = None

    def initUI(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.populate_port_combo()
        top_layout.addWidget(self.port_combo)
        self.start_button = QPushButton("Старт")
        self.start_button.clicked.connect(self.start_logging)
        top_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Стоп")
        self.stop_button.clicked.connect(self.stop_logging)
        self.stop_button.setEnabled(False)
        top_layout.addWidget(self.stop_button)
        main_layout.addLayout(top_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        main_layout.addWidget(self.text_edit)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Serial Data Logger")

    def populate_port_combo(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        current_port = self.port_combo.currentText()
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        if current_port in ports:
            self.port_combo.setCurrentText(current_port)

    def start_logging(self):
        port_name = self.port_combo.currentText()
        self.serial_thread = SerialReadThread(port_name, self)
        self.serial_thread.data_received.connect(self.update_text_edit)
        self.file = open('data.txt', 'a')
        self.serial_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_logging(self):
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread.wait()
        if self.file:
            self.file.close()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_text_edit(self, data):
        self.text_edit.append(data)
        if self.file:
            self.file.write(data + '\n')
            self.file.flush()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    logger = SerialDataLogger()
    logger.show()
    sys.exit(app.exec_())