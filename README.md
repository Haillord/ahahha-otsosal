# 🎯 Stealth AI Aimer — Hardware Mouse Aiming System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![TensorRT](https://img.shields.io/badge/TensorRT-8.5+-green.svg)
![Arduino](https://img.shields.io/badge/Arduino-Leonardo-yellow.svg)
![GPU](https://img.shields.io/badge/GPU-RTX_5070_Ready-green.svg)

**StealthAimer** — это аппаратный аим-ассистент нового поколения (2026 Edition). Система использует нейросети YOLOv11 с оптимизацией TensorRT и внешние микроконтроллеры для полной имитации физической мыши.

---

## 📌 Оглавление

- [Как это работает](#-как-это-работает)
- [Готовый исполняемый файл (Release)](#-готовый-исполняемый-файл-release)
- [Инструкция по сборке](#-сборка-и-запуск)
---

## 🧠 Как это работает

Система построена на принципе разделения вычислений и действий:

1. **Захват экрана** — `dxcam` вырезает FOV с минимальной задержкой.
2. **Детекция целей** — YOLOv11 (TensorRT) на **RTX 5070** определяет цели < 1 мс.
3. **Адаптивный хитбокс** — динамическое смещение точки прицеливания.
4. **Hardware Mouse** — координаты уходят на **Arduino Leonardo**, которая эмулирует USB-мышь.

---

## 🖥️ Необходимое оборудование

| Компонент | Рекомендации |
| :--- | :--- |
| **Arduino** | Leonardo / Pro Micro (ATmega32U4) |
| **Видеокарта** | RTX 5070 / 40 / 30 series |
| **Процессор** | Ryzen 5 5600 или выше |

---

## 🔧 Сборка и запуск

> **Сами разберетесь как собрать нахуй блять**

---


## 📦 Готовый исполняемый файл (Release)

🚀 **[Скачать StealthAimer v1.0 Stable](https://github.com/Haillord/ahahha-otsosal/releases/tag/1.0)**

**Порядок запуска:**

1. Подключите Arduino к ПК.
2. Запустите `StealthAimer.exe`.
3. Вкладка **Прошивка** → выберите COM-порт → **Прошить**.
4. Нажмите **F1** для активации в игре.
