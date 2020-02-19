import json
import os


_conf = {}


def find_config():
    if os.path.exists(os.getcwd() + os.sep + "RoboRadarConfig.json"):
        return os.getcwd() + os.sep + "RoboRadarConfig.json"
    return __file__[:-10] + os.sep + "RoboRadarConfig.json"


def load_config(filePath=None):
    global _conf
    if filePath is None:
        filePath = find_config()
    print(filePath)
    print(find_config())
    with open(filePath) as f:
        _conf = json.load(f)
        if _conf["ROBOT"]["IP_ADDRESS"] is None:
            _conf["ROBOT"]["IP_ADDRESS_SET"] = False
            if _conf["TEAM"]["NUMBER"] != 0:
                set_nt_address(_conf["TEAM"]["NUMBER"])
        else:
            _conf["ROBOT"]["IP_ADDRESS_SET"] = True


def set_nt_address(tn):
    if not _conf["ROBOT"]["IP_ADDRESS_SET"]:
        tn = str(tn).zfill(4)
        tn = (tn[0:2], tn[2:4])
        iaf = _conf["ROBOT"]["IP_ADDRESS_FORMAT"]
        _conf["ROBOT"]["IP_ADDRESS"] = iaf.format(tn[0], tn[1])


def get_config():
    if not _conf:
        load_config()
    return _conf
