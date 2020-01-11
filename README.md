
# GoBattleSim-Python

Tools to play around with [GoBattleSim-Engine](https://github.com/biowpn/GoBattleSim-Engine), including GameMaster parser & PokeQuery builder.


## Prerequisites

64-bit Windows

64-bit Python 3.5+

## Installing

`git clone` the repository and install:

```
pip install -e .
```

I'll introduce each module by a step-by-step example of generating a **kanto starter battle matrix** from raw GAME MASTER.

## Module: Game Master

The official Game Master [GAME_MASTER.json](game_master/GAME_MASTER.json) can be found in online resources such as [this repository](https://github.com/pokemongo-dev-contrib/pokemongo-game-master).

Let's make the big and heavy Game Master more organized:

```
python -m gobattlesim.GameMaster game_master/GAME_MASTER.json -o examples/gbs_game_master.json
```

The result [gbs_game_master.json](examples/gbs_game_master.json) can be used to configure GoBattleSim Engine.

## Module: PokeQuery

We usually simulate many combinations of Pokemon and Move at a time (batch simulation). Specifying each one of them by hand could sometimes be very tedious. Module `PokeQuery` is here to help. It generates such combinations based on special queries (let's called them `PokeQuery`), which works much like the in-game search bar.

In our example, we can do:

```
python -m gobattlesim.PokeQuery "(charmander,bulbasaur,squirtle) & !(purified,shadow,fall,norm)" "*" "*" -c examples/gbs_game_master.json -o examples/kanto_starters.csv
```

- The nasty term "`& !(purified,shadow,fall,norm)`" is used to filter out those special forms, leaving only the OG starters.

- "`*`" matches all moves in the Pokemon's movepool.

- "`-c examples/gbs_game_master.json`" uses our Game Master from the previous step.

- "`-o examples/kanto_starters.csv`" saves the generated Pokemon list to the file we desire. Other format options are available; run with "`-h`" for details.

## Module: Battle Matrix

Great, now we have species and moves information ready, but we are still missing the Pokemon stats (attack, defense, maxHP). Our next Module `Matrix` can derive stats for each Pokemon based on the targe PvP league.

Let's do:

```
python -m gobattlesim.Matrix examples/kanto_starters.csv -c examples/gbs_game_master.json --league great --pokemon -o examples/kanto_starters_with_stats.csv
```

- "`--league great`" tells the tool to derive the stats based on target CP 1500.

- "`--pokemon`" tells the tool to only export the pokemon pool and not run the matrix. It is a good habit to verify the input before simulation. In this instance we want to check whether the derived stats are correct.

To run the matrix simulations, just remove the "`--pokemon`" flag (and change the output path):

```
python -m gobattlesim.Matrix examples/kanto_starters.csv -c examples/gbs_game_master.json --league great -o examples/matrix.csv
```

Note that we can also use [kanto_starters_with_stats.csv](examples/kanto_starters_with_stats.csv) from earlier step. This way the tool can grab the derived stats instead of doing the derivation again.

## Module: Engine

This is the core module, the juice of the meat.

To test the `Engine` module works with your machine:

```
python -m gobattlesim
```

If no error pops up, then you are good to go!

If othwerise the error says:

```
WindowsError: ... not a valid Win32 application
```

This could be that your Python is 32-bit. I only compiled a 64-bit `libGoBattleSim.dll`. 
You can either install a 64-bit Python, or build the library from [source](https://github.com/biowpn/GoBattleSim-Engine) yourself.

Of course, it's 100% fine to use the other tools without the `Engine` module.

`Engine` takes different types of simulation input, including `BattleMatrix`. Refer to [GoBattleSim-Engine/examples](https://github.com/biowpn/GoBattleSim-Engine/tree/master/examples) for other types of simulation input supported.

Using above `Matrix` module, we can alternatively save the actual simulation input and check it:

```
python -m gobattlesim.Matrix examples/kanto_starters.csv -c examples/gbs_game_master.json --league great -iz -o examples/matrix_input.json
```

- The "`-i`" exports the simulation input instead of running the matrix.

- The "`-z`" keeps only the necessary fields for Pokemon.

We can then directly use `Engine` to process the input:

```
python -m gobattlesim examples/matrix_input.json -c examples/gbs_game_master.json
```
