
from gobattlesim.engine import *


###########################################################################
#          In this demo, we will be simulating a T4 Tyranitar Duo         #
###########################################################################


# Set random seed first
set_random_seed(1000)


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
move_counter = Move(poketype=0, power=12, energy=8, duration=900, dws=700)
move_dynamic_punch = Move(poketype=0, power=90, energy=-50, duration=2700, dws=1200)
move_bite = Move(poketype=1, power=6, energy=4, duration=500, dws=300)
move_stone_edge = Move(poketype=2, power=100, energy=-100, duration=2300, dws=700)

# Define Pokemon
# Here we use L40 perfect Machamp.
# The three core stats have been calculated beforehand.
pokemon_machamp = Pokemon(poketype1=0, attack=196.78470249, defense=136.72190173, max_hp=174)
pokemon_machamp.fmove = move_counter
pokemon_machamp.cmove = move_dynamic_punch

pokemon_tyranitar = Pokemon(poketype1=1, poketype2=2, attack=210.14000570774078, defense=175.3800047636032, max_hp=9000)
pokemon_tyranitar.fmove = move_bite
pokemon_tyranitar.cmove = move_stone_edge

# Define party
attacker_party = Party(pokemon=[pokemon_machamp]*6)

raid_boss_party = Party(pokemon=[pokemon_tyranitar])


# Define player
attacker = Player(
    parties=[attacker_party],
    team = 1
)


# Use built-in strategy
attacker.strategy = STRATEGY_ATTACKER_NO_DODGE
#attacker.strategy = STRATEGY_ATTACKER_DODGE_CHARGED
#attacker.strategy = STRATEGY_ATTACKER_DODGE_ALL

# Use custom strategy. Juicy!
# The on_free callback is called when the subject Pokemon is free. It should return an Action object.
def burst_charged_on_free(state):
    # This is "Bursting" Charged Move strategy - use Charged Moves in a row after energy is full
    if state.subject.energy + state.subject.cmove.energy >= 0:
        # Has enough energy to use a Charged Move. But should it?
        if state.subject.energy == 100 or state.subject_action.type == atype_Charged:
            # If energy is full, or current action is a Charged Move (in bursting), use it
            return Action(atype_Charged)
    return Action(atype_Fast)

# Note: Custom strategy has significant performance cost.
#attacker.strategy = Strategy(on_free=burst_charged_on_free)


raid_boss = Player()
raid_boss.parties = [raid_boss_party]
# Important: Raid Boss must be team 0
raid_boss.team = 0
# Defender strategy
raid_boss.strategy = STRATEGY_DEFENDER



# Define battle
battle = Battle()
battle.players = [raid_boss, attacker, attacker]
battle.time_limit = 180000
battle.weather = -1             # Since we didn't define which weather boost which types,
                                # all types are default to be boosted in weather 0.
                                # We set it to -1 to indicate no boost.



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


