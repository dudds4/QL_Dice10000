import numpy as np
import pickle

class QLPlayer():
    def __init__(self, params=None, verbose=False):
        self.qtable = np.zeros((1,7,2))
        self.lr = params['lr'] if (not params is None) and 'lr' in params else 0.2
        self.er = params['er'] if (not params is None) and 'er' in params else 0.1
        self.df = params['df'] if (not params is None) and 'df' in params else 0.1
        self.state_converter = params['state_converter'] if (not params is None) and 'state_converter' in params else (lambda x: x)
        self.learn_select = params['learn_select'] if (not params is None) and 'learn_select' in params else QLPlayer.select_max  
        self.verbose = verbose
        self.is_learning = True

    @staticmethod
    def select_max(q_value_list):
        return max(q_value_list, key=lambda x:x[1])

    def debug(self, obj):
        if(self.verbose):
            print(obj) 

    def get_qvalue(self, state_action):
        self.ensure_qtable_size(state_action)
        points, dice, rolling = state_action
        return self.qtable[points,dice,int(rolling)]

    def set_qvalue(self, state_action, value):
        self.ensure_qtable_size(state_action)
        points, dice, rolling = state_action
        self.qtable[points,dice,int(rolling)] = value

    def ensure_qtable_size(self, state):
        i, j, rolling = state
        n_rows = i + 1 - self.qtable.shape[0]
        if n_rows > 0:
            segment = np.repeat(self.qtable[[-1],:,:], n_rows, axis=0)
            self.qtable = np.concatenate([self.qtable, segment], axis=0)

    def select_state(self, states):

        # if we are learning, we may choose to do random exploration
        if self.is_learning and np.random.uniform() < self.er:
                idx = np.random.randint(len(states))
                self.debug('Player plays randomly...')
        # otherwise we need to compute the q values
        # and apply either the learning selection function, 
        else:
            q_values = [(i, self.get_qvalue(self.state_converter(state))) for i,state in enumerate(states)]
            idx, q_value = self.learn_select(q_values) if self.is_learning else QLPlayer.select_max(q_values)

        return states[idx]

    def receive_reward(self, state, reward, new_state):
        if not self.is_learning:
            return

        state = self.state_converter(state)
        oldVal = self.get_qvalue(state)

        pts, dice, _ = self.state_converter(new_state)
        self.ensure_qtable_size((pts, dice, False))
        future_val = np.amax( self.qtable[pts,dice,:] ) if state[2] else self.qtable[pts,dice,0]
        newVal = (1 - self.lr) * oldVal + self.lr * (reward + self.df * future_val)
        self.set_qvalue(state, newVal)

    @staticmethod
    def from_file(filename):
        with open(filename, 'rb') as fin:
            x = pickle.load(fin)
        x.learn_select = QLPlayer.select_max
        return x

    def to_file(self, filename):
        temp1 = self.state_converter
        temp2 = self.learn_select
        self.state_converter = None
        self.learn_select = None
        with open(filename, 'wb') as fout:
            pickle.dump(self, fout, pickle.HIGHEST_PROTOCOL)
        self.state_converter = temp1
        self.learn_select = temp2

class CircusSelector():
    def __init__ (self, bias=1, key=lambda x: x[1]):
        self.bias=bias
        self.key=key

    def __call__(self, choices):
        ordered_choices = sorted(choices, key=self.key, reverse=True)
        bias = self.bias + (1-min(ordered_choices, key=self.key)[1])
        total_qvalue = sum(self.key(x) for x in ordered_choices) + bias * len(ordered_choices)
        cutOff = np.random.randint(0,total_qvalue)

        runningTotal = 0
        for choice in ordered_choices:
            runningTotal += self.key(choice) + bias
            if runningTotal > cutOff:
                return choice

        return ordered_choices[-1]