import pygame as pg
import pymunk as pm

from config import *

class Simulation:
    def __init__(self):
        # Physics space and simulation paramaters
        self.space = pm.Space()
        self.space.gravity = pm.Vec2d(0.0, 981.0)
        
        # Cart init
        self.cart = pm.Body(
            cart_mass,
            pm.moment_for_box(cart_mass, cart_size),
            pm.Body.DYNAMIC
        )
        self.cart.position = cart_origin
        self.cart_shape = pm.Poly.create_box(self.cart, cart_size)

        self.space.add(self.cart)
        self.space.add(self.cart_shape)

        # Groove init
        self.groove_joint = pm.GrooveJoint(
            self.space.static_body,
            self.cart,
            groove_start,
            groove_end,
            (0, 0)
        )
        self.space.add(self.groove_joint)
        
        # Bob init
        self.bob = pm.Body(
            bob_mass,
            pm.moment_for_circle(
                bob_mass,
                0.0,
                bob_radius
            ),
            pm.Body.DYNAMIC
        )
        
        self.bob.position = bob_origin
        self.bob_shape = pm.Circle(self.bob, bob_radius)

        self.space.add(self.bob)
        self.space.add(self.bob_shape)

        # Rod init
        self.rod = pm.PinJoint(self.cart, self.bob)
        self.space.add(self.rod)


    def draw(self, screen):
        # Background
        screen.fill(WHITE)
              
        # Groove
        groove_rect = pg.Rect(
            groove_start[0],
            groove_start[1]-groove_half_height,
            groove_size[0],
            groove_size[1]
        )
        pg.draw.rect(screen, GRAY, groove_rect)
        
        # Cart
        vertices = self.cart_shape.get_vertices()
        top_left = self.cart.local_to_world( vertices[-1] )
        pg.draw.rect(screen, BLUE, pg.Rect(top_left, cart_size)) 
        
        # Rod
        pg.draw.aaline( ## anti aliasing line
            screen,
            BLACK,
            (self.cart.position.x, self.cart.position.y),
            (self.bob.position.x, self.bob.position.y)
        )
        
        # Change bob color depending on its angle
        if abs(self.get_bob_angular_position()) > balance_threshold:
            bob_color = GREEN
        else:
            bob_color = RED
            
        # Bob
        pg.draw.circle(
            screen, 
            bob_color,
            (self.bob.position.x, self.bob.position.y),
            bob_radius
        )
    
    
    def get_cart_position(self):
        return self.cart.position.x - MID_WIDTH
    
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
    
    def get_normalized_state(self):
        return [
            self.get_bob_angular_position() / math.pi,
            self.get_bob_angular_velocity / 50.0,
            self.get_cart_position / 300.0,
            self.cart.velocity.x / 50.0
        ]
    
    # Reset the cart and pendulum
    def reset(self):
        self.cart.position = cart_origin
        self.cart.velocity = pm.Vec2d(0.0, 0.0)
        self.bob.position = bob_origin
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
            force = push_force
            applied_force = force*int(right_pressed) - force*int(left_pressed)
            self.cart.apply_force_at_local_point(
                (applied_force, 0.0),
                (0.0, 0.0)
            )
        else:
            if abs(self.cart.velocity.x) > 0.0:
                self.cart.velocity = (
                    self.cart.velocity.x * (1.0 - cart_damping),
                    0.0
                )

        
    
    




