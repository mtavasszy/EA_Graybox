import os
from os import listdir
import shutil
import copy
import json
import time


class Command:
    def __init__(self, cmd, flags, params, param_order):
        self.cmd = cmd
        self.flags = flags
        self.params = params
        self.param_order = param_order

    def __repr__(self):
        flagstr = " ".join(self.flags)
        parlist = list(map(lambda p: str(self.params[p]), self.params))
        paramstr = " ".join(parlist)
        return " ".join([self.cmd, flagstr, paramstr])


def datafiles(path):
    return [f for f in listdir(path)
            if os.path.isfile(f)
            and f.endswith(".dat")]


def create_commands(cmd, flags, params, param_order):
    c = Command(cmd, flags, {}, param_order)
    return create_commands_rec(c, params, param_order)


def create_commands_rec(base_command, params, param_order):
    commands = []
    param = param_order[0]

    for val in params[param]:
        command = copy.deepcopy(base_command)
        command.params[param] = val
        commands.append(command)

    if len(param_order) == 1:
        return commands

    full_commands = []

    for new_command in commands:
        full_commands += create_commands_rec(new_command, params, param_order[1::])

    return full_commands


param_order = ["pro", "dim", "low", "upp", "rot", "tau", "pop",
               "nop", "dmd", "srt", "eva", "vtr", "imp", "tol", "sec"]

base = "gomea\\\\gomea.exe"
flags = ["-g", "-r", "-f 1", "-b"]

results = listdir("results")
for result in results:
    if "Black" in result:
        cmd = "results/" + result + "/cmd.json.dat"
        with open(cmd) as f:
            params = eval(f.readlines()[0])
        if params["pro"] == 0:
            problem = "Sphere"
        elif params["pro"] == 7:
            problem = "Rosenbrock"
        else:
            problem = "Ellipsoid"

        params["sec"] = 1000000000
        command = Command(base, flags, params, param_order)
        print(command)
        output = os.popen(str(command)).readlines()[0].split()

        time_taken = output[5]
        evals = output[1]
        n = result.split("-")[-1]
        with open("data/cmd.json.dat", "w") as file:
            file.write(json.dumps(command.params))

        with open("data/time.dat", "w") as file:
            file.write(str(time_taken))

        with open("data/statistics.dat", "w") as file:
            t = str(int(float(evals)))
            tt = t + " " + t + " " + t + " " + t + " \r\n"
            file.write(tt + tt + tt + tt)

        results_path = "results\\" + "popPerSizeGomea" + problem + \
            str(params["vtr"]) + "-" + str(params["dim"]) + "-" + str(n)

        files_to_move = listdir("data/")
        if not os.path.exists(results_path):
            os.mkdir(results_path)
        for file in files_to_move:
            print("data/" + file)
            print(results_path)
            shutil.move("data/" + file, results_path)
