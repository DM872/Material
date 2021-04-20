import tsputil
from collections import OrderedDict
import pyomo.environ as po
import time

##################################################
MY_ID = 35  # YOUR_ID
##################################################


def solve_Dantzig(points, subtours=[]):
    points = list(points)
    V = set(range(len(points)))
    T = V
    A = [(i, j) for i in V for j in V if i != j]
    AT = [(i, j, t) for (i, j) in A for t in T]
    cost = {a: tsputil.distance(points[a[0]], points[a[1]]) for a in A}

    m = po.ConcreteModel("Dantzig")
    # m.setPresolve(SCIP_PARAMSETTING.OFF)
    # m.setHeuristics(SCIP_PARAMSETTING.OFF)
    # m.disablePropagation()
    # m.setCharParam("lp/initalgorithm", "p")  # let's use the primal simplex
    # solving stops, if the relative gap = |primal - dual|/MIN(|dual|,|primal|) is below the given value
    #m.setParam("limits/gap", 1.0)
    # maximal memory usage in MB; reported memory usage is lower than real memory usage! default: 8796093022208
    #m.setParam("limits/memory", 32000)
    # m.setParam("limits/time", 100)  # maximal time in seconds to run
    infinity = float('inf')
    # BEGIN: Write here your model
    m.x = po.Var(AT, bounds=(0, 1), domain=po.Binary)

    # Objective
    m.OBJ = po.Objective(expr=sum(cost[a] * m.x[(a[0], a[1], t)]
                                  for a in A for t in T), sense=po.minimize)

    # Constraints
    m.visit_once = po.ConstraintList()
    for v in V:
        m.visit_once.add(expr=sum(m.x[(v, j, t)] for j in V if (v, j) in A for t in T) == 1)

    m.flow_balance = po.ConstraintList()
    for v in V:
        for t in T-{0}:
            m.flow_balance.add(expr=sum(m.x[(j, v, t-1)] for j in V if (j, v) in A) -
                               sum(m.x[(v, j, t)] for j in V if (v, j) in A) == 0)

    for v in V:
        m.flow_balance.add(expr=sum(m.x[(j, v, len(V)-1)] for j in V if (
            j, v) in A) - sum(m.x[(v, j, 0)] for j in V if (v, j) in A) == 0)

    # END

    # m.pprint()
    # m.write("svestka.lp")
    solver = po.SolverFactory('gurobi')
    results = solver.solve(m, tee=True, keepfiles=False)

    if (results.solver.status == po.SolverStatus.ok) and (results.solver.termination_condition == po.TerminationCondition.optimal):
        print('The optimal objective is ', m.OBJ())
        return {(i, j): sum(m.x[i, j, t]() for t in T) for i, j in A}
    else:
        print("Something wrong")
        exit(0)


import sys

if __name__ == '__main__':
    if len(sys.argv) == 1:
        # BEGIN: Update this part with what you need
        points = tsputil.Cities(20, seed=MY_ID)
        # plot_situation(points)
        t0 = time.perf_counter()
        lpsol = solve_Dantzig(points)
        t1 = time.perf_counter()
        print("Computation time {:.2f}".format(t1-t0))
        tsputil.plot_situation(points, lpsol)
        # cutting_plane_alg(points)
        # END
    elif len(sys.argv) == 2:
        # BEGIN: Update this part for Task 7 and on
        locations = tsputil.read_instance(sys.argv[1])
        # plot_situation(locations)
        # lpsol = solve_tsplp(locations)
        # plot_situation(locations, lpsol)
        # cutting_plane_alg(locations)
        # END
    else:
        print('Use either with no input file or with an input file argument.')
