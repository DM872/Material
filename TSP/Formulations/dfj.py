import tsputil
from collections import OrderedDict
import pyomo.environ as po
import time
import sys

from itertools import chain, combinations


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def solve_DFJ(points, subtours=[], vartype=po.Binary, solver="gurobi", silent=True):
    points=list(points)
    V = list(range(len(points)))
    E = [(i,j) for i in V for j in V if i<j] # complete graph


    subtours = list(powerset(range(len(points))))
    # The first element of the list is the empty set and the last element is the full set, hence we remove them.
    subtours = subtours[1:(len(subtours)-1)]

    print(len(subtours))
    print(sys.getsizeof(subtours)/1024/1024, " MB")

    cost = {e: tsputil.distance(points[e[0]],points[e[1]]) for e in E}
    
    m = po.ConcreteModel("TSP0")
     
    ######### BEGIN: Write here your model for Task 1
    m.x = po.Var(E, bounds=(0.0,1.0), within=vartype)
    
    ## Objective
    m.value = po.Objective(expr=sum(cost[e]*m.x[e] for e in E), sense=po.minimize)
    
    ## Constraints
    m.flow_balance=po.ConstraintList()
    for v in V:
        m.flow_balance.add(expr=sum(m.x[(v,i)] for i in V if (v,i) in E) + sum(m.x[(i,v)] for i in V if (i,v) in E) == 2)
    
    m.subtour_elimination=po.ConstraintList()
    for S in subtours:
        if len(S)>1:
            m.subtour_elimination.add(expr=sum(m.x[(i,j)] for i in S for j in S if i<j)<=len(S)-1)
                                  
    ######### END
    solver = po.SolverFactory(solver) #glpk
    results = solver.solve(m, tee=True, keepfiles=False)

    #m.write("tsplp.lp")
    
    if str(results.Solver.status) == 'ok':
        print('The optimal objective is %g' % m.value())
        return {e: po.value(m.x[e]) for e in E}
    else:
        print("Something wrong in solve_tsp")
        exit(0)

    



if __name__ == '__main__':
   

    ##################################################
    _SIZE = 15
    _SEED = 25  # YOUR_ID
    ##################################################

    if len(sys.argv) == 1:
        # BEGIN: Update this part with what you need
        points = tsputil.Cities(_SIZE, seed=_SEED)
        # plot_situation(points)
        t0 = time.perf_counter()
        lpsol = solve_DFJ(points)
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

