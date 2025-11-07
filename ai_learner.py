import numpy as np
import os
import random
from collections import deque
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from entities import DroneState

class QLearningAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0   # exploration rate (start with full exploration)
        self.epsilon_min = 0.1  # Keep some exploration even after training
        self.epsilon_decay = 0.998  # Slower decay for more exploration
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.model_dir = 'saved_models'
        os.makedirs(self.model_dir, exist_ok=True)
        self.steps = 0
    
    def _build_model(self):
        """Membangun model neural network untuk Q-learning"""
        model = Sequential()
        # Simplified model for faster training
        model.add(Dense(16, input_dim=self.state_size, activation='relu'))
        model.add(Dense(16, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(
            loss='mse',
            optimizer=Adam(learning_rate=0.0005),  # Reduced learning rate
            metrics=['accuracy']
        )
        return model
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        self.steps += 1
        if np.random.rand() <= self.epsilon:
            action = random.randrange(self.action_size)
            # print(f"Random action: {action}, epsilon: {self.epsilon:.2f}")
            return action
            
        try:
            act_values = self.model.predict(state, verbose=0)
            action = np.argmax(act_values[0])
            # print(f"Model action: {action}, values: {act_values[0]}")
            return action
        except Exception as e:
            print(f"Error in act(): {e}")
            return random.randrange(self.action_size)
    
    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0])
            
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            
            self.model.fit(state, target_f, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def save_model(self, filename='drone_ai_model.weights.h5'):
        """Save the model weights with the correct filename format"""
        if not filename.endswith('.weights.h5'):
            if filename.endswith('.h5'):
                filename = filename[:-3] + '.weights.h5'
            else:
                filename += '.weights.h5'
        self.model.save_weights(os.path.join(self.model_dir, filename))
    
    def load_model(self, filename='drone_ai_model.weights.h5'):
        """Load the model weights with the correct filename format"""
        if not filename.endswith('.weights.h5'):
            if filename.endswith('.h5'):
                filename = filename[:-3] + '.weights.h5'
            else:
                filename += '.weights.h5'
        
        model_path = os.path.join(self.model_dir, filename)
        if os.path.exists(model_path):
            self.model.load_weights(model_path)
            self.epsilon = self.epsilon_min  # Set epsilon to minimum when using trained model
            print(f"Loaded model weights from {model_path}")
        else:
            print(f"No saved model found at {model_path}, starting with random weights")

class DroneAI:
    def __init__(self, state_size=7, action_size=4):
        self.agent = QLearningAgent(state_size, action_size)
        self.batch_size = 32
        
    def get_state(self, drone, survivors):
        """Mengubah state drone menjadi format yang bisa diproses model"""
        min_dist = float('inf')
        for s in survivors:
            if not s.rescued:
                dist = np.sqrt((drone.x - s.x)**2 + (drone.y - s.y)**2)
                min_dist = min(min_dist, dist)
        
        return np.array([
            drone.x / 40,  # Normalisasi posisi x
            drone.y / 30,  # Normalisasi posisi y
            drone.battery / 100.0,
            min_dist / np.sqrt(40**2 + 30**2),
            int(drone.state == DroneState.EXPLORING),
            int(drone.state == DroneState.RESCUING),
            int(drone.state == DroneState.RETURNING)
        ])
    
    def get_reward(self, drone, prev_state, survivors, action_taken):
        """Menghitung reward untuk aksi yang diambil"""
        reward = 0.0
        
        # Large reward for finding a survivor
        if hasattr(drone, 'survivor') and drone.survivor and not drone.survivor.rescued:
            reward += 50.0  # Increased from 10 to 50
            print(f"Drone found survivor! +50 reward")
            
        # Large reward for returning to base with a survivor
        if drone.x == 0 and drone.y == 0 and hasattr(drone, 'survivor') and drone.survivor:
            reward += 100.0  # Increased from 20 to 100
            print(f"Drone delivered survivor to base! +100 reward")
            
        # Small reward for exploring new areas
        if not hasattr(self, 'visited'):
            self.visited = set()
        pos = (drone.x, drone.y)
        if pos not in self.visited:
            self.visited.add(pos)
            reward += 5.0  # Reward for exploring new areas
            
        # Reward for moving towards survivors when in EXPLORING state
        if drone.state == DroneState.EXPLORING and survivors:
            # Find closest survivor
            closest_dist = float('inf')
            for s in survivors:
                if not s.rescued:
                    dist = (drone.x - s.x)**2 + (drone.y - s.y)**2
                    if dist < closest_dist:
                        closest_dist = dist
            
            # If we're getting closer to a survivor, give a small reward
            if hasattr(self, 'prev_closest_dist'):
                if closest_dist < self.prev_closest_dist:
                    reward += 1.0
            self.prev_closest_dist = closest_dist
            
        # Penalty for running out of battery
        if drone.battery <= 0:
            reward -= 50.0  # Increased penalty
            
        # Small penalty for each step to encourage efficiency
        reward -= 0.5  # Increased from 0.1 to 0.5 to encourage faster rescues
        
        return reward
    
    def train_step(self, drone, survivors, action_taken, next_drone_state, done):
        """Melakukan satu langkah training"""
        state = self.get_state(drone, survivors)
        # Use the current drone state for next_state since we don't have the updated state yet
        next_state = state  # Use current state as next state for simplicity
        reward = self.get_reward(drone, state, survivors, action_taken)
        
        # Simpan ke memori
        self.agent.remember(
            np.reshape(state, [1, self.agent.state_size]),
            action_taken,
            reward,
            np.reshape(next_state, [1, self.agent.state_size]),
            done
        )
        
        # Training
        if len(self.agent.memory) > self.batch_size:
            self.agent.replay(self.batch_size)
            
        return reward
    
    def get_action(self, drone, survivors):
        """Mendapatkan aksi dari model"""
        state = self.get_state(drone, survivors)
        state = np.reshape(state, [1, self.agent.state_size])
        return self.agent.act(state)
    
    def save_model(self, filename='drone_ai_model.weights.h5'):
        """Save the model weights with the correct filename format"""
        self.agent.save_model(filename)
    
    def load_model(self, filename='drone_ai_model.weights.h5'):
        """Load the model weights with the correct filename format"""
        self.agent.load_model(filename)
