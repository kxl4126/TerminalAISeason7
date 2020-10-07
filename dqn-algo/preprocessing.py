# preprocessing utils used to preprocess game_state info received at the beginning of every turn

import numpy as np
from itertools import chain, combinations
from constants import *


# expects dict with keys health, cores, bits, turn
def scale_other_stats(stats_dict, feature_range=(0, 1)):
    MIN_DICT = {
        'health': 0,
        'sp': 0,
        'mp': 0,
        'turn': 0
    }
    MAX_DICT = {
        'health': 40,
        'sp': 500,
        'mp': 100,
        'turn': 100
    }

    scaled_dict = {}
    for key in stats_dict.keys():
        value_std = (stats_dict[key] - MIN_DICT[key]) / \
            (MAX_DICT[key] - MIN_DICT[key])
        value_scaled = value_std * \
            (feature_range[1] - feature_range[0]) + feature_range[0]
        scaled_dict[key] = value_scaled
    return scaled_dict

    # health_scaler = MinMaxScaler(feature_range=(MIN_HEALTH, MAX_HEALTH))
    # cores_scaler = MinMaxScaler(feature_range=(MIN_CORES, MAX_CORES))
    # bits_scaler = MinMaxScaler(feature_range=(MIN_BITS, MAX_BITS))
    # turn_scaler = MinMaxScaler(feature_range=(MIN_TURNS, MAX_TURNS))

    # return health_scaler, cores_scaler, bits_scaler, turn_scaler


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def action_to_vector(action):
    return [int(x) for x in list('{0:06b}'.format(action))]


if __name__ == '__main__':
    print(DEFEND_TOP_LEFT)
    s = {DEFEND_TOP_LEFT, DEFEND_TOP_MIDDLE, DEFEND_TOP_RIGHT, DEFEND_BOTTOM}
    result = list(powerset(s))
    print(list(result))
