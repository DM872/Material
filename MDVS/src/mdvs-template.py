#!/usr/bin/python3
import argparse
import pyomo.environ as po
import sys


def readData(F):
    data = open(F, 'r')
    header = data.readline().split('\t')
    m = int(header[0])  # Number of depots
    n = int(header[1])  # Number of trips
    k = list(map(lambda z: int(z), header[2:]))
    ######################################
    # TODO: Change here the capacity for ex 2
    ######################################
    # k = [25,25,25,25]
    Ts = []
    for i, line in enumerate(data):
        row = map(lambda z: int(z), line.strip().split('\t'))
        for j, c in enumerate(row):
            if c != -1:
                if i < m and j >= m:  # Pull-out trip
                    Ts += [[i, j, i, c]]
                if i >= m and j < m:  # Pull-in trip
                    Ts += [[(n+m)+i, (n+m)+j, j, c]]
                if i >= m and j >= m:  # Cost of performing j after i
                    for h in range(m):
                        Ts += [[(n+m)+i, j, h, c]]
    # Add reverse arcs
    for i in [i+m for i in range(n)]:
        for h in range(m):
            Ts += [[i, (n+m)+i, h, 0]]
    # Add circulation arcs
    for h in range(m):
        Ts += [[(n+m)+h, h, h, 0]]
    return n, m, k, Ts


def model_mdvs(n, m, k, Arcs):
    # Model
    model = po.ConcreteModel("VehicleScheduling")

    # Determine the set of trips S and of depots D
    # S = set([i+m for i in range(n)])
    model.S = po.Set(initialize=[i+m+n+m for i in range(n)])
    model.N = po.Set(initialize=range(2*(n+m)))
    model.D = po.Set(initialize=range(len(k)))

    print("Number of trips:", len(model.S), " Number of depots:", len(model.D))

    inf = float("inf")
    # Introduce the arc variables
    model.I = po.Set(initialize=[(i, j, h) for i, j, h, _ in Arcs])
    model.x = po.Var(model.I, bounds=(0, inf), within=po.Reals)
    # for h in range(m):
    #    model.x[((n+m)+h, h, h)].ub=k[h]

    # The objective is to minimize the total costs
    model.obj = po.Objective(expr=po.quicksum(model.x[i, j, h]*cost for i, j, h, cost in Arcs))

    print("Posting cover constraints")
    # Cover Constraint

    def cover_constraints(model, i):
        return po.quicksum(model.x[i, j, h] for s, j, h, _ in Arcs if s == i) == 1
    model.cover = po.Constraint(model.S, rule=cover_constraints)

    print("Posting flow balance constraints")
    # Flow Balance Constraint

    def flow_balance_constraint(model, i, h):
        BS = [b for b in Arcs if b[1] == i and b[2] == h]  # .select('*',i,h,'*')
        FS = [f for f in Arcs if f[0] == i and f[3] == h]  # Arcs.select(i,'*',h,'*')
        if FS and BS:
            return po.quicksum(model.x[j, s, h] for j, s, h, _ in BS) - sum(model.x[s, j, h] for s, j, h, _ in FS) == 0
        else:
            return po.Constraint.Skip
    model.flow_balance = po.Constraint(model.N, model.D, rule=flow_balance_constraint)

    print("Posting capacity constraints")
    # Capacity constraint

    def capacity_constraint(model, h):
        return model.x[(n+m)+h, h, h] <= k[h]
    model.capacity_cons = po.Constraint(model.D, rule=capacity_constraint)

    # model.pprint()
    # model.write("mdvs.lp")
    # Optimize
    results = po.SolverFactory("gurobi").solve(model, tee=True)

    if str(results.Solver.status) != 'ok':
        print("Something wrong")
        exit(0)

    print('The optimal objective is %g' % model.obj())
    # Check number of depots and of vehicles
    R = set()
    E = set()
    # x_star = model.getAttr('X', x)

    x_star = {(i, j, h): model.x[i, j, h]() for i, j, h, _ in Arcs}
    # print(x_star)
    ###############################################################
    # TODO: Change here to get the data you need to fill Table 1
    ##############################################################
    sol = {}
    for h in D:
        for s, i, k, c in Arcs:
            if s == h:
                if x_star[h, i, h] > 0.999:
                    if h in sol:
                        sol[h] += 1
                    else:
                        sol[h] = 1
                    R.add(i)
                    E.add(h)

    print("Vehicles:", len(R), " Depots:", len(E), " Sol:", sol)


def main():
    parser = argparse.ArgumentParser(description='MILP solver for timetabling.')
    parser.add_argument(dest="filename", type=str, help='filename')
    parser.add_argument("-e", "--example", type=str, dest="example",
                        default="value", metavar="[value1|value2]", help="Explanation [default: %default]")

    args = parser.parse_args()  # by default it uses sys.argv[1:]

    n, m, k, Arcs = readData(args.filename)
    model_mdvs(n, m, k, Arcs)


if __name__ == "__main__":
    main()
