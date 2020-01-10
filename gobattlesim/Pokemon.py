
from .GameMaster import GameMaster
from .Move import Move

ROLE_PVE_ATTACKER = "ae"
ROLE_PVP_ATTACKER = "ap"
ROLE_GYM_DEFENDER = "gd"
ROLE_RAID_BOSS = "rb"


class Pokemon:

    @staticmethod
    def calc_cp(bAtk, bDef, bStm, cpm, atkiv, defiv, stmiv):
        Atk = (bAtk + atkiv) * cpm
        Def = (bDef + defiv) * cpm
        Stm = (bStm + stmiv) * cpm
        return max(10, int(Atk * (Def * Stm)**0.5 / 10))

    @staticmethod
    def infer_cpm_and_IVs(bAtk, bDef, bStm, target_cp):
        CPMultipliers = GameMaster.CurrentInstance.CPMultipliers
        closest = None
        closest_cp = 0
        min_cpm_i = 0
        max_cpm_i = len(CPMultipliers) - 1
        while min_cpm_i < max_cpm_i:
            if Pokemon.calc_cp(bAtk, bDef, bStm, CPMultipliers[min_cpm_i], 15, 15, 15) >= target_cp:
                break
            min_cpm_i += 1
        while max_cpm_i > min_cpm_i:
            if Pokemon.calc_cp(bAtk, bDef, bStm, CPMultipliers[max_cpm_i], 0, 0, 0) <= target_cp:
                break
            max_cpm_i -= 1
        for cpm in CPMultipliers[min_cpm_i: max_cpm_i + 1]:
            for stmiv in range(16):
                for defiv in range(16):
                    for atkiv in range(16):
                        cp = Pokemon.calc_cp(
                            bAtk, bDef, bStm, cpm, atkiv, defiv, stmiv)
                        if cp == target_cp:
                            return (cpm, atkiv, defiv, stmiv)
                        elif closest_cp < cp and cp < target_cp:
                            closest_cp = cp
                            closest = (cpm, atkiv, defiv, stmiv)
        return closest

    def __init__(self, *args, **kwargs):
        '''
        All named parameters should be passed via keyword arguments, including:
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
        game_master = GameMaster.CurrentInstance
        if len(args) > 0:
            if isinstance(args[0], str):
                kwargs["name"] = args[0]
                args = args[1:]
            elif isinstance(args[0], dict):
                kwargs.update(args[0])
                args = args[1:]
        if "name" in kwargs:
            kwargs.update(game_master.search_pokemon(kwargs["name"]))

        role = kwargs.get("role", ROLE_PVE_ATTACKER)
        self.tier = None
        if role == ROLE_RAID_BOSS or "tier" in kwargs:
            self.tier = str(kwargs["tier"])
            tier_setting = game_master.search_raid_tier(self.tier)
            kwargs["attack"] = (kwargs["baseAtk"] + 15) * tier_setting["cpm"]
            kwargs["defense"] = (kwargs["baseDef"] + 15) * tier_setting["cpm"]
            kwargs["maxHP"] = tier_setting["maxHP"]
        elif len(args) < 5:
            if "cp" in kwargs:
                cp = kwargs["cp"]
                if not isinstance(cp, int):
                    raise TypeError("Expected int, got {}".format(type(cp)))
                cpm, atkiv, defiv, stmiv = Pokemon.infer_cpm_and_IVs(
                    kwargs["baseAtk"], kwargs["baseDef"], kwargs["baseStm"], cp)
            else:
                cpm = game_master.search_cpm(kwargs.get("level", 40))
                atkiv = int(kwargs.get("atkiv", 15))
                defiv = int(kwargs.get("defiv", 15))
                stmiv = int(kwargs.get("stmiv", 15))
            kwargs["attack"] = (kwargs["baseAtk"] + atkiv) * cpm
            kwargs["defense"] = (kwargs["baseDef"] + defiv) * cpm
            kwargs["maxHP"] = int((kwargs["baseStm"] + stmiv) * cpm)
            if role == ROLE_GYM_DEFENDER:
                kwargs["maxHP"] *= 2

        self.pokeType1 = kwargs["pokeType1"]
        self.pokeType2 = kwargs["pokeType2"]
        self.attack = kwargs["attack"]
        self.defense = kwargs["defense"]
        self.maxHP = kwargs["maxHP"]

        # Set up moves
        pvp = (role == ROLE_PVP_ATTACKER) or kwargs.get("pvp", False)
        if "fmove" in kwargs:
            self.fmove = Move(kwargs["fmove"], pvp=pvp,
                              game_master=game_master)
        raw_cmoves = []
        if "cmove" in kwargs:
            raw_cmoves = [kwargs["cmove"]]
            if "cmove2" in kwargs:
                raw_cmoves.append(kwargs["cmove2"])
        elif "cmoves" in kwargs:
            raw_cmoves = kwargs["cmoves"]
        cmoves = []
        for move in raw_cmoves:
            cmoves.append(Move(move, pvp=pvp))
        self.cmoves = cmoves

        # Set up other attributes
        self.immortal = kwargs.get("immortal", False)
        if "num_shields" in kwargs or "strategy2" in kwargs or "shield" in kwargs:
            self.num_shields = kwargs.get(
                "num_shields", kwargs.get("strategy2", kwargs.get("shield")))
