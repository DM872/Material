import pyomo.environ as po
from data import BinPackingExample, Lister, FFD
import itertools


def bpp(s, B):
    n = len(s)
    U = len(FFD(s, B))
    model = po.ConcreteModel("bpp")
    model.var_indices = po.Set(initialize=itertools.product(range(n), range(U)))
    model.x = model.Var(model.var_indices, within=po.Binary)
    model.y = model.Var(range(U), within=po.Binary)

    model.z = po.Objective(po.quicksum(model.y[j] for j in range(U)), sense=po.minimize)

    model.assign = model.ConstraintList()
    for i in range(n):
        model.assign.add(expr=po.quicksum(model.x[i, j] for j in range(U)) == 1)
    for j in range(U):
        model.add(po.quicksum(s[i]*model.x[i, j]
                              for i in range(n)) <= B*model.y[j], "Capac(%s)" % j)
    # for j in range(U):
    #    for i in range(n):
    #        model.addCons(model.x[i, j] <= model.y[j], "Strong(%s,%s)" % (i, j))

    # model.data = x, y
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
