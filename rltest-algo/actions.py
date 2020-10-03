# file to decode action and actually realize that action in arena
import gamelib
from constants import *
import pickle


def do_action(action, game_state, game_json, defense_unit_costs, attack_unit_costs):
    resource_multiplier = (100 - game_json['p1Stats'][HEALTH_INDEX])/100
    # sp_to_spend = int(resource_multiplier * game_json['p1Stats'][SP_INDEX])
    # mp_to_spend = int(resource_multiplier * game_json['p1Stats'][MP_INDEX])
    sp_to_spend = game_state.get_resource(0)
    mp_to_spend = game_state.get_resource(1)
    # gamelib.debug_write("SP TO SPEND:", sp_to_spend)
    # gamelib.debug_write("MP TO SPEND:", mp_to_spend)
    deploy_defenders(action[:ACTION_SPLIT_INDEX],
                     sp_to_spend, game_state, defense_unit_costs)
    deploy_attackers(action[ACTION_SPLIT_INDEX:],
                     mp_to_spend, game_state, attack_unit_costs)


def deploy_defenders(defense_actions, sp_to_spend, game_state, defense_unit_costs):
    num_actions = sum(defense_actions)
    if not num_actions:
        return
    action_to_coords = {
        DEFEND_TOP_LEFT: TOP_LEFT_COORDS,
        DEFEND_TOP_MIDDLE: TOP_MIDDLE_COORDS,
        DEFEND_TOP_RIGHT: TOP_RIGHT_COORDS,
        DEFEND_BOTTOM: BOTTOM_COORDS,
    }
    resources_per_action = sp_to_spend//num_actions
    for i, action in enumerate(defense_actions):
        if action:
            gamelib.debug_write("taking defense action : " + str(i))
            deploy_defenders_in_region(
                resources_per_action, game_state, action_to_coords[i], defense_unit_costs)


def deploy_attackers(attack_actions, mp_to_spend, game_state, attack_unit_costs):
    num_actions = sum(attack_actions)
    if not num_actions:
        return
    action_to_coords = {
        ATTACK_LEFT: game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT),
        ATTACK_RIGHT: game_state.game_map.get_edge_locations(
            game_state.game_map.BOTTOM_LEFT)
    }
    resources_per_action = int(mp_to_spend/num_actions)
    for i, action in enumerate(attack_actions):
        if action:
            gamelib.debug_write("taking attack action : " + str(i))
            deploy_attackers_in_region(
                resources_per_action, game_state, action_to_coords[i], attack_unit_costs)


# individual action options here

# extend to be more specific with wall placement vs other units
def deploy_defenders_in_region(resources_per_action, game_state, coords, defense_unit_costs):
    # middle = ((coords[0][0] + coords[-1][0])/2,
    #           (coords[0][1] + coords[-1][1])/2)  # approximate middle
    # coords = sorted(coords, key=lambda coord: (
    #     coord[0] - middle[0])**2 + (coord[1] - middle[1]))  # sort by distance from approximated middle
    available_units = ["BLAH", "BLAH", "BLAH"]
    resources_per_unit = resources_per_action // len(available_units)
    # or sort by y axis
    coords = sorted(coords, key=lambda coord: coord[1], reverse=True)
    defense_units = sorted(defense_unit_costs.keys(),
                           key=lambda x: defense_unit_costs[x], reverse=True)
    coord_index = 0
    for unit in defense_units:
        resources_left_per_unit = resources_per_unit
        # gamelib.debug_write("Resetting resources left for unit " + unit + " of cost " + str(game_state.type_cost(unit)[0]) + " : " +
        # str(resources_left_per_unit))
        # second conditional is optional sanity check
        # and game_state.get_resource(1) >= game_state.type_cost(unit)[1]:
        while coord_index < len(coords) and resources_left_per_unit >= game_state.type_cost(unit)[0]:
            # gamelib.debug_write("Resources left for unit " + unit + " : " +
            # str(resources_left_per_unit))
            if game_state.can_spawn(unit, coords[coord_index]):
                # if would_block(unit, coords[coord_index], game_state):
                #     gamelib.debug_write(
                #         "Spawning " + str(unit) + " at " + str(coords[coord_index]) + " would have blocked, skipping this coord")
                # else:
                num_spawned = game_state.attempt_spawn(
                    unit, coords[coord_index])
                resources_left_per_unit -= num_spawned * \
                    game_state.type_cost(unit)[0]
                resources_per_action -= num_spawned * \
                    game_state.type_cost(unit)[0]
                # gamelib.debug_write("Spawned " + unit + ", now i have " +
                #                     str(resources_left_per_unit))
            else:
                pass
                # gamelib.debug_write(
                #     "Cant spawn " + str(unit) + " at " + str(coords[coord_index]) + ", cost is " + str(game_state.type_cost(unit)[0]) + " and we have " + str(resources_left_per_unit))
            coord_index += 1


def deploy_attackers_in_region(resources_per_action, game_state, coords, attack_unit_costs):
    available_units = ["BLAH", "BLAH", "BLAH"]
    resources_per_unit = int(resources_per_action / len(available_units))
    # or sort by y axis
    coords = sorted(coords, key=lambda coord: coord[1])
    coord_index = 0
    attack_units = sorted(attack_unit_costs.keys(),
                          key=lambda x: attack_unit_costs[x], reverse=True)
    for unit in attack_units:
        resources_left_per_unit = resources_per_unit
        # gamelib.debug_write("Resetting resources left for unit " + unit + " of cost " + str(game_state.type_cost(unit)[1]) + " : " +
        #                     str(resources_left_per_unit))
        # second conditional is optional sanity check
        # and game_state.get_resource(1) >= game_state.type_cost(unit)[1]:
        while resources_left_per_unit >= game_state.type_cost(unit)[1]:
            # gamelib.debug_write("Resources left for unit " + unit + " : " +
            #                     str(resources_left_per_unit))
            if game_state.can_spawn(unit, coords[coord_index]):
                num_spawned = game_state.attempt_spawn(
                    unit, coords[coord_index])
                resources_left_per_unit -= num_spawned * \
                    game_state.type_cost(unit)[1]
                resources_per_action -= num_spawned * \
                    game_state.type_cost(unit)[1]
                gamelib.debug_write("Spawned " + unit + ", now i have " +
                                    str(resources_left_per_unit))
            # can stack attack units
            else:
                gamelib.debug_write(
                    "Cant spawn " + str(unit) + " at " + str(coords[coord_index]) + ", cost is " + str(game_state.type_cost(unit)[1]) + " and we have " + str(resources_left_per_unit))
                gamelib.debug_write(
                    "Attack resources left for this player " + str(game_state.get_resource(1)))
            coord_index = (coord_index + 1) % len(coords)

    # unit_type = "PI"
    # for coord in coords:
    #     mp_to_spend = game_state.get_resource(1)
    #     gamelib.debug_write("Current attack resources: " + str(mp_to_spend))
    #     if game_state.can_spawn(unit_type, list(coord)):
    #         num_spawned = game_state.attempt_spawn(
    #             unit_type, list(coord))
    #         gamelib.debug_write("Able to spawn " + str(num_spawned) + " " +
    #                             unit_type + ". Remaining resources: " + str(mp_to_spend))
    #     else:
    #         gamelib.debug_write(
    #             "Cant spawn " + str(unit_type) + " at " + str(coord) + ", cost is " + str(game_state.type_cost(unit_type)[1]) + " and we have " + str(mp_to_spend))


def would_block(unit, unit_coord, game_state):  # this function pretty slow though
    game_map = game_state.game_map
    game_state.game_map.add_unit(unit, unit_coord)
    found = False
    for coord in game_map.get_edge_locations(game_map.BOTTOM_LEFT):
        path = game_state.find_path_to_edge(coord)
        ending_coord = path[-1]
        if ending_coord[1] > 13:
            gamelib.debug_write(
                "found path to other side from " + str(coord) + ": " + str(path))
            found = True
    if not found:
        game_state.game_map.remove_unit(unit_coord)
        return True
    for coord in game_map.get_edge_locations(game_map.BOTTOM_RIGHT):
        path = game_state.find_path_to_edge(coord)
        ending_coord = path[-1]
        if ending_coord[1] > 13:
            gamelib.debug_write(
                "found path to other side from " + str(coord) + ": " + str(path))
            found = True
    if not found:
        game_state.game_map.remove_unit(unit_coord)
        return True
    game_state.game_map.remove_unit(unit_coord)
    return False
