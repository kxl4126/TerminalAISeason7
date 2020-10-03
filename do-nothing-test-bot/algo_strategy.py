import gamelib


class DoNothingBot(gamelib.AlgoCore):
    def on_game_start(self, config):
        self.config = config
        global WALL, FACTORY, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        FACTORY = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0

    def on_turn(self, turn_state):
        game_state = gamelib.GameState(self.config, turn_state)
        game_state.enable_warnings = False

        gamelib.debug_write('Performing turn {} of do nothing bot'.format(
            game_state.turn_number))

        self.spawn_defenses(game_state)
        game_state.submit_turn()

    def spawn_defenses(self, game_state):
        defense_spawns = [
            (WALL, [14, 0]),
            (FACTORY, [13, 0]),
            (TURRET, [12, 1]),
            (TURRET, [15, 1]),
            (SCOUT, [26, 12])
        ]
        for defense in defense_spawns:
            if game_state.can_spawn(defense[0], defense[1]):
                game_state.attempt_spawn(defense[0], defense[1])
                # gamelib.debug_write("Able to spawn " +
                #                     str(defense[0]) + " at " + str(defense[1]))


if __name__ == "__main__":
    algo = DoNothingBot()
    algo.start()
