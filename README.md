# QL_Dice10000

This project applies q-learning, a type of reinforcement learning, to the dice 10,000 game. You can try playing against the currently generated player by cloning the repository, and running tryme.py (you will need numpy installed). The player is certainly not perfect (yet) but it does learn to play the game pretty well.

## The Game

Dice 10,000 is a fun board-game-esque game that requires very little equipment; only 6 dice. 

The basic premise of the game is this: 

 - at the start of a players turn; they have 6 dice, and 0 points in the pot
 - the player rolls the dice, and the resulting roll potentially has some number of combinations
   - combinations include things like triple's of one number, or a straight 1,2,3,4,5,6
 - if there are no combinations in the roll, the player loses the pot, and the next player's turn starts
 - otherwise the player can select as many of the combinations rolled as they like, and either 
   - a: roll again with only the remaining dice (rolling no combinations and losing the pot becomes more likely), or
   - b: stopping
 - once a player has chosen to stop, the next player may choose to either steal using the remaining dice, or start from scratch. Therefore, if I choose to stop with 1000 points, and 4 dice left, the next player will surely choose to steal since the odds of a successful steal are quite good. Unsuccessful steals result in loss of turn.
  
For a more complete description of the game, see [it's wikipedia page](https://en.wikipedia.org/wiki/Dice_10000).

## Motivation

While playing this game with some friends, I became very interested in figuring out the optimal strategy. Surely you should be able to think about stopping/stealing/continuing as a simple computation of expected value: value * probability of success. However things become very complicated when multiple actors with different policies become involved. So I decided to apply some basic reinforcement learning to the problem.

## Explanation

The main components of this repo are:

 - numpy used for generating random integers
 - dice_combos.py defines callable objects which check a dice roll to see if there is a legal combination that is worth points
 - dice_game.py defines a DiceGame object which allows players (policies) to play against one another. Additionally contains logic for generating all possible combinations of combinations from a dice roll.
 - qlplayer.py and simpleplayer.py define some objects which implement policies for playing the game.
 - dice.py is a script in which I generate, train, and compare a couple different policies.
 
 ## Results
 
Currently the q-learning player does successfully learn the game, and beats many simple policies. However it's not quite done yet; I'm not satisfied since it can still be beaten by at least one basic policy. Many decisions were made along the way to constrain the problem and the q-learner, since this particular game does not lend well to run-of-the-mill q-learning.
