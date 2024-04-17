import tsputil
from collections import OrderedDict
import gurobipy as gp
from gurobipy import GRB
import time
import myargparse
import sys

from itertools import chain, combinations


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def solve_DFJ(points, subtours=[]):
    points=list(points)
    V = list(range(len(points)))
    E = [(i,j) for i in V for j in V if i<j] # complete graph


    subtours = list(powerset(range(len(points))))
    # The first element of the list is the empty set and the last element is the full set, hence we remove them.
    subtours = subtours[1:(len(subtours)-1)]

    print(len(subtours))
    print(sys.getsizeof(subtours)/1024/1024, " MB")

    cost = {e: tsputil.distance(points[e[0]],points[e[1]]) for e in E}
    
    m = gp.Model("TSP0")
     
    ######### BEGIN: Write here your model for Task 1
    x = m.addVars(E, lb=0.0, ub=1.0, vtype=GRB.BINARY)
    
    ## Objective
    m.setObjective(sum(cost[e] * x[e] for e in E), sense=GRB.MINIMIZE)
    
    ## Constraints
    flow_balance=[]
    for v in V:
        m.addConstr(sum(x[(v,i)] for i in V if (v,i) in E) + sum(x[(i,v)] for i in V if (i,v) in E) == 2)
    
    #subtour_elimination=[]
    for S in subtours:
        if len(S)>1:
            #subtour_elimination=
            m.addConstr(sum(x[(i,j)] for i in S for j in S if i<j)<=len(S)-1)
    
    #m.update()
    #m.display()
    #m.write("tsplp.lp")
    m.optimize()

    if m.status == GRB.status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        return {e: x[e].x for e in E}
    else:
        print("Something wrong in solve_tsp")
        exit(0)

    

if __name__ == '__main__':
    args = myargparse.myargparse()
    if args.instance_file is None: #len(sys.argv) == 1:
        # BEGIN: Update this part with what you need
        points = tsputil.Cities(args.size, seed=args.seed)
        # plot_situation(points)
        t0 = time.perf_counter()
        lpsol = solve_DFJ(points)
        t1 = time.perf_counter()
        print("Computation time {:.2f}".format(t1-t0))
        tsputil.plot_situation(points, lpsol)
        # cutting_plane_alg(points)
        # END
    else: #if len(sys.argv) == 2:
        # BEGIN: Update this part for Task 7 and on
        locations = tsputil.read_instance(args.instance_file) #sys.argv[1])
        # plot_situation(locations)
        # lpsol = solve_tsplp(locations)
        # plot_situation(locations, lpsol)
        # cutting_plane_alg(locations)
        # END
