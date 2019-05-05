
# GoBattleSim Python API

A Pokemon Go Battle Simulator (GoBattleSim) with Python API.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

64-bit Windows Operating System

### Installing

First, install the package using pip in command line window:

```
pip install gobattlesim
```

Right now, there is only the core <b>engine</b> sub-module available.
It's enough to run any multi-player raid/gym battles, but you'd need to specify a lot of game parameters manually.
In the future, I'll add some sort of game master parser and other useful high-level application functions (like find_best_counter()).

For now, include gobattlesim engine as:

```
include gobattlesim.engine
```

If no error pops up, then you are good to go!

## Running the tests

A [demo.py](demo.py) has been given in the repo. Run that file and it should produce some battle results.


## Contributing

.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/ymenghank/GoBattleSim-Python). 

## Authors

* **Hank Meng** - *Initial work* - [BIOWP](https://github.com/ymenghank)

See also the list of [contributors](https://github.com/ymenghank/GoBattleSim-Python) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Web GoBattleSim (https://github.com/ymenghank/GoBattleSim) has been for over a year. A lot of improvements have been made, but the key issue persists - speed performance. 
So I wanted to make a faster one. I want to make it fly. And there it is, core engine written in C++, exported as DLL, and wrapped in Python.
