
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


def is_pokemon_specific(pkm):
    '''
    Check if the pokemon is specific (all five core stats and moves specified).
    '''

    core_params = ["poketype1", "poketype2", "attack", "defense", "max_hp"]
    for param in core_params:
        if param not in pkm:
            return False
    if not isinstance(pkm.get("fmove"), dict):
        return False
    if not isinstance(pkm.get("cmove"), dict):
        return False
    if "cmove2" in pkm and not isinstance(pkm.get("cmove2"), dict):
        return False
    return True


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
        

    def handle_request(self, client_req):
        '''
        Handle a client request.

        {client_req} must have the following attributes:
            reqId
            reqType
            reqInput
            
        A response will returned, adding the following attributes to client_req:
            reqOutput
            message
            
        '''

        resp = {
            "reqId": client_req['reqId'],
            "reqType": client_req['reqType'],
            "reqInput": client_req['reqInput']
        }
            
        method_name = "handle_request_" + resp["reqType"]
        if hasattr(self, method_name):
            resp["reqOutput"] = getattr(self, method_name)(resp["reqInput"])
            resp["message"] = "Done"
        else:
            resp["message"] = "Unknown Request Type"

        return resp


    def handle_request_BattleMatrix(self, req_input):
        enum_shields = req_input.get('enumShields', False)

        if 'GameMaster' in req_input:
            game_master = GameMaster()
            game_master.from_json(req_input['GameMaster'])
            game_master.apply()
            del req_input['GameMaster']
        else:
            game_master = GameMaster.CurrentInstance
        pkm_list = []
        for pkm in req_input['pokemonList']:
            if "cmove2" in pkm and str(pkm["cmove2"]).strip() == '':
                del pkm["cmove2"]
            if is_pokemon_specific(pkm):
                pkm_list.append(pkm)
            else:
                pkm_list.extend(game_master.batch_pokemon(pkm))
            
        pkm_list = get_unique_pokemon(pkm_list)
        bm = BattleMatrix([IPokemon(pkm, pvp=True, game_master=game_master) for pkm in pkm_list], enum_shields)
        bm.run()

        return {
            "pokemonList": pkm_list,
            "enumShields": enum_shields,
            "matrix": bm.get()
        }


    def handle_request_Battle(self, req_input):
        if 'GameMaster' in req_input:
            game_master = GameMaster()
            game_master.from_json(req_input['GameMaster'])
            game_master.apply()
            del req_input['GameMaster']
        else:
            game_master = GameMaster.CurrentInstance
        battle = IBattle(req_input, game_master=game_master)
        return battle.run()
    

    def handle_request_QuickRaidBattle(self, req_input):
        if 'GameMaster' in req_input:
            game_master = GameMaster()
            game_master.from_json(req_input['GameMaster'])
            game_master.apply()
            del req_input['GameMaster']
        else:
            game_master = GameMaster.CurrentInstance
        return quick_raid_battle(**req_input, game_master=game_master)
    

    def handle_request_GetGameMaster(self, req_input):
        return GameMaster.CurrentInstance.to_json()



