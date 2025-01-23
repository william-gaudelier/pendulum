# -*- coding: utf-8 -*-
import pygame as pg
import pymunk as pm
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



# Pygame constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 512
MID_WIDTH = WINDOW_WIDTH // 2
MID_HEIGHT = WINDOW_HEIGHT // 2
FPS = 60.



# Create a physics space
space = pm.Space()
space.gravity = pm.Vec2d(0.0, 981.0)



# Parameters
rod_length = 150.

cart_mass = 4.0
cart_size = (80., 40.)
cart_damping = 0.125

push_force = 6500.

groove_size = (600., 8.0)

bob_angle = 0.0
bob_mass = 0.01
bob_radius = 20.




# Cart
cart = pm.Body(
    cart_mass,
    pm.moment_for_box(cart_mass, cart_size),
    pm.Body.DYNAMIC
)
cart_origin = (MID_WIDTH, MID_HEIGHT)
cart.position = cart_origin
cart_shape = pm.Poly.create_box(cart, cart_size)

space.add(cart)
space.add(cart_shape)



# Groove for the cart
groove_half_width = groove_size[0] // 2
groove_half_height = groove_size[1] // 2
groove_start = (MID_WIDTH-groove_half_width, cart.position.y) 
groove_end = (MID_WIDTH+groove_half_width, cart.position.y)
groove_joint = pm.GrooveJoint(
    space.static_body,
    cart,
    groove_start,
    groove_end,
    (0, 0)
)

space.add(groove_joint)



# Bob
bob = pm.Body(
    bob_mass,
    pm.moment_for_circle(bob_mass, 0.0, bob_radius),
    pm.Body.DYNAMIC
)
bob_origin = (
    cart.position[0] + rod_length * math.sin(bob_angle),
    cart.position[1] + rod_length * math.cos(bob_angle)
)
bob.position = bob_origin
bob_shape = pm.Circle(bob, bob_radius)

space.add(bob)
space.add(bob_shape)



# Rod
rod = pm.PinJoint(cart, bob)
space.add(rod)



# Drawing pymunk objects with pygame
def draw(screen):
    # Groove
    groove_rect = pg.Rect(
        groove_start[0],
        groove_start[1]-groove_half_height,
        groove_size[0],
        groove_size[1]
    )
    pg.draw.rect( screen, GRAY, groove_rect )
    
    # Cart
    vertices = cart_shape.get_vertices()
    top_left = cart.local_to_world( vertices[-1] )
    pg.draw.rect( screen, BLUE, pg.Rect(top_left, cart_size) ) 
    
    # Rod
    pg.draw.aaline( ## anti aliasing line
        screen,
        BLACK,
        (cart.position.x, cart.position.y),
        (bob.position.x, bob.position.y)
    )
    
    # Bob
    pg.draw.circle(
        screen, 
        RED,
        (bob.position.x, bob.position.y),
        bob_radius
    )
    


# User inputs handler
def handle_input():
    # Controlling the cart
    keys_pressed = pg.key.get_pressed()
    
    left_pressed = keys_pressed[pg.K_LEFT]
    right_pressed = keys_pressed[pg.K_RIGHT]
    
    if not (left_pressed ^ right_pressed) and abs(cart.velocity.x) > 0.0:
        cart.velocity = ( cart.velocity.x * (1.0 - cart_damping), 0.0 )
    elif left_pressed:
        cart.apply_force_at_local_point( (-push_force, 0.0), (0.0, 0.0) )
    elif right_pressed:
        cart.apply_force_at_local_point( (push_force, 0.0), (0.0, 0.0) )
        
    # Reset
    if keys_pressed[pg.K_r]:
        cart.position = cart_origin
        cart.velocity = pm.Vec2d(0.0, 0.0)
        bob.position = bob_origin
        bob.velocity = pm.Vec2d(0.0, 0.0)
    
    

# Angle between vertical line and the rod
def get_bob_angular_position():
    vertical_vector = pm.Vec2d(0.0, 100.0)
    bob_cart_vector = bob.position - cart.position
    angle = bob_cart_vector.get_angle_between(vertical_vector)
    
    return angle
    
    
# Angular velocity centered on cart
def get_bob_angular_velocity():
    relative_position = bob.position - cart.position
    relative_velocity = bob.velocity - cart.velocity
    distance_squared = relative_position.length ** 2

    p1 = relative_position.x * relative_velocity.y 
    p2 = relative_position.y * relative_velocity.x
    angular_velocity = (p1 - p2) / distance_squared

    return angular_velocity


# Pygame initialisation
pg.init()
screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Cart-pendulum")
clock = pg.time.Clock()



# Main loop
running = True
while running:
    
    # Handling input and updating
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    
    handle_input()
    space.step( 1.0 / FPS )
    
    # Drawing
    screen.fill(WHITE)
    draw(screen)
    pg.display.flip()
    
    clock.tick(FPS)
    
pg.quit()
