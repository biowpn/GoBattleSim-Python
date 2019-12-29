
import gobattlesim.interface as gbs
import json


# Load and apply game master
gbs.GameMaster("data/GAME_MASTER.json").apply()


# Quick raid battle
result = gbs.quick_raid_battle(
    {
        "name": "machamp",
        "fmove": "counter",
        "cmove": "dynamic punch"
    },
    {
        "name": "tyranitar",
        "fmove": "bite",
        "cmove": "crunch",
        "tier": 4
    },
    player_multiplier=2
)

print("Machamp duo T4 Tyranitar:")
print(result)
print()


# Simple PvP Battle
pvp_battle_score = gbs.quick_pvp_battle(
    {
        "name": "lucario",
        "fmove": "counter",
        "cmoves": ["power up punch", "shadow ball"],
        "cp": 2500
    },
    {
        "name": "giratina altered",
        "fmove": "shadow claw",
        "cmoves": ["dragon claw", "ancient power"],
        "cp": 2500
    },
    num_shields=[0, 0]
)

print("Lucario vs Giratina Altered:")
print(pvp_battle_score)
print()


# Battle Matrix

pkm_list = [
    gbs.IPokemon(name="tyranitar", fmove="bite", cmove="crunch",
                 cmove2="fire blast", cp=1500, pvp=True),
    gbs.IPokemon(name="machamp", fmove="counter", cmove="cross chop",
                 cmove2="rock slide", cp=1500, pvp=True),
    gbs.IPokemon(name="lugia", fmove="dragon tail",
                 cmove="sky attack", cmove2="futuresight", cp=1500, pvp=True)
]

matrix = gbs.BattleMatrix(pkm_list, pkm_list, True)
matrix.run()
print(*matrix.get(), sep='\n')
print()
