import gamelib  # NEED TO KEEP IN MIND WHICH PACKAGES AVAILABLE ON SERVER
import json
import pickle
import numpy as np
from preprocessing import scale_other_stats, powerset, action_to_vector
from constants import *
from actions import *
import os
import random


# gamelib.debug_write("TOPLEFT:", TOP_LEFT_COORDS)
# only 3 attackers and 3 defenders, so maybe the actions can be derived off of considering every possible subset of a
# combination of these 6 different units, which would be 2^6 combinations
# would also have to decide how much money to spend after deciding which combination of units to use
# Is there a way to separate attackers and defenders in the actions? (one neural net focuses on
# attacking and one on defending? this seems difficult to implement
# as I would need to designate reward in a way that maybe wouldn't be as simple as just winning is positive reward and vice-versa)

# Each unit has stats. Maybe I make the actions to be framed like "defend these 40 units" and attack these spots with 50 health.
# Example action would be "Defend these 50 units with 20 damage (encryption?) and attack with 500 health and 30 speed". Then I
# use some algorithm to fulfill these demands by the neural net. If I don't have enough money, receive negative reward for erroneous action.
# Not sure how reward can be implemented directly by me into the AlphaZero algo. The API abstraction seems to prefer me just
# implementing actions/game states, maybe need to check if moves are legal before doing them and not instantly give negative reward.

# need to consider location of deployment as well
# should I train multiple neural nets (one to consider location of deployment of attackers, one to consider location of deployment of defenders
# , one to consider which offensive units, and one to consider which defensive units?)

# can I do some type of actions based off of a default or current preference
# For example, actions would be - spawn more/less attackers, spawn more/less defenders combined with spawn attackers left/right/middle
# and same with defenders, this would be around (2*2*3*3 = 36 actions) just base actions off of game state? but this seems like it is too crude?

# Weird idea - Can I train a a neural network for every square in the game map (the outer squares would have more actions, as they can also place attackers), this would be around ~225 neural nets, and it wouldn’t be one agent controlling the whole map, so unsure if this is viable. Would train by giving reward through wins and losses the same way. The inputs would be the same as other techniques with the entire game state being passed in? Then one neural net specifically controls one square and effects game state by changing the one square.

# edge_list should be in order TOP_RIGHT, TOP_LEFT, BOTTOM_LEFT, BOTTOM_RIGHT

# list out all coordinates from left to right, top to bottom in order (so can later flatten to pass into neural net?)

# do I use conventional Q-learning technique where a target network tries to predict the q values of each state and that is used as the target
# or is the target based on win/loss, for example, if the player wins, every move in the past game is given a positive reward (multiplied
# by some factor for earlier moves) and then that is used as the target? it seems alpha go uses latter?

# for experience replay, use the latest created file and process the entire replay file into proper format (state, action, reward, next_state)

# another consideration - do i only allow the agent to interact with spots in the grid or do i make a square that contains the actual
# diamond arena and then set everything uninteractable to -1 or something?

# How do I deal with invalid moves? These moves will not be recorded in the replay file as they are not valid, so how should I attribute reward to these attemps?
# My actions are defined more generally so maybe I just check to make sure they are always valid and make the moves I can and the algo
# should sort itself out and learn not to do it?

# maybe have one output head for each square, each connected to the last input layer, and the weights would all be different?
# so output would be each square's potential action (NUMBER DEFENSE UNITS outputs for each square as probability)
# Maybe this is better, as our output space is well defined but then the dimensionality would be (NUM DEFENSE UNITS * NUM COORDS)
# Then we would consider attacking units? How do we add "output heads"?


# do I need to differentiate between enemy and friendly units?


# indices of resources/other stats in stats

# maybe move this to utils and call this once, as the game_map overall coords shouldn't change


def list_coordinates(game_map):
    edges = game_map.get_edges()
    top_half = []
    for top_left_edge, top_right_edge in zip(edges[game_map.TOP_LEFT], edges[game_map.TOP_RIGHT]):
        y = top_left_edge[1]
        top_half.append([(x, y) for x in range(
            top_left_edge[0], top_right_edge[0] + 1)])  # append the row
    bottom_half = []
    for bottom_left_edge, bottom_right_edge in zip(edges[game_map.BOTTOM_LEFT], edges[game_map.BOTTOM_RIGHT]):
        y = bottom_left_edge[1]
        bottom_half.append([(x, y) for x in range(
            bottom_left_edge[0], bottom_right_edge[0] + 1)])  # append the row
    map_coords = []
    for row in top_half:
        map_coords.extend(row)
    bottom_half.reverse()  # must reverse as edges go from bottom to top order
    for row in bottom_half:
        map_coords.extend(row)
    # gamelib.debug_write(edges[game_map.BOTTOM_LEFT])
    print(map_coords)
    # with open('map_coords.pkl', 'wb') as fp:
    #     pickle.dump(map_coords, fp)
    return map_coords


def init_game_state_dict(map_coords):
    game_state_dict = {}
    for coord in map_coords:
        game_state_dict[coord] = [0] * (NUM_DEFENSE_TYPES + CONSIDER_UNIT_TEAM)
    with open('map_coords_initial_dict.pkl', 'wb') as fp:
        pickle.dump(game_state_dict, fp)


class DQNAlgo(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        gamelib.debug_write("Default exploration rate: " +
                            str(DEFAULT_EXPLORATION_RATE))
        # seed = random.randrange(maxsize)
        # random.seed(seed)
        # gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        self.config = config
        global WALL, FACTORY, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        FACTORY = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        # MP = 1
        # SP = 0
        # self.defense_unit_costs, self.attack_unit_costs = self.init_unit_costs()
        self.ATTACK_OPTIONS = {ATTACK_LEFT, ATTACK_RIGHT}
        # need to define what squares these correspond to later
        self.DEFENSE_OPTIONS = {DEFEND_TOP_LEFT,
                                DEFEND_TOP_MIDDLE, DEFEND_TOP_RIGHT, DEFEND_BOTTOM}
        self.ACTION_OPTIONS = self.init_action_combinations()
        # initialize neural nets

    def init_unit_costs(self):
        attack_unit_costs = {}
        defense_unit_costs = {}
        for unit in self.config['unitInformation'][0:3]:
            defense_unit_costs[unit['shorthand']] = unit['cost1']
        for unit in self.config['unitInformation'][3:6]:
            attack_unit_costs[unit['shorthand']] = unit['cost2']
        return defense_unit_costs, attack_unit_costs

    def init_action_combinations(self):
        defense_subsets = list(powerset(self.DEFENSE_OPTIONS))
        attack_subsets = list(powerset(self.ATTACK_OPTIONS))
        action_options = []
        for attack_combination in attack_subsets:
            for defense_combination in defense_subsets:
                action = {}
                action['ATTACK'] = attack_combination
                action['DEFENSE'] = defense_combination
                action_options.append(action)
        return action_options

    def on_turn(self, turn_state):
        game_state = gamelib.GameState(self.config, turn_state)
        game_state.enable_warnings = False
        gamelib.debug_write('Performing turn {} of RL bot'.format(
            game_state.turn_number))
        game_json = json.loads(game_state.serialized_string)
        processed_game_state = self.get_processed_game_state(
            game_json, game_state)
        # action_vector = [0] * (len(self.ATTACK_OPTIONS) +
        #                        len(self.DEFENSE_OPTIONS))
        # # pick action here by going thru every combination of actions and argmaxing (can maybe pick numerical action and we convert to binary string to encode actions)
        # random_action = random.randint(0, NUM_ACTIONS - 1)
        # random_action = action_to_vector(random_action)
        # assert len(random_action) == 6
        # # can add how much money to spend later
        # action_num = 59
        # action_vector = action_to_vector(action_num)
        # for i in range(len(action_vector)-2, len(action_vector)):
        #     action_vector[i] = random.randint(0, 1)
        action_num = self.agent.pick_action(processed_game_state)
        action_vector = action_to_vector(action_num)
        reward = 0
        # arbitrary multiplier so we spend more when we are dying
        do_action(action_vector, game_state, game_json)
        if TRAINING:
            self.agent.train_on_memory()
        # gamelib.debug_write("INSIDE algo strategy" +
        #                     str(self.agent.NN.model.layers[-1].get_weights()[0][0]))
        # choose action and see reward
        game_state.submit_turn()
        return processed_game_state, action_num, reward

    # make an array the same size as list_coordinates, but make it have 3 channels (one for each type of defender, essentially one
    # hot encodes each square)
    # take note that the game_state is always from current player perspective (p2Units always refers to opponent, but in replay files,
    # p2 refers to the actual player two)
    # ^ this could be problematic, so I should probably record the actions taken in game as the game goes on and record the corresponding turn number of each action
    # then match this up with the replay file to get the game states after each turn (so record action for turn 0, then go to replay file after game
    # to extract initial state and resulting state), game winning state is actually second to last line in replay, last line just reiterates the same stats as above line and gives endStats
    def get_processed_game_state(self, game_json, game_state):

        # map_coords = []
        # can add a channel for enemy/friendly 0 or 1
        processed_game_state = []
        game_state_dict = {}
        map_coords_in_order = []
        # care for directory program is ran from
        with open(MAP_COORDS_INITIAL_DICT_PATH, 'rb') as fp:
            # can maybe even make more efficient by just loading once and then setting all to 0 every game start
            game_state_dict = pickle.load(fp)
        with open(MAP_COORDS_PATH, 'rb') as fp:
            map_coords_in_order = pickle.load(fp)
        # extract location of units from game_json, put a 1 in the dictionary in the index corresponding to correct unit
        game_state_dict = self.put_unit_locations_into_game_state(game_state_dict,
                                                                  game_json['p1Units'])
        game_state_dict = self.put_unit_locations_into_game_state(game_state_dict,
                                                                  game_json['p2Units'])
        # gamelib.debug_write("GAME STATE DICT: ", list(
        #     game_state_dict.items())[:10])
        # p1 in this context always refers to the current player running this algo (p1 is me in my perspective)
        # now convert the dictionary values to a long list
        game_state_list = []
        for coord in map_coords_in_order:
            game_state_list.append(game_state_dict[tuple(coord)])

        # just manually flatten? this should be consistent im pretty sure
        processed_game_state = [
            x for coord_sublist in game_state_list for x in coord_sublist]

        # now append the other aspects of the game state (BITS/CORES FOR EACH PLAYER),
        # [my bits, my cores, enemy bits, enemy cores, turn number] etc. include all p1 stats, p2 stats
        # make sure to scale properly, maybe do normalization and guess max/mins until we observe more game states?
        other_stats = self.process_other_stats(game_json, game_state)

        processed_game_state.extend(other_stats)
        return processed_game_state

    def put_unit_locations_into_game_state(self, game_state_dict, unit_locations):
        for i in range(UNIT_LOC_START_INDEX, UNIT_LOC_END_INDEX):
            for unit_location in unit_locations[i]:
                x, y, health, identifier = unit_location
                # go to the correct coordinate and set corresponding index for the unit to 1
                game_state_dict[(x, y)][i] = 1
        return game_state_dict

    # keep in mind p1 always is in perspective of this agent
    def process_other_stats(self, game_json, game_state):
        p1_stats_dict = {
            'health': game_json['p1Stats'][HEALTH_INDEX],
            'sp': game_state.get_resources(0)[0],
            'mp': game_state.get_resources(0)[1],
            'turn': game_state.turn_number
        }
        p1_stats_scaled = scale_other_stats(p1_stats_dict)
        p2_stats_dict = {
            'health': game_json['p2Stats'][HEALTH_INDEX],
            'sp': game_state.get_resources(1)[0],
            'mp': game_state.get_resources(1)[1],
            'turn': game_state.turn_number
        }
        p2_stats_scaled = scale_other_stats(p2_stats_dict)
        stats_list = []
        stats_list.extend(p1_stats_scaled.values())
        stats_list.extend(p2_stats_scaled.values())
        return stats_list


if __name__ == "__main__":
    algo = DQNAlgo()
    algo.start()
    # with open('map_coords.pkl', 'rb') as fp:
    #     map_coords = pickle.load(fp)
    # print(map_coords)
    # init_game_state_dict(map_coords)
    # with open('map_coords_initial_dict.pkl', 'rb') as fp:
    #     map_coords = pickle.load(fp)
    # print(map_coords)
