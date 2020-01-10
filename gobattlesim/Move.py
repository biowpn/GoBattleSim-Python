
from .GameMaster import GameMaster


class Move:

    def __init__(self, *args, pvp=False, **kwargs):
        '''
        The named move paramters can be passed via keyword arguments,
        or via a str or dict as the first positional argument:

            Move("Counter"), Move({"name": "Counter"}), Move(name="Counter")

        give the same thing.
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
            if pvp:
                kwargs.update(game_master.search_pvp_move(kwargs["name"]))
            else:
                kwargs.update(game_master.search_pve_move(kwargs["name"]))
        self.pokeType = kwargs["pokeType"]
        self.power = kwargs["power"]
        self.energy = kwargs["energy"]
        self.duration = kwargs["duration"]
        self.dws = kwargs["dws"]
        if "effect" in kwargs:
            self.effect = kwargs["effect"]
