import random
from copy import deepcopy
from unittest import TestCase

from hypothesis import given, assume, strategies as st

from module import Module
from Validation.configuration_validation import contains_only_one_line, get_paths


@st.composite
def modules(draw):
  m_id = draw(st.integers(min_value=1))
  w_id = draw(st.integers())
  p_time = draw(st.integers())
  t_time = draw(st.integers())
  c_rate = draw(st.integers(min_value=0))
  cons = []
  return Module(m_id, w_id, p_time, t_time, c_rate, cons)


@st.composite
def configurations(draw, min_num_of_modules=0):
  mods = draw(st.lists(modules()))
  assume(len(mods) >= min_num_of_modules)
  return mods


@st.composite
def proper_configurations(draw):
  num_of_modules = random.randint(2, 10)
  mods = []
  for i in range(1, num_of_modules + 1):
    m_id = i
    w_type = draw(st.integers())
    p_time = draw(st.integers())
    t_time = draw(st.integers())
    c_rate = draw(st.integers())
    # cons = draw(st.lists(st.integers(min_value=i, max_value=num_of_modules).filter(lambda x: x != i), max_size=4, unique=True))
    mods.append(Module(m_id, w_type, p_time, t_time, c_rate, []))

  modules_without_connections = deepcopy(mods)
  current_module = random.choice(modules_without_connections)
  modules_without_connections.remove(current_module)

  while len(modules_without_connections) > 0:
    if len(current_module.connections) < 4:
      random_choice = random.choice(modules_without_connections)
      current_module.connections.append(random_choice)
      mods[mods.index(next(mod for mod in mods if mod.module_id == current_module.module_id))] = current_module
      modules_without_connections.remove(random_choice)
    if len(current_module.connections) == 4:
      current_module = random.choice(current_module.connections)
  return mods


class TestModule(TestCase):
  @given(modules())
  def test_module_equality(self, mod1, mod2):
    mod1_cpy = deepcopy(mod1)
    mod2_cpy = deepcopy(mod2)
    assert mod1 == mod1_cpy
    assert mod2 == mod2_cpy
    if mod1.module_id == mod2.module_id and \
                    mod1.connections == mod2.connections and \
                    mod1.num_of_connections == mod2.num_of_connections and \
                    mod1.work_type == mod2.worktype and \
                    mod1.cost_rate == mod2.cost_rate and \
                    mod1.processing_time == mod2.processing_time and \
                    mod1.transport_time == mod2.transport_time:
      assert mod1 == mod2
    else:
      assert not mod1 == mod2

  @given(modules())
  def test_get_connections_correct_length(self, mod):
    assert len(mod.get_connections()) == len(mod.connections)

  @given(modules())
  def test_get_connections_correct_type(self, mod):
    assert isinstance(mod.get_connections(), list)
    for elem in mod.get_connections():
      assert isinstance(elem, int)

  @given(modules())
  def test_module_equality(self, mod):
    mod2 = Module(mod.module_id, mod.work_type, mod.processing_time, mod.transport_time, mod.cost_rate, mod.connections)
    assert mod == mod2
    assert not mod != mod2


class TestConfiguration(TestCase):
  @given(configurations())
  def test_contains_only_one_line_correct_type(self, mods):
    assert isinstance(contains_only_one_line(mods), bool)

  @given(configurations())
  def test_contains_only_one_line_always_same_answer(self, mods):
    assert contains_only_one_line(mods) == contains_only_one_line(mods)

  @given(proper_configurations())
  def test_proper_configurations_always_create_connected_configurations(self, mods):
    assert contains_only_one_line(mods)

  @given(proper_configurations())
  def test_get_paths_correct_type(self, mods):
    paths = get_paths(mods, mods[0], [[mods[0]]])
    assert isinstance(paths, list)
    for path in paths:
      assert isinstance(path, list)
      assert isinstance(path[0], int) or isinstance(path[0], Module)
      for module in path[1:]:
        assert isinstance(module, Module)

  def test_create_dependencies(self):
    pass

  def test_is_placeable(self):
    pass

  def test_is_valid(self):
    pass
