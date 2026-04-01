# flasher.py
import subprocess
import os
import sys
import threading

def get_resource_path(relative_path):
    """Получить путь к ресурсу, учитывая сборку PyInstaller"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def flash_arduino(port, log_callback):
    """
    Прошивает Arduino через avrdude.
    port: COM-порт (например, "COM3")
    log_callback: функция для вывода логов
    """
    def run():
        avrdude_path = get_resource_path("resources/avrdude.exe")
        conf_path = get_resource_path("resources/avrdude.conf")
        hex_path = get_resource_path("resources/firmware.hex")
        
        if not os.path.isfile(avrdude_path):
            log_callback("Ошибка: avrdude.exe не найден")
            return
        if not os.path.isfile(hex_path):
            log_callback("Ошибка: firmware.hex не найден")
            return
        
        # Команда для Leonardo/Pro Micro (avr109)
        cmd = [
            avrdude_path,
            "-C", conf_path,
            "-p", "atmega32u4",
            "-c", "avr109",
            "-P", port,
            "-b", "115200",
            "-U", f"flash:w:{hex_path}:i"
        ]
        log_callback(f"Запуск прошивки: {' '.join(cmd)}")
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            for line in process.stdout:
                log_callback(line.strip())
            process.wait()
            if process.returncode == 0:
                log_callback("Прошивка успешно завершена!")
            else:
                log_callback(f"Ошибка прошивки (код {process.returncode})")
        except Exception as e:
            log_callback(f"Исключение: {e}")
    
    threading.Thread(target=run, daemon=True).start()