import pickle
import gamelib
import os
from constants import *
import json
import csv
# with open('map_coords.pkl', 'rb') as fp:
#     # can maybe even make more efficient by just loading once and then setting all to 0 every game start
#     game_state_dict = pickle.load(fp)
# print(game_state_dict)

# print(TOP_LEFT_COORDS)

# with open('dqn-algo/memory.pkl', 'rb') as f:
#     memory = pickle.load(f)
# print(len(memory))

with open('dqn-algo/result_counter.txt', 'r') as f:
    results = [int(x) for x in f.read().split(',')]

with open('dqn-algo/result_counter.txt', 'w') as f:
    results[0] += 1
    f.write(str(','.join([str(x) for x in results])))
