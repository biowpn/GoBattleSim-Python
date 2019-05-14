
# GoBattleSim Engine with Python API

A Pokemon Go Battle Simulator (GoBattleSim) with Python API.

## Getting Started

### Prerequisites

64-bit Windows/Linux

64-bit Python 3.5+

### Installing

The below instructions will get you a local version of GoBattleSim engine.

First, install the package using pip in command line window:

```
pip install gobattlesim
```

Then:

```
import gobattlesim.interface
```

If no error pops up, then you are good to go!

Some of the common errors include:

```
WindowsError: ... not a valid Win32 application
```

This could be that your Python is 32-bit. I only compiled the simulator core into a 64-bit DLL. Therefore, again, 64-bit Python is required.

## Quick Start

The `gobattlesim.interface` module saves a lot of typing. To use the module, you need to first acquire a game master file in json format.
You can find one in sources online such as [this repo](https://github.com/pokemongo-dev-contrib/pokemongo-game-master).

Suppose the game master file is "GAME_MASTER.json" and is placed in the same folder with your script. Then do:

```
import gobattlesim.interface as gbs

gbs.GameMaster("GAME_MASTER.json").apply()
```

Now game master file has been parsed and applied to the simulator.

Let's run some simulations on the classic Tyranitar Duo with two teams of max perfect Machamp:

```
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

```

The `result` is a dict containing some performance metrics, such as "Average TDO%". A sample output could be:

```
Machamp duo T4 Tyranitar:
{'win': 1.0, 'duration': 130157.966, 'tdo_percent': 1.010376666666664, 'num_deaths': 3.506}
```

One may find `gobattlesim.interface.quick_raid_battle` (and `gobattlesim.interface.quick_pvp_battle`) rather limited, 
and may want more control on the simulations. If so, the `gobattlesim.engine` is best for this purpose.

More [examples](https://github.com/ymenghank/GoBattleSim-Python/tree/master/examples) of using `gobattlesim.engine` alone to run simulations have been given in the repo.


## Documentations

Coming up!


## Contributing

The feature requests and known bugs are listed in the [issues](https://github.com/ymenghank/GoBattleSim-Python/issues) section.
You are more than welcome to help by adding items to that list!

Note that this repo is the interface part of the simulator. The core part that contains the actual battle logic will be in another repo.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ymenghank/GoBattleSim-Python/tags). 

## Author

* **Hank Meng** - *Initial work* - [BIOWP](https://github.com/ymenghank)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* [Web GoBattleSim](https://github.com/ymenghank/GoBattleSim) has been for over a year. A lot of improvements have been made, but the key issue persists - speed performance. 
So I wanted to make a faster one. I want to make it fly. And there it is, core engine written in C++, exported as DLL, and wrapped in Python.
