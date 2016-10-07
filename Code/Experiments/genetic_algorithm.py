import random
import bisect
from verifytaAPI import run_verifyta, get_best_cost
from xml_generator import generate_xml, generate_query


p1 = {1: [2], 2: [3, 4], 3: [6], 4: [5], 5: [3], 6: [0]}
p2 = {1: [2], 2: [4], 3: [6], 4: [5], 5: [6], 6: [0]}
p3 = {1: [2], 2: [3], 3: [4], 4: [5], 5: [6], 6: [0]}
p4 = {1: [2, 3, 4, 5, 6], 2: [1], 3: [1], 4: [1], 5: [1], 6: [0]}

population = list(zip([p1, p2, p3, p4], [50, 60, 30, 70]))

def genetic_algorithm(start_population, number_of_fucks, modules, recipes):
    """
    :param start_population:
    :param number_of_fucks:
    :return:
    """
    population = start_population
    for i in range(number_of_fucks):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        z = random.randint(0, 100)

        mom, dad = selection(population)
        child = crossover(mom, dad)

        if x < 3:
            mutation_add_connection(child)
        if y < 3:
            mutation_remove_connection(child)
        if z < 10:
            mutation_swap_modules(child)

        cfit = get_fitness(child, modules, recipes)

        kill_individual(population)
        population.append((child, cfit))

    return population


def get_fitness(indiviudal, modules, recipes):
    for m in modules:
        m.set_connections(indiviudal)
    generate_xml(template_file='../../Modeler/iter1.xml', modules=modules, recipes=recipes, new_file_name='temp.xml')
    result, trace = run_verifyta('temp.xml', 'temp.q', '-t 3', verifyta='../Experiments/verifyta')
    fitness = get_best_cost(result)
    return fitness


def kill_individual(population):
    """
    :param population:
    :return:
    """
    individuals, fits = zip(*population)
    min_fit = min(fits)
    max_fit = max(fits)

    weights = []
    for fit in fits:
        if max_fit != min_fit:
            w = 1 - ((fit - min_fit) / (max_fit - min_fit))
        else:
            w = 1
        weights.append(w)

    choices = list(zip(individuals, weights))

    p, w, i = weighted_choice(choices)

    population.remove(population[i])

    return population


def selection(population):
    individuals, fits = zip(*population)
    min_fit = min(fits)
    max_fit = max(fits)

    weights = []
    for fit in fits:
        if max_fit != min_fit:
            w = (fit - min_fit) / (max_fit - min_fit)
        else:
            w = 1
        weights.append(w)

    choices = list(zip(individuals, weights))

    p1, w1, i1 = weighted_choice(choices)
    choices.remove((p1, w1))
    p2, w2, i2 = weighted_choice(choices)

    return p1, p2



def weighted_choice(choices):
    values, weights = zip(*choices)
    total = 0
    cum_weights = []
    for w in weights:
        total += w
        cum_weights.append(total)
    x = random.random() * total
    i = bisect.bisect(cum_weights, x)
    return values[i], weights[i], i # TODO Sometimes out of bounds, figure out why and fix


def crossover(p1, p2):
    child = {}
    for i in range(1, len(p1) + 1):
        choice = random.choice([0, 1, 2])
        if choice == 0:
            child[i] = p1[i]
        elif choice == 1:
            child[i] = p2[i]
        else:
            child[i] = list(set(p1[i]) | set(p2[i]))
    return child


def mutation_swap_modules(c):
    keys = list(c.keys())
    k1 = random.choice(keys)
    k2 = random.choice(keys)

    temp = c[k1]
    c[k1] = c[k2]
    c[k2] = temp

    return c


def mutation_add_connection(c):
    keys = list(c.keys())
    k1 = random.choice(keys)
    keys.append(0)      # So we can add a random connection to 0
    k2 = random.choice(keys)

    if k2 != k1:
        c[k1].append(k2)

    return c


def mutation_remove_connection(c):
    keys = list(c.keys())
    k = random.choice(keys)

    if len(c[k]) > 1:
        values = c[k]
        v = random.choice(values)
        c[k].remove(v)

    return c