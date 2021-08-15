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


class DDQNNetwork:
    def __init__(self, path, learning_rate=0.0001, state_size=STATE_SIZE,
                 action_size=NUM_ACTIONS, hidden_size=64):

        self.model = Sequential()

        self.model.add(Dense(hidden_size, activation='relu',
                             input_dim=state_size))
        self.model.add(Dense(hidden_size, activation='relu'))
        self.model.add(Dense(hidden_size//2, activation='relu'))
        self.model.add(Dense(action_size, activation='linear'))

        self.optimizer = Adam(lr=learning_rate)  # clip value?
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

    def sample(self, batch_size=BATCH_SIZE):
        if len(self.buffer) < batch_size:
            return []
        idx = np.random.choice(np.arange(len(self.buffer)),
                               size=batch_size,
                               replace=False)
        return [self.buffer[i] for i in idx]


class DDQNAgent():
    def __init__(self, gamma=0.99):
        self.gamma = gamma
        self.NN1 = DDQNNetwork(MODEL1_PATH)
        self.NN2 = DDQNNetwork(MODEL2_PATH)
        # self.tgt_NN.model.set_weights(self.NN.model.get_weights())

    def pick_action(self, state, exploration_rate=DEFAULT_EXPLORATION_RATE):
        state = np.reshape(state, (-1, STATE_SIZE))
        if TRAINING and random.uniform(0, 1) < exploration_rate:
            action = random.randint(0, NUM_ACTIONS - 1)
            gamelib.debug_write("PICKING RANDOM ACTION " + str(action))
        else:
            Q_vals1 = self.NN1.model.predict(state)[0]
            Q_vals2 = self.NN2.model.predict(state)[0]
            Q_vals = np.minimum(Q_vals1, Q_vals2)
            action = np.argmax(Q_vals)
            gamelib.debug_write(
                "PICKING ACTION " + str(action) + " with Q value of " + str(Q_vals[action]))
        return action

    def train_on_memory(self, batch_size=BATCH_SIZE):
        memory = Memory()  # maybe move this to init and say self.memory = Memory()
        inputs = np.zeros((batch_size, STATE_SIZE))
        targets1 = np.zeros((batch_size, NUM_ACTIONS))
        targets2 = np.zeros((batch_size, NUM_ACTIONS))

        minibatch = memory.sample(batch_size)
        if not minibatch:
            return
        for i, (state, action, reward, next_state, done) in enumerate(minibatch):
            state = np.reshape(state, (-1, STATE_SIZE))
            inputs[i] = state
            target = reward
            if not done:
                next_state = np.reshape(next_state, (-1, STATE_SIZE))
                Q_vals1 = self.NN1.model.predict(next_state)[0]
                Q_vals2 = self.NN2.model.predict(next_state)[0]
                next_Qs = np.minimum(Q_vals1, Q_vals2)
                target = reward + self.gamma * np.amax(next_Qs)
            # do you update each model with respect to all the minimums or just minimum for action chosen
            targets1[i] = self.NN1.model.predict(state)
            targets1[i][action] = target
            targets2[i] = self.NN2.model.predict(state)
            targets2[i][action] = target
        self.NN1.model.fit(inputs, targets1, epochs=1,
                           verbose=0, batch_size=batch_size)
        self.NN2.model.fit(inputs, targets2, epochs=1,
                           verbose=0, batch_size=batch_size)

    def save_model(self):
        self.NN1.model.save(MODEL1_PATH)
        self.NN2.model.save(MODEL2_PATH)


if __name__ == '__main__':
    agent = DDQNAgent()
    agent.save_model()
