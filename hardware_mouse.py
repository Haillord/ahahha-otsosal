# hardware_mouse.py
import threading
import serial
import logging

log = logging.getLogger("Aimer")

class HardwareMouse:
    def __init__(self, port: str, baudrate: int, timeout: float = 0.1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.lock = threading.Lock()
        self._connect()
    
    def _connect(self):
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            log.info(f"Arduino подключена на {self.port}")
        except Exception as e:
            log.error(f"Ошибка подключения к Arduino: {e}")
            self.serial = None
    
    def move(self, x: int, y: int):
        if self.serial is None:
            return
        x = max(-127, min(127, x))
        y = max(-127, min(127, y))
        if x == 0 and y == 0:
            return
        try:
            with self.lock:
                self.serial.write(f"{x},{y}\n".encode())
        except Exception as e:
            log.warning(f"Ошибка отправки на Arduino: {e}")
            self._connect()
    
    def close(self):
        if self.serial and self.serial.is_open:
            self.serial.close()