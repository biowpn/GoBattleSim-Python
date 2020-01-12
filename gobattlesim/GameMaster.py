
'''
This module provides game master file parsing (into GoBattleSim compatible format).
'''

import argparse
import copy
import json
import re
import sys


PoketypeList = ["normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost",
                "steel", "fire", "water", "grass", "electric", "psychic", "ice", "dragon", "dark", "fairy"]

InversedPoketypeList = dict([(name, i)
                             for i, name in enumerate(PoketypeList)])


def rm_underscores(Str, Category):
    if Category == 'p':
        return '-'.join([s.lower() for s in Str.split('_')][2:])
    elif Category == "fast":
        return ' '.join([s.lower() for s in Str.split('_')[:-1]])
    elif Category == "charged":
        return ' '.join([s.lower() for s in Str.split('_')])
    elif Category == 't':
        return Str.split('_')[-1].lower()


class GameMaster:
    '''
    The class parses the official Game Master json and organize the data.
    '''

    CurrentInstance = None

    def __init__(self, file=None):
        '''
        @param file the filepath to the game master json file.
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
            {"name": "3", "cpm": 0.7300000190734863,
                "maxHP": 3600, "timelimit": 180000},
            {"name": "4", "cpm": 0.7900000214576721,
                "maxHP": 9000, "timelimit": 180000},
            {"name": "5", "cpm": 0.7900000214576721,
                "maxHP": 15000, "timelimit": 300000},
            {"name": "6", "cpm": 0.7900000214576721,
                "maxHP": 18750, "timelimit": 3000000}
        ]

        if file is not None:
            self.parse(file)

    def clear(self):
        '''
        Clear all data.
        '''
        self.__init__()
        return self

    def parse(self, file):
        '''
        Load and process a game master json file @param file.
        @param path to game master json.
        '''
        with open(file) as fd:
            gmdata = json.load(fd)

        for template in gmdata["itemTemplates"]:
            tid = template['templateId']

            # Match Pokemon
            if re.fullmatch(r'V\d+_POKEMON_.+', tid):
                pokemon = {}
                pkmInfo = template["pokemonSettings"]
                pokemon['dex'] = int(tid.split('_')[0][1:])
                pokemon['name'] = rm_underscores(tid, 'p')
                pokemon['pokeType1'] = rm_underscores(
                    pkmInfo['type'], 't')
                pokemon['pokeType2'] = rm_underscores(
                    pkmInfo.get('type2', 'none'), 't')
                pokemon['baseAtk'] = pkmInfo["stats"]["baseAttack"]
                pokemon['baseDef'] = pkmInfo["stats"]["baseDefense"]
                pokemon['baseStm'] = pkmInfo["stats"]["baseStamina"]
                pokemon['fastMoves'] = [rm_underscores(
                    s, "fast") for s in pkmInfo.get('quickMoves', [])]
                pokemon['chargedMoves'] = [rm_underscores(
                    s, "charged") for s in pkmInfo.get('cinematicMoves', '')]
                evolution = [s.lower()
                             for s in pkmInfo.get('evolutionIds', [])]
                if any(evolution):
                    pokemon['evolution'] = evolution
                if 'rarity' in pkmInfo:
                    pokemon['rarity'] = pkmInfo['rarity']

                self.Pokemon.append(pokemon)

            # Match move, either Fast or Charged
            elif re.fullmatch(r'V\d+_MOVE_.+', tid):
                moveInfo = template['moveSettings']
                move = {}
                move['movetype'] = "fast" if tid.endswith(
                    '_FAST') else "charged"
                move['name'] = rm_underscores(
                    moveInfo["movementId"], move['movetype'])
                move['pokeType'] = rm_underscores(moveInfo["pokemonType"], 't')
                move['power'] = int(moveInfo.get("power", 0))
                move['duration'] = int(moveInfo["durationMs"])
                move['dws'] = int(moveInfo["damageWindowStartMs"])
                move['energy'] = int(moveInfo.get("energyDelta", 0))

                self.PvEMoves.append(move)

            # Match PvP Moves
            elif re.fullmatch(r'COMBAT_V\d+_MOVE_.+', tid):
                moveInfo = template['combatMove']
                move = {}
                move['movetype'] = "fast" if tid.endswith(
                    '_FAST') else "charged"
                move['name'] = rm_underscores(
                    moveInfo["uniqueId"], move['movetype'])
                move['pokeType'] = rm_underscores(moveInfo["type"], 't')
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
                        self.CPMultipliers.append(
                            ((cpm**2 + self.CPMultipliers[-1]**2)/2)**0.5)
                    self.CPMultipliers.append(cpm)

            # Match Pokemon Types
            elif re.fullmatch(r'POKEMON_TYPE_.+', tid):
                pokemonType = rm_underscores(tid, 't')
                self.TypeEffectiveness[pokemonType] = {}
                for idx, mtp in enumerate(template["typeEffective"]["attackScalar"]):
                    self.TypeEffectiveness[pokemonType][PoketypeList[idx]] = mtp

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
                self.WeatherSettings[wname] = [rm_underscores(
                    s, 't') for s in template["weatherAffinities"]["pokemonType"]]
            elif tid == 'WEATHER_BONUS_SETTINGS':
                self.PvEBattleSettings['weatherAttackBonusMultiplier'] = template["weatherBonusSettings"]["attackBonusMultiplier"]

            # Match friend settings
            elif re.fullmatch(r'FRIENDSHIP_LEVEL_\d+', tid):
                multiplier = template["friendshipMilestoneSettings"]["attackBonusPercentage"]
                self.FriendAttackBonusMultipliers.append(
                    {"name": tid, "multiplier": multiplier})

        self.FriendAttackBonusMultipliers.sort(key=lambda x: x["multiplier"])

    def to_json(self):
        '''
        Export this instance in json.
        '''
        return self.__dict__

    def from_json(self, source):
        '''
        The reverse of to_json().
        @param source a dict-like object
        '''
        for name, value in source.items():
            if name in self.__dict__:
                self.__dict__[name] = value

    def apply(self):
        '''
        Pass the data to simulator engine and apply, and
        set GameMaster.CurrentInstance to this instance.
        '''
        GameMaster.CurrentInstance = self

    @staticmethod
    def _search(_universe, criteria, _all):
        if isinstance(criteria, str):
            def cbfn(x):
                return x['name'].strip().lower() == criteria.strip().lower()
        elif isinstance(criteria, int):
            def cbfn(x):
                return x.get('dex') == criteria
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
            return None

    def search_pokemon(self, criteria, _all=False):
        return GameMaster._search(self.Pokemon, criteria, _all)

    def search_pve_fmove(self, criteria, _all=False):
        return GameMaster._search(filter(lambda x: x.get('movetype') == "fast", self.PvEMoves), criteria, _all)

    def search_pve_cmove(self, criteria, _all=False):
        return GameMaster._search(filter(lambda x: x.get('movetype') == "charged", self.PvEMoves), criteria, _all)

    def search_pvp_fmove(self, criteria, _all=False):
        return GameMaster._search(filter(lambda x: x.get('movetype') == "fast", self.PvPMoves), criteria, _all)

    def search_pvp_cmove(self, criteria, _all=False):
        return GameMaster._search(filter(lambda x: x.get('movetype') == "charged", self.PvPMoves), criteria, _all)

    def search_cpm(self, level):
        idx = round(2 * float(level) - 2)
        return self.CPMultipliers[idx]

    def search_weather(self, weather_name):
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
        return 1

    def search_raid_tier(self, tier):
        '''
        Return {boss cpm, boss max_hp, time limit} of tier {tier}.
        {tier} is string, such as "3" (tier 3).
        '''

        tier = str(tier)
        for rt in self.RaidTierSettings:
            if rt["name"] == tier:
                return rt
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=str,
                        help="path to official game master json")
    parser.add_argument("-z", "--minimize", action="store_true",
                        help="leaving out Pokemon and Move data")
    parser.add_argument("-o", "--out", type=argparse.FileType('w'), default=open("./GBS.json", "w"),
                        help="output filepath")
    args = parser.parse_args()

    gm = GameMaster(args.infile)
    j = gm.to_json()
    if args.minimize:
        j.pop("Pokemon")
        j.pop("PvPMoves")
        j.pop("PvEMoves")
    json.dump(j, args.out, indent=4)


if __name__ == "__main__":
    main()
