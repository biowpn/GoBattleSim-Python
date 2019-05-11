
import gobattlesim.interface as gbs


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
    num_players=2
)

print("Machamp duo T4 Tyranitar:")
print(result)



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
