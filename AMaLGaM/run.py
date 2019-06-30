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


dir = "./popPerSize/"
for filename in os.listdir(dir):
    pro = 0
    pro = 13 if "Ellipsoid" in filename else pro
    pro = 7 if "Rosenbrock" in filename else pro
    pro = 0 if "Sphere" in filename else pro

    vtr = 0
    vtr = 0.0000001 if "E-7" in filename else vtr
    vtr = 0.0000000001 if "E-10" in filename else vtr

    cmd = ""
    cmd = "amalgam-grey.exe" if "Gray" in filename else cmd
    cmd = "amalgam-black.exe" if "Black" in filename else cmd
    cmd = "gomea\\\\gomea.exe" if "Gomea" in filename else cmd

    with open(dir + filename) as f:
        popPerSize = eval(f.readlines()[0])

    flags = ["-g", "-r"]
    pro = [pro]
    # dim = [1]
    low = [-115]
    upp = [100] if pro == [13] else [-100]
    rot = [0]
    tau = [0.35]  # Re-written by -g
    # pop = [5, 10, 30]  # Re-written by -g
    # nop = [1]
    dmd = [1]  # Re-written by -g
    srt = [0.9]  # Re-written by -g
    eva = [100000000000]
    vtr = [vtr]
    imp = [0]  # Re-written by -g
    tol = [1e-19]
    # psz = [30]

    for size in popPerSize.keys():
        pop = [popPerSize[size]]
        if "Gray" in filename:
            psz = size
            nop = int(size/5) if pro == [13] else size
            dim = 5 if pro == [13] else 1
            psz = [psz]
        elif "Black" in filename:
            dim = size
            nop = 1
        elif "Gomea" in filename:
            dim = size
            nop = 1
            sec = [1000000000]

        dim = [dim]
        nop = [nop]

        # How many times to run each experiment
        n_runs = 10

        params = {"pro": pro, "dim": dim, "low": low,
                  "upp": upp, "rot": rot,
                  "tau": tau, "pop": pop,
                  "nop": nop, "dmd": dmd,
                  "srt": srt, "eva": eva,
                  "vtr": vtr, "imp": imp,
                  "tol": tol}

        param_order = ["pro", "dim", "low", "upp", "rot", "tau", "pop",
                       "nop", "dmd", "srt", "eva", "vtr", "imp", "tol"]

        if "Gray" in filename:
            params["psz"] = psz
            param_order.append("psz")
        if "Gomea" in filename:
            params["sec"] = sec
            param_order.append("sec")

        commands = create_commands(cmd, flags, params, param_order)

        # Clean-up previous attempts
        files_to_delete = datafiles(".")
        for file in files_to_delete:
            os.remove(file)

        if not os.path.exists("results"):
            os.mkdir("results")
        if not os.path.exists("data"):
            os.mkdir("data")

        for i in range(len(commands)):
            n = 0
            while n < n_runs:
                results_path = "results\\" + filename + "-" + str(size) + "-" + str(n)
                if not os.path.exists(results_path):
                    os.mkdir(results_path)

                print(commands[i])

                time1 = time.time()
                output = os.popen(str(commands[i])).readlines()
                time2 = time.time()
                time_taken = time2 - time1
                print(time_taken)
                if output[-1].rstrip() == "VTR reached - terminating" or "Gomea" in filename:
                    with open("data/cmd.json.dat", "w") as file:
                        file.write(json.dumps(commands[i].params))

                    with open("data/time.dat", "w") as file:
                        file.write(str(time_taken))

                    if "Gomea" in filename:
                        evals = output[0].split()[1]
                        with open("data/statistics.dat", "w") as file:
                            t = str(int(float(evals)))
                            tt = t + " " + t + " " + t + " " + t + " \r\n"
                            file.write(tt + tt + tt + tt)

                    files_to_move = listdir("data/")
                    for file in files_to_move:
                        shutil.move("data/" + file, results_path)

                    n += 1
                else:
                    files_to_delete = listdir("data/")
                    for file in files_to_move:
                        shutil.rmtree("data/" + file, results_path)
