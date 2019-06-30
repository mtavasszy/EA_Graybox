import pandas as pd
from os import listdir
import json
import matplotlib.pyplot as plt
from math import log2

datadir = "results/"


def read_data(dir):
    data_dirs = listdir(dir)
    data_frame = []
    for data in data_dirs:
        data_dir = dir + data + "/"
        stats_file = data_dir + "statistics.dat"
        cmd_file = data_dir + "cmd.json.dat"
        time_file = data_dir + "time.dat"

        with open(cmd_file) as f:
            cmd = json.loads(f.readlines()[0])

        with open(stats_file) as f:
            evals = int(f.readlines()[-2].split()[1])

        with open(time_file) as f:
            time = float(f.readlines()[0])

        problem = ""
        problem = "Sphere" if cmd["pro"] == 0 else problem
        problem = "Rosenbrock" if cmd["pro"] == 7 else problem
        problem = "RotatedEllipsoids" if cmd["pro"] == 13 else problem

        type = ""
        type = "AMaLGaM-Blackbox" if "Black" in data_dir else type
        type = "AMaLGaM-Graybox" if "Gray" in data_dir else type
        type = "Gomea" if "Gomea" in data_dir else type

        problem_size = cmd["psz"] if type == "AMaLGaM-Graybox" else cmd["dim"]

        pop = cmd["pop"]
        vtr = cmd["vtr"]

        if type == "Gomea":
            pop = 36.1 + 7.58*log2(problem_size)

        data_frame.append([problem, type, problem_size, pop, vtr, time, evals])

    return pd.DataFrame(data_frame, columns=["problem", "type", "problem_size", "population", "vtr", "time", "evals"])


df = read_data(datadir)
print(df)
df2 = df.groupby(["problem", "type", "problem_size", "population", "vtr"])
mean = df2.mean().reset_index()
std = df2.std().reset_index()

print(mean)

problems = ["Sphere", "Rosenbrock", "RotatedEllipsoids"]
vtrs = [1E-7, 1E-10]

# Evals vs problem size
for p in problems:
    for vtr in vtrs:
        plt.figure()
        df3 = mean[mean.problem == p][mean.vtr == vtr].pivot(
            index="problem_size", columns="type", values="evals")
        print(df3)
        df4 = std[std.problem == p][std.vtr == vtr].pivot(
            index="problem_size", columns="type", values="evals")
        df3.plot(yerr=df4)
        plt.ylabel("evals")
        plt.yscale("log")
        plt.xscale("log")
        plt.savefig("evals-vs-psize-" + p + "-" + str(vtr) + ".png")
        plt.close()

# Time vs problem size
for p in problems:
    for vtr in vtrs:
        plt.figure()
        df3 = mean[mean.problem == p][mean.vtr == vtr].pivot(
            index="problem_size", columns="type", values="time")
        df4 = std[std.problem == p][std.vtr == vtr].pivot(
            index="problem_size", columns="type", values="time")
        df3.plot(yerr=df4)
        plt.ylabel("time")
        plt.yscale("log")
        plt.xscale("log")
        plt.savefig("time-vs-psize-" + p + "-" + str(vtr) + ".png")
        plt.close()

# Population vs problem size
for p in problems:
    for vtr in vtrs:
        plt.figure()
        df3 = mean[mean.problem == p][mean.vtr == vtr].pivot(
            index="problem_size", columns="type", values="population")
        df3.plot()
        plt.ylabel("population")
        plt.yscale("log")
        plt.xscale("log")
        plt.savefig("pop-vs-psize-" + p + "-" + str(vtr) + ".png")
        plt.close()
