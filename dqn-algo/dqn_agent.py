from constants import *
import keras
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import pickle
import os
import random
import gamelib

# same agent for attack/defense


class DQNNetwork:
    def __init__(self, path, learning_rate=0.0001, state_size=STATE_SIZE,
                 action_size=NUM_ACTIONS, hidden_size=64):

        self.model = Sequential()

        self.model.add(Dense(hidden_size, activation='relu',
                             input_dim=state_size))
        self.model.add(Dense(hidden_size, activation='relu'))
        self.model.add(Dense(hidden_size//2, activation='relu'))
        self.model.add(Dense(action_size, activation='linear'))

        self.optimizer = Adam(lr=learning_rate, clipvalue=1)
        self.model.compile(loss='mse', optimizer=self.optimizer)

        if (os.path.exists(path)):
            loaded_model = keras.models.load_model(path)
            self.model.set_weights(loaded_model.get_weights())


class Memory():
    def __init__(self, max_size=MEMORY_SIZE):
        self.buffer = []
        if os.path.exists(MEMORY_PATH):
            with open(MEMORY_PATH, 'rb') as f:
                self.buffer = pickle.load(f)

    def sample(self, batch_size=32):
        if len(self.buffer) < batch_size:
            return []
        idx = np.random.choice(np.arange(len(self.buffer)),
                               size=batch_size,
                               replace=False)
        return [self.buffer[i] for i in idx]


class DQNAgent():
    def __init__(self, gamma=0.99):
        self.gamma = gamma
        self.NN = DQNNetwork(MODEL_PATH)
        self.tgt_NN = DQNNetwork(TGT_MODEL_PATH)
        # self.tgt_NN.model.set_weights(self.NN.model.get_weights())

    def pick_action(self, state, exploration_rate=DEFAULT_EXPLORATION_RATE):
        state = np.reshape(state, (-1, STATE_SIZE))
        if TRAINING and random.uniform(0, 1) < exploration_rate:
            action = random.randint(0, NUM_ACTIONS - 1)
            gamelib.debug_write("PICKING RANDOM ACTION " + str(action))
        else:
            Q_vals = self.NN.model.predict(state)[0]
            action = np.argmax(Q_vals)
            gamelib.debug_write(
                "PICKING ACTION " + str(action) + " with Q value of " + str(Q_vals[action]))
        return action

    def train_on_memory(self, batch_size=32):
        memory = Memory()  # maybe move this to init and say self.memory = Memory()
        inputs = np.zeros((batch_size, STATE_SIZE))
        targets = np.zeros((batch_size, NUM_ACTIONS))

        minibatch = memory.sample(batch_size)
        if not minibatch:
            return
        for i, (state, action, reward, next_state, done) in enumerate(minibatch):
            state = np.reshape(state, (-1, STATE_SIZE))
            inputs[i] = state
            target = reward
            if not done:
                next_state = np.reshape(next_state, (-1, STATE_SIZE))
                next_Qs = self.tgt_NN.model.predict(next_state)[0]
                target = reward + self.gamma * np.amax(next_Qs)
            targets[i] = self.NN.model.predict(state)
            targets[i][action] = target
        self.NN.model.fit(inputs, targets, epochs=1, verbose=0)

    def transfer_weights(self):
        self.tgt_NN.model.set_weights(self.NN.model.get_weights())

    def save_model(self):
        self.NN.model.save(MODEL_PATH)
        self.tgt_NN.model.save(TGT_MODEL_PATH)


if __name__ == '__main__':
    agent = DQNAgent(MODEL_PATH)
    agent.tgt_NN.model.set_weights(agent.NN.model.get_weights())
    agent.save_model()
