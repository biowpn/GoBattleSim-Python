
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
# Different from raid battles, the durations are in turns.
move_counter = Move(poketype=1, power=8, energy=7, duration=2)
move_shadow_claw = Move(poketype=3, power=6, energy=8, duration=2)

# Effect: subject (activation chance, my attack change, my defense change, enemy attack change, enemy defense change
move_power_up_punch = Move(poketype=1, power=40, energy=-35, effect=MoveEffect(1, 1))
move_shadow_ball = Move(poketype=3, power=100, energy=-55)
move_dragon_claw = Move(poketype=0, power=50, energy=-35)
move_ancient_power = Move(poketype=4, power=70, energy=-45, effect=MoveEffect(0.1, 2, 2))

# Define Pokemon
# The three core stats have been calculated beforehand.
pokemon_lucario = PvPPokemon(poketype1=1, poketype2=2, attack=190.39096, defense=121.08865056, max_hp=142)
pokemon_lucario.fmove = move_counter
pokemon_lucario.cmoves = [move_power_up_punch]
# Use built-in PvP Strategy
pokemon_lucario.pvp_strategy = PVP_STRATEGY_BASIC_0_SHIELD
# PvP attack multiplier
pokemon_lucario.attack_multiplier = 1.3

pokemon_giratina = PvPPokemon(poketype1=0, poketype2=3, attack=137.59531384, defense=162.11725095999998, max_hp=203)
pokemon_giratina.fmove = move_shadow_claw
pokemon_giratina.cmoves = [move_dragon_claw, move_ancient_power]
pokemon_giratina.pvp_strategy = PVP_STRATEGY_BASIC_0_SHIELD
pokemon_giratina.attack_multiplier = 1.3


# Since this is a SimplePvPBattle, we don't need to define party or player, just define the battle
battle = SimplePvPBattle(pokemon_lucario, pokemon_giratina)

battle.init()
battle.start()
outcome = battle.get_outcome()

print("Lucario TDO%:", outcome.tdo_percent[0])
print("Giratina TDO%:", outcome.tdo_percent[1])


