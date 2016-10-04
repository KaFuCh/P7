from copy import deepcopy


class Module:
  """
  Represents a module in the Festo system
  """

  def __init__(self, module_id, work_type, processing_time, transport_time, cost_rate, connections):
    """
    :param module_id: A unique identifier for the module
    :param connections: A list of IDs, which the module connects to.
    :param work_type: An identifier for the work type of the module (integer)
    :param processing_time: An integer specifying the processing time of the module
    :param transport_time: An integer specifying the transport time of the module
    """

    if module_id == 0:
      raise ValueError("Module_id may not be set to 0")
    else:
      self.module_id = module_id
    self.connections = connections
    self.num_of_connections = len(connections)
    self.work_type = work_type
    self.cost_rate = cost_rate
    self.processing_time = processing_time
    self.transport_time = transport_time

  def __eq__(self, other):
      if isinstance(other, self.__class__):
        equal = True
        for attr in self.__dict__:
          if attr not in other.__dict__:
            equal = False
        return equal
      else:
          return False

  def __ne__(self, other):
      return not self.__eq__(other)

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

  def get_paths(self, module, paths):
    """
    Gets all possible paths from a single module.
    A path is a list of modules, which represents a flow through the system.
    If a path has a loop in it, this will be indicated by an integer, as the first element of the returned list.
    This integer is the id of the module which can be looped back onto, at the end of the list.
    :param module: the module to get all paths from
    :param paths: Is used to recursively build the paths. Call with [[module]].
    :return: A list of possible paths (lists of modules), from the given module
    """
    paths_copy = deepcopy(paths)
    for path in [x for x in paths_copy if type(x[0]) is not int]:
      if len(path[-1].get_connections()) == 1:
        if [x for x in self.modules if path[-1].get_connections()[0] == x.module_id][0] not in path:
          paths.append(path + [x for x in self.modules if x.module_id == path[-1].get_connections()[0]])
          paths.remove(path)
        else:
          paths[paths.index(path)] = [path[-1].get_connections()[0]] + paths[paths.index(path)]
      else:
        looping_paths = []
        for connection in path[-1].get_connections():
          if [x for x in self.modules if connection == x.module_id][0] not in path:
            paths.append(path + [x for x in self.modules if x.module_id == connection])
          else:
            if path not in looping_paths:
              paths[paths.index(path)] = [connection] + paths[paths.index(path)]
              looping_paths.append(path)
    if paths_copy == paths:
      return paths
    else:
      clean_paths = deepcopy(paths)
      for pth in paths:
        for pth2 in paths:
          if pth != pth2 and pth == pth2[:len(pth)] and pth in clean_paths:
            clean_paths.remove(pth)
      paths = deepcopy(clean_paths)
    return self.get_paths(module, paths)

  def create_dependencies(self):
    """
    Creates a dict of dependencies, key is module_id, value is a list of module_ids that the key depends on
    :return: a dict of dependencies, i.e. a dict(int -> [int])
    """
    dependencies = {}
    for module in self.modules:
      if module.module_id not in dependencies:
        dependencies[module.module_id] = []
      for connection in module.get_connections():
        if connection not in dependencies:
          dependencies[connection] = []
        if connection not in dependencies[module.module_id]:
          dependencies[module.module_id].append(connection)
        if module.module_id not in dependencies[connection]:
          dependencies[connection].append(module.module_id)
    return dependencies

  def is_placeable(self):
    """
    Used to determine if the Configuration is placeable in real life.
    :return: True if placeable. False, otherwise.
    """
    self_loop_okay = True
    direct_connections_okay = True

    for module in self.modules:  # check that there are always an uneven no of modules between a self-loop
      paths = [x for x in self.get_paths(module, [[module]]) if type(x[0]) is int]
      if len(paths) == 0:
        continue
      for path in paths:
        loop_index = path.index([x for x in path[1:] if x.module_id == path[0]][0])
        if (len(path) - loop_index) % 2 == 1:
          self_loop_okay = False
          break
    if not self_loop_okay:
      return False

    for module in self.modules:  # check if direct and indirect connection, indirect connection has even no of modules
      paths = self.get_paths(module, [[module]])
      for path in paths:
        for direct_connection in [x for x in self.modules if x.module_id in module.get_connections() and x in path]:
          if (path.index(direct_connection) - path.index(module)) % 2 == 0:
            direct_connections_okay = False
            break
    if not direct_connections_okay:
      return False

    dependencies = self.create_dependencies()  # check that a module doesn't share too many dependencies
    for dependency in dependencies:
      no_of_one_shares = 0
      no_of_two_shares = 0
      no_of_three_shares = 0
      for other_dependency in [x for x in dependencies if x != dependency]:
        len_shared_modules = len(set(dependencies[dependency]).intersection(set(dependencies[other_dependency])))
        if len_shared_modules > 0:
          no_of_one_shares += 1
        if len_shared_modules > 1:
          no_of_two_shares += 1
        if len_shared_modules > 2:
          no_of_three_shares += 1
      if no_of_one_shares / 2 > 3 or no_of_two_shares / 2 > 1 or no_of_three_shares / 2 > 0:
        return False
    return True

  def is_valid(self):
    """
    Checks for validity of the Configuration, i.e. is the Configuration legal/realistic
    :return: True, if the Configuration is valid. False, otherwise.
    """
    for module in self.modules:
      if len(module.get_connections()) > 4:  # Check if module has more than 4 connections
        return False
      if module.module_id in module.get_connections():  # Check if module connects to itself
        return False
      for index in module.get_connections():
        if not any(x.module_id == index for x in self.modules):  # Check if module connects to non-existing module
          return False
    if not self.contains_only_one_line():  # Check if module contains more than 1 production line
      return False
    if not self.is_placeable():  # Check if module is placeable
      return False
    return True


# Below are som useful debugging functions for this module

def printable_paths(paths):
  """
  Used for debugging purposes.
  :param paths: a list of paths, i.e. a list of list of modules
  :return: paths as a string in a printable format
  """
  s = "["
  for path in paths:
    s += printable_path(path) + ", "
  if len(s) > 1:
    return s[:-2] + "]"
  else:
    return s + "]"


def printable_path(path):
  """
  Used for debugging purposes.
  :param path: a single path, i.e a list of modules
  :return: a path as a string in a printable format
  """
  s = "["
  for module in path:
    if type(module) is Module:
      s += str(module.module_id) + ", "
    else:
      s += "(Looping index: " + str(module) + ") "
  if len(s) > 1:
    return s[:-2] + "]"
  else:
    return s + "]"
