
# GoBattleSim-Python

Tools to play around with [GoBattleSim-Engine](https://github.com/biowpn/GoBattleSim-Engine), including GameMaster parser & PokeQuery builder.


## Prerequisites

64-bit Windows/Linux

64-bit Python 3.5+

## Installing

`git clone` the repository and install:

```
pip install -e .
```

To test the package is good:

```
python -m gobattlesim
```

If no error pops up, then you are good to go!

If the error says:

```
WindowsError: ... not a valid Win32 application
```

This could be that your Python is 32-bit. I only compiled a 64-bit `lib GoBattleSim`. 
You can either install a 64-bit Python, or recompile GoBattleSim-Engine yourself.

Of course, it's 100% fine to use the other tools without the `Engine` module.

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
python -m gobattlesim.PokeQuery "(charmander,bulbasaur,squirtle) & !(purified,shadow,fall,norm)" "*" "*" -c examples/GAME_MASTER.json -o examples/kanto_starters.csv
```

- The nasty term "`& !(purified,shadow,fall,norm)`" is used to filter out those special forms, leaving only the OG starters.

- "`*`" matches all moves in the Pokemon's movepool.

- "`-c examples/GAME_MASTER.json`" uses our Game Master from the previous step.

- "`-o examples/kanto_starters.csv`" saves the generated Pokemon list to the file we desire. Other formats are also available; run with "`-h`" for more info.

## Module: Battle Matrix

Great, now we have species and moves information ready, but we are still missing the battle stats. We only need to tell our next Module `Matrix` the PvP league we are interested in, and it'll figure out the stats.

First, let's do:

```
python -m gobattlesim.Matrix examples/kanto_starters.csv -c examples/gbs_game_master.json --league great --pokemon -o examples/kanto_starters_with_stats.csv
```

- As always, we use "`-c`" to tell the tool to use our organized Game Master.

- "`--league great`" tells the tool to derive the stats based on target CP 1500.

- "`--pokemon`" tells the tool that we only want to see the pokemon pool, not actually running the matrix. It is a good habit to verify the input before simulation. In this instance we want to check whether the stats are correct.

- As always, we use "`-o`" to save the output to the file we desire.

To run the matrix, remove the "`--pokemon`" flag and change the output path:

```
python -m gobattlesim.Matrix examples/kanto_starters.csv -c examples/gbs_game_master.json --league great -o examples/matrix.csv
```

Note that we can also use [kanto_starters_with_stats.csv](examples/kanto_starters_with_stats.csv). This way it will save some time since the tool can grab the stats instead of deriving them again.

## Module: Engine

This is the core module, the juice of the meat.

`Engine` takes different types of simulation input, including `BattleMatrix`. Refer to [GoBattleSim-Engine/examples](https://github.com/biowpn/GoBattleSim-Engine/tree/master/examples) for other types of simulation input supported.

Using above `Matrix` module, we can alternatively save the actual simulation input and check it:

```
python -m gobattlesim.Matrix examples/kanto_starters.csv -c examples/gbs_game_master.json --league great -iz -o examples/matrix_input.json
```

- The "`-i`" flag tells the `Matrix` to export the simulation input instead of running the matrix.

- The "`-z`" flag tells the `Matrix` to keep only the necessary fields.

We can then directly use `Engine` to process the input:

```
python -m gobattlesim examples/matrix_input.json -c examples/gbs_game_master.json
```

