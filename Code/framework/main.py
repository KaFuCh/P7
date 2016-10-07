from configuration import Module
from verifytaAPI import run_verifyta, get_best_cost
from xml_generator import generate_xml, generate_query
from genetic_algorithm import genetic_algorithm

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
pop = genetic_algorithm(start_population, 100, 20, get_fitness)

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