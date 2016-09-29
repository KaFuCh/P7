from Experiments.configuration import Module, Configuration
from Experiments.xml_generator import create_model_xml


def generate_xml(template_file, modules, recipes):
  """
  Creates an xml file readable by uppaal.
  :param template_file: A file template to base the new file one
  :param modules: The modules in the system
  :param recipes: A list of dependencies
  :return: nothing
  """


  system_string = generate_module_declarations(modules)
  for i in range(len(recipes)):
    system_string += generate_recipe_declaration(i, recipes[i])

  system_string += "rem = Remover();\n"
  system_string += "cos = Coster();\n"
  system_string += generate_system_declaration(len(modules), len(recipes))

  S = set()
  for m in modules:
    S.add(m.work_type)
  number_of_worktypes = len(S)


  global_decl_string = generate_global_declarations(len(modules), number_of_worktypes, len(recipes))

  replace_dict = {"system": system_string, "declaration": global_decl_string}  # TODO generate different connections for the modules and make an xml file for each
  create_model_xml(template_file, replace_dict, "test.xml")


def generate_global_declarations(number_of_modules, number_of_worktypes, number_of_recipes):
  """
  Generates global declarations for UPPAAL
  :param number_of_modules: The amount of modules
  :param number_of_worktypes: The amount of different worktypes spread over modules
  :param number_of_recipes: The amount of recipes
  :return: a string declaring global variables for UPPAAL
  """

  s = "const int NUMBER_OF_MODULES = " + str(number_of_modules) + ";\n"
  s += "const int NUMBER_OF_WORKTYPES = " + str(number_of_worktypes) + ";\n"
  s += "const int NUMBER_OF_RECIPES = " + str(number_of_recipes) + ";\n\n"

  s += """chan transport[NUMBER_OF_MODULES];
chan work[NUMBER_OF_WORKTYPES];
chan handshake[NUMBER_OF_RECIPES];

clock global_c;

typedef int[-1, NUMBER_OF_RECIPES - 1] rid_t;
typedef int[0, NUMBER_OF_WORKTYPES - 1] wid_t;
typedef int[0, NUMBER_OF_MODULES - 1] id_t;

rid_t var = 0;

meta int remaining = 0;
"""

  return  s



def generate_module_declarations(modules):
  """
  Generates a system declaration readable by uppaal
  :param modules: The modules in the system
  :return: the system declaration as a string
  """
  s = ""

  for module in modules:  # Define connections
    s += "int connections" + str(module.module_id) + "[4] = {"  # TODO a module has a maximum of 4 connections
    if len(module.get_connections()) > 4:
      return False
    for index in module.get_connections():
      s += str(index) + ", "

    for i in range(0, 4 - len(module.get_connections())):
      s += "-1, "

    s = s[:-2]  # remove last comma and space, added in loop
    s += "};\n"

  for module in modules:  # Define processes
    s += "m" + str(module.module_id) + \
         " = Module(" + str(module.module_id) + \
         ", " + str(module.work_type) + \
         ", " + str(module.processing_time) + \
         ", " + str(module.transport_time) + \
         ", " + "connections" + str(module.module_id) + \
         ", " + str(module.num_of_connections) + ");\n"

  return s


def generate_recipe_declaration(id, dependencies):
    s = "wid_t " + "deps" + str(id) +"[12][12] = {\n"
    for i in range(12):
        if not i == 0:
            s += ","
        if i > len(dependencies) - 1:
            s += "{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}\n"
        else:
            s += "{"
            for j in range(12):
                if not j == 0:
                    s += ", "
                if j > len(dependencies[i]) - 1:
                    s += "0"

                else:
                    s += str(dependencies[i][j])
            s += "}\n"
    s += "};\n\n"

    s += "wid_t lengths" + str(id) + "[12] = {"
    for i in range(12):
        if not i == 0:
            s += ", "
        if i > len(dependencies) - 1:
            s += "0"
        else:
            s += str(len(dependencies[i]))
    s += "};\n\n"
    s += "r" + str(id) + " = Recipe(" + str(id) + ", " + "deps" + str(id) + ", " + "lengths" + str(id) + ", " + str(len(dependencies)) + ");"

    return s


def generate_system_declaration(number_of_modules, number_of_recipes):
  s = "system rem, cos"
  for i in range(number_of_modules):  # add processes/modules to system definition
    s += ", m" + str(i)

  for i in range(number_of_recipes):
    s += ", r" + str(i)

  s += ";"
  return s