import json

from .game_state import GameState
from .util import get_command, debug_write, BANNER_TEXT, send_command

LOCAL_MATCH = True
# root changes depending if its on server or local run match
ROOT = 'rltemplate-algo' if LOCAL_MATCH else ''
# index constants
STATE = 0
ACTION = 1
REWARD = 2
NEXT_STATE = 3

MEMORY_SIZE = 50


class AlgoCore(object):
    """
    This class handles communication with the game engine. \n
    algo_strategy.py subclasses it.

    Attributes :
        * config (JSON): json object containing information about the game

    """

    def __init__(self):
        self.config = None
        self.memory_file_path = ROOT + '/memory.txt'
        self.memory = []

    def on_game_start(self, config):
        """
        This function is called once at the start of the game.
        By default, it just initializes the config. \n
        You can override it it in algo_strategy.py to perform start of game setup
        """
        self.config = config

    def on_turn(self, game_state):
        """
        This step function is called at the start of each turn.
        It is passed the current game state, which can be used to initiate a new GameState object.
        By default, it sends empty commands to the game engine. \n
        algo_strategy.py inherits from AlgoCore and overrides this on turn function.
        Adjusting the on_turn function in algo_strategy is the main way to adjust your algo's logic.
        """
        send_command("[]")
        send_command("[]")
        return []

    def on_action_frame(self, action_frame_game_state):
        """
        After each deploy phase, the game engine will run the action phase of the round.
        The action phase is made up of a sequence of distinct frames.
        Each of these frames is sent to the algo in order.
        They can be handled in this function.
        """
        pass

    def start(self):
        """
        Start the parsing loop.
        After starting the algo, it will wait until it recieves information from the game
        engine, proccess this information, and respond if needed to take it's turn.
        The algo continues this loop until it recieves the "End" turn message from the game.
        """
        debug_write(BANNER_TEXT)

        while True:
            # Note: Python blocks and hangs on stdin. Can cause issues if connections aren't setup properly and may need to
            # manually kill this Python program.
            game_state_string = get_command()
            if "replaySave" in game_state_string:
                """
                This means this must be the config file. So, load in the config file as a json and add it to your AlgoStrategy class.
                """
                parsed_config = json.loads(game_state_string)
                self.on_game_start(parsed_config)
            elif "turnInfo" in game_state_string:
                state = json.loads(game_state_string)
                stateType = int(state.get("turnInfo")[0])
                turn_num = int(state.get("turnInfo")[1])
                # note the replay files only record the game_state in action phase (after selecting information/firewall units),
                # while the game_state string in the on_turn method gives data during deploy phase (before selecting/spending on attackers/defenders)
                if stateType == 0:
                    """
                    This is the game turn game state message. Algo must now print to stdout 2 lines, one for build phase one for
                    deploy phase. Printing is handled by the provided functions.
                    """
                    # can return (state, action, None, None) and fill in rest later
                    # debug_write("MADE IT BEFORE ON TURN")
                    # self.memory.append(game_state_string)
                    turn_info = self.on_turn(
                        game_state_string)
                    state, action, reward = turn_info
                    if len(self.memory) > 0:
                        # set previous tuple's next state
                        self.memory[-1][NEXT_STATE] = state[-10:]
                    curr_tuple = [None] * 4
                    curr_tuple[:NEXT_STATE] = state[-10:], action, reward
                    self.memory.append(curr_tuple)
                    # debug_write("MADE IT HERE")
                    # debug_write("RL ALGO TURN NUMBER: " + str(turn_num))
                    # debug_write("RL ALGO TURN STATE: ", turn_info[0][:10])
                    # debug_write("RL ALGO TURN INFO: ", turn_info[1:])
                    # can I make on_turn return the action chosen so that it can be appended to a list then processed
                    # and matched up with game states when the replay is created.
                    # can also create the entire (state, action, reward, next_state) matrix in this loop, and append to it accordingly as the game goes on
                    # For example, on turn 2, the game state is extracted from game_state_string. the game state data
                    # is then placed into the next_state tuple position for turn 1's action and the state tuple position for turn 2
                    # I will need to deal with "waiting a turn" to get the next_state value for the tuple and edge cases of initial state and final state

                    # also will probably need to add both sides experiences to experience file? as they are both the same agent essentially?
                elif stateType == 1:
                    """
                    If stateType == 1, this game_state_string string represents a single frame of an action phase
                    """
                    self.on_action_frame(game_state_string)
                elif stateType == 2:
                    """
                    This is the end game message. This means the game is over so break and finish the program.
                    """
                    debug_write("Got end state, game over. Stopping algo.")

                    # either here or after doing a run_match, get latest replay created (is the file created by this point in the program)
                    # and save to experience replay, every game we check if experience buffer is met, then we can chop off some of the oldest
                    # experiences and then sample X experiences to train model, every Y games of retraining, we can pit previous model against current model
                    # and replace the best model if current model wins, make copy of best model to continue training

                    # Note - replay buffer should probably just be a large file containing a tuple of
                    # (state, action, reward, next_state) so it can be moved between scripts

                    # may need to remove last line of experiences as the final_state has no action associated with it.

                    # maybe better to grab the game_state_string itself and append it to whatever file we are writing, make sure not to duplicate
                    # this line and this line is appended properly, will need to test to see how the end state is received

                    # self.memory.append(game_state_string)

                    self.memory[-1][REWARD] = 1 if state.get(
                        "endStats")['winner'] == 1 else -1
                    # do i assign reward to last 2 states or 1?
                    self.memory[-2][REWARD] = self.memory[-1][REWARD]
                    with open(self.memory_file_path, 'r+') as f:
                        # uncomment lines when I want to write properly for experience replay
                        # original = f.read().split('\n')
                        # f.seek(0, 0)
                        for tup in self.memory:
                            f.write(str(tup) + '\n')
                        # for i in range(min(MEMORY_SIZE, len(original))):
                            # debug_write(original[i])
                            # f.write(original[i] + '\n')
                    break
                else:
                    """
                    Something is wrong? Received an incorrect or improperly formatted string.
                    """
                    debug_write("Got unexpected string with turnInfo: {}".format(
                        game_state_string))
            else:
                """
                Something is wrong? Received an incorrect or improperly formatted string.
                """
                debug_write("Got unexpected string : {}".format(
                    game_state_string))
