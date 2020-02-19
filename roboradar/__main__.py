#!/usr/bin/python3

import roboradar
try:
    from roboradar import config
except ImportError:
    import config
import argparse

if __name__ == "__main__" or __name__ == "independent":
    conf = config.get_config()
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', action='store_true')
    options = parser.parse_args()
    if options.l:
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
