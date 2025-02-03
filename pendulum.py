# -*- coding: utf-8 -*-
import pygame as pg
import pymunk as pm
import math
from dataclasses import dataclass



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



# Cart-pendulum simulation parameters
@dataclass
class Parameters:
    rod_length: float = 150.0

    cart_mass: float = 4.0
    cart_size: pm.Vec2d = (80.0, 40.0)
    cart_damping: float = 0.125
    cart_origin = (MID_WIDTH, MID_HEIGHT)
    
    push_force: float = 6500.0

    groove_size = (600.0, 8.0)
    groove_half_width = groove_size[0] // 2
    groove_half_height = groove_size[1] // 2
    groove_start = (MID_WIDTH-groove_half_width, cart_origin[1]) 
    groove_end = (MID_WIDTH+groove_half_width, cart_origin[1])    

    bob_angle: float = math.pi / 2.0
    bob_mass: float = 0.01
    bob_radius: float = 20.0
    bob_origin: pm.Vec2d = (
        cart_origin[0] + rod_length * math.sin(bob_angle),
        cart_origin[1] + rod_length * math.cos(bob_angle)
    )



class Simulation:
    def __init__(self, params: Parameters):
        # Physics space and simulation paramaters
        self.space = pm.Space()
        self.space.gravity = pm.Vec2d(0.0, 981.0)
        self.params = params
        
        # Cart init
        self.cart = pm.Body(
            self.params.cart_mass,
            pm.moment_for_box(self.params.cart_mass, self.params.cart_size),
            pm.Body.DYNAMIC
        )
        self.cart.position = self.params.cart_origin
        self.cart_shape = pm.Poly.create_box(self.cart, self.params.cart_size)

        self.space.add(self.cart)
        self.space.add(self.cart_shape)

        # Groove init
        self.groove_joint = pm.GrooveJoint(
            self.space.static_body,
            self.cart,
            self.params.groove_start,
            self.params.groove_end,
            (0, 0)
        )

        self.space.add(self.groove_joint)
        
        # Bob init
        self.bob = pm.Body(
            self.params.bob_mass,
            pm.moment_for_circle(
                self.params.bob_mass,
                0.0,
                self.params.bob_radius
            ),
            pm.Body.DYNAMIC
        )
        
        self.bob.position = self.params.bob_origin
        self.bob_shape = pm.Circle(self.bob, self.params.bob_radius)

        self.space.add(self.bob)
        self.space.add(self.bob_shape)

        # Rod init
        self.rod = pm.PinJoint(self.cart, self.bob)
        self.space.add(self.rod)


    def draw(self, screen):
        # Groove
        groove_rect = pg.Rect(
            self.params.groove_start[0],
            self.params.groove_start[1]-self.params.groove_half_height,
            self.params.groove_size[0],
            self.params.groove_size[1]
        )
        pg.draw.rect(screen, GRAY, groove_rect)
        
        # Cart
        vertices = self.cart_shape.get_vertices()
        top_left = self.cart.local_to_world( vertices[-1] )
        pg.draw.rect(screen, BLUE, pg.Rect(top_left, self.params.cart_size)) 
        
        # Rod
        pg.draw.aaline( ## anti aliasing line
            screen,
            BLACK,
            (self.cart.position.x, self.cart.position.y),
            (self.bob.position.x, self.bob.position.y)
        )
        
        # Bob
        pg.draw.circle(
            screen, 
            RED,
            (self.bob.position.x, self.bob.position.y),
            self.params.bob_radius
        )

    
    # Angle between vertical line and the rod
    def get_bob_angular_position(self):
        vertical_vector = pm.Vec2d(0.0, 100.0)
        bob_cart_vector = self.bob.position - self.cart.position
        angle = bob_cart_vector.get_angle_between(vertical_vector)
        
        return angle
        
        
    # Angular velocity centered on cart
    def get_bob_angular_velocity(self):
        relative_position = self.bob.position - self.cart.position
        relative_velocity = self.bob.velocity - self.cart.velocity
        distance_squared = relative_position.length ** 2

        p1 = relative_position.x * relative_velocity.y 
        p2 = relative_position.y * relative_velocity.x
        angular_velocity = (p1 - p2) / distance_squared

        return angular_velocity
    
    # Reset the cart and pendulum
    def reset(self):
        self.cart.position = self.params.cart_origin
        self.cart.velocity = pm.Vec2d(0.0, 0.0)
        self.bob.position = self.params.bob_origin
        self.bob.velocity = pm.Vec2d(0.0, 0.0)
        
    # Handle the user (or AI) input for the cart
    def handle_cart(self, keys_pressed, ai=None):
        if ai == None:
            left_pressed = keys_pressed[pg.K_LEFT]
            right_pressed = keys_pressed[pg.K_RIGHT]
        else:
            bob_angular_position = self.get_bob_angular_position()
            bob_angular_velocity = self.get_bob_angular_velocity()
            ai_decision = False, False #ai.compute(np.array([
            #    bob_angular_position, 
            #    bob_angular_velocity,
            #    self.cart.position.x,
            #    self.cart.velocity.x
            #]))
            left_pressed, right_pressed = ai_decision
        
        # Move the cart
        if left_pressed ^ right_pressed:
            force = self.params.push_force
            applied_force = force*int(right_pressed) - force*int(left_pressed)
            self.cart.apply_force_at_local_point(
                (applied_force, 0.0),
                (0.0, 0.0)
            )
        else:
            if abs(self.cart.velocity.x) > 0.0:
                self.cart.velocity = (
                    self.cart.velocity.x * (1.0 - self.params.cart_damping),
                    0.0
                )

        
    
    



# Pygame initialisation
pg.init()
screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Cart-pendulum")
clock = pg.time.Clock()

params = Parameters()
simulation = Simulation(params)



# Main loop
running = True
while running:
    
    # Handling input and updating
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                simulation.reset()
    
    keys_pressed = pg.key.get_pressed()
    simulation.handle_cart(keys_pressed)
    simulation.space.step( 1.0 / FPS )
    
    # Drawing
    screen.fill(WHITE)
    simulation.draw(screen)
    pg.display.flip()
    
    clock.tick(FPS)
    
pg.quit()
