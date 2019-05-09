
# GoBattleSim Engine with Python API

A Pokemon Go Battle Simulator (GoBattleSim) with Python API.

## Getting Started

### Prerequisites

64-bit Windows Operating System

64-bit Python 3

### Installing

First, install the package using pip in command line window:

```
pip install gobattlesim
```

<i>Right now, there is only the core `engine` sub-module available.
It's enough to run any multi-player raid/gym battle, but you'd need to specify a lot of game parameters manually.
In the future, I'll add some sort of game master parser and other useful high-level application functions (like find_best_counter()).</i>

Then:

```
import gobattlesim.engine
```

If no error pops up, then you are good to go!

Some of the common errors include:

```
WindowsError: ... not a valid Win32 application
```

This could be that your Python is 32-bit. I only compiled the simulator core into a 64-bit DLL. Therefore, again, 64-bit Python is required.

## Quick Start

Some [examples](examples/) have been given in the repo.


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
