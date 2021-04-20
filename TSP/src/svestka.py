import tsputil
from collections import OrderedDict
import pyomo.environ as po
import time

##################################################
MY_ID = 35  # YOUR_ID
##################################################


def solve_Svestka(points, subtours=[]):
    points = list(points)
    V = set(range(len(points)))
    E = [(i, j) for i in V for j in V if i != j]

    m = po.ConcreteModel("Svestka")
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
    m.x = po.Var(E, bounds=(0, 1), domain=po.Binary)
    m.y = po.Var(E, bounds=(0, infinity), domain=po.NonNegativeReals)
    m.f = po.Param(initialize=0.1, domain=po.PositiveReals)

    # Objective
    m.OBJ = po.Objective(expr=sum(tsputil.distance(
        points[e[0]], points[e[1]]) * m.x[e] for e in E), sense=po.minimize)

    # Constraints
    m.arrive_cities = po.ConstraintList()
    for v in V:
        if v == 0:
            m.arrive_cities.add(expr=sum(m.y[(0, j)] for j in V if (0, j) in E) == 1)
        else:
            m.arrive_cities.add(expr=sum(m.y[(j, v)] for j in V if (j, v) in E) >= 1)

    m.flow_gain = po.ConstraintList()
    for v in V-{0}:
        m.flow_gain.add(expr=sum(m.y[(v, j)] for j in V if (v, j) in E) -
                        sum(m.y[(j, v)] for j in V if (j, v) in E) == m.f)

    # cadrinality constraint
    m.only_pos_vars = po.Constraint(expr=sum(m.x[e] for e in E) <= len(V))

    m.link_constraints = po.ConstraintList()
    for e in E:
        m.link_constraints.add(expr=m.y[e] <= (1+len(V)*m.f)*m.x[e])

    # END

    # m.pprint()
    # m.write("svestka.lp")
    solver = po.SolverFactory('gurobi')
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
        lpsol = solve_Svestka(points)
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
