import gurobipy as gp
from data import BinPackingExample, Lister, FFD
import itertools


def bpp(s, B):
    n = len(s)
    U = len(FFD(s, B))

    # Your Gurobi model for the compact formulation
    return model


def solveBinPacking(s, B):
    n = len(s)
    U = len(FFD(s, B))
    model = bpp(s, B)
    solver = po.SolverFactory('glpk')
    results = solver.solve(model)
    bins = [[] for i in range(U)]
    for (i, j) in model.var_indices:
        if model.x[i, j]() > .5:
            bins[j].append(s[i])
    for i in range(bins.count([])):
        bins.remove([])
    for b in bins:
        b.sort()
    bins.sort()
    return bins


if __name__ == '__main__':
    # s, B = BinPackingExample()
    s, B = Lister()
    bins = solveBinPacking(s, B)
    print(len(bins))
    for b in bins:
        print((b, sum(b)))
