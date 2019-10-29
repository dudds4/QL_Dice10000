from dice_utils import *
from dice_combos import get_checkers

global_cache = {}
global_cache['123456'] = [(1000, [], [1,2,3,4,5,6])] # cache a straight
checkers = get_checkers()

def rollDice(n: int):
    """Rolls n 6-sided dice, and returns the integer values as a sorted numpy array"""
    return sorted(np.random.randint(1,7,n))

def cache_get(dice_list):
    """Turns the given dice list into a key for the cache, and looks up the value in the cache
        
        function expects dice_list to be sorted already
        returns None if item is not cached
    """
    key = "".join([str(d) for d in dice_list])
    if key in global_cache:
        return global_cache[key]
    return None

def cache_put(dice_list, combos):
    """Turns the given dice list into a key for the cache, and sets cache[key] = combos
        
        function expects dice_list to be sorted already
    """    
    key = "".join([str(d) for d in dice_list])
    global_cache[key] = combos

def analyzeRoll(roll):
    """ Identifies all possible options available from the given roll. Returns a list of tuples (points, dice used, dice remaining).

        ie: If a player rolls [1,2,2,2,4,5], they have a number of legal choices
                1) select 1 -> 100 and continue rolling the 5 remaining dice
                2) select 2,2,2 -> 200 and continue rolling the 3 remaining dice
                3) select 5 -> 50 and continue rolling the remaining 5 dice
                4) select 1,2,2,2 -> 300 ...
                5) select 1,5 -> 150 ...
                6) select 2,2,2,5 -> 250 ...
                7) select 1,2,2,2,5, -> 350 ...

        Note that in some cases the options may be mutually exclusive with one another,
        so combining options is not always possible.
    """


    roll = sorted(roll)
    num_dice = len(roll)

    cached = cache_get(roll)
    if cached is not None:
        return cached

    first_order = [check(roll) for check in checkers]
    first_order = [augment(f, roll) for f in first_order if f is not None]

    second_order = []
    for i in range(len(first_order)):
        for j in range(i+1, len(first_order)):
            op1 = first_order[i]
            op2 = first_order[j]

            if not_mutually_exclusive(op1, op2):
                second_order.append(combine(op1, op2))

    n_order = first_order
    n1_order = second_order

    while(len(n1_order) > 0):
        n2_order = [combine(op1, op2) for op1,op2 in zip(n_order, n1_order) if not_mutually_exclusive(op1,op2)]
        n_order = n_order + n1_order
        n1_order = n2_order

    cache_put(roll, n_order)
    return n_order

def analysis_to_options(analyzed_roll, point_total):
    """ Converts the output of the analysis function to game states, returns a list of game state tuples (points, num dice, rolling)
    """
    options = [(roll[0] + point_total, 6 if len(roll[1]) == 0 else len(roll[1])) for roll in analyzed_roll]
    return [(op[0], op[1], True) for op in options] + [(op[0], op[1], False) for op in options]

class DiceGame():
    """ A monster class that basically plays out an entire game, and also doles out intermediate rewards to the players.

        The meat of this class is the .play() method, everything else is basically helper functions for updating
        internal state, and printing, in an effort to make .play() less painful.
    """
    def __init__(self, players, goal_score=5000, tags=None, verbose=True):
        assert(len(players) >= 2)

        self.players = players
        self.goal_score = goal_score
        self.tags = ['Player {}'.format(i+1) for i in range(len(players))] if tags is None else tags
        self.scores = [0] * len(players)
        self.turn_counter = 0
        self.base_state = (0, 6, True)
        self.turn_state = self.base_state
        self.player_idx = 0
        self.next_player_idx = 1
        self.factor = 10
        self.verbose = verbose

    def debug(self, obj):
        if(self.verbose):
            print(obj)

    def is_game_over(self):
        return max(self.scores) >= self.goal_score
    
    def winning_player(self):
        return self.scores.index(max(self.scores))

    def getRoller(self):
        return self.players[self.player_idx], self.tags[self.player_idx]

    def getStealer(self):
        return self.players[self.next_player_idx], self.tags[self.next_player_idx]

    def advance_turns(self, points, next_state):
        """Awards points to the current player, then goes to the next player's turn, setting initial state=next_state"""
        self.scores[self.player_idx] += points
        self.player_idx = (self.player_idx + 1) % len(self.players)
        self.next_player_idx = (self.next_player_idx + 1) % len(self.players)
        self.turn_state = next_state
        self.turn_counter += 1

    def print_turn_start(self):
        """Convenience function for printing things at the beginning of a turn"""
        player_tag = self.tags[self.player_idx]
        scores_string = (', '.join([tag + ': ' + str(score) for tag,score in zip(self.tags, self.scores)]))
        self.debug('Turn {}'.format(self.turn_counter + 1) + ' ------------\t\t\t ' + scores_string)
        if self.turn_state != self.base_state:
            self.debug('{} rolling with {} pts, {} dice'.format(player_tag, self.turn_state[0], self.turn_state[1]))
        else:
            self.debug('{} starts'.format(player_tag))        

    def roll(self, state, idx, is_stealing=False):
        """Rolls some dice, generates options, and does printing based on the results"""
        player_roll = rollDice(state[1])
        analysis = analyzeRoll(player_roll)
        options = analysis_to_options(analysis, state[0])
        tag = self.tags[idx]

        if len(options) > 0:
            format_str = '\t{} rolled {}' if not is_stealing else '\t{} successfully stole ({}).'
        else:
            format_str = '\t{} failed to roll combinations ({})' if not is_stealing else '\t{} failed to steal ({})'

        self.debug(format_str.format(tag, player_roll))
        return options

    def select(self, options, idx, is_stealing=False):
        """Asks a player to select an option, and does printing based on the results"""
        selected_state = self.players[idx].select_state(options)
        if not is_stealing:
            assert(selected_state in options)
            option_str = '{} pts, {} dice, {}'.format(selected_state[0], selected_state[1], 'and rolling...' if selected_state[2] else 'stopped.')
            self.debug('\t{} chose option: {}'.format(self.tags[idx], option_str))
        elif selected_state != self.base_state:
            self.debug('\t{} chose to steal!'.format(self.tags[idx]))
        else:
            self.debug('\t{} chose not to steal.'.format(self.tags[idx]))

        return selected_state

    def roll_until_done(self, p_idx, tstate):
        """Has player at p_idx roll until it either chooses to stop rolling, or fails to roll an option
        
           this function has no side-effects """
        failed = False
        while tstate[2] and (not failed):
            options = self.roll(tstate, p_idx)
            failed = len(options) == 0
            if not failed:
                selected_state = self.select(options, p_idx)
                if selected_state[2]:
                    self.players[p_idx].receive_reward(tstate, tstate[0] / self.factor, selected_state)
                tstate = selected_state

        return failed, tstate

    def play(self):

        while(not self.is_game_over()):
            self.print_turn_start()
            player, player_tag = self.getRoller()

            # player rolls until it fails, or chooses to stop
            failed, self.turn_state = self.roll_until_done(self.player_idx, self.turn_state)

            # if the player failed to roll anything, we give it negative reward, and move on to the next turn
            if failed:      
                player.receive_reward(self.turn_state, -self.turn_state[0] / self.factor, (0,0,0))
                self.advance_turns(0, self.base_state)
                continue

            # if the player didn't fail, the next player gets to choose whether to steal
            stealer, stealer_tag = self.getStealer()
            stealable_state = (self.turn_state[0], self.turn_state[1], True)
            chose_to_steal = self.select([stealable_state, self.base_state], self.next_player_idx, True) == stealable_state
            
            # if next player chooses not to steal, we award the current player points, and move on to the next turn 
            if not chose_to_steal:
                player.receive_reward(self.turn_state, self.turn_state[0], self.base_state)
                self.advance_turns(self.turn_state[0], self.base_state)
            # if the player does choose to steal, it has to roll and hope it rolls some options
            else:
                options = self.roll(self.turn_state, self.next_player_idx, True)
                successful_steal = len(options) > 0
                stealer_state = stealer.select_state(options) if successful_steal else self.base_state

                player.receive_reward(self.turn_state, 0 if successful_steal else self.turn_state[0], self.base_state)
                stealer.receive_reward(stealable_state,  stealable_state[0] / self.factor if successful_steal else 0, stealer_state)

                # on a successful steal, the next player gets to continue with the current pot
                if(successful_steal):
                    self.advance_turns(0, stealer_state)
                # on an unsuccessful steal, the next player has its turn skipped
                else:
                    self.advance_turns(self.turn_state[0], self.base_state)
                    self.advance_turns(0, self.base_state)

        winning_player = self.scores.index(max(self.scores))
        self.debug('{} won!'.format(self.tags[winning_player]))

        return self.scores
