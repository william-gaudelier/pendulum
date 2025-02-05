import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from pendulum import *

class PolicyNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(4, 32)
        self.layer2 = nn.Linear(32, 2)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        return torch.sigmoid(self.fc2(x))
        # each output is an independent probability
    
    def sample_actions(self, state, size=1):
        with torch.no_grad():
            state = torch.FloatTensor(state)
            left_prob, right_prob = self.forward(state)
            repeated_probs = torch.stack(
                [left_prob.repeat(size), right_prob.repeat(size)],
                dim=1
            )
            
            # Sample each action independently
            actions = torch.bernoulli(repeated_probs)
            log_probs = torch.log(
                actions * repeated_probs 
                + (1 - actions) * (1 - repeated_probs)
            )
            actions = [(bool(l), bool(r)) for l, r in actions]
            return actions, log_probs
        
    
    def compute_group_advantages(self, rewards):
        rewards = torch.tensor(rewards)
        return (rewards - rewards.mean()) / (rewards.std() + 1e-8)
        # adding 1e-8 to avoid division by zero



class Episode:
    def __init__(self):
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []
        self.threshold_passed = False
        self.cumulative_reward = 0
    
    def add_step(self, state: np.ndarray, action: Tuple[bool, bool], 
                 log_prob: torch.Tensor, reward: float):
        self.states.append(state)
        self.actions.append(action)
        self.log_probs.append(log_prob)
        self.rewards.append(reward)
        self.cumulative_reward += reward

    @property
    def current_length(self):
        return len(self.states)
        
        
        
class Trainer:
    def __init__(self):
        self.d = 10.0 # coefficient used in the reward computation
        self.ep = Episode()
        self.agent = PolicyNetwork()
        self.current_episode_number = 0
        
    
    # Reward (computed every frame)
    def compute_reward(self, bob_angular_position, cart_position):
        in_interval = abs(bob_angular_position) > balance_threshold
        if in_interval:
            self.ep.threshold_passed = True
            reward = 1 - abs(cart_position)/self.d
        elif self.ep.threshold_passed:
            reward = - abs(cart_position)/self.d
        else:
            reward = -1 - abs(cart_position)/self.d
        self.ep.cumulative_reward += reward
        return reward
    
    def reset_reward(self):
        self.ep.cumulative_reward = 0
        self.ep.threshold_passed = False
        
    def draw_cumulative_reward(self, screen, font):
        text = font.render(
            f"Reward: {self.ep.cumulative_reward:.2f}",
            True,
            BLACK
        )
        text_rect = text.get_rect()
        text
        text_rect.topleft = (10, 10)
        screen.blit(text, text_rect)
        
        


