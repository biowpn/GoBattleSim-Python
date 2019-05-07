
from gobattlesim.engine import *


###########################################################################
#          In this demo, we will be simulating a T4 Tyranitar Duo         #
###########################################################################


# Set some parameters for game master
# The number of types (only three types are concerned in this demo)
set_num_types(3)
# Each type is an index
# In this demo, 0 = Fighting, 1 = Dark, 2 = Rock
# Set the relevant type effectiveness
set_effectiveness(0, 1, 1.6)
set_effectiveness(0, 2, 1.6)
set_effectiveness(1, 0, 1/1.6)
set_effectiveness(2, 0, 1/1.6)


# Define moves
# (Type, Power, Energy, Duration, Damage Window)
move_counter = Move(0, 12, 8, 900, 700)
move_dynamic_punch = Move(0, 90, -50, 2700, 1200)
move_bite = Move(1, 6, 4, 500, 300)
move_stone_edge = Move(2, 100, -100, 2300, 700)

# Define Pokemon
# (Type1, Type2, Attack, Defense, Max HP)
# Here we use L40 perfect Machamp.
# The three core stats have been calculated beforehand.
pokemon_machamp = Pokemon(0, -1, 196.78470249, 136.72190173, 174)
pokemon_machamp.add_fmove(move_counter)
pokemon_machamp.add_cmove(move_dynamic_punch)

pokemon_tyranitar = Pokemon(1, 2, 210.14000570774078, 175.3800047636032, 9000)
pokemon_tyranitar.add_fmove(move_bite)
pokemon_tyranitar.add_cmove(move_stone_edge)

# Define party
attacker_party = Party()
for _ in range(6):
    attacker_party.add(pokemon_machamp)

raid_boss_party = Party()
raid_boss_party.add(pokemon_tyranitar)

# Define player
attacker = Player()
attacker.set_team(1)
attacker.add(attacker_party)

# Use built-in strategy
attacker.set_strategy(STRATEGY_ATTACKER_NO_DODGE)
#attacker.set_strategy(STRATEGY_ATTACKER_DODGE_CHARGED)
#attacker.set_strategy(STRATEGY_ATTACKER_DODGE_ALL)

# Use custom strategy. Juicy!
# The my_on_free callback is called when the subject Pokemon is free.
# Return specs of an Action as tuple (type, delay, value)
def my_on_free(strategy_input):
    # Use fast move only with no delay whenever free
    return atype_Fast, 0, 0

my_strat = Strategy()
my_strat.set_on_free(my_on_free)
#attacker.set_custom_strategy(my_strat)

raid_boss = Player()
raid_boss.set_team(0)
raid_boss.add(raid_boss_party)
raid_boss.set_strategy(STRATEGY_DEFENDER)



# Define battle
battle = Battle()
battle.add(raid_boss)    # Important: Raid boss must be added first (to be indexed 0).
battle.add(attacker)
battle.add(attacker)
battle.set_time_limit(180000)
battle.set_weather(-1)          # Since we didn't define which weather boost which types,
                                # all types are default to be boosted in weather 0.
                                # We set it to -1 to indicate no boost.
battle.set_random_seed(1000)


# Run many simulations
sum_duration, sum_wins, sum_tdo_percent, sum_deaths = 0, 0, 0, 0
NUM_SIMS = 1000
print(f"In {NUM_SIMS} battles:")
for i in range(NUM_SIMS):
    battle.init()   # Important: must init() before every new simulation
    battle.start()
    battle_outcome = battle.get_outcome(1)    # From team 1 (attacker) 's perspective
    sum_duration += battle_outcome.duration
    sum_wins += 1 if battle_outcome.win else 0
    sum_tdo_percent += battle_outcome.tdo_percent
    sum_deaths += battle_outcome.num_deaths
print("Average Duration:", sum_duration / NUM_SIMS)
print("Win rate:", sum_wins / NUM_SIMS)
print("Average TDO%:", sum_tdo_percent / NUM_SIMS)
print("Average #Deaths:", sum_deaths / NUM_SIMS)


