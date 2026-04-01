# aimer_core.py
import threading
import time
import math
import logging
import os
import random
from collections import deque
import dxcam
from ultralytics import YOLO
from hardware_mouse import HardwareMouse
from humanized_aimer import HumanizedAimer
from settings import Settings

log = logging.getLogger("Aimer")

class AimerCore(threading.Thread):
    def __init__(self, settings: Settings, log_callback=None):
        super().__init__(daemon=True)
        self.settings = settings
        self.log_callback = log_callback or (lambda x: None)
        self.stop_event = threading.Event()
        self.model = None
        self.camera = None
        self.mouse = None
        self.aimer = None
        self.frame_queue = deque(maxlen=2)
        self.target_queue = deque(maxlen=1)
    
    def run(self):
        self.log("Инициализация...")
        try:
            # Загрузка модели
            if not os.path.isfile(self.settings.model_path):
                raise Exception(f"Модель не найдена: {self.settings.model_path}")
            self.model = YOLO(self.settings.model_path, task='detect')
            self.log("Модель загружена")
            
            # Захват экрана
            screen_w, screen_h = self._get_screen_res()
            f = self.settings.fov
            region = (
                (screen_w - f)//2, (screen_h - f)//2,
                (screen_w + f)//2, (screen_h + f)//2
            )
            self.camera = dxcam.create(region=region, output_color="BGR")
            if self.camera is None:
                raise Exception("Не удалось создать захват экрана")
            self.camera.start(target_fps=0, video_mode=True)
            self.log("Захват экрана запущен")
            
            # Arduino
            self.mouse = HardwareMouse(self.settings.com_port, self.settings.baudrate, self.settings.arduino_timeout)
            self.aimer = HumanizedAimer(self.mouse, self.settings)
            
            self.log("Готово. Запуск обработки...")
            while not self.stop_event.is_set():
                frame = self.camera.get_latest_frame()
                if frame is None:
                    time.sleep(0.0001)
                    continue
                self.frame_queue.append(frame)
                self._process_frame()
        except Exception as e:
            self.log(f"Ошибка: {e}")
        finally:
            self.cleanup()
    
    def _process_frame(self):
        if not self.frame_queue:
            return
        frame = self.frame_queue[-1]
        results = self.model.predict(frame, conf=self.settings.conf, imgsz=self.settings.imgsz,
                                     half=self.settings.use_half, verbose=self.settings.verbose)
        best = None
        min_dist = float('inf')
        center = self.settings.fov / 2.0
        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                if int(box.cls) != 0:
                    continue
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                hx = (x1 + x2) / 2.0
                hy = y1 + (y2 - y1) / 8.0
                dist = math.hypot(hx - center, hy - center)
                if dist < min_dist:
                    min_dist = dist
                    best = (hx, hy, x2 - x1)
        
        self.target_queue.append(best)
        
        # Обработка цели
        if best:
            hx, hy, box_width = best
            if self.aimer.should_process():
                if random.random() < self.settings.miss_chance:
                    self.log("Пропуск цели (промах)")
                    self.aimer.reset()
                    return
                tx, ty = self.aimer.get_humanized_target(hx, hy, box_width)
                dx = tx - center
                dy = ty - center
                self.aimer.aim(dx, dy)
        else:
            self.aimer.reset()
    
    def _get_screen_res(self):
        try:
            cam = dxcam.create()
            if cam:
                return cam.screen_resolution
        except:
            pass
        import tkinter as tk
        root = tk.Tk()
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        root.destroy()
        return w, h
    
    def stop(self):
        self.stop_event.set()
    
    def cleanup(self):
        if self.camera:
            self.camera.stop()
        if self.mouse:
            self.mouse.close()
        self.log("Остановлено")
    
    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)