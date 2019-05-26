
'''
The interface module.

This module provides game master file parsing, setting game parameters,
and more convenient battle objects initialization (built on top of engine.py).

'''

import json
import re
import copy
import itertools

from .engine import *


'''
    Classes
'''


class GameMaster:
    '''
    This class stores all the releveant the game data.
    It can also pass the data to gobattlesim.Engine.
    '''

    # The default GameMaster instance
    # It is the last instance that calls apply()
    CurrentInstance = None
    
    PoketypeList = ["normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost",
        "steel", "fire", "water", "grass", "electric", "psychic", "ice", "dragon", "dark", "fairy"]
    InversedPoketypeList = dict([(name, i) for i, name in enumerate(PoketypeList)])

    @staticmethod
    def rm_udrscrs(Str, Category):
        if Category == 'p':
            return ' '.join([s.lower() for s in Str.split('_')][2:])
        elif Category == "fast":
            return ' '.join([s.lower() for s in Str.split('_')[:-1]])
        elif Category == "charged":
            return ' '.join([s.lower() for s in Str.split('_')])
        elif Category == 't':
            return Str.split('_')[-1].lower()


    def __init__(self, file=None):
        '''
        {file} is the filepath to the game master json file.
        '''
        self.clear()
        if file is not None:
            self.feed(file)

    def clear(self):
        '''
        Clear all data.
        '''
        self.Pokemon = []
        self.PvEMoves = []
        self.PvPMoves = []
        self.CPMultipliers = []
        self.WeatherSettings = {}
        self.FriendAttackBonusMultipliers = []
        self.TypeEffectiveness = {}
        self.PvEBattleSettings = {}
        self.PvPBattleSettings = {}
        # Note: for now, raid tiers data are hard coded because they are not in the game master file.
        self.RaidTierSettings = [
            {"name": "1", "cpm": 0.6, "maxHP": 600, "timelimit": 180000},
            {"name": "2", "cpm": 0.67, "maxHP": 1800, "timelimit": 180000},
            {"name": "3", "cpm": 0.7300000190734863, "maxHP": 3600, "timelimit": 180000},
            {"name": "4", "cpm": 0.7900000214576721, "maxHP": 9000, "timelimit": 180000},
            {"name": "5", "cpm": 0.7900000214576721, "maxHP": 15000, "timelimit": 300000},
            {"name": "6", "cpm": 0.7900000214576721,"maxHP": 18750, "timelimit": 3000000}
        ]
        return self


    def from_json_join(self, source):
        '''
        Supply this instance with additional Pokemon and Moves from {source}, a GameMaster-like dict object.
        '''
        for pkm in source.get("Pokemon", []):
            pkm["name"] = pkm.get("name", "")
            if "pokeType1" in pkm:
                pkm["poketype1"] = GameMaster.InversedPoketypeList.get(pkm["pokeType1"], -1)
            if "pokeType2" in pkm:
                pkm["poketype2"] = GameMaster.InversedPoketypeList.get(pkm["pokeType2"], -1)
            try:
                pkm_cur = self.search_pokemon(pkm["name"])
                for k, v in pkm.items():
                    pkm_cur[k] = v
            except:
                self.Pokemon.append(pkm)
        for move in source.get("PvEMoves", []):
            move["name"] = move.get("name", "")
            if "pokeType" in move:
                move["poketype"] = GameMaster.InversedPoketypeList.get(move["pokeType"], -1)
            try:
                move_cur = self.search_pve_move(move["name"])
                for k, v in move.items():
                    move_cur[k] = v
            except:
                self.PvEMoves.append(move)
        for move in source.get("PvPMoves", []):
            move["name"] = move.get("name", "")
            if "pokeType" in move:
                move["poketype"] = GameMaster.InversedPoketypeList.get(move["pokeType"], -1)
            try:
                move_cur = self.search_pvp_move(move["name"])
                for k, v in move.items():
                    move_cur[k] = v
            except:
                self.PvPMoves.append(move)


    def from_json(self, source):
        '''
        Overwrite this instance with {source}, a GameMaster-like dict object.
        Warning: this is very likely to corrupt the game master instance.
        '''
        for name, value in source.items():
            if name in self.__dict__:
                self.__dict__[name] = value
        for pkm in self.Pokemon:
            if "pokeType1" in pkm:
                pkm["poketype1"] = GameMaster.InversedPoketypeList.get(pkm["pokeType1"], -1)
            if "pokeType2" in pkm:
                pkm["poketype2"] = GameMaster.InversedPoketypeList.get(pkm["pokeType2"], -1)
        for move in self.PvEMoves:
            if "pokeType" in move:
                move["poketype"] = GameMaster.InversedPoketypeList.get(move["pokeType"], -1)
        for move in self.PvPMoves:
            if "pokeType" in move:
                move["poketype"] = GameMaster.InversedPoketypeList.get(move["pokeType"], -1)


    def to_json(self):
        '''
        Export this instance to a GameMaster-like dict. Also include some other data.
        '''
        res = self.__dict__
        res['PoketypeList'] = GameMaster.PoketypeList
        res['PvEStraties'] = []
        res['PvPStraties'] = []
        for name in globals():
            if name.startswith("STRATEGY_"):
                res['PvEStraties'].append({
                    'name': name,
                    'value': globals()[name]
                })
            elif name.startswith("PVP_STRATEGY_"):
                res['PvPStraties'].append({
                    'name': name,
                    'value': globals()[name]
                })
        return res

    
    def feed(self, file):
        '''
        Load and process a game master json file with filepath {file}.
        '''
        with open(file) as gmfile:
            gmdata = json.load(gmfile)

        for template in gmdata["itemTemplates"]:
            tid = template['templateId']

            # Match Pokemon
            if re.fullmatch(r'V\d+_POKEMON_.+', tid):
                pokemon = {}
                pkmInfo = template["pokemonSettings"]
                pokemon['dex'] = int(tid.split('_')[0][1:])
                pokemon['name'] = GameMaster.rm_udrscrs(tid, 'p')
                pokemon['poketype1'] = GameMaster.InversedPoketypeList[GameMaster.rm_udrscrs(pkmInfo['type'], 't')]
                pokemon['poketype2'] = GameMaster.InversedPoketypeList.get(GameMaster.rm_udrscrs(pkmInfo.get('type2',''), 't'), -1)
                pokemon['baseAtk'] = pkmInfo["stats"]["baseAttack"]
                pokemon['baseDef'] = pkmInfo["stats"]["baseDefense"]
                pokemon['baseStm'] = pkmInfo["stats"]["baseStamina"]
                pokemon['fastMoves'] = [GameMaster.rm_udrscrs(s,"fast") for s in pkmInfo.get('quickMoves', [])]
                pokemon['chargedMoves'] = [GameMaster.rm_udrscrs(s,"charged") for s in pkmInfo.get('cinematicMoves', '')]
                evolution = [GameMaster.rm_udrscrs(s,'p') for s in pkmInfo.get('evolutionIds', [])]
                if evolution:
                    pokemon['evolution'] = evolution
                if 'rarity' in pkmInfo:
                    pokemon['rarity'] = pkmInfo['rarity']

                self.Pokemon.append(pokemon)
            
            # Match move, either Fast or Charged
            elif re.fullmatch(r'V\d+_MOVE_.+', tid):
                moveInfo = template['moveSettings']
                move = {}
                move['movetype'] = "fast" if tid.endswith('_FAST') else "charged"
                move['name'] = GameMaster.rm_udrscrs(moveInfo["movementId"], move['movetype'])
                move['poketype'] = GameMaster.InversedPoketypeList[GameMaster.rm_udrscrs(moveInfo["pokemonType"], 't')]
                move['power'] = int(moveInfo.get("power", 0))
                move['duration'] = int(moveInfo["durationMs"])
                move['dws'] = int(moveInfo["damageWindowStartMs"])
                move['energy'] = int(moveInfo.get("energyDelta", 0))
                
                self.PvEMoves.append(move)

            # Match PvP Moves
            elif re.fullmatch(r'COMBAT_V\d+_MOVE_.+', tid):
                moveInfo = template['combatMove']
                move = {}
                move['movetype'] = "fast" if tid.endswith('_FAST') else "charged"
                move['name'] = GameMaster.rm_udrscrs(moveInfo["uniqueId"], move['movetype'])
                move['poketype'] = GameMaster.InversedPoketypeList[GameMaster.rm_udrscrs(moveInfo["type"], 't')]
                move['power'] = int(moveInfo.get("power", 0))
                move['duration'] = int(moveInfo.get('durationTurns', 0)) + 1
                move['energy'] = int(moveInfo.get("energyDelta", 0))
                if "buffs" in moveInfo:
                    move['effect'] = {
                        "activation_chance": moveInfo["buffs"]["buffActivationChance"],
                        "self_attack_stage_delta": moveInfo["buffs"].get("attackerAttackStatStageChange", 0),
                        "self_defense_stage_delta": moveInfo["buffs"].get("attackerDefenseStatStageChange", 0),
                        "target_attack_stage_delta": moveInfo["buffs"].get("targetAttackStatStageChange", 0),
                        "target_defense_stage_delta": moveInfo["buffs"].get("targetDefenseStatStageChange", 0)
                    }

                self.PvPMoves.append(move)
        
            # Match CPM's
            elif tid == 'PLAYER_LEVEL_SETTINGS':
                for cpm in template["playerLevel"]["cpMultiplier"]:
                    if self.CPMultipliers:
                        # Half level
                        self.CPMultipliers.append(((cpm**2 + self.CPMultipliers[-1]**2)/2)**0.5)
                    self.CPMultipliers.append(cpm)

            # Match Pokemon Types
            elif re.fullmatch(r'POKEMON_TYPE_.+', tid):
                pokemonType = GameMaster.rm_udrscrs(tid, 't')
                self.TypeEffectiveness[pokemonType] = {}
                for idx, mtp in enumerate(template["typeEffective"]["attackScalar"]):
                    self.TypeEffectiveness[pokemonType][GameMaster.PoketypeList[idx]] = mtp

            # Match PvE Battle settings
            elif tid == 'BATTLE_SETTINGS':
                self.PvEBattleSettings = template["battleSettings"]

            # Match PvP Battle settings
            elif tid == 'COMBAT_SETTINGS':
                for name, value in template["combatSettings"].items():
                    self.PvPBattleSettings[name] = value

            # Match PvP Battle settings for buff stats
            elif tid == 'COMBAT_STAT_STAGE_SETTINGS':
                for name, value in template["combatStatStageSettings"].items():
                    self.PvPBattleSettings[name] = value

            # Match weather settings
            elif re.fullmatch(r'WEATHER_AFFINITY_.+', tid):
                wname = template["weatherAffinities"]["weatherCondition"]
                if wname == 'OVERCAST':
                    wname = 'CLOUDY'
                self.WeatherSettings[wname] = [GameMaster.rm_udrscrs(s,'t') for s in template["weatherAffinities"]["pokemonType"]]
            elif tid == 'WEATHER_BONUS_SETTINGS':
                self.PvEBattleSettings['weatherAttackBonusMultiplier'] = template["weatherBonusSettings"]["attackBonusMultiplier"]

            # Match friend settings
            elif re.fullmatch(r'FRIENDSHIP_LEVEL_\d+', tid):
                multiplier = template["friendshipMilestoneSettings"]["attackBonusPercentage"]
                self.FriendAttackBonusMultipliers.append({"name": tid, "multiplier": multiplier})

        self.FriendAttackBonusMultipliers.sort(key=lambda x: x["multiplier"])

        return self


    def apply(self):
        '''
        Pass the data to simulator engine and apply, and
        set GameMaster.CurrentInstance to this instance.
        '''
        GameMaster.CurrentInstance = self

        # Single-valued battle parameters
        for name, value in self.PvEBattleSettings.items():
            if name == 'sameTypeAttackBonusMultiplier':
                set_parameter("same_type_attack_bonus_multiplier", value)
            elif name == 'maximumEnergy':
                set_parameter("max_energy", value)
            elif name == 'energyDeltaPerHealthLost':
                set_parameter("energy_delta_per_health_lost", value)
            elif name == 'dodgeDurationMs':
                set_parameter("dodge_duration", value)
            elif name == 'swapDurationMs':
                set_parameter("swap_duration", value)
            elif name == 'dodgeDamageReductionPercent':
                set_parameter("dodge_damage_reduction_percent", value)
            elif name == 'weatherAttackBonusMultiplier':
                set_parameter("weather_attack_bonus_multiplier", value)
        # PvP specific parameters
        # Todo: some could conflict with PvE paramters, like STAB.
        for name, value in self.PvPBattleSettings.items():
            if name == "fastAttackBonusMultiplier":
                set_parameter("pvp_fast_attack_bonus_multiplier", value)
            elif name == "chargeAttackBonusMultiplier":
                set_parameter("pvp_charged_attack_bonus_multiplier", value)
        set_stage_multipliers(self.PvPBattleSettings["attackBuffMultiplier"],
                              self.PvPBattleSettings.get("minimumStatStage", None))
        
        # Type effectiveness
        set_num_types(len(GameMaster.PoketypeList))
        for t1, t1_name in enumerate(GameMaster.PoketypeList):
            for t2, t2_name in enumerate(GameMaster.PoketypeList):
                set_effectiveness(t1, t2, self.TypeEffectiveness[t1_name][t2_name])

        # Set weather
        for i, weather in enumerate(sorted(self.WeatherSettings.keys())):
            for t_name in self.WeatherSettings[weather]:
                set_type_boosted_weather(GameMaster.InversedPoketypeList[t_name], i)

        return self
        

    @staticmethod
    def _search(_universe, criteria, _all):
        if isinstance(criteria, str):
            cbfn = lambda x: x['name'].strip().lower() == criteria.strip().lower()
        elif isinstance(criteria, int):
            cbfn = lambda x: x.get('dex') == criteria
        else:
            cbfn = criteria
        results = []
        for entity in _universe:
            if cbfn(entity):
                if _all:
                    results.append(entity)
                else:
                    return entity
        if _all:
            return results
        else:
            raise Exception("Entity '{}' not found".format(criteria))

        
    def search_pokemon(self, criteria, _all=False):
        '''
        Fetch and return the Pokemon satisfying the criteria.
        
        {criteria} can be string or a callback
        In the first case, it will match each entity's name, case-insensitive
        If {_all} is False, it will return the first match. Otherwise, all matches
        '''
        return GameMaster._search(self.Pokemon, criteria, _all)

    def search_move(self, criteria, _all=False):
        '''
        Same as search_pve_move
        '''
        return self.search_pve_move(criteria, _all)

    def search_fmove(self, criteria, _all=False):
        '''
        Same as search_pve_fmove
        '''
        return self.search_pve_fmove(criteria, _all)

    def search_cmove(self, criteria, _all=False):
        '''
        Same as search_pve_cmove
        '''
        return self.search_pve_cmove(criteria, _all)

    def search_pve_fmove(self, criteria, _all=False):
        '''
        Same as search_pve_move, but return only the Fast moves.
        '''
        return GameMaster._search(filter(lambda x: x.get('movetype') == "fast", self.PvEMoves), criteria, _all)

    def search_pve_cmove(self, criteria, _all=False):
        '''
        Same as search_pve_move, but return only the Charged moves.
        '''
        return GameMaster._search(filter(lambda x: x.get('movetype') == "charged", self.PvEMoves), criteria, _all)

    def search_pvp_fmove(self, criteria, _all=False):
        '''
        Same as search_pvp_move, but return only the Fast moves.
        '''
        return GameMaster._search(filter(lambda x: x.get('movetype') == "fast", self.PvPMoves), criteria, _all)

    def search_pvp_cmove(self, criteria, _all=False):
        '''
        Same as search_pvp_move, but return only the Charged moves.
        '''
        return GameMaster._search(filter(lambda x: x.get('movetype') == "charged", self.PvPMoves), criteria, _all)

    def search_pve_move(self, criteria, _all=False):
        '''
        Fetch and return the PvE Move satisfying the criteria.
        
        {criteria} can be string or a callback
        In the first case, it will match each entity's name, case-insensitive
        If {_all} is False, it will return the first match. Otherwise, all matches
        '''
        return GameMaster._search(self.PvEMoves, criteria, _all)

    def search_pvp_move(self, criteria, _all=False):
        '''
        Fetch and return the PvP Move satisfying the criteria.
        
        {criteria} can be string or a callback
        In the first case, it will match each entity's name, case-insensitive
        If {_all} is False, it will return the first match. Otherwise, all matches
        '''
        return GameMaster._search(self.PvPMoves, criteria, _all)

    def search_cpm(self, level):
        '''
        Fetch and return the CPM corresponding to {level}.
        '''
        idx = round(2 * float(level) - 2)
        return self.CPMultipliers[idx]

    def search_weather(self, weather_name):
        '''
        Return the index of the weather by the name {weather_name}. -1 if not found.
        Case-insensitive search.
        
        '''
        for i, wname in enumerate(sorted(self.WeatherSettings.keys())):
            if wname.lower() == weather_name.lower():
                return i
        return -1
    
    def search_friend(self, friendship):
        '''
        Return the friend attack bonus multiplier of friendship {friendship}.
        Example: "FRIENDSHIP_LEVEL_1", or 1, or "1", "Great", or "great"
        '''
        friendship = str(friendship).strip().lower()
        alter_names = ["none", "good", "great", "ultra", "best"]
        for i, friend_setting in enumerate(self.FriendAttackBonusMultipliers):
            if friendship == str(i):
                return friend_setting["multiplier"]
            elif friendship == alter_names[i]:
                return friend_setting["multiplier"]
        raise Exception("Friend '{}' not found".format(friendship))

    def search_raid_tier(self, tier):
        '''
        Return {boss cpm, boss max_hp, time limit} of tier {tier}.
        {tier} is string, such as "3" (tier 3).
        '''

        tier = str(tier)
        for rt in self.RaidTierSettings:
            if rt["name"] == tier:
                return rt
        raise Exception("Tier {} not found".format(tier))


    def batch_pokemon(self, pkm_dict):
        '''
        Return the product by all possible values of all the wild card queries, if any.
        
        The attribute fields that can contain wild card query:
            name
            fmove
            cmove
            cmove2
        [cmove2] is optional, while the others are mandoratory.
        '''
        results = []
        species_matches = []
        fmove_matches = []
        cmove_matches = []
        cmove2_matches = []
        has_cmove2 = "cmove2" in pkm_dict
        pkm_dict['fmove'] = pkm_dict.get("fmove", "*")
        pkm_dict['cmove'] = pkm_dict.get("cmove", "*")

        # Try for direct match first. Only if no direct match will the program try for query match.
        try:
            species_matches = [self.search_pokemon(pkm_dict['name'])]
        except:
            species_matches = self.search_pokemon(PokeQuery(pkm_dict['name']), True)
        try:
            fmove_matches = [self.search_fmove(pkm_dict['fmove'])]
        except:
            pass
        try:
            cmove_matches = [self.search_cmove(pkm_dict['cmove'])]
        except:
            pass
        if has_cmove2:
            try:
                cmove2_matches = [self.search_cmove(pkm_dict['cmove2'])]
            except:
                pass
        
        for species in species_matches:
            if fmove_matches:
                cur_fmove_matches = fmove_matches
            else:
                cur_fmove_matches = self.search_fmove(PokeQuery(pkm_dict['fmove'], species, "fast"), True)
            if cmove_matches:
                cur_cmove_matches = cmove_matches
            else:
                cur_cmove_matches = self.search_cmove(PokeQuery(pkm_dict['cmove'], species, "charged"), True)
            if has_cmove2:
                if cmove2_matches:
                    cur_cmove2_matches = cmove2_matches
                else:
                    cur_cmove2_matches = self.search_cmove(PokeQuery(pkm_dict['cmove2'], species, "charged"), True)
                for fmove, cmove, cmove2 in itertools.product(cur_fmove_matches, cur_cmove_matches, cur_cmove2_matches):
                    cur_pokemon = copy.copy(pkm_dict)
                    cur_pokemon['name'] = species['name']
                    cur_pokemon['fmove'] = fmove['name']
                    cur_pokemon['cmove'] = cmove['name']
                    cur_pokemon['cmove2'] = cmove2['name']
                    if cur_pokemon['cmove2'] != cur_pokemon['cmove']:
                        results.append(cur_pokemon)
            else:
                for fmove, cmove in itertools.product(cur_fmove_matches, cur_cmove_matches):
                    cur_pokemon = copy.copy(pkm_dict)
                    cur_pokemon['name'] = species['name']
                    cur_pokemon['fmove'] = fmove['name']
                    cur_pokemon['cmove'] = cmove['name']
                    results.append(cur_pokemon)

        return results
    


'''
    PokeQuery modules.
'''

def BasicPokeQuery(query_str, pkm=None, movetype="fast"):
    '''
    Create a basic PokeQuery from string {query_str}.
    The {pkm} is needed if the entity is Move.
    Return a callback predicate that accepts one parameter (the entity to be examined).
    '''
    query_str = str(query_str).lower().strip(" *")

    # Default predicate for empty query
    if query_str == "":
        if pkm is not None:
            pd1 = BasicPokeQuery("current", pkm, movetype)
            pd2 = BasicPokeQuery("legacy", pkm, movetype)
            pd3 = BasicPokeQuery("exclusive", pkm, movetype)
            return lambda x: (pd1(x) or pd2(x) or pd3(x))
        else:
            return lambda x: True

    # Match by dex. For Pokemon
    elif query_str.isdigit():
        dex = int(query_str)
        def predicate(entity):
            return entity.get('dex') == dex
    elif query_str[:3] == 'dex':
        num_part = query_str[3:]
        if '-' in num_part:
            min_dex, max_dex = [int(v.strip()) for v in num_part.split('-')][:2]
        else:
            min_dex = max_dex = int(num_part)
        def predicate(entity):
            return min_dex <= entity.get('dex') <= max_dex
    
    # Match by type. For Pokemon, Move
    elif query_str in GameMaster.PoketypeList or query_str == 'none':
        _idx = -1 if query_str == 'none' else GameMaster.InversedPoketypeList[query_str] 
        def predicate(entity):
            return _idx in [entity.get('poketype'), entity.get('poketype1'), entity.get('poketype2')]

    # Match by rarity Legendary. For Pokemon
    elif query_str == "legendary":
        def predicate(entity):
            return entity.get('rarity') == 'POKEMON_RARITY_LEGENDARY'

    # Match by rarity Mythical. For Pokemon
    elif query_str == "mythic" or query_str == "mythical":
        def predicate(entity):
            return entity.get('rarity') == 'POKEMON_RARITY_MYTHIC'

    # Match by current move availability
    elif query_str == "current":
        movepool = pkm.get(movetype + "Moves", [])
        def predicate(entity):
            return entity['name'] in movepool
    elif query_str == "legacy":
        movepool = pkm.get(movetype + "Moves_legacy", [])
        def predicate(entity):
            return entity['name'] in movepool
    elif query_str == "exclusive":
        movepool = pkm.get(movetype + "Moves_exclusive", [])
        def predicate(entity):
            return entity['name'] in movepool

    # Default: Match by name. For Pokemon, Move
    else:
        def predicate(entity):
            return query_str in entity['name']

    return predicate


POKE_QUERY_LOGICAL_OPERATORS = {
    ':': 0,
    ',': 0,
    ';': 0,
    '&': 1,
    '|': 1,
    '!': 2
}


def PokeQuery(query_str, pkm=None, movetype="fast"):
    '''
    Create a PokeQuery from string {query_str}. Supports logical operators and parenthesis.
    The {pkm} is needed if the entity if moves.
    Return a callback predicate that accepts one parameter (the entity to be examined).
    '''

    global POKE_QUERY_LOGICAL_OPERATORS
    OPS = POKE_QUERY_LOGICAL_OPERATORS

    # Tokenize the input query string
    tokens = []
    tk = ""
    for c in query_str:
        if c in OPS or c in ['(', ')']:
            tk = tk.strip()
            if tk:
                tokens.append(tk)
            tokens.append(c)
            tk = ""
        else:
            tk += c
    tk = tk.strip()
    if tk:
        tokens.append(tk)

    vstack = []
    opstack = []
    default_pred = lambda x: False
    def eval_simple(op, vstack):
        if OPS[op] == 0:
            rhs = vstack.pop()
            lhs = vstack.pop()
            vstack.append(lambda x: lhs(x) or rhs(x))
        elif OPS[op] == 1:
            rhs = vstack.pop()
            lhs = vstack.pop()
            vstack.append(lambda x: lhs(x) and rhs(x))
        elif OPS[op] == 2:
            rhs = vstack.pop()
            vstack.append(lambda x: not rhs(x))
            
    for tk in tokens:
        if tk in OPS:
            while opstack and opstack[-1] != '(' and OPS[opstack[-1]] > OPS[tk]:
                eval_simple(opstack.pop(), vstack)
            opstack.append(tk)
        elif tk == '(':
            opstack.append(tk)
        elif tk == ')':
            while opstack:
                op = opstack.pop()
                if op == '(':
                    break
                eval_simple(op, vstack)
        else:
            vstack.append(BasicPokeQuery(tk, pkm=pkm, movetype=movetype))
    while opstack:
        eval_simple(opstack.pop(), vstack)

    return vstack.pop()




'''
    Inferface Classes for engine.
'''


ROLE_PVE_ATTACKER = "ae"
ROLE_PVP_ATTACKER = "ap"
ROLE_GYM_DEFENDER = "gd"
ROLE_RAID_BOSS = "rb"



class IMove(Move):
    '''
    Interface Move class.
    Convinient for contructing gobattlesim.engine.Move objects.
    '''

    def __init__(self, *args, game_master=None, **kwargs):
        '''
        The first positional argument can be a string (name of the move to search) or a dict.
        IMove("Counter") will search for a move named "Counter" but IMove(name="Counter") will not.
        '''
        game_master = game_master or GameMaster.CurrentInstance
        if "name" in kwargs:
            if kwargs.get("pvp", False):
                kwargs.update(game_master.search_pvp_move(kwargs["name"]))
            else:
                kwargs.update(game_master.search_pve_move(kwargs["name"]))
        move_dict_clean = {}
        for k, v in kwargs.items():
            if isinstance(v, int) or isinstance(v, dict) or isinstance(v, MoveEffect):
                setattr(self, k, v)



class IPokemon(PvPPokemon):
    '''
    Interface Pokemon class.
    Convinient for contructing gobattlesim.engine.Pokemon(/PvPPokemon) objects.
    '''

    @staticmethod
    def calc_cp(bAtk, bDef, bStm, cpm, atkiv, defiv, stmiv):
        Atk = (bAtk + atkiv) * cpm
        Def = (bDef + defiv) * cpm
        Stm = (bStm + stmiv) * cpm
        return max(10, int( Atk * (Def * Stm)**0.5 / 10 ))

    @staticmethod
    def infer_level_and_IVs(bAtk, bDef, bStm, target_cp):
        CPMultipliers = GameMaster.CurrentInstance.CPMultipliers
        closest = None
        closest_cp = 0
        min_cpm_i = 0
        max_cpm_i = len(CPMultipliers) - 1
        while min_cpm_i < max_cpm_i:
            if IPokemon.calc_cp(bAtk, bDef, bStm, CPMultipliers[min_cpm_i], 15, 15, 15) >= target_cp:
                break
            min_cpm_i += 1
        while max_cpm_i > min_cpm_i:
            if IPokemon.calc_cp(bAtk, bDef, bStm, CPMultipliers[max_cpm_i], 0, 0, 0) <= target_cp:
                break
            max_cpm_i -= 1
        for cpm in CPMultipliers[min_cpm_i : max_cpm_i + 1]:
            for stmiv in range(16):
                for defiv in range(16):
                    for atkiv in range(16):
                        cp = IPokemon.calc_cp(bAtk, bDef, bStm, cpm, atkiv, defiv, stmiv)
                        if cp == target_cp:
                            return (cpm, atkiv, defiv, stmiv)
                        elif closest_cp < cp and cp < target_cp:
                            closest_cp = cp
                            closest = (cpm, atkiv, defiv, stmiv)
        return closest
    

    def __init__(self, *args, game_master=None, **kwargs):
        '''
        All Pokemon parameters should be passed via keyword arguments, including:
            name, fmove, cmove, cmoves, level, atkiv, defiv, stmiv, cp, role, tier, immortal, strategy
            
        Some examples:
            Define an attacker:
                (name, fmove, cmove/cmoves, level, atkiv, defiv, stmiv)
            Define an attacker by cp (infer the stats):
                (name, fmove, cmove/cmoves, cp)
            Define a raid boss:
                (name, fmove, cmove, role=ROLE_RAID_BOSS, tier)
            Define a gym defender by cp (infer the stats, too):
                (name, fmove, cmove, cp, role=ROLE_GYM_DEFENDER)
        '''
        game_master = game_master or GameMaster.CurrentInstance
        self.__dict__['tier'] = None

        if "name" in kwargs:
            kwargs.update(game_master.search_pokemon(kwargs["name"]))
        if "poketype1" in kwargs:
            self.poketype1 = kwargs["poketype1"]
        if "poketype2" in kwargs:
            self.poketype2 = kwargs["poketype2"]

        role = kwargs.get("role", ROLE_PVE_ATTACKER)
        if role == ROLE_RAID_BOSS or "tier" in kwargs:
            tier = str(kwargs["tier"])
            tier_setting = game_master.search_raid_tier(tier)
            self.attack = (kwargs["baseAtk"] + 15) * tier_setting['cpm']
            self.defense = (kwargs["baseDef"] + 15) * tier_setting['cpm']
            self.max_hp = tier_setting["maxHP"]
            self.__dict__['tier'] = tier
        elif len(args) < 5:
            if "cp" in kwargs:
                cp = kwargs["cp"]
                if not isinstance(cp, int):
                    raise TypeError("cp is of wrong type. Expected int, got {}".format(type(cp)))
                cpm, atkiv, defiv, stmiv = IPokemon.infer_level_and_IVs(kwargs["baseAtk"], kwargs["baseDef"], kwargs["baseStm"], cp)
            else:
                cpm = game_master.search_cpm(kwargs.get("level", 40))
                atkiv = int(kwargs.get("atkiv", 15))
                defiv = int(kwargs.get("defiv", 15))
                stmiv = int(kwargs.get("stmiv", 15))
            self.attack = (kwargs["baseAtk"] + atkiv) * cpm
            self.defense = (kwargs["baseDef"] + defiv) * cpm
            self.max_hp = int((kwargs["baseStm"] + stmiv) * cpm)
            if role == ROLE_GYM_DEFENDER:
                self.max_hp *= 2
        
        # Set up moves
        pvp = (role == ROLE_PVP_ATTACKER) or kwargs.get("pvp", False)
        if "fmove" in kwargs:
            if isinstance(kwargs["fmove"], str):
                self.fmove = IMove(name=kwargs["fmove"], pvp=pvp, game_master=game_master)
            elif isinstance(kwargs["fmove"], dict):
                self.fmove = IMove(**kwargs["fmove"], pvp=pvp, game_master=game_master)
            elif isinstance(kwargs["fmove"], Move):
                self.fmove = Move.cast(kwargs["fmove"]._addr)
            else:
                raise TypeError("Expected int/dict/Move, got {}".format(type(kwargs["fmove"])))
        raw_cmoves = []
        if "cmove" in kwargs:
            raw_cmoves = [kwargs["cmove"]]
            if "cmove2" in kwargs:
                raw_cmoves.append(kwargs["cmove2"])
        elif "cmoves" in kwargs:
            raw_cmoves = kwargs["cmoves"]
        cmoves = []
        for move in raw_cmoves:
            if isinstance(move, str):
                cmoves.append(IMove(name=move, pvp=pvp, game_master=game_master))
            elif isinstance(move, dict):
                cmoves.append(IMove(**move, pvp=pvp, game_master=game_master))
            elif isinstance(move, Move):
                cmoves.append(move)
            else:
                raise TypeError("Expected int/dict/Move, got {}".format(type(move)))
        self.cmoves = cmoves

        # Set up other attributes
        self.immortal = kwargs.get("immortal", False)
        if "num_shields" in kwargs or "strategy2" in kwargs or "shield" in kwargs:
            self.num_shields = kwargs.get("num_shields", kwargs.get("strategy2", kwargs.get("shield")))



class IParty(Party):
    '''
    Interface Party class.
    Convinient for contructing gobattlesim.engine.Party objects.
    '''

    def __init__(self, *arg, game_master=None, **kwargs):
        '''
        All Party parameters should be passed via keyword arguments, which can include:
            pokemon, revive (revive_policy)
        '''
        game_master = game_master or GameMaster.CurrentInstance
        if "pokemon" in kwargs:
            arg_pkm = kwargs["pokemon"]
            if isinstance(arg_pkm, list):
                kwargs["pokemon"] = [IPokemon(pkm, game_master=game_master) for pkm in arg_pkm]
            elif isinstance(arg_pkm, dict) or isinstance(arg_pkm, Pokemon):
                kwargs["pokemon"] = [IPokemon(arg_pkm, game_master=game_master)]
            else:
                raise TypeError("Wrong type for pokemon")
        revive_policy = kwargs.get("revive_policy", kwargs.get("revive", 0))
        if isinstance(revive_policy, str):
            revive_policy = int(revive_policy)
        elif isinstance(revive_policy, bool):
            revive_policy = -1 if revive_policy else 0
        else:
            TypeError("Wrong type for revive_policy: {}".format(type(revive_policy)))
        kwargs["revive_policy"] = revive_policy
        for k, v in kwargs.items():
            setattr(self, k, v)



def IPlayer(Player):
    '''
    Interface Player class.
    Convinient for contructing gobattlesim.engine.Player objects.
    '''

    def __init__(self, *arg, game_master=None, **kwargs):
        '''
        All Player parameters should be passed via keyword arguments, which can include:
            parties (party), attack_multiplier, clone_multiplier
        '''
        game_master = game_master or GameMaster.CurrentInstance
        if "parties" in kwargs or "party" in kwargs:
            arg_party = kwargs.get("parties", kwargs["party"])
            if isinstance(arg_party, list):
                kwargs["parties"] = [IParty(pty, game_master=game_master) for pty in arg_party]
            elif isinstance(arg_party, dict) or isinstance(arg_party, Party):
                kwargs["parties"] = [IParty(arg_party, game_master=game_master)]
            else:
                raise TypeError("Wrong type for parties: {}".format(type(arg_party)))
        if "friend" in kwargs:
            kwargs["attack_multiplier"] = kwargs.get("attack_multiplier", 1) * game_master.search_friend(kwargs["friend"])
        for k, v in kwargs.items():
            setattr(self, k, v)



class IBattle(Battle):
    '''
    Interface Battle class.
    Convinient for contructing gobattlesim.engine.Battle objects.
    '''
        
    def __init__(self, *arg, game_master=None, **kwargs):
        '''
        All Battle parameters should be passed via keyword arguments, which can include:
            players (player), weather, time_limit, num_sims
        '''
        game_master = game_master or GameMaster.CurrentInstance
        if "players" in kwargs or "player" in kwargs:
            arg_player = kwargs.get("players", kwargs["players"])
            if isinstance(arg_player, list):
                kwargs["players"] = [IPlayer(player, game_master=game_master) for player in arg_player]
            elif isinstance(arg_player, dict) or isinstance(arg_player, Player):
                kwargs["players"] = [IPlayer(arg_player, game_master=game_master)]
            else:
                raise TypeError("Wrong type for players: {}".format(type(arg_player)))
        if "weather" in kwargs:
            if isinstance(kwargs["weather"], str):
                kwargs["weather"] = game_master.search_weather(kwargs["weather"])
        self.__dict__['num_sims'] = max(1, int(kwargs.get("num_sims", 1)))
        for k, v in kwargs.items():
            setattr(self, k, v)


    def run(self):
        '''
        Run the battle for {num_sims} times and returns the average outcome.
        '''

        # Run many simulations
        sum_duration = sum_wins = sum_tdo_percent = sum_deaths = 0
        for _ in range(self.num_sims):
            self.init()
            self.start()
            battle_outcome = battle.get_outcome(1)
            sum_duration += battle_outcome.duration
            sum_wins += 1 if battle_outcome.win else 0
            sum_tdo_percent += battle_outcome.tdo_percent
            sum_deaths += battle_outcome.num_deaths
        return {
            "win": sum_wins / self.num_sims,
            "duration": sum_duration / self.num_sims,
            "tdo_percent": sum_tdo_percent / self.num_sims,
            "num_deaths": sum_deaths / self.num_sims
        }




'''
    Useful functions
'''

def quick_raid_battle(attacker,
                      boss,
                      party_size=6,
                      player_multiplier=1,
                      friend=0,
                      strategy=STRATEGY_ATTACKER_NO_DODGE,
                      rejoin=0,
                      weather="extreme",
                      time_limit=None,
                      num_sims=2000,
                      random_seed=0,
                      game_master=None):
    '''
    Simulate a simple raid battle.
    Returns a dict of average outcome.
    '''
    
    game_master = game_master or GameMaster.CurrentInstance
    set_random_seed(random_seed)

    pkm_list = []
    if isinstance(attacker, list):
        pkm_list = [IPokemon(**atkr, game_master=game_master) for atkr in attacker]
    else:
        pkm_list = [IPokemon(**attacker, game_master=game_master)]

    d_pokemon = IPokemon(**boss, game_master=game_master)
    d_party = Party()
    d_party.add(d_pokemon)
    d_player = Player()
    d_player.add(d_party)
    d_player.team = 0
    d_player.strategy = STRATEGY_DEFENDER
    
    players_list = [d_player]
    for pkm in pkm_list:
        a_party = Party()
        a_party.pokemon = [pkm] * party_size
        a_party.revive_policy = rejoin
        a_player = Player()
        a_player.parties = [a_party]
        a_player.team = 1
        a_player.strategy = strategy
        a_player.clone_multiplier = player_multiplier
        a_player.attack_multiplier = game_master.search_friend(friend)
        players_list.append(a_player)

    battle = Battle()
    battle.players = players_list
    battle.weather = game_master.search_weather(weather)
    if time_limit is None:
        battle.time_limit = game_master.search_raid_tier(d_pokemon.tier)['timelimit']
    else:
        battle.time_limit = int(time_limit)

    sum_duration = sum_wins = sum_tdo_percent = sum_deaths = 0
    for i in range(num_sims):
        battle.init()
        battle.start()
        battle_outcome = battle.get_outcome(1)
        sum_duration += battle_outcome.duration
        sum_wins += 1 if battle_outcome.win else 0
        sum_tdo_percent += battle_outcome.tdo_percent
        sum_deaths += battle_outcome.num_deaths
    return {
        "win": sum_wins / num_sims,
        "duration": sum_duration / num_sims,
        "tdo_percent": sum_tdo_percent / num_sims,
        "num_deaths": sum_deaths / num_sims
    }



def quick_pvp_battle(pokemon_0,
                     pokemon_1,
                     num_shields=[0, 0],
                     game_master=None):
    '''
    Simulate a quick PvP battle.
    Returns the battle score of pokemon_0.
    '''

    game_master = game_master or GameMaster.CurrentInstance
    
    p0 = IPokemon(**pokemon_0, pvp=True, game_master=game_master)
    p1 = IPokemon(**pokemon_1, pvp=True, game_master=game_master)

    battle = SimplePvPBattle(p0, p1)
    battle.set_num_shields_max(num_shields[0], num_shields[1])
    battle.init()
    battle.start()
    tdo_percent = battle.get_outcome().tdo_percent

    return min(tdo_percent[0], 1) - min(tdo_percent[1], 1)

