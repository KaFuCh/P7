from Experiments.configuration import Module, Configuration
from Experiments.xml_generator import create_model_xml


def generate_configurations(template_file, modules):
  """
  Creates an xml file readable by uppaal.
  :param template_file: A file template to base the new file one
  :param modules: The modules in the system
  :return: nothing
  """
  replace_dict = {"system": generate_system_declaration(modules)}  # TODO generate different connections for the modules and make an xml file for each
  create_model_xml(template_file, replace_dict, "test.xml")


def generate_system_declaration(modules):
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
    s += "Process" + str(module.module_id) + \
         " = Modul(" + str(module.module_id) + \
         ", " + str(module.work_type) + \
         ", " + str(module.processing_time) + \
         ", " + str(module.transport_time) + \
         ", " + "connections" + str(module.module_id) + \
         ", " + str(module.num_of_connections) + ");\n"

  s += "recipe1 = RecipePar2();\n"  # Instantiate recipes

  s += "system recipe1, "  # define system
  for module in modules:  # add processes/modules to system definition
    s += "Process" + str(module.module_id)
    s += ", "
  s = s[:-2]  # remove last comma and space, added in loop
  s += ";"
  return s
