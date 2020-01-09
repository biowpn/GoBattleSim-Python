
import argparse
import json
import sys

from .engine import GBS


def print_version():
    print("GoBattleSim Engine " + GBS.version())
    exit(0)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("sim_input", nargs="?",
                        help="simulation input json")
    parser.add_argument("-v", "--version", action="store_true",
                        help="show GBS engine version and exit")
    parser.add_argument("-c", "--config", nargs="?", default=False,
                        help="print game master, or (with argument) set game master by path")
    parser.add_argument("-o", "--out", type=argparse.FileType('w'), default=sys.stdout,
                        help="file to save simulation output")
    args = parser.parse_args()

    if args.version:
        print_version()

    if args.config is None:
        print(json.dumps(GBS.config(), indent=4))
        exit(0)

    if not args.sim_input:
        print_version()

    if args.config:
        with open(args.config) as fd:
            j = json.load(fd)
            GBS.config(j)

    with open(args.sim_input) as fd:
        j = json.load(fd)
    try:
        GBS.prepare(j)
        GBS.run()
        sim_output = GBS.collect()
    except Exception as e:
        gbs_error = GBS.error()
        if gbs_error:
            print("GBS Engine error:", gbs_error)
        else:
            print(str(e))
        return

    json.dump(sim_output, args.out, indent=4)


if __name__ == "__main__":
    main()
