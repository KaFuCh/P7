from unittest import TestCase
from hypothesis import given, assume, settings, strategies as st
from Experiments.configuration import Module
from Experiments.configuration import Configuration


@st.composite
def modules(draw):
  m_id = draw(st.integers(min_value=1))
  w_id = draw(st.integers())
  p_time = draw(st.integers())
  t_time = draw(st.integers())
  c_rate = draw(st.integers(min_value=0))
  cons = draw(st.lists(st.integers(), max_size=4))
  return Module(m_id, w_id, p_time, t_time, c_rate, cons)


@st.composite
def configurations(draw, min_num_of_modules=0):
  mods = draw(st.lists(modules()))
  assume(len(mods) >= min_num_of_modules)
  return Configuration(mods)


@st.composite  # TODO Generate connected configurations
def proper_configurations(draw, num_of_modules):
  mods = []
  for i in range(1, num_of_modules+1):
    m_id = i
    w_type = draw(st.integers())
    p_time = draw(st.integers())
    t_time = draw(st.integers())
    c_rate = draw(st.integers())
    cons = draw(st.lists(st.integers(min_value=i, max_value=num_of_modules).filter(lambda x: x != i),
                         max_size=4, unique=True))
    mods.append(Module(m_id, w_type, p_time, t_time, c_rate, cons))
  return Configuration(mods)


class TestModule(TestCase):
  @given(modules())
  def test_get_connections_correct_length(self, mod):
    assert mod.num_of_connections == len(mod.get_connections())
    assert mod.num_of_connections == len(mod.connections)

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
  def test_contains_only_one_line_correct_type(self, conf):
    assert isinstance(conf.contains_only_one_line(), bool)

  @given(configurations())
  def test_contains_only_one_line_always_same_answer(self, conf):
    assert conf.contains_only_one_line() == conf.contains_only_one_line()

  @given(proper_configurations(num_of_modules=3))
  def test_get_paths_correct_type(self, conf):
    print("start\n" + str(proper_configurations(3).example()))
    paths = conf.get_paths(conf.modules[0], [[conf.modules[0]]])
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
