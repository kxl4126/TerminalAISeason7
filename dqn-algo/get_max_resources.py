# utility script to just get an idea of the ranges appropriate for the min max scaler
import json

REPLAY_FILE = '/Users/kevinli/TerminalAI/C1GamesStarterKit/replays/p1-01-09-2020-17-16-53-1598998613573-1182222729.replay'


def get_max_resources(file_name):
    max_cores = 0
    max_bits = 0
    max_health = 0
    with open(file_name) as file:
        for line in file:
            line = line.strip()
            if line != '':
                data = json.loads(line)
                if 'p1Stats' in data:
                    # print(data)
                    p1Stats = data['p1Stats']
                    p2Stats = data['p2Stats']
                    max_turn_health = p1Stats[0] if p1Stats[0] > p2Stats[0] else p2Stats[0]
                    max_turn_cores = p1Stats[1] if p1Stats[1] > p2Stats[1] else p2Stats[1]
                    max_turn_bits = p1Stats[2] if p1Stats[2] > p2Stats[2] else p2Stats[2]

                    max_health = max_health if max_health > max_turn_health else max_turn_health
                    max_cores = max_cores if max_cores > max_turn_cores else max_turn_cores
                    max_bits = max_bits if max_bits > max_turn_bits else max_turn_bits

    print("MAX HEALTH: ", max_health)
    print("MAX CORES: ", max_cores)
    print("MAX BITS: ", max_bits)

    return max_health, max_cores, max_bits


if __name__ == '__main__':
    get_max_resources(REPLAY_FILE)
