from numpy import round

import sys
sys.path.append("..")  # Adds the parent directory to the sys.path
import data 
#from data import FFD, BinPackingExample
import gurobipy as gp
import matplotlib.pyplot as plt
import math

LOG = True
EPS = 1.e-6  # error margin allowed for rounding


def generate_initial_patterns(s, B):
    # Generate initial patterns with one size for each item width
    t = []
    m = len(s)
    for i in range(m):
        pat = [0]*m  # vector of number of orders to be packed into one bin
        pat[i] = int(B/s[i])
        t.append(pat)
    return t


def solve_pricing_problem(s, B, pi):

    subMIP = gp.Model("Knapsack")     # knapsack sub-problem
    # Turning off presolve
    #subMIP.setParam(gp.GRB.param.Presolve, 0)
    subMIP.setParam(gp.GRB.param.OutputFlag, 0)
    # Setting the verbosity level to 0
    # subMIP.hideOutput()
    K = len(s)
    y = {}
    #print(pi, s)
    for i in range(K):
        y[i] = subMIP.addVar(lb=0, vtype=gp.GRB.INTEGER, name="y(%s)" % i)

    subMIP.addConstr(gp.quicksum(s[i]*y[i] for i in range(K)) <= B, "Width")

    subMIP.setObjective(gp.quicksum(pi[i]*y[i] for i in range(K)), gp.GRB.MAXIMIZE)
    
    subMIP.optimize()
    pat = [int(round(y[i].x,0)) for i in y]
    return subMIP.objVal, pat


def solve_linear_master_problem_by_cg(s, B, ub):
    """ use column generation (Gilmore-Gomory approach).
    Parameters:
        - s: list of item's width
        - B: bin/roll capacity
    Returns a solution: list of lists, each of which with elements in the bin.
    """
    m = len(s)
    t = generate_initial_patterns(s, B)
    K = len(t)

    if LOG:
        print("sizes of orders=", s)
        print("bins size=", B)
        print("initial patterns", t)
    
    RLMP = gp.Model("Restricted Linear Master Problem")
    RLMP.setParam(gp.GRB.param.Presolve, 0)
    RLMP.Params.OutputFlag = 0 # silent mode

    x = {}
    for k in range(K):
        x[k] = RLMP.addVar(vtype=gp.GRB.CONTINUOUS, name="x(%s)" % k)  # note: we consider the LP relaxation

    orders = {}

    for i in range(m):
        orders[i] = RLMP.addConstr(
            gp.quicksum(t[k][i]*x[k] for k in range(K) if t[k][i] > 0) >= 1, "Order(%s)" % i)

    RLMP.setObjective(gp.quicksum(x[k] for k in range(K)), gp.GRB.MINIMIZE)

    best_dual_bound=-math.inf
    history = []
    iter = 0
    while True:
        iter += 1
        print("="*10,iter)
        RLMP.optimize()
        pi = [c.Pi for c in RLMP.getConstrs()]  # keep dual variables

        z_PP, pattern = solve_pricing_problem(s, B, pi)               

        print("objective of knapsack problem:", z_PP)
        unrestricted_dual_bound=RLMP.ObjVal+ub*(1-z_PP)
        best_dual_bound=max(best_dual_bound, math.ceil(unrestricted_dual_bound))
        history.append((RLMP.ObjVal, unrestricted_dual_bound, best_dual_bound) )

        if z_PP < 1+EPS:  # break if no more columns
            break

        print("Added pattern: ", pattern)
        
        # new pattern
        t.append(pattern)

        # add new column to the master problem        
        col = gp.Column(coeffs=t[K],constrs=RLMP.getConstrs())        
        x[K] = RLMP.addVar(vtype=gp.GRB.CONTINUOUS, obj=1.0, column=col)
        # master.write("MP" + str(iter) + ".lp")
        K += 1
        if iter % 500==0:
            make_plot(history)

    print("LMP solved. Lower bound to MP: ",RLMP.ObjVal)
    print(RLMP.x)
    make_plot(history)
    return t, RLMP


def make_plot(history) -> None:

    plt.plot(list(range(len(history))), [val[0] for val in history], 'o-', c='r', label="z_RLMP")
    #plt.scatter(list(range(len(history))), [val[0] for val in history], c='r')
    plt.plot(list(range(len(history))), [val[1] for val in history], 'o-', c='g', label="lower bound")    
    #plt.scatter(list(range(len(history))), [val[1] for val in history], c='g')
    plt.step(list(range(len(history))), [val[2] for val in history], c='g', where="post", label="ceil(lower bound)")    
    plt.legend()
    
    plt.xlabel('iteration')
    plt.ylabel('objective function value')
    title = 'solution: ' + str(history[-1][0])
    plt.title(title)
    plt.grid(color = 'green', linestyle = '--', linewidth = 0.5)
    plt.show()


def solve_MIP_heuristic(s, B, t, LRPM):
    K = len(t)
    m = len(s)

    # Solve the restricted Linear Master to integrality    
    for x in LRPM.getVars():
        x.vtype=gp.GRB.INTEGER
    
    LRPM.optimize()
    print(LRPM.ObjVal)

    return LRPM.getVars()


def solveBinPacking(s, B, ub):
    t, LRMP = solve_linear_master_problem_by_cg(s, B, ub)
    # Finally, solve the IP
    # if LOG:
    #     master.Params.OutputFlag = 1 # verbose mode
    x = solve_MIP_heuristic(s, B, t, LRMP)

    bins = []
    for k in range(len(t)):
        if x[k].X>0.5:
            bins+=[t[k]]
    if LOG:
        print( "final heuristic solution (price and branch):  objective =", len(bins))
        print( "patterns:")
        for k in range(len(t)):
            if x[k].X > EPS:
                print( "pattern",k,end='')
                print( "\tsizes:",end='')
                print( [s[i] for i in range(len(s)) if t[k][i]>0 for j in range(t[k][i]) ],end='')
                print("--> %s rolls" % int(x[k].X+.5) )
    
    # retrieve solution
    return bins


if __name__ == "__main__":
    
    s, B = data.BinPackingExample()
    #s, B = data.BinPackingLister()
    #w,q,B=data.generateCuttingStockExample()
    #w,q,B=data.CuttingStockExample1()
    #s=data.mkBinPacking(w,q)
    ffd = data.FFD(s, B)

    print("\n\n\nSolution of FFD:")
    print(ffd)
    print(len(ffd), "bins")

    print("\n\n\nBin Packing, column generation:")
    bins = solveBinPacking(s, B, len(ffd))
    print(len(bins), "rolls:")
    print(bins)