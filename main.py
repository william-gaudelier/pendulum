from ai import *

STATE_USER = 0
STATE_AI_TRAINING = 1
STATE_AI_DEMO = 2
NB_STATES = 3

current_game_state = STATE_USER


# Pygame initialisation
pg.init()
screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Cart-pendulum")
font = pg.font.Font(None, 36)
clock = pg.time.Clock()

simulation = Simulation()
trainer = Trainer()


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
                trainer.reset_reward()
            elif event.key == pg.K_t:  # 't' for toggle
                current_game_state = ( current_game_state + 1 ) % NB_STATES
    
    # may actually write handle_cart(keys_pressed, game_state) later
    if current_game_state == STATE_USER:
        keys_pressed = pg.key.get_pressed()
        simulation.handle_cart(keys_pressed)
        simulation.space.step( 1.0 / FPS )
        trainer.compute_reward(
            simulation.get_bob_angular_position(),
            simulation.get_cart_position()/300.0
        )
        simulation.draw(screen)
        trainer.draw_cumulative_reward(screen, font)
    elif current_game_state == STATE_AI_TRAINING:
        pass
    elif current_game_state == STATE_AI_DEMO:
        pass
    
    
    
    pg.display.flip()
    
    clock.tick(FPS)
    
pg.quit()