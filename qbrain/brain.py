import json
import os
import random
import numpy as np
from collections import deque


class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        batch = random.sample(self.buffer, min(batch_size, len(self.buffer)))
        states, actions, rewards, next_states, dones = zip(*batch)
        return states, actions, rewards, next_states, dones
    
    def __len__(self):
        return len(self.buffer)


class QBrain:
    def __init__(self, env):
        self.env = env
        self.q = {}
        self.q_target = {}
        
        self.alpha = 0.1
        self.gamma = 0.99
        self.epsilon = 1.0
        self.min_epsilon = 0.01
        self.decay = 0.995
        self.target_update_freq = 10
        
        self.use_double = True
        self.update_count = 0
        
        self.replay = ReplayBuffer(capacity=20000)
        self.batch_size = 32
        self.learn_freq = 4
        
        self.step_count = 0
        self.action_history = []
        
        self.path = os.path.join(os.path.dirname(__file__), "brain.json")
        self.target_path = os.path.join(os.path.dirname(__file__), "brain_target.json")


    def bias_towards(self, path):
        for i in range(len(path) - 1):
            s = self._key(path[i])
            if s in self.q:
                best_a = self.q[s].index(max(self.q[s]))
                self.q[s][best_a] += 0.2


    def penalize(self, path):
        for i in range(len(path) - 1):
            s = self._key(path[i])
            if s in self.q:
                worst_a = self.q[s].index(min(self.q[s]))
                self.q[s][worst_a] -= 0.2


    def reward_transition(self, state, next_state, value):
        k1 = self._key(state)
        k2 = self._key(next_state)

        if k1 not in self.q:
            self.q[k1] = [0, 0, 0, 0]
        if k2 not in self.q:
            self.q[k2] = [0, 0, 0, 0]
        if k2 not in self.q_target:
            self.q_target[k2] = self.q[k2].copy()

        best_next = max(self.q_target[k2])
        
        for i in range(4):
            self.q[k1][i] += value * 0.1 * (best_next - self.q[k1][i])


    def _key(self, state):
        return f"{self.env.world_type}:{state}"


    def _get_q(self, state, target=False):
        k = self._key(state)
        if target:
            if k not in self.q_target:
                self.q_target[k] = self.q.get(k, [0, 0, 0, 0]).copy()
            return self.q_target[k]
        else:
            if k not in self.q:
                self.q[k] = [0, 0, 0, 0]
            return self.q[k]


    def choose_action(self, state, training=True):
        q_vals = self._get_q(state)

        if hasattr(self, "meta") and training:
            stats = self.meta.stats()
            if stats is not None:
                if stats["mean"] < 0.3 and stats["trend"] < -0.2:
                    if random.random() < 0.9:
                        action = random.randint(0, 3)
                        self.action_history.append(action)
                        return action

        if training and random.random() < self.epsilon:
            action = random.randint(0, 3)
        else:
            action = int(max(range(4), key=lambda a: q_vals[a]))
        
        self.action_history.append(action)
        return action


    def learn(self, state, action, reward, next_state):
        self.step_count += 1
        
        done = reward == 10
        self.replay.push(state, action, reward, next_state, done)
        
        if len(self.replay) >= self.batch_size and self.step_count % self.learn_freq == 0:
            self._replay_learn()
        
        if self.update_count % self.target_update_freq == 0:
            self._update_target()
        
        self.update_count += 1
        
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.decay


    def _replay_learn(self):
        states, actions, rewards, next_states, dones = self.replay.sample(self.batch_size)
        
        for i in range(len(states)):
            s = states[i]
            a = actions[i]
            r = rewards[i]
            ns = next_states[i]
            d = dones[i]
            
            k1 = self._key(s)
            k2 = self._key(ns)
            
            if k1 not in self.q:
                self.q[k1] = [0, 0, 0, 0]
            if k2 not in self.q:
                self.q[k2] = [0, 0, 0, 0]
            if k2 not in self.q_target:
                self.q_target[k2] = self.q[k2].copy()
            
            if self.use_double:
                best_a = int(max(range(4), key=lambda x: self.q[k2][x]))
                target_val = r + self.gamma * self.q_target[k2][best_a] * (1 - d)
            else:
                target_val = r + self.gamma * max(self.q_target[k2]) * (1 - d)
            
            self.q[k1][a] += self.alpha * (target_val - self.q[k1][a])


    def _update_target(self):
        for k in self.q:
            self.q_target[k] = self.q[k].copy()


    def get_stats(self):
        return {
            "epsilon": self.epsilon,
            "q_size": len(self.q),
            "replay_size": len(self.replay),
            "step_count": self.step_count,
        }


    def save(self):
        data = {
            "q": self.q,
            "epsilon": self.epsilon,
            "step_count": self.step_count,
        }
        with open(self.path, "w") as f:
            json.dump(data, f)


    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                data = json.load(f)
                self.q = data.get("q", {})
                self.epsilon = data.get("epsilon", 1.0)
                self.step_count = data.get("step_count", 0)
