import pickle
import numpy as np
# configs
LOCAL_MATCH = False
TRAINING = False
# root changes depending if its on server or local run match
ALGO_NAME = 'dqn-algo'
ROOT = ALGO_NAME if LOCAL_MATCH else ''
MAP_COORDS_INITIAL_DICT_PATH = ROOT + '/map_coords_initial_dict.pkl'
MAP_COORDS_PATH = ROOT + '/map_coords.pkl'
MEMORY_PATH = ROOT + '/memory.pkl'
MODEL_PATH = ROOT + '/dqn_model.model'
TGT_MODEL_PATH = ROOT + '/tgt_model.model'
RESULTS_PATH = ROOT + '/result_counter.txt'
# deploy phase actions.
ATTACK_LEFT = 0
ATTACK_RIGHT = 1
DEFEND_TOP_LEFT = 0
DEFEND_TOP_MIDDLE = 1
DEFEND_TOP_RIGHT = 2
DEFEND_BOTTOM = 3
ACTION_SPLIT_INDEX = 4

# stats indices
HEALTH_INDEX = 0
SP_INDEX = 1
MP_INDEX = 2
TURN_INDEX = 1

# configuration for intializing game_state_dict
NUM_DEFENSE_TYPES = 3
CONSIDER_UNIT_TEAM = 0

# which units to include in game state before every action
UNIT_LOC_START_INDEX = 0
UNIT_LOC_END_INDEX = 3

# constants for algo core
STATE = 0
ACTION = 1
REWARD = 2
NEXT_STATE = 3

MEMORY_SIZE = 50000

# shorthands
WALL_SHORT = "FF"
TURRET_SHORT = "DF"
FACTORY_SHORT = "EF"
SCOUT_SHORT = "PI"
DEMOLISHER_SHORT = "EI"
INTERCEPTOR_SHORT = "SI"

# define map regions

with open(MAP_COORDS_PATH, 'rb') as fp:
    coords = pickle.load(fp)

LEAVE_OPEN_COORDS = [[i, 13-i] for i in range(14)]
LEAVE_OPEN_COORDS.extend([[i, 14-i] for i in range(1, 14)])
LEAVE_OPEN_COORDS.extend([[14+i, i] for i in range(14)])
LEAVE_OPEN_COORDS.extend([[13+i, i] for i in range(1, 14)])


# do i want to let my structures be placed on edges?
TOP_LEFT_COORDS = [list(coord) for coord in coords if coord[0] >=
                   0 and coord[0] <= 7 and coord[1] >= 6 and coord[1] <= 13 and list(coord) not in LEAVE_OPEN_COORDS]
TOP_MIDDLE_COORDS = [list(coord) for coord in coords if coord[0] >=
                     8 and coord[0] <= 19 and coord[1] >= 6 and coord[1] <= 13 and list(coord) not in LEAVE_OPEN_COORDS]
TOP_RIGHT_COORDS = [list(coord) for coord in coords if coord[0] >=
                    20 and coord[0] <= 27 and coord[1] >= 6 and coord[1] <= 13 and list(coord) not in LEAVE_OPEN_COORDS]
BOTTOM_COORDS = [list(coord) for coord in coords if coord[0] >=
                 8 and coord[0] <= 19 and coord[1] >= 0 and coord[1] <= 5 and list(coord) not in LEAVE_OPEN_COORDS]

# DQN configs
NUM_ACTIONS = 64
STATE_SIZE = 1268
WEIGHT_TRANSFER_FREQ = 10
with open(RESULTS_PATH, 'r') as f:
    results = [int(x) for x in f.read().split(',')]
EXPLORE_START = 1.0
EXPLORE_STOP = 0.01
DECAY_RATE = 0.0002
TRAIN_EPISODES = 2000
# DEFAULT_EXPLORATION_RATE = EXPLORE_STOP + \
#     (EXPLORE_START - EXPLORE_STOP)*np.exp(-DECAY_RATE*sum(results))
DEFAULT_EXPLORATION_RATE = 0.5
BATCH_SIZE = 64
HEALTH_REWARD = 0.5
# RL Indices

STATE = 0
ACTION = 1
REWARD = 2
NEXT_STATE = 3
DONE = 4
