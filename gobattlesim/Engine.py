
'''
This module provide methods to access GoBattleSim engine.
'''

import argparse
from ctypes import *
import json
import os
import platform
import sys

if platform.system() == "Windows":
    lib = CDLL(os.path.join(os.path.dirname(__file__), "libGoBattleSim.dll"))
else:
    lib = CDLL(os.path.join(os.path.dirname(__file__), "libGoBattleSim.so"))


class GBS:

    lib.GBS_version.argtypes = []
    lib.GBS_version.restype = c_char_p
    @staticmethod
    def version():
        return lib.GBS_version().decode()

    lib.GBS_error.argtypes = []
    lib.GBS_error.restype = c_char_p
    @staticmethod
    def error():
        return lib.GBS_error().decode()

    lib.GBS_config.argtypes = [c_char_p]
    lib.GBS_config.restype = c_char_p
    @staticmethod
    def config(game_master=None):
        if game_master is not None:
            g_str = json.dumps(game_master)
            lib.GBS_config(g_str.encode())
        g_str = lib.GBS_config(None).decode()
        return json.loads(g_str)

    lib.GBS_prepare.argtypes = [c_char_p]
    lib.GBS_prepare.restype = c_void_p
    @staticmethod
    def prepare(sim_input):
        in_str = json.dumps(sim_input)
        lib.GBS_prepare(in_str.encode())

    lib.GBS_run.argtypes = []
    lib.GBS_run.restype = c_void_p
    @staticmethod
    def run():
        lib.GBS_run()

    lib.GBS_collect.argtypes = []
    lib.GBS_collect.restype = c_char_p
    @staticmethod
    def collect():
        out_str = lib.GBS_collect().decode()
        return json.loads(out_str)


def print_version():
    print("GoBattleSim Engine " + GBS.version())


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
        return 0

    if args.config is None:
        print(json.dumps(GBS.config(), indent=4))
        return 0

    if not args.sim_input:
        print_version()
        return 0

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
        return -1

    json.dump(sim_output, args.out, indent=4)


if __name__ == "__main__":
    main()
