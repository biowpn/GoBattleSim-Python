
# GoBattleSim-Python

Wrapper for [GoBattleSim-Engine](https://github.com/biowpn/GoBattleSim-Engine). Also includes GameMaster & PokeQuery module.


## Prerequisites

64-bit Windows/Linux

64-bit Python 3.5+

## Installing

`git clone` the repository and install the package as:

```
pip install -e .
```

To test the package is good:

```
python -m gobattlesim.test
```

If no error pops up, then you are good to go!

Some of the common errors include:

```
WindowsError: ... not a valid Win32 application
```

This could be that your Python is 32-bit. I only compiled a 64-bit library. Therefore, again, 64-bit Python is required.

## Usage: Game Master parsing

The official game master is not very organized. To make it more so, you can do

```
python -m gobattlesim.GameMaster data/GAME_MASTER.json -o data/GBS_GAME_MASTER.json
```

The result can be used to configure [GoBattleSim-Engine](https://github.com/biowpn/GoBattleSim-Engine).

## Usage: PokeQuery

Finding Pokemon matching some criteria in game master. For example:

```
python -m gobattlesim.PokeQuery "fire & flying" data/GAME_MASTER.json
```

This should return the list of Pokemon that are Fire and Flying dual-typed. 

Most of the in-game search features are supported. You can also search by base stats.

Other options are also available; run with `-h` to see the list of them.
