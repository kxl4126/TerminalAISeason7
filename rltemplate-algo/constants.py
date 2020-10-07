import pickle
# configs
LOCAL_MATCH = True
# root changes depending if its on server or local run match
ROOT = 'rltemplate-algo' if LOCAL_MATCH else ''
MAP_COORDS_INITIAL_DICT_PATH = ROOT + '/map_coords_initial_dict.pkl'
MAP_COORDS_PATH = ROOT + '/map_coords.pkl'
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

MEMORY_SIZE = 50

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
