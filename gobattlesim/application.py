
'''
Handles client request and return with output.
'''

from .interface import *


class GoBattleSimApp:

    
    def __init__(self, client_info=None):
        self.game_master = GameMaster()


    def bind_game_master(self, filepath):
        self.game_master = GameMaster(filepath).apply()
        
    

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
            resp["message"] = "Unknown reqType"

        return resp


    def handle_request_BattleMatrix(self, req_input):
        pokemon_list = req_input['pokemonList']
        enum_shields = req_input.get('enumShields', False)

        pokemon_list_batched = []
        for pkm in pokemon_list:
            if "cmove2" in pkm and str(pkm["cmove2"]).strip() == '':
                del pkm["cmove2"]
            pokemon_list_batched.extend(self.game_master.batch_pokemon(pkm))
        pokemon_list_unique = get_unique_pokemon(pokemon_list_batched)
        
        bm = BattleMatrix([IPokemon(pkm, pvp=True) for pkm in pokemon_list_unique], enum_shields)
        bm.run()

        return {
            "pokemonList": pokemon_list_unique,
            "enumShields": enum_shields,
            "matrix": bm.get()
        }


    def handle_request_Battle(self, req_input):
        battle = IBattle(req_input)
        return battle.run()
    

    def handle_request_QuickRaidBattle(self, req_input):
        return quick_raid_battle(**req_input)
    

    def handle_request_SyncGameMaster(self, req_input):
        return self.game_master.sync(req_input)
    

    def handle_request_OverwriteGameMaster(self, req_input):
        return self.game_master.overwrite(req_input)



def get_unique_pokemon(pkm_list):
    unique_pkm_list = []
    for pkm in pkm_list:
        unique = True
        for pkm2 in unique_pkm_list:
            if set([pkm['cmove'], pkm.get('cmove2')]) == set([pkm2['cmove'], pkm2.get('cmove2')]):
                unique = any([v != pkm2.get(k) for k, v in pkm.items() if k != 'cmove' and k!= 'cmove2'])
        if unique:
            unique_pkm_list.append(pkm)
    return unique_pkm_list



