
'''
Handles client request and return with output.
'''

from .interface import *


def set_default_game_master(game_master):
    if isinstance(game_master, str):
        GameMaster(game_master).apply()
    elif isinstance(game_master, dict):
        gm = GameMaster()
        gm.from_json(game_master)
        gm.apply()
    elif isinstance(game_master, GameMaster):
        game_master.apply()
    else:
        raise TypeError("For game_master: Expected str or dict or GameMaster, got {}".format(type(game_master)))


def get_unique_pokemon(pkm_list):
    '''
    Return a unqiue list of Pokemon.
    '''
    unique_pkm_list = []
    for pkm in pkm_list:
        unique = True
        for pkm2 in unique_pkm_list:
            if set([pkm['cmove'], pkm.get('cmove2')]) == set([pkm2['cmove'], pkm2.get('cmove2')]):
                unique = any([v != pkm2.get(k) for k, v in pkm.items() if k != 'cmove' and k!= 'cmove2'])
        if unique:
            unique_pkm_list.append(pkm)
    return unique_pkm_list
        


class RequestHandler:

    def __init__(self):
        pass
        

    def handle_request(self, req):
        '''
        Handle a client request.

        {req} must have the following attributes:
            reqId
            reqType
            reqInput
            
        A response will returned, withg the following attributes:
            reqId
            reqType
            reqOutput
        '''

        resp = {
            "reqId": req["reqId"],
            "reqType": req["reqType"],
            "reqOutput": {}
        }

        if "GameMasterSupplement" in req["reqInput"]:
            GameMaster.CurrentInstance.from_json_join(req["reqInput"].pop("GameMasterSupplement"))
        elif "GameMaster" in req["reqInput"]:
            GameMaster.CurrentInstance.from_json(req["reqInput"].pop("GameMaster"))
            
        method_name = "handle_request_" + req["reqType"]
        if hasattr(self, method_name):
            resp["reqOutput"] = getattr(self, method_name)(req["reqInput"])
        else:
            raise Exception("Unknown Request Type: {}".format(req["reqType"]))

        return resp


    def handle_request_BattleMatrix(self, req_input):
        enum_shields = req_input.get('enumShields', False)

        row_pkm = []
        for pkm in req_input['rowPokemon']:
            if "cmove2" in pkm and str(pkm["cmove2"]).strip() == '':
                del pkm["cmove2"]
            row_pkm.extend(GameMaster.CurrentInstance.batch_pokemon(pkm))
            
        col_pkm = []
        for pkm in req_input['colPokemon']:
            if "cmove2" in pkm and str(pkm["cmove2"]).strip() == '':
                del pkm["cmove2"]
            col_pkm.extend(GameMaster.CurrentInstance.batch_pokemon(pkm))
            
        row_pkm = get_unique_pokemon(row_pkm)
        col_pkm = get_unique_pokemon(col_pkm)
        row_ipkm = [IPokemon(**pkm, pvp=True) for pkm in row_pkm]
        col_ipkm = [IPokemon(**pkm, pvp=True) for pkm in col_pkm]
        if len(col_ipkm) == 0:
            col_ipkm = row_ipkm
            col_pkm = row_pkm
        
        battle_matrix = BattleMatrix(row_ipkm, col_ipkm, enum_shields)
        battle_matrix.run()
        matrix = battle_matrix.get()

        rowOptimalStrategy = ""
        colOptimalStrategy = ""
        if len(row_ipkm) * len(col_ipkm) <= 16384:
            try:
                from GameSolver import Game
            except ImportError:
                rowOptimalStrategy = "GameSolver library not found"
            else:
                game = Game(matrix)
                game.solve()
                rowOptimalStrategy = game.get_solution(True)
                colOptimalStrategy = game.get_solution(False)
        else:
            rowOptimalStrategy = "Matrix too large. Skipped game solving"

        return {
            "rowPokemon": row_pkm,
            "colPokemon": col_pkm,
            "matrix": matrix,
            "rowOptimalStrategy": rowOptimalStrategy,
            "colOptimalStrategy": colOptimalStrategy
        }


    def handle_request_Battle(self, req_input):
        battle = IBattle(**req_input)
        return battle.run()
    

    def handle_request_QuickRaidBattle(self, req_input):
        return quick_raid_battle(**req_input)
    

    def handle_request_GetGameMaster(self, req_input):
        return GameMaster.CurrentInstance.to_json()



