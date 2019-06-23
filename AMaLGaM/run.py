import os
from os import listdir
import shutil
import copy
import json


class Command:
    def __init__(self, cmd, flags, params, param_order):
        self.cmd = cmd
        self.flags = flags
        self.params = params
        self.param_order = param_order

    def __repr__(self):
        flagstr = " ".join(flags)
        parlist = list(map(lambda p: str(self.params[p]), self.params))
        paramstr = " ".join(parlist)
        return " ".join([cmd, flagstr, paramstr])


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


# a.exe -v -g 7 1 -100 100 0 0 0 10 0 0 1000000 -2 0 0.5 10
cmd = "a.exe"
flags = ["-g", "-v", "-s", "-w"]
pro = [1, 2, 7]
dim = [1]
low = [-100]
upp = [100]
rot = [0]
tau = [0]  # Re-written by -g
pop = [5, 10, 30]  # Re-written by -g
nop = [1]
dmd = [1]  # Re-written by -g
srt = [0]  # Re-written by -g
eva = [1000000]
vtr = [-2]
imp = [0]  # Re-written by -g
tol = [0.5]
psz = [30]

# How many times to run each experiment
n_runs = 2

params = {"pro": pro, "dim": dim, "low": low,
          "upp": upp, "rot": rot,
          "tau": tau, "pop": pop,
          "nop": nop, "dmd": dmd,
          "srt": srt, "eva": eva,
          "vtr": vtr, "imp": imp,
          "tol": tol, "psz": psz}

param_order = ["pro", "dim", "low", "upp", "rot", "tau", "pop",
               "nop", "dmd", "srt", "eva", "vtr", "imp", "tol", "psz"]

commands = create_commands(cmd, flags, params, param_order)
ncommands = len(commands)

print("The EA is going to be ran {} times.".format(str(ncommands)))

# Clean-up previous attempts
files_to_delete = datafiles(".")
for file in files_to_delete:
    os.remove(file)

if not os.path.exists("results"):
    os.mkdir("results")

for i in range(len(commands)):
    for n in range(n_runs):
        results_path = "results\\" + str(i) + "_" + str(n)
        if not os.path.exists(results_path):
            os.mkdir(results_path)

        os.popen(str(commands[i])).readlines()

        with open("cmd.json.dat", "w") as file:
            file.write(json.dumps(commands[i].params))

        files_to_move = datafiles(".")
        for file in files_to_move:
            shutil.move(file, results_path)

    percent_done = "%.2f" % ((i + 1)/ncommands * 100)
    print("Run #{} finished, {}% done.".format(str(i), percent_done))
