
from gobattlesim.engine import *


###########################################################################
# In this demo, we will be simulating Lucario vs Giratina in Ultra league #
###########################################################################



# Set the stage multipliers for attack/defense buff/debuff.
# These values can be found in game master.
set_stage_multipliers([0.5, 0.5714286, 0.66666669, 0.8, 1, 1.25, 1.5, 1.75, 2])


# Set some parameters for game master
# The number of types (only five types are concerned in this demo)
set_num_types(5)
# Each type is an index
# In this demo, 0 = Dragon, 1 = Fighting, 2 = Steel, 3 = Ghost, 4 = Rock
# Set the relevant type effectiveness
set_effectiveness(0, 0, 1.6)
set_effectiveness(0, 2, 1/1.6)
set_effectiveness(1, 2, 1.6)
set_effectiveness(1, 3, 1/1.6/1.6)
set_effectiveness(3, 3, 1.6)
set_effectiveness(4, 1, 1/1.6)
set_effectiveness(4, 2, 1/1.6)


# Define moves
# poketype, power, energy, duration, dws (ununsed for PvP)
# Different from raid battles, the durations are in turns.
move_counter = Move(1, 8, 7, 2)
move_shadow_claw = Move(3, 6, 8, 2)

# Effect: subject (activation chance, my attack change, my defense change, enemy attack change, enemy defense change
move_power_up_punch = Move(1, 40, -35)
move_power_up_punch.effect = MoveEffect(1, 1)

move_shadow_ball = Move(3, 100, -55)
move_dragon_claw = Move(0, 50, -35)

move_ancient_power = Move(4, 70, -45)
move_ancient_power.effect = MoveEffect(0.1, 2, 2)

# Define Pokemon
# poketype1, poketype2, attack, defense, max_hp
# The three core stats have been calculated beforehand.
pokemon_lucario = PvPPokemon(1, 2, 190.39096, 121.08865056, 142)
pokemon_lucario.fmove = move_counter
pokemon_lucario.cmoves = [move_power_up_punch, move_shadow_ball]

pokemon_giratina = PvPPokemon(0, 3, 137.59531384, 162.11725095999998, 203)
pokemon_giratina.fmove = move_shadow_claw
pokemon_giratina.cmoves = [move_dragon_claw, move_ancient_power]


# Since this is a SimplePvPBattle, we don't need to define party or player, just define the battle
battle = SimplePvPBattle(pokemon_lucario, pokemon_giratina)

# Set the number of shields
battle.set_num_shields_max(1, 1)

battle.init()
battle.start()
outcome = battle.get_outcome()

print("Lucario TDO%:", outcome.tdo_percent[0])
print("Giratina TDO%:", outcome.tdo_percent[1])


