
from .engine import *


def test_engine_raid_solo():
    set_random_seed(1000)
    set_num_types(3)
    set_effectiveness(0, 1, 1.6)
    set_effectiveness(0, 2, 1/1.6)
    set_effectiveness(1, 0, 1/1.6)
    set_effectiveness(1, 2, 1.6)
    set_type_boosted_weather(0, 1)

    move_confusion = Move(0, 20, 15, 1600, 600)
    move_psychic = Move(0, 100, -100, 2800, 1300)
    move_counter = Move(1, 12, 8, 900, 700)
    move_dynamic_punch = Move(1, 90, -50, 2700, 1200)

    pokemon_mewtwo = Pokemon(0, -1, 248.94450315, 155.68910197000002, 180)
    pokemon_mewtwo.fmove = move_confusion
    pokemon_mewtwo.cmove = move_psychic

    pokemon_machamp = Pokemon(1, -1, 181.7700047492981,
                              127.02000331878662, 3600)
    pokemon_machamp.fmove = move_counter
    pokemon_machamp.cmove = move_dynamic_punch

    attacker_party = Party()
    attacker_party.add(pokemon_mewtwo)
    raid_boss_party = Party()
    raid_boss_party.add(pokemon_machamp)

    attacker = Player()
    attacker.add(attacker_party)
    attacker.team = 1
    attacker.strategy = STRATEGY_ATTACKER_DODGE_ALL

    raid_boss = Player()
    raid_boss.add(raid_boss_party)
    raid_boss.team = 0
    raid_boss.strategy = STRATEGY_DEFENDER

    battle = Battle()
    battle.add(raid_boss)
    battle.add(attacker)

    battle.time_limit = 180000
    battle.weather = 1
    battle.has_log = True
    battle.init()
    battle.start()

    assert(len(battle.get_log()) > 0)

    pokemon_mewtwo = battle.players[1].parties[0].pokemon[0]
    pokemon_machamp = battle.players[0].parties[0].pokemon[0]

    assert(battle.outcome.duration > 0)
    assert(pokemon_mewtwo.tdo > 0)
    assert(pokemon_machamp.tdo > 0)


def test_engine_raid_duo():
    set_random_seed(1000)
    set_num_types(3)
    set_effectiveness(0, 1, 1.6)
    set_effectiveness(0, 2, 1.6)
    set_effectiveness(1, 0, 1/1.6)
    set_effectiveness(2, 0, 1/1.6)

    move_counter = Move(0, 12, 8, 900, 700)
    move_dynamic_punch = Move(0, 90, -50, 2700, 1200)
    move_bite = Move(1, 6, 4, 500, 300)
    move_stone_edge = Move(2, 100, -100, 2300, 700)

    pokemon_machamp = Pokemon(0, -1, 196.78470249, 136.72190173, 174)
    pokemon_machamp.fmove = move_counter
    pokemon_machamp.cmove = move_dynamic_punch

    pokemon_tyranitar = Pokemon(
        1, 2, 210.14000570774078, 175.3800047636032, 9000)
    pokemon_tyranitar.fmove = move_bite
    pokemon_tyranitar.cmove = move_stone_edge

    attacker_party = Party()
    attacker_party.pokemon = [pokemon_machamp]*6
    raid_boss_party = Party()
    raid_boss_party.pokemon = [pokemon_tyranitar]

    attacker = Player()
    attacker.parties = [attacker_party]
    attacker.team = 1
    attacker.strategy = STRATEGY_ATTACKER_DODGE_CHARGED

    raid_boss = Player()
    raid_boss.parties = [raid_boss_party]
    raid_boss.team = 0
    raid_boss.strategy = STRATEGY_DEFENDER

    battle = Battle()
    battle.players = [raid_boss, attacker, attacker]
    battle.time_limit = 180000
    battle.weather = -1

    battle.init()
    battle.start()
    battle.get_outcome(1)


def test_engine_pvp():
    set_stage_multipliers(
        [0.5, 0.5714286, 0.66666669, 0.8, 1, 1.25, 1.5, 1.75, 2])
    set_num_types(5)
    set_effectiveness(0, 0, 1.6)
    set_effectiveness(0, 2, 1/1.6)
    set_effectiveness(1, 2, 1.6)
    set_effectiveness(1, 3, 1/1.6/1.6)
    set_effectiveness(3, 3, 1.6)
    set_effectiveness(4, 1, 1/1.6)
    set_effectiveness(4, 2, 1/1.6)

    move_counter = Move(1, 8, 7, 2)
    move_shadow_claw = Move(3, 6, 8, 2)
    move_power_up_punch = Move(1, 40, -35)
    move_power_up_punch.effect = MoveEffect(1, 1)

    move_shadow_ball = Move(3, 100, -55)
    move_dragon_claw = Move(0, 50, -35)
    move_ancient_power = Move(4, 70, -45)
    move_ancient_power.effect = MoveEffect(0.1, 2, 2)

    pokemon_lucario = PvPPokemon(1, 2, 190.39096, 121.08865056, 142)
    pokemon_lucario.fmove = move_counter
    pokemon_lucario.cmoves = [move_power_up_punch, move_shadow_ball]

    pokemon_giratina = PvPPokemon(0, 3, 137.59531384, 162.11725095999998, 203)
    pokemon_giratina.fmove = move_shadow_claw
    pokemon_giratina.cmoves = [move_dragon_claw, move_ancient_power]

    battle = SimplePvPBattle(pokemon_lucario, pokemon_giratina)
    battle.set_num_shields_max(1, 1)
    battle.init()
    battle.start()
    outcome = battle.get_outcome()

    assert(outcome.tdo_percent[0] > 0)
    assert(outcome.tdo_percent[1] > 0)


def do_test_all():
    num_passed, num_failed = 0, 0
    for name, func in globals().items():
        if name.startswith("test_") and callable(func):
            print(name, "...", end=' ')
            try:
                func()
            except:
                print("failed")
                num_failed += 1
            else:
                print("passed")
                num_passed += 1
    if num_failed == 0:
        print(f"all {num_passed} tests passed")
    else:
        print(f"passed {num_passed} test(s), failed {num_failed} test(s)")


if __name__ == "__main__":
    do_test_all()
