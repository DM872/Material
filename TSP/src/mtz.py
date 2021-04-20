import tsputil
from collections import OrderedDict
import pyomo.environ as po
import time

##################################################
MY_ID = 35  # YOUR_ID
##################################################


def solve_MTZ(points, subtours=[]):
    points = list(points)
    V = set(range(len(points)))
    E = [(i, j) for i in V for j in V if i != j]

    m = po.ConcreteModel("MTZ")
    # m.setPresolve(SCIP_PARAMSETTING.OFF)
    # m.setHeuristics(SCIP_PARAMSETTING.OFF)
    # m.disablePropagation()
    # m.setCharParam("lp/initalgorithm", "p")  # let's use the primal simplex
    # solving stops, if the relative gap = |primal - dual|/MIN(|dual|,|primal|) is below the given value
    #m.setParam("limits/gap", 1.0)
    # maximal memory usage in MB; reported memory usage is lower than real memory usage! default: 8796093022208
    #m.setParam("limits/memory", 32000)
    # m.setParam("limits/time", 100)  # maximal time in seconds to run

    # BEGIN: Write here your model
    m.x = po.Var(E, bounds=(0, 1), domain=po.Binary)
    m.u = po.Var(V-{0}, bounds=(0, len(V)-2), domain=po.Reals)

    # Objective
    m.OBJ = po.Objective(expr=sum(tsputil.distance(
        points[e[0]], points[e[1]]) * m.x[e] for e in E), sense=po.minimize)

    # Constraints
    m.mass_balance = po.ConstraintList()
    for v in V:
        m.mass_balance.add(expr=sum(m.x[(v, i)] for i in V if (v, i) in E) == 1)
        m.mass_balance.add(expr=sum(m.x[(i, v)] for i in V if (i, v) in E) == 1)

    m.counter = po.ConstraintList()
    for (i, j) in E:
        if i == 0 or j == 0:
            continue
        m.counter.add(expr=m.u[i]+1 <= m.u[j] + len(V)*(1-m.x[i, j]))
    # END

    #m.pprint()
    #m.write("mtz.lp")
    solver = po.SolverFactory('glpk')
    results = solver.solve(m, tee=True, keepfiles=False)

    if (results.solver.status == po.SolverStatus.ok) and (results.solver.termination_condition == po.TerminationCondition.optimal):
        print('The optimal objective is ', m.OBJ())
        return {(i, j): m.x[i, j]() for i, j in E}
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
        lpsol = solve_MTZ(points)
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
