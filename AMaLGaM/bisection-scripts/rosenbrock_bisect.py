import os
from os import listdir
import shutil
import copy
import json
import subprocess


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


#print("The EA is going to be ran {} times.".format(str(ncommands)))

# Clean-up previous attempts
files_to_delete = datafiles(".")
for file in files_to_delete:
    os.remove(file)
if not os.path.exists("results"):
    os.mkdir("results")
if not os.path.exists("data"):
    os.mkdir("data")

with open("results.dat", "w") as file:
    file.write("i L Pop\n")
    file.close()

prob_size = [5, 10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5120, 10240,
             20480, 40960, 81920, 163840, 327680, 655360, 1310720, 2621440, 5242880]

i = 0
N = 10
N_limit = 40960
VTR_n = 0

cmd = "amalgam-grey.exe"
flags = ["-g", "-v", "-r", "-s"]
pro = [7]
dim = [1]
low = [-115]
upp = [-100]
rot = [0]
tau = [0.35]  # Re-written by -g
dmd = [1]  # Re-written by -g
srt = [0.9]  # Re-written by -g
eva = [100000000000]
vtr = [0.0000000001]
imp = [0]  # Re-written by -g
tol = [0.0000000000000000001]

popPerSize = {}

for L in prob_size:
    nop = [L]
    psz = [L]

    while VTR_n < 10:
        if N >= N_limit:
            break
        pop = [N]
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

        output = os.popen(str(commands[0])).readlines()

        if output[-1].rstrip() == "VTR reached - terminating":
            VTR_n += 1
            print(str(i) + " - " + str(VTR_n) + "x VTR for pop size " + str(N))
        else:
            print(str(i) + " - " + "cant reach 10x VTR with pop size " + str(N) + ", doubling N")
            VTR_n = 0
            N = N * 2

    # No convergence
    if VTR_n != 10:
        break

    VTR_n = 0

    b = N
    a = N/2
    N = round((a+b) / 2)

    limit = 20

    while (abs(a-b) > 1 and limit > 0):
        while VTR_n < 10:
            pop = [N]
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

            output = os.popen(str(commands[0])).readlines()

            if output[-1].rstrip() == "VTR reached - terminating":
                VTR_n += 1
                print(str(VTR_n) + "x VTR for pop size " + str(N))
            else:
                print(str(i) + " - " + "failed with pop size " + str(N) + ", checking higher range")
                VTR_n = 0
                a = N
                N = round((a+b) / 2)
                if (abs(a-b) <= 1):
                    break
                limit -= 1

        print(str(i) + " - " + "succeeded with pop size " + str(N) + ", checking lower range")
        VTR_n = 0
        b = N
        N = round((a+b) / 2)

        limit -= 1

    if limit == 0:
        print(str(i) + " - " + "limit of iterations reached")
        N = b

    results_path = "results\\" + str(i)
    if not os.path.exists(results_path):
        os.mkdir(results_path)

    with open("cmd.json.dat", "w") as file:
        file.write(json.dumps(commands[0].params))
        file.close()
        shutil.move("cmd.json.dat", results_path)

    with open("results.dat", "a") as file:
        file.write(str(i) + " " + str(L) + " " + str(N) + "\n")
        file.close()

    files_to_move = listdir("data/")
    for file in files_to_move:
        shutil.copy("data/" + file, results_path)

    print(str(i) + " - " + "Problem with size " + str(L) + " solved with population size " + str(N))

    popPerSize[L] = N

    i += 1
    N = 10
    VTR_n = 0

    with open("popPerSizeGrayRosenbrock.dat", "w") as file:
        file.write(str(popPerSize))
        file.close()

    #percent_done = "%.2f" % ((i + 1)/ncommands * 100)
    # print("Run #{} finished, {}% done.".format(str(i), percent_done))
