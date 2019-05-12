
from gobattlesim.application import GoBattleSimApp


app = GoBattleSimApp()
app.bind_game_master("data/GAME_MASTER.json")


sample_request_1 = {
    'reqId': 0,
    'reqType': "BattleMatrix",
    'reqInput': {
        "pokemonList": [
          {
            "name": "(fighting, psychic, dark) & !legendary & !mythical",
            "fmove": "*",
            "cmove": "*",
            "cmove2": "*",
            "cp": 1500
          }
        ],
        "enumShields": False
    }
}

sample_request_2 = {
    'reqId': 1,
    'reqType': "QuickRaidBattle",
    'reqInput': {
        "attacker": {
            "name": "rayquaza",
            "fmove": "dragon tail",
            "cmove": "outrage"
        },
        "boss": {
            "name": "giratina origin",
            "fmove": "shadow claw",
            "cmove": "shadow ball",
            "tier": 5
        },
        "num_players": 2,
        "rejoin": True,
        "num_sims": 10000
    }
}



resp = app.handle_request(sample_request_2)


print("reqInput:")
print(resp['reqInput'])
print()

print("reqOutput:")
print(resp['reqOutput'])



