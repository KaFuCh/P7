from configuration import Module, Configuration
from verifytaAPI import run_verifyta, get_best_cost
from xml_generator import generate_xml, generate_query
from genetic_algorithm import genetic_algorithm
from random import randint, choice, random, shuffle
from bisect import bisect_left
from itertools import combinations
from bisect import bisect_left

def generate_configuration(modules):
    """
    From a list of modules a random FESTO factory configuration is generated
    :param modules: A list of FESTO modules that do not have any connections yet
    :return: A factory configuration in the form of a dictionary of lists
    """
    configuration = {}
    for m in modules:
        configuration[m.module_id] = []

    module_ids = list(configuration.keys())
    copy_module_ids = module_ids.copy()

    # Placing the first module at center point
    placed_modules = {}
    x = choice(module_ids)
    copy_module_ids.remove(x)
    placed_modules[(0, 0)] = x

    # Each module is placed adjacent to an already placed module
    for i in copy_module_ids:
        selectable = []

        for pos in list(placed_modules.keys()):
            x = pos[0]
            y = pos[1]

            selectable.append((x - 1, y))
            selectable.append((x + 1, y))
            selectable.append((x, y - 1))
            selectable.append((x, y + 1))

        # Randomly chooses one of the selectable positions and places down the module
        shuffle(selectable)
        for pos in selectable:
            if pos not in placed_modules.keys():
                placed_modules[pos] = i
                break

    # For each module, connections are established to at least one of the adjacent modules
    for pos, m in placed_modules.items():
        possible_neighbours = []
        x = pos[0]
        y = pos[1]

        possible_neighbours.append((x - 1, y))
        possible_neighbours.append((x + 1, y))
        possible_neighbours.append((x, y - 1))
        possible_neighbours.append((x, y + 1))

        # Does not pick positions where no neighbour exists
        selectable_neighbours = []
        for x in possible_neighbours:
            if x in placed_modules.keys():
                selectable_neighbours.append(placed_modules[x])

        # Creates a list of all combinations of selectable neighbours
        selectable_neighbours_combo = []
        for i in range(1, len(selectable_neighbours) + 1):
            selectable_neighbours_combo = selectable_neighbours_combo + (list(combinations(selectable_neighbours, i)))

        # Generates a cummulative possibility over combinations and chooses one of them
        total = 0
        cum_weights = []

        for x in selectable_neighbours_combo:
            total += 1 / len(x)
            cum_weights.append(total)

        x = random() * total
        i = bisect_left(cum_weights, x)
        configuration[m] = list(selectable_neighbours_combo[i])

    # Adds a single exit point to the configuration
    configuration[choice(module_ids)].append(0)

    return configuration

recipes = [[[1, 2], [3, 4]],
           [[1, 2], [3, 4]]]

m1 = Module(
    module_id=1,
    work_type=1,
    processing_time=5,
    transport_time=5,
    cost_rate=5,
)

m2 = Module(
    module_id=2,
    work_type=2,
    processing_time=5,
    transport_time=10,
    cost_rate=5,
)

m3 = Module(
    module_id=3,
    work_type=2,
    processing_time=5,
    transport_time=10,
    cost_rate=5,
)

m4 = Module(
    module_id=4,
    work_type=3,
    processing_time=5,
    transport_time=5,
    cost_rate=5,
)

m5 = Module(
    module_id=5,
    work_type=3,
    processing_time=5,
    transport_time=5,
    cost_rate=5,
)

m6 = Module(
    module_id=6,
    work_type=4,
    processing_time=5,
    transport_time=5,
    cost_rate=5,
)

m7 = Module(
    module_id=7,
    work_type=4,
    processing_time=5,
    transport_time=5,
    cost_rate=5,
)

mlist = [m1, m2, m3, m4, m5, m6, m7]

config1 = {1: [2],
           2: [3],
           3: [4],
           4: [5],
           5: [6],
           6: [7],
           7: [0]}

config2 = {1: [2, 3],
           2: [4],
           3: [4],
           4: [5],
           5: [6],
           6: [7],
           7: [0]}

config3 = {1: [2],
           2: [3],
           3: [4, 5],
           4: [5],
           5: [6],
           6: [7],
           7: [0]}

config4 = {1: [2],
           2: [3],
           3: [4],
           4: [5],
           5: [6, 7],
           6: [7],
           7: [0]}

config5 = {1: [2],
           2: [3],
           3: [4],
           4: [6],
           5: [6],
           6: [7],
           7: [0]}

start_configs = [config1, config2, config3, config4, config5]

start_population = []

generate_query(len(recipes), 'temp.q')

print('Making start population')
for config in start_configs:
    print('Verifying: ' + str(config))
    for m in mlist:
        m.set_connections(config)
    generate_xml(template_file='../../Modeler/iter1.xml', modules=mlist, recipes=recipes, new_file_name='temp.xml')
    result, trace = run_verifyta('temp.xml', 'temp.q', '-t 3', verifyta='../Experiments/verifyta')
    fitness = get_best_cost(result, 300)
    start_population.append((config, fitness))

def get_fitness(configuration):
    for m in mlist:
        m.set_connections(configuration)
    generate_xml(template_file='../../Modeler/iter1.xml', modules=mlist, recipes=recipes, new_file_name='temp.xml')
    result, trace = run_verifyta('temp.xml', 'temp.q', '-t 3', verifyta='../Experiments/verifyta')
    fitness = get_best_cost(result, 300)
    return fitness

print('Starting GA')
pop = genetic_algorithm(start_population, 1000, 20, get_fitness)

best_config = {1: [2, 3],   # work 1
               2: [4],   # work 2
               3: [5],   # work 2
               4: [6],   # work 3
               5: [7],   # work 3
               6: [0],   # work 4
               7: [0]}      # work 4
for m in mlist:
    m.set_connections(best_config)

x = get_fitness(best_config)