Just a cart-pendulum simulation for the moment

Written with pygame for the graphics and events, and pymunk for the physics

Currently implementing an AI that balances the pendulum, using GRPO

Will later do the same for a double pendulum

Code is currently messy and unfinished

The dependence hierarchy is the following (may change):

Config -> Pendulum -> AI -> main

config: Constants, parameters for simulation and AI
pendulum: Physics simulation using pymunk, visualization using pygame
ai: AI implementation including
	- PolicyNetwork (the NN itself)
	- Episode (storing the data related to episodes)
	- Trainer (manages the training process, and interface with the simulation)
main: Game state management and main loop