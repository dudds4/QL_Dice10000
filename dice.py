import numpy as np
import math
from dice_game import DiceGame
from qlplayer import QLPlayer, CircusSelector
from simpleplayer import DiceThresholdPlayer
import os

np.random.seed()
filename = 'trained_player.pkl'
simple_player = DiceThresholdPlayer(1)

if os.path.isfile(filename):
    trained_player = QLPlayer.from_file(filename)
    trained_player.state_converter = lambda x: (int(x[0]/100), x[1], x[2])
else:
    params = {}
    params['df'] = 0.9
    params['state_converter'] = lambda x: (int(x[0]/100), x[1], x[2])
    params['learn_select'] = CircusSelector(bias=200)
    trained_player = QLPlayer(params=params)

    for _ in range(10):
        for i in range(10000):
            DiceGame([trained_player, simple_player], 5000, verbose=False).play()
        trained_player.lr /= 1.414
        trained_player.learn_select.bias /= 1.414

    trained_player.is_learning = False
    trained_player.to_file(filename)

trained_player.is_learning = False

# players = [trained_player, DiceThresholdPlayer(2), simple_player]
players = [DiceThresholdPlayer(1), simple_player]
tags = ['QLPlayer', 'BasePlayer1', 'BasePlayer2']

scores = DiceGame(players, tags=tags, verbose=True).play()

wins = [0] * len(players)
for i in range(1000):
    game = DiceGame(players, 10000, verbose=False)
    scores = game.play()
    winning_player = scores.index(max(scores))
    wins[winning_player] += 1

print(wins)