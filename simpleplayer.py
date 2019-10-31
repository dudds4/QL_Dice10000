class DiceThresholdPlayer():
    """ A player that decides whether to continue rolling based on how many dice are left.

        Player always chooses the option with the maximum number of points.
        When stealing, it will only steal if the # of dice available is greater than its threshold
    """
    def __init__(self, M: int):
        self.m = M
    def select_state(self, states):
        x = ((i, state[0]) for i, state in enumerate(states))
        idx = sorted(x, key=lambda pr: pr[1])[-1][0]
        points, num_dice,_ = states[idx]
        keeps_rolling = num_dice > self.m
        return points, num_dice, keeps_rolling

    def receive_reward(self, state, reward, next_state):
        pass

class GenericMaxPlayer():
    def __init__(self, Foo):
        self.foo = Foo
    def select_state(self, states):
        x = [(i, state[0]) for i, state in enumerate(states)]
        idx = x.index(max(x, key=lambda pr: pr[1]))
        points, num_dice,_ = states[idx]
        keepsRolling = self.foo(points, num_dice)
        return points, num_dice, keepsRolling

    def receive_reward(self, state, reward, next_state):
        pass

class HumanPlayer():

    def __init__(self):
        self.x = 1

    def select_state(self, states):
        idx = -1
        is_steal = len(states) == 2 and states[1] == (0,6,True)
        
        while type(idx) != int or idx < 0 or idx >= len(states):

            if is_steal:
                print('\t\tYou have the option to steal or leave the {} pot with {} dice'.format(states[0][0], states[0][1]))
                print('\t\tDo you want to steal [0] or leave [1]?')
            else:            
                print('\t\tSelect a choice...')
                for i, s in enumerate(states):
                    rollstr = 'still rolling' if s[2] else 'stop rolling'
                    print('\t\t[{}]: {} points, {} dice left, and {}'.format(i, s[0], s[1], rollstr))

            try:
                idx = int(input('\t\tType in the choice id for your selection (then enter): ')) 
            except ValueError:
                idx = -1

        return states[idx]

    def receive_reward(self, state, reward, next_state):
        pass