
from gobattlesim.engine import *


###########################################################################
#        In this demo, we will be simulating a T3 Machamp 1v1 Solo        #
###########################################################################


# First of all, set the random seed, because RNGesus
set_random_seed(1000)

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
move_confusion = Move(poketype=0, power=20, energy=15, duration=1600, dws=600)
move_zen_headbutt = Move(poketype=0, power=12, energy=10, duration=1100, dws=850)
move_psychic = Move(poketype=0, power=100, energy=-100, duration=2800, dws=1300)
move_counter = Move(poketype=1, power=12, energy=8, duration=900, dws=700)
move_bullet_punch = Move(poketype=2, power=9, energy=10, duration=900, dws=300)
move_dynamic_punch = Move(poketype=1, power=90, energy=-50, duration=2700, dws=1200)


# Define Pokemon
# Here we use L40 perfect Mewtwo.
# The three core stats have been calculated beforehand.
pokemon_mewtwo = Pokemon(poketype1=0, attack=248.94450315, defense=155.68910197000002, max_hp=180)
pokemon_mewtwo.fmove = move_confusion
pokemon_mewtwo.cmove = move_psychic

pokemon_latios = Pokemon(poketype1=0, attack=223.65490283000003, defense=179.39810227, max_hp=162)
pokemon_latios.fmove = move_zen_headbutt
pokemon_latios.cmove = move_psychic

pokemon_machamp = Pokemon(poketype1=1, attack=181.7700047492981, defense=127.02000331878662, max_hp=3600)
pokemon_machamp.fmove = move_counter
pokemon_machamp.cmove = move_dynamic_punch


# Define party
attacker_party = Party(pokemon=[pokemon_mewtwo])

raid_boss_party = Party(pokemon=[pokemon_machamp])


# Define player
attacker = Player(parties=[attacker_party])
# Attacker is team 1
attacker.team = 1
# Use built-in strategy
attacker.strategy = STRATEGY_ATTACKER_DODGE_ALL

raid_boss = Player(parties=[raid_boss_party])
# Raid boss must be team 0
raid_boss.team = 0
# Defender strategy
raid_boss.strategy = STRATEGY_DEFENDER


# Define battle
battle = Battle(players=[raid_boss, attacker])

# Time limit unit in miliseconds
battle.time_limit = 180000
# Recall that we define 1 = Windy.
battle.weather = 1

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


