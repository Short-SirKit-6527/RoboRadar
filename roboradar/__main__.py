#!/usr/bin/python3

import os
try:
    import roboradar
except ImportError:
    import __init__ as roboradar
try:
    from roboradar import config
except ImportError:
    import config
import argparse


def file_path(p=None, *args, **kwargs):
    if p is None:
        return None
    elif os.path.exists(p):
        return p
    else:
        raise FileNotFoundError(p)


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local', action='store_true')
    parser.add_argument('-c', '--conf', type=file_path)
    options = parser.parse_args()
    if options.conf is not None:
        config.load_config(options.conf)
    conf = config.get_config()
    if options.local:
        conf["ROBOT"]["IP_ADDRESS"] = "127.0.0.1"
        conf["ROBOT"]["IP_ADDRESS_SET"] = True
        config.set_config(conf)
    else:
        if conf["TEAM"]["NUMBER"] == 0:
            num = input("TEAM.NUMBER option is set to 0, please enter one: ")
            try:
                conf["TEAM"]["NUMBER"] = float(num.strip())
            except ValueError:
                print("No TEAM.NUMBER entered, or non-numeric input given.")
                exit(1)
        if conf["TEAM"]["NUMBER"] <= 0:
            print("Invalid TEAM.NUMBER. TEAM.NUMBER must be greater than 0.")
            exit(1)
        if int(conf["TEAM"]["NUMBER"]) != conf["TEAM"]["NUMBER"]:
            print("Invalid TEAM.NUMBER. TEAM.NUMBER must be an integer.")
            exit(1)
        if not isinstance(conf["TEAM"]["NUMBER"], int):
            conf["TEAM"]["NUMBER"] = int(conf["TEAM"]["NUMBER"])
        if len(str(conf["TEAM"]["NUMBER"])) > 4:
            print("Invalid TEAM.NUMBER. TEAM.NUMBER must be 4 digits or less.")
            exit(1)
        config.set_nt_address(conf["TEAM"]["NUMBER"])
    conf = config.get_config()
    roboradar.start_independent()


if __name__ == "__main__":
    start()
