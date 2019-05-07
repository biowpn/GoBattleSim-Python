
from gobattlesim.engine import *


###########################################################################
#        In this demo, we will be simulating a T3 Machamp 1v1 Solo        #
###########################################################################


# Set some parameters for game master
# The number of types (only three types are concerned in this demo)
set_num_types(3)
# Each type is an index
# In this demo, 0 = Psychic, 1 = Fighting, 2 = Steel
# Set the relevant type effectiveness
set_effectiveness(0, 1, 1.6)    
set_effectiveness(0, 2, 1/1.6)
set_effectiveness(1, 0, 1/1.6)
set_effectiveness(1, 2, 1.6)
# Set Psychic (index 0) is boosted in Windy (any weather code, here we use 1)
set_type_boosted_weather(0, 1)


# Define moves
# (Type, Power, Energy, Duration, Damage Window)
move_confusion = Move(0, 20, 15, 1600, 600)
move_zen_headbutt = Move(0, 12, 10, 1100, 850)
move_psychic = Move(0, 100, -100, 2800, 1300)
move_counter = Move(1, 12, 8, 900, 700)
move_bullet_punch = Move(2, 9, 10, 900, 300)
move_dynamic_punch = Move(1, 90, -50, 2700, 1200)


# Define Pokemon
# (Type1, Type2, Attack, Defense, Max HP)
# Here we use L40 perfect Mewtwo.
# The three core stats have been calculated beforehand.
pokemon_mewtwo = Pokemon(0, -1, 248.94450315, 155.68910197000002, 180)
pokemon_mewtwo.add_fmove(move_confusion)
pokemon_mewtwo.add_cmove(move_psychic)

pokemon_latios = Pokemon(0, -1, 223.65490283000003, 179.39810227, 162)
pokemon_latios.add_fmove(move_zen_headbutt)
pokemon_latios.add_cmove(move_psychic)

pokemon_machamp = Pokemon(1, -1, 181.7700047492981, 127.02000331878662, 3600)
pokemon_machamp.add_fmove(move_counter)
pokemon_machamp.add_cmove(move_dynamic_punch)


# Define party
attacker_party = Party()
attacker_party.add(pokemon_mewtwo)

raid_boss_party = Party()
raid_boss_party.add(pokemon_machamp)

# Define player
attacker = Player()
attacker.set_team(1)
attacker.add(attacker_party)
# Use built-in strategy
attacker.set_strategy(STRATEGY_ATTACKER_DODGE_ALL)

raid_boss = Player()
raid_boss.set_team(0)
raid_boss.add(raid_boss_party)
raid_boss.set_strategy(STRATEGY_DEFENDER)



# Define battle
battle = Battle()
battle.add(raid_boss)    # Important: Raid boss must be added first (to be indexed 0).
battle.add(attacker)
battle.set_time_limit(180000)
battle.set_weather(0)           # Recall that we define 1 = Windy.
battle.set_random_seed(1000)


# Run many simulations
sum_duration, sum_wins, sum_tdo_percent, sum_deaths = 0, 0, 0, 0
NUM_SIMS = 1000
print(f"In {NUM_SIMS} battles:")
for i in range(NUM_SIMS):
    battle.init()   # Important: must init() before every new simulation
    battle.start()
    battle_outcome = battle.get_outcome(1)  # From team 1 (attacker) 's perspective
    sum_duration += battle_outcome.duration
    sum_wins += 1 if battle_outcome.win else 0
    sum_tdo_percent += battle_outcome.tdo_percent
    sum_deaths += battle_outcome.num_deaths
print("Average Duration:", sum_duration / NUM_SIMS)
print("Win rate:", sum_wins / NUM_SIMS)
print("Average TDO%:", sum_tdo_percent / NUM_SIMS)
print("Average #Deaths:", sum_deaths / NUM_SIMS)


