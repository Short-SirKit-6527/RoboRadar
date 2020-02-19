import roboradar

if __name__ == "__main__" or __name__ == "independent":
    if roboradar.conf["TEAM"]["NUMBER"] == 0:
        num = input("TEAM.NUMBER option is set to 0, please enter one: ")
        try:
            roboradar.conf["TEAM"]["NUMBER"] = float(num.strip())
        except ValueError:
            print("No TEAM.NUMBER entered, or non-numeric input given.")
            exit(1)
    if roboradar.conf["TEAM"]["NUMBER"] <= 0:
        print("Invalid TEAM.NUMBER. TEAM.NUMBER must be greater than 0.")
        exit(1)
    if int(roboradar.conf["TEAM"]["NUMBER"]) != roboradar.conf["TEAM"]["NUMBER"]:
        print("Invalid TEAM.NUMBER. TEAM.NUMBER must be an integer.")
        exit(1)
    if not isinstance(roboradar.conf["TEAM"]["NUMBER"], int):
        roboradar.conf["TEAM"]["NUMBER"] = int(roboradar.conf["TEAM"]["NUMBER"])
    if len(str(roboradar.conf["TEAM"]["NUMBER"])) > 4:
        print("Invalid TEAM.NUMBER. TEAM.NUMBER must be 4 digits or less.")
        exit(1)
    roboradar.config.set_nt_address(roboradar.conf["TEAM"]["NUMBER"])
    roboradar.conf = roboradar.config.get_config()
    roboradar.start_independent()
