# humanized_aimer.py
import time
import random
import math
from hardware_mouse import HardwareMouse
from settings import Settings

class HumanizedAimer:
    def __init__(self, mouse: HardwareMouse, settings: Settings):
        self.mouse = mouse
        self.s = settings
        self._prev_x = 0.0
        self._prev_y = 0.0
        self._last_target_time = 0.0
        self._reaction_delay = 0.0
    
    def get_humanized_target(self, cx: float, cy: float, box_width: float):
        offset_px = box_width * self.s.hitbox_base
        offset_px = max(self.s.hitbox_min, min(self.s.hitbox_max, offset_px))
        rx = cx + random.uniform(-offset_px, offset_px)
        ry = cy + random.uniform(-offset_px, offset_px)
        return rx, ry
    
    def aim(self, dx: float, dy: float):
        smooth = self.s.smooth_base + random.uniform(-self.s.jitter_range, self.s.jitter_range)
        smooth = max(0.05, min(0.95, smooth))
        mx = self._prev_x * smooth + dx * (1.0 - smooth)
        my = self._prev_y * smooth + dy * (1.0 - smooth)
        mx = max(-self.s.max_move_delta, min(self.s.max_move_delta, mx))
        my = max(-self.s.max_move_delta, min(self.s.max_move_delta, my))
        self._prev_x, self._prev_y = mx, my
        self.mouse.move(int(round(mx)), int(round(my)))
    
    def should_process(self) -> bool:
        now = time.time()
        if now - self._last_target_time >= self._reaction_delay:
            self._reaction_delay = random.uniform(self.s.reaction_delay_min, self.s.reaction_delay_max)
            self._last_target_time = now
            return True
        return False
    
    def reset(self):
        self._prev_x = self._prev_y = 0.0
        self._last_target_time = 0.0
        self._reaction_delay = random.uniform(self.s.reaction_delay_min, self.s.reaction_delay_max)