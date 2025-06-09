# interface.py
# encoding: utf-8

import sys
import json
import requests
import subprocess

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox
)
from PySide6.QtCore import QThread, Signal, QObject

from ui_form import Ui_MainWindow

class EmittingStream:
    def __init__(self, append_func):
        self.append_func = append_func

    def write(self, text):
        if text.strip():
            self.append_func(text)

    def flush(self):
        pass

class CallAnalysisWorker(QObject):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            response = requests.post("http://localhost:8030/", json=data, timeout=120)
            if response.status_code == 200:
                self.finished.emit(response.json())
            else:
                self.error.emit(f"Сервер вернул ошибку: {response.status_code}\n{response.text}")
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.call_history.clicked.connect(self.run_call_analysis)
        self.ui.extraction.clicked.connect(self.run_extraction)

    def run_call_analysis(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите JSON-файл", "", "JSON Files (*.json)")
        if not file_path:
            return

        self.thread = QThread()
        self.worker = CallAnalysisWorker(file_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_call_analysis_finished)
        self.worker.error.connect(self.on_call_analysis_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_call_analysis_finished(self, result):
        QMessageBox.information(self, "Результат", json.dumps(result, indent=4, ensure_ascii=False))

    def on_call_analysis_error(self, error_message):
        QMessageBox.critical(self, "Ошибка", f"Что-то пошло не так:\n{error_message}")

    def run_extraction(self):
        try:
            subprocess.run(["python", "extractor/extract.py"], check=True)
            QMessageBox.information(self, "Извлечение данных", "Извлечение завершено успешно.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при извлечении данных:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
