from xml.etree.ElementTree import parse
from copy import deepcopy


def create_model_xml(file, global_decl_string, recipe_strings, system_string, new_file):
    tree = parse(file)

    global_decl = tree.find("declaration")
    global_decl.text = global_decl_string

    templates = tree.findall("template")
    for t in templates:
        if t.find("name").text == "Recipe":
            recipe_template = t
            break

    tree.getroot().remove(recipe_template)

    system_decl = tree.find("system")
    tree.getroot().remove(system_decl)

    for r in recipe_strings:
        temp_copy = deepcopy(recipe_template)

        n = temp_copy.find("name")
        n.text = r["name"]

        p = temp_copy.find("parameter")
        p.text = r["parameter"]

        tree.getroot().append(temp_copy)

    system_decl.text = system_string
    tree.getroot().append(system_decl)

    tree.write(new_file)


def generate_xml(template_file, modules, recipes, new_file_name="test.xml"):

    S = set()
    for m in modules:
        S.add(m.work_type)
    number_of_worktypes = len(S)
    global_decl_string = generate_global_declarations(len(modules), number_of_worktypes, recipes)

    recipe_strings = generate_recipe_templates(recipes)

    system_string = generate_module_declarations(modules)

    for id, r in enumerate(recipes):
        system_string += generate_recipe_declaration(id, r)

    system_string += "rem = Remover();\n"
    system_string += "cos = Coster(1);\n"
    system_string += generate_system_declaration(len(modules), len(recipes))
    # TODO generate different connections for the modules and make an xml file for each
    create_model_xml(template_file, global_decl_string, recipe_strings, system_string, new_file_name)


def generate_global_declarations(number_of_modules, number_of_worktypes, recipes):
    s = "const int NUMBER_OF_MODULES = " + str(number_of_modules) + ";\n"
    s += "const int NUMBER_OF_WORKTYPES = " + str(number_of_worktypes) + ";\n"
    s += "const int NUMBER_OF_RECIPES = " + str(len(recipes)) + ";\n"
    for id, r in enumerate(recipes):
        s += "const int N_OF_NOD" + str(id) + " = " + str(len(r)) + ";\n"

    s += """chan transport[NUMBER_OF_MODULES + 1];
chan work[NUMBER_OF_WORKTYPES + 1];
chan handshake[NUMBER_OF_RECIPES + 1];

clock global_c;

typedef int[-1, NUMBER_OF_RECIPES] rid_t;
typedef int[0, NUMBER_OF_WORKTYPES] wid_t;
typedef int[0, NUMBER_OF_MODULES] id_t;

rid_t var = 0;

meta int remaining = 0;
"""

    return s


def generate_recipe_templates(number_of_recipes):
    recipe_string_list = []
    for r in range(number_of_recipes):
        recipe_string = {}

        recipe_string["name"] = "Recipe" + str(r)

        recipe_string["parameter"] = \
            "rid_t rid, wid_t& n_work[N_OF_NOD" + str(r) + \
            "],  int& n_num_parents[N_OF_NOD" + str(r) + \
            "], int& n_children[N_OF_NOD" + str(r) + \
            "][N_OF_NOD" + str(r) + \
            "], int& n_children_len[N_OF_NOD" + str(r) + "]"

        recipe_string_list.append(recipe_string)

    return recipe_string_list


def generate_recipe_declaration(id, recipe):

    size = "N_OF_NOD" + str(id)
    n_works = []
    n_num_parents = []
    n_children = []
    n_children_len = []

    for work, deps in recipe.items():
        n_works.append(work)
        n_num_parents.append(len(deps))
        children = []
        for id, parents in enumerate(recipe.values()):
            if work in parents:
                children.append(id)

        n_children.append(children)
        n_children_len.append(len(children))

    number_of_nodes = len(recipe)
    for children in n_children:
        while(len(children) < number_of_nodes):
            children.append(-1)

    s = ""
    s += "wid_t n_works[N_OF_NOD" + str(size) + "] = {" + ",".join(map(str,n_works)) + "}"

    print(n_works)
    print(n_num_parents)
    print(n_children)
    print(n_children_len)
    print(s)

def generate_module_declarations(modules):

    s = ""
    for module in modules:  # Define connections
        s += "int connections" + str(module.module_id) + "[4] = {"  # TODO a module has a maximum of 4 connections
        for index in module.get_connections():
            s += str(index) + ", "

        for i in range(0, 4 - len(module.get_connections())):
            s += "-1, "

        s = s[:-2]  # remove last comma and space, added in loop
        s += "};\n"

    s += "\n"
    for module in modules:  # Define processes
        s += "m" + str(module.module_id) + \
             " = Module(" + str(module.module_id) + \
             ", " + str(module.work_type) + \
             ", " + str(module.processing_time) + \
             ", " + str(module.transport_time) + \
             ", " + str(module.cost_rate) + \
             ", " + "connections" + str(module.module_id) + \
             ", " + str(module.num_of_connections) + ");\n"

    s += "\n\n"
    return s


    def generate_system_declaration(number_of_modules, number_of_recipes):
        s = "system rem, cos"
        for i in range(number_of_modules):  # add processes/modules to system definition
            s += ", m" + str(i + 1)

        for i in range(number_of_recipes):
            s += ", r" + str(i + 1)

        s += ";"
        return s


def generate_query(number_of_recipes, new_file_name="test.q"):
    s = "E<> "
    for i in range(number_of_recipes):
        if i + 1 != 1:
            s += " && "
        s += "r" + str(i + 1) + ".done"
    f = open(new_file_name, 'w')
    f.write(s)
    f.close()

generate_recipe_declaration(1, {3:set([2,4]), 2: set([1]), 4:set([1]), 1:set([])})

