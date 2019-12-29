
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
# poketype, power, energy, duration, dws
move_confusion = Move(0, 20, 15, 1600, 600)
move_psychic = Move(0, 100, -100, 2800, 1300)
move_counter = Move(1, 12, 8, 900, 700)
move_dynamic_punch = Move(1, 90, -50, 2700, 1200)


# Define Pokemon
# poketype1, poketype2, attack, defense, max_hp
# The three core stats have been calculated beforehand.
pokemon_mewtwo = Pokemon(0, -1, 248.94450315, 155.68910197000002, 180)
pokemon_mewtwo.fmove = move_confusion
pokemon_mewtwo.cmove = move_psychic

pokemon_machamp = Pokemon(1, -1, 181.7700047492981, 127.02000331878662, 3600)
pokemon_machamp.fmove = move_counter
pokemon_machamp.cmove = move_dynamic_punch


# Define party
attacker_party = Party()
attacker_party.add(pokemon_mewtwo)

raid_boss_party = Party()
raid_boss_party.add(pokemon_machamp)

# Define player
attacker = Player()
attacker.add(attacker_party)
# Attacker is team 1
attacker.team = 1
# Use built-in strategy
attacker.strategy = STRATEGY_ATTACKER_DODGE_ALL

raid_boss = Player()
raid_boss.add(raid_boss_party)
# Raid boss must be team 0
raid_boss.team = 0
# Defender strategy
raid_boss.strategy = STRATEGY_DEFENDER


# Define battle
battle = Battle()
battle.add(raid_boss)
battle.add(attacker)

# Time limit unit in miliseconds
battle.time_limit = 180000
# Recall that we define 1 = Windy.
battle.weather = 1

# Run one simulation with battle log
battle.has_log = True
# Important: must init() before every new simulation
battle.init()
battle.start()


print("Time(s)", "Type", "Pokemon", sep='\t')
for entry in battle.get_log():
    print(entry.time / 1000,
          ETYPE_NAMES[entry.type],
          "Mewtwo" if entry.player == 1 else "Machamp",
          sep='\t')


pokemon_mewtwo = battle.players[1].parties[0].pokemon[0]
pokemon_machamp = battle.players[0].parties[0].pokemon[0]

print()
print("The battle lasts", battle.outcome.duration / 1000, "seconds")
print("Mewtwo deals", pokemon_mewtwo.tdo, "damage")
print("When the battle ends, Mewtwo has", pokemon_mewtwo.hp, "HP left")
print("Boss Machamp has", pokemon_machamp.hp, "HP left")
