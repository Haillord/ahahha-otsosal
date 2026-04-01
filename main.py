# main.py
import sys
import os
import logging
import serial.tools.list_ports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from settings import Settings
from aimer_core import AimerCore
from flasher import flash_arduino

# Перехват логов для вывода в GUI
class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    
    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.core = None
        self.settings = Settings()
        self.initUI()
        self.setup_logging()
    
    def initUI(self):
        self.setWindowTitle("Stealth AI Aimer")
        self.setFixedSize(700, 550)
        
        # Центральный виджет с вкладками
        tabs = QTabWidget()
        self.setCentralWidget(tabs)
        
        # ---- Вкладка "Прошивка" ----
        flash_tab = QWidget()
        flash_layout = QVBoxLayout()
        
        self.port_combo_flash = QComboBox()
        self.refresh_ports()
        refresh_btn = QPushButton("Обновить порты")
        refresh_btn.clicked.connect(self.refresh_ports)
        flash_btn = QPushButton("Прошить Arduino")
        flash_btn.clicked.connect(self.flash_arduino)
        
        flash_layout.addWidget(QLabel("Выберите COM-порт:"))
        flash_layout.addWidget(self.port_combo_flash)
        flash_layout.addWidget(refresh_btn)
        flash_layout.addWidget(flash_btn)
        flash_layout.addStretch()
        flash_tab.setLayout(flash_layout)
        tabs.addTab(flash_tab, "Прошивка")
        
        # ---- Вкладка "Настройки" ----
        settings_tab = QWidget()
        settings_layout = QFormLayout()
        
        # Модель
        self.model_path_edit = QLineEdit(self.settings.model_path)
        model_browse_btn = QPushButton("Обзор")
        model_browse_btn.clicked.connect(self.browse_model)
        model_layout = QHBoxLayout()
        model_layout.addWidget(self.model_path_edit)
        model_layout.addWidget(model_browse_btn)
        settings_layout.addRow("Модель (.engine):", model_layout)
        
        # Confidence
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(20, 80)
        self.conf_slider.setValue(int(self.settings.conf * 100))
        self.conf_label = QLabel(f"{self.settings.conf:.2f}")
        self.conf_slider.valueChanged.connect(lambda v: self.conf_label.setText(f"{v/100:.2f}"))
        settings_layout.addRow("Confidence:", self.conf_slider)
        settings_layout.addRow("", self.conf_label)
        
        # FOV
        self.fov_spin = QSpinBox()
        self.fov_spin.setRange(200, 800)
        self.fov_spin.setValue(self.settings.fov)
        settings_layout.addRow("FOV (px):", self.fov_spin)
        
        # Smooth
        self.smooth_slider = QSlider(Qt.Horizontal)
        self.smooth_slider.setRange(0, 100)
        self.smooth_slider.setValue(int(self.settings.smooth_base * 100))
        self.smooth_label = QLabel(f"{self.settings.smooth_base:.2f}")
        self.smooth_slider.valueChanged.connect(lambda v: self.smooth_label.setText(f"{v/100:.2f}"))
        settings_layout.addRow("Smooth:", self.smooth_slider)
        settings_layout.addRow("", self.smooth_label)
        
        # Hitbox
        self.hitbox_slider = QSlider(Qt.Horizontal)
        self.hitbox_slider.setRange(0, 100)
        self.hitbox_slider.setValue(int(self.settings.hitbox_base * 100))
        self.hitbox_label = QLabel(f"{self.settings.hitbox_base:.2f}")
        self.hitbox_slider.valueChanged.connect(lambda v: self.hitbox_label.setText(f"{v/100:.2f}"))
        settings_layout.addRow("Hitbox size (%):", self.hitbox_slider)
        settings_layout.addRow("", self.hitbox_label)
        
        # Miss chance
        self.miss_slider = QSlider(Qt.Horizontal)
        self.miss_slider.setRange(0, 50)
        self.miss_slider.setValue(int(self.settings.miss_chance * 100))
        self.miss_label = QLabel(f"{self.settings.miss_chance:.2f}")
        self.miss_slider.valueChanged.connect(lambda v: self.miss_label.setText(f"{v/100:.2f}"))
        settings_layout.addRow("Miss chance:", self.miss_slider)
        settings_layout.addRow("", self.miss_label)
        
        # COM-порт для аима
        self.port_combo_aim = QComboBox()
        self.refresh_ports_aim()
        refresh_aim_btn = QPushButton("Обновить")
        refresh_aim_btn.clicked.connect(self.refresh_ports_aim)
        settings_layout.addRow("COM-порт (аим):", self.port_combo_aim)
        settings_layout.addRow("", refresh_aim_btn)
        
        settings_tab.setLayout(settings_layout)
        tabs.addTab(settings_tab, "Настройки")
        
        # ---- Вкладка "Управление" ----
        control_tab = QWidget()
        control_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("Запустить аим")
        self.start_btn.clicked.connect(self.start_aimer)
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.clicked.connect(self.stop_aimer)
        self.stop_btn.setEnabled(False)
        
        self.status_label = QLabel("Статус: не активен")
        self.status_label.setStyleSheet("color: red")
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.status_label)
        control_layout.addStretch()
        control_tab.setLayout(control_layout)
        tabs.addTab(control_tab, "Управление")
        
        # ---- Вкладка "Логи" ----
        log_tab = QWidget()
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_tab.setLayout(log_layout)
        tabs.addTab(log_tab, "Логи")
        
        # Горячие клавиши
        self.shortcut_start = QShortcut(QKeySequence("F1"), self)
        self.shortcut_start.activated.connect(self.start_aimer)
        self.shortcut_stop = QShortcut(QKeySequence("F2"), self)
        self.shortcut_stop.activated.connect(self.stop_aimer)
    
    def setup_logging(self):
        logger = logging.getLogger("Aimer")
        logger.setLevel(logging.INFO)
        handler = QTextEditLogger(self.log_text)
        logger.addHandler(handler)
        # Также выводим в консоль для отладки (если запущено из консоли)
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(console)
    
    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo_flash.clear()
        self.port_combo_flash.addItems(ports)
    
    def refresh_ports_aim(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo_aim.clear()
        self.port_combo_aim.addItems(ports)
    
    def browse_model(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите модель", "", "TensorRT Engine (*.engine)")
        if path:
            self.model_path_edit.setText(path)
    
    def flash_arduino(self):
        port = self.port_combo_flash.currentText()
        if not port:
            QMessageBox.warning(self, "Ошибка", "Выберите COM-порт")
            return
        
        def log_callback(msg):
            QMetaObject.invokeMethod(self.log_text, "append", Qt.QueuedConnection, Q_ARG(str, msg))
        
        flash_arduino(port, log_callback)
    
    def start_aimer(self):
        # Собрать настройки из GUI
        self.settings.model_path = self.model_path_edit.text()
        self.settings.conf = self.conf_slider.value() / 100.0
        self.settings.fov = self.fov_spin.value()
        self.settings.smooth_base = self.smooth_slider.value() / 100.0
        self.settings.hitbox_base = self.hitbox_slider.value() / 100.0
        self.settings.miss_chance = self.miss_slider.value() / 100.0
        self.settings.com_port = self.port_combo_aim.currentText()
        
        # Проверка наличия модели
        if not os.path.isfile(self.settings.model_path):
            QMessageBox.warning(self, "Ошибка", "Модель не найдена")
            return
        
        # Проверка COM-порта
        if not self.settings.com_port:
            QMessageBox.warning(self, "Ошибка", "Выберите COM-порт для аима")
            return
        
        # Запуск в отдельном потоке
        self.core = AimerCore(self.settings, log_callback=self.log_text.append)
        self.core.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Статус: активен")
        self.status_label.setStyleSheet("color: green")
    
    def stop_aimer(self):
        if self.core:
            self.core.stop()
            self.core = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Статус: не активен")
        self.status_label.setStyleSheet("color: red")
    
    def closeEvent(self, event):
        self.stop_aimer()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())