# -*- coding: utf-8 -*-
import pygame as pg
from pygame.locals import *
import math

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

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 512
FPS = 60.
G = 9.81
PIXELS_PER_METER = 100

# Phase Portrait
class PhasePortrait:
    def __init__(self):
        self.size = 200
        self.rect = pg.Rect(
            WINDOW_WIDTH-self.size-20,
            WINDOW_HEIGHT-self.size-20, 
            self.size,
            self.size
        )
        self.points = []
        self.scale = 20.

    def add_point(self, angle, velocity):
        x = self.rect.centerx + angle * self.scale
        y = self.rect.centery - velocity * self.scale
        self.points.append((x, y))

    def draw(self, screen):
        # Border
        pg.draw.rect(screen, BLACK, self.rect, 1)
        
        # Axes
        start = (self.rect.left, self.rect.centery)
        end = (self.rect.right-1, self.rect.centery)
        pg.draw.line(screen, GRAY, start, end, 1)
        start = (self.rect.centerx, self.rect.top)
        end = (self.rect.centerx, self.rect.bottom-1)
        pg.draw.line(screen, GRAY, start, end, 1)

        # Content
        pg.draw.lines(screen, RED, False, self.points, 1)

class Pendulum:
    def __init__(self):
        # Rail
        self.rail_width = 600
        self.rail_height = 4
        self.rail_pos = WINDOW_WIDTH//2 - self.rail_width//2, WINDOW_HEIGHT//2-self.rail_height//2

        # Cart
        cart_width = 100
        cart_height = 50
        self.cart = pg.Rect(
            WINDOW_WIDTH//2 - cart_width//2,
            WINDOW_HEIGHT//2 - cart_height//2,
            cart_width,
            cart_height
        )
        self.cart_velocity = 0.
        self.old_cart_velocity = 0.
        self.cart_acceleration = 0.
        self.is_cart_dragged = False
        self.old_mouse_pos = None
        self.pivot_x = self.cart.centerx
        self.pivot_y = self.cart.centery
        
        # Physical values
        self.length = 2.
        self.angle = -math.pi + 0.001
        self.angular_velocity = 0.
        self.angular_acceleration = 0.

        # Bob
        length_in_pixels = self.length * PIXELS_PER_METER
        self.bob_mass = 2.
        self.bob_x = self.pivot_x + length_in_pixels * math.sin(self.angle)
        self.bob_y = self.pivot_y + length_in_pixels * math.cos(self.angle)
        self.bob_radius = 0.2

        self.last_update_time = pg.time.get_ticks()
    
    def update(self, friction=0.4, fluid_density=1.23):
        # dt
        current_update_time = pg.time.get_ticks()
        dt = (current_update_time - self.last_update_time) / 1000.
        self.last_update_time = current_update_time

        # Gravity
        gravity_force = self.bob_mass * G
        tangential_component_of_gravity_force = gravity_force * math.sin(self.angle)
        gravity_torque = -tangential_component_of_gravity_force * self.length

        # Friction
        friction_torque = - friction * self.angular_velocity
        
        # Air resistance
        # tangential_velocity = self.angular_velocity * self.length
        # drag_coef = 0.47 # for a smooth sphere, fluid dynamics is complicated
        # area = math.pi * (self.bob_radius ** 2)
        # air_torque = - 0.5 * fluid_density * tangential_velocity * abs(tangential_velocity) * drag_coef * # # area # the absolute value takes care of the sign of the velocity

        # Cart
        cart_torque = - self.bob_mass * self.cart_acceleration * self.length * math.cos(self.angle)

        # Total
        total_torque = gravity_torque + friction_torque + cart_torque # + air_torque 

        # Computing pendulum's new values
        moment_of_inertia = self.bob_mass * (self.length ** 2) 
        self.angular_acceleration = total_torque / moment_of_inertia
        self.angular_velocity += self.angular_acceleration * dt
        self.angle = self.angle + self.angular_velocity * dt

        length_in_pixels = self.length * PIXELS_PER_METER
        self.bob_x = self.pivot_x + length_in_pixels * math.sin(self.angle)
        self.bob_y = self.pivot_y + length_in_pixels * math.cos(self.angle)

    def move_cart(self, dist):
        current_update_time = pg.time.get_ticks()
        dt = (current_update_time - self.last_update_time) / 1000.
        self.cart_velocity = (dist / PIXELS_PER_METER) / dt
        self.cart_acceleration = (self.cart_velocity - self.old_cart_velocity) / dt
        self.old_cart_velocity = self.cart_velocity

        self.cart.x += dist
        self.cart.x = max(
            WINDOW_WIDTH//2-(self.rail_width//2)-(self.cart.width),
            self.cart.x
        )
        self.cart.x = min(
            WINDOW_WIDTH//2+(self.rail_width//2)-(self.cart.width//2),
            self.cart.x
        )
        self.pivot_x = self.cart.centerx
        self.pivot_y = self.cart.centery

    def handle_cart(self):
        if pg.mouse.get_pressed()[0]:
            mouse_pos = pg.mouse.get_pos()
            if self.is_cart_dragged:
                self.move_cart(mouse_pos[0] - self.old_mouse_pos[0])
                self.old_mouse_pos = mouse_pos
            elif self.cart.collidepoint(mouse_pos):
                self.is_cart_dragged = True
                self.old_mouse_pos = mouse_pos
        else:
            self.is_cart_dragged = False
            self.cart_velocity = 0.
            self.cart_acceleration = 0.
            self.old_cart_velocity = 0.
            
    def draw(self, screen):
        pg.draw.rect(screen, BLUE, self.cart)
        pg.draw.rect(screen, GRAY, (self.rail_pos, (self.rail_width, self.rail_height)))
        pg.draw.line(screen, DARK_GRAY, (self.pivot_x, self.pivot_y), (self.bob_x, self.bob_y), 2)
        bob_radius_in_pixels = self.bob_radius * PIXELS_PER_METER
        pg.draw.circle(screen, ORANGE, (int(self.bob_x), int(self.bob_y)), int(bob_radius_in_pixels))
        pg.draw.circle(screen, DARK_GRAY, (self.pivot_x, self.pivot_y), 5)

# Init
pg.init()
screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Pendulum")

pendulum = Pendulum()
phase_portrait = PhasePortrait()
phase_portrait.add_point(pendulum.angle, pendulum.angular_velocity)
phase_portrait.add_point(pendulum.angle, pendulum.angular_velocity)

clock = pg.time.Clock()

# Main loop
running = True
while running:
    for event in pg.event.get():
        if event.type == QUIT:
            running = False

    # Update
    pendulum.handle_cart()
    pendulum.update()
    phase_portrait.add_point(pendulum.angle, pendulum.angular_velocity)

    # Draw
    screen.fill(WHITE)
    pendulum.draw(screen)
    phase_portrait.draw(screen)
    pg.display.flip()

    clock.tick(FPS)
pg.quit()