def ve_msg(m1, m2):
    return 'Can not connect ' + str(m1.__class__) + " to " + str(m2.__class__)

def re_msg(m, attr):
    return 'The attribute ' + attr + ' is not available in ' + str(m.__class__)


class FestoModule:
    """
    """
    def __init__(self, right, up, down, id, w_type, p_time, t_time, c_rate):
        self.right = right
        self.up = up
        self.down = down
        self.id = id
        self.w_type = w_type
        self.p_time = p_time
        self.t_time = t_time
        self.c_rate = c_rate

        self.in_avail_dict = {'L': False, 'U': False, 'D': False}

    def get_conn_out(self):
        return {'R': self._right, 'U': self._up, 'D': self._down}

    def set_conn_out(self, conn_out_dict):
        self._right = conn_out_dict['R']
        self._up = conn_out_dict['U']
        self._down = conn_out_dict['D']

    @staticmethod
    def check_if_can_connect(module, direction):
        if not module:
            return True
        else:
            return module.in_avail_dict[direction]

    # right Property
    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, right):
        if self.check_if_can_connect(right, 'L'):
            self._right = right
        else:
            raise ValueError(ve_msg(self, right))

    @property
    def up(self):
        return self._up

    @up.setter
    def up(self, up):
        if self.check_if_can_connect(up, 'U'):
            self._up = up
        else:
            raise ValueError(ve_msg(self, up))

    # down Property
    @property
    def down(self):
        return self._down

    @down.setter
    def down(self, down):
        if self.check_if_can_connect(down, 'D'):
            self._down = down
        else:
            raise ValueError(ve_msg(self, down))

    def __repr__(self):
        s = str(self.__class__)
        s += '\n    id: ' + str(self.id)
        s += '\n    right -> ' + str(self.__get_module_id(self.right))
        s += '\n    up    -> ' + str(self.__get_module_id(self.up))
        s += '\n    down  -> ' + str(self.__get_module_id(self.down))
        return s

    @staticmethod
    def __get_module_id(module):
        if module:
            return module.id
        else:
            return None


class WorkModule(FestoModule):
    """
    """
    def __init__(self, right, up, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, up, None, id, w_type, p_time, t_time, c_rate)

    @FestoModule.down.getter
    def down(self):
        raise RuntimeError(re_msg(self, 'down'))

    @FestoModule.down.setter
    def down(self, down):
        raise RuntimeError(re_msg(self, 'down'))




class SplitterModule(FestoModule):
    """
    """
    def __init__(self, right, up, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, up, down, id, w_type, p_time, t_time, c_rate)


class A0Module(WorkModule):
    """
    """
    def __init__(self, right, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': False, 'D': False}

    @FestoModule.up.getter
    def up(self):
        raise RuntimeError(re_msg(self, 'up'))

    @FestoModule.up.setter
    def up(self, up):
        raise RuntimeError(re_msg(self, 'up'))




class A1Module(WorkModule):
    """
    """
    def __init__(self, up, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': False, 'D': False}


class A2Module(WorkModule):
    """
    """
    def __init__(self, right, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': False, 'U': True, 'D': False}


class A3Module(WorkModule):
    """
    """
    def __init__(self, up, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': False, 'U': True, 'D': False}


class A4Module(WorkModule):
    """
    """
    def __init__(self, right, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': True, 'D': False}


class A5Module(WorkModule):
    """
    """
    def __init__(self, up, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': True, 'D': False}


class U0I0Module(SplitterModule):
    """
    """
    def __init__(self, right, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': False, 'D': True}


class U0I1Module(SplitterModule):
    """
    """
    def __init__(self, up, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': False, 'D': True}


class U1I0Module(SplitterModule):
    """
    """
    def __init__(self, right, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': False, 'U': True, 'D': True}


class U1I1Module(SplitterModule):
    """
    """
    def __init__(self, up, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': False, 'U': True, 'D': True}


class U2I0Module(SplitterModule):
    """
    """
    def __init__(self, right, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(right, None, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': True, 'D': True}


class U2I1Module(SplitterModule):
    """
    """
    def __init__(self, up, down, id, w_type, p_time, t_time, c_rate):
        super().__init__(None, up, down, id, w_type, p_time, t_time, c_rate)
        self.in_avail_dict = {'L': True, 'U': True, 'D': True}



