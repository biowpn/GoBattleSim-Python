
'''
Provide methods to access for GoBattleSim engine
'''

from ctypes import *
import json
import os
import platform

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
