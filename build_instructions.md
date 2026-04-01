# Сборка StealthAimer

## Требования
- Python 3.8+
- Установленные зависимости: `pip install pyinstaller ultralytics pyserial dxcam numpy PyQt5`

## Подготовка ресурсов
1. Скомпилировать Arduino скетч в `.hex` (Arduino IDE → Экспорт бинарного файла).
2. Переименовать `.hex` в `firmware.hex` и положить в папку `resources/`.
3. Скопировать `avrdude.exe` и `avrdude.conf` из папки Arduino (`hardware/tools/avr/`) в `resources/`.
4. Поместить модель `yolov11m.engine` в корень проекта (или указать путь в настройках).

## Сборка
```bash
pyinstaller --onefile --windowed --add-data "resources;resources" --hidden-import PyQt5.sip --hidden-import serial --name "StealthAimer" main.py