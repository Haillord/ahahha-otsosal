# settings.py
from dataclasses import dataclass

@dataclass
class Settings:
    model_path: str = "yolov11m.engine"
    conf: float = 0.45
    fov: int = 400
    imgsz: int = 640
    com_port: str = "COM3"
    baudrate: int = 115200
    
    # Сглаживание
    smooth_base: float = 0.3
    jitter_range: float = 0.15
    
    # Хитбокс
    hitbox_base: float = 0.02
    hitbox_min: int = 2
    hitbox_max: int = 12
    
    # Реакция
    reaction_delay_min: float = 0.05
    reaction_delay_max: float = 0.25
    miss_chance: float = 0.05
    
    # Безопасность
    max_move_delta: int = 200
    
    # Таймауты
    arduino_timeout: float = 0.1
    frame_timeout: float = 0.5
    
    use_half: bool = True
    verbose: bool = False