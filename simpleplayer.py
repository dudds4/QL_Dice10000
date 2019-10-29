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

    def receiveReward(self, state, reward, next_state):
        pass