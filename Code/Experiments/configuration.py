class Module:
  """
  Represents a module in the Festo system
  """

  def __init__(self, module_id, connections, num_of_connections):
    """
    :param module_id: A unique identifier for the module
    :param connections: A list of IDs, which the module connects to.
                        This can include values, other than the connections, as long as num_of_connections is specified
    :param num_of_connections: The number of connections for the module
    """
    # TODO Not sure if num_of_connections is really needed. We only use it here for verification purposes (We have it from uppaal anyway)
    if num_of_connections > len(connections):
      del self
    self.module_id = module_id
    self.connections = connections
    self.num_of_connections = num_of_connections

  def get_connections(self):
    """
    :return: A list of IDs, which the module connects to
    """
    res = []
    for i in range(0, self.num_of_connections):
      res.append(self.connections[i])
    return res


class Configuration:
  """
  Represents a configuration of the Festo system, i.e. a collection of modules
  """
  def __init__(self, modules):
    """
    :param modules: A list of modules, which the Configuration consists of
    """
    self.modules = modules

  def contains_only_one_line(self):
    """
    Checks if there is only a single production line in the Configuration.
    Is used in is_valid.
    :return: True, if there is only a single production line. False, otherwise.
    """
    if len(self.modules) < 2:  # if there are 1 or 0 modules, then there is only a single line
      return True
    reached_modules = [self.modules[0]]  # Create a list of reached modules, with a starting module

    while len(reached_modules) < len(self.modules):  # Run until all modules are reached
      reached_modules_copy = reached_modules.copy()

      for module in reached_modules_copy:  # Add all modules, that reached modules connect to
        reached_modules = reached_modules + [x for x in self.modules
                                             if x.module_id in module.get_connections()
                                             and x not in reached_modules]

      for module in self.modules:  # Add all modules that connect to reached modules
        if module not in reached_modules:
          for reached_module in reached_modules_copy:
            if reached_module.module_id in module.get_connections():
              reached_modules.append(module)

      if len(reached_modules) == len(reached_modules_copy):  # If we have not reached any new modules, but are not done
        return False
    return True

  def is_valid(self):
    """
    Checks for validity of the Configuration, i.e. is the Configuration legal/realistic
    :return: True, if the Configuration is valid. False, otherwise.
    """
    for module in self.modules:
      if module.module_id in module.get_connections():  # Check if module connects to itself
        return False
      for index in module.get_connections():
        if not any(x.module_id == index for x in self.modules):  # Check if module connects to non-existing module
          return False
    if not self.contains_only_one_line():  # Check if module contains more than 1 production line
      return False
    return True
