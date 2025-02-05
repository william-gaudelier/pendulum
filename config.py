# -*- coding: utf-8 -*-
import math
from typing import List, Tuple

# Colors
BLACK = (0, 0, 0)
DARK_GRAY = (55, 55, 55)
GRAY = (110, 110, 110)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Pygame constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 512
MID_WIDTH = WINDOW_WIDTH // 2
MID_HEIGHT = WINDOW_HEIGHT // 2
FPS = 60.

rod_length: float = 150.0

cart_mass: float = 4.0
cart_size: Tuple[float, float] = (80.0, 40.0)
cart_damping: float = 0.125
cart_origin: Tuple[float, float] = (MID_WIDTH, MID_HEIGHT)

push_force: float = 6500.0

groove_size: Tuple[float, float] = (600.0, 8.0)
groove_half_width: float = groove_size[0] // 2
groove_half_height: float = groove_size[1] // 2
groove_start: Tuple[float, float] = (MID_WIDTH-groove_half_width, cart_origin[1]) 
groove_end: Tuple[float, float] = (MID_WIDTH+groove_half_width, cart_origin[1])    

bob_angle: float = -0.9*math.pi
bob_mass: float = 0.01
bob_radius: float = 20.0
bob_origin: Tuple[float, float] = (
    cart_origin[0] + rod_length * math.sin(bob_angle),
    cart_origin[1] + rod_length * math.cos(bob_angle)
)
bob_color: Tuple[int, int, int] = BLACK

# AI parameters
balance_threshold = 0.9 * math.pi
group_size = 64
frames_per_step = 6 # 0.1 second
steps_per_episode = 100
frames_per_episode = frames_per_step * steps_per_episode # 10 seconds