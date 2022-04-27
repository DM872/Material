import gurobipy as gp
from numpy import round
from data import FFD, BinPackingExample

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

    subMIP = gp.Model("PricingProblem")     # knapsack sub-problem
    # Turning off presolve
    subMIP.setParam(gp.GRB.param.Presolve, 0)
    subMIP.setParam(gp.GRB.param.Method, 0)

    # write here the model

    # solve
    subMIP.optimize()

    # extract the pattern found
    pattern = []

    return subMIP.objVal, pattern


def solve_master_problem_by_cg(s, B):
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

        
    LRRMP = gp.Model("Linear Relaxation of Restricted Master")  # master LP problem
    LRRMP.setParam(gp.GRB.param.Presolve, 0)
    LRRMP.setParam(gp.GRB.param.Method, 0)

    ####
    # YOUR CODE FOR THE MODEL
    ####

    iter = 0
    while True:
        iter += 1

        LRRMP.optimize()

        # Get the values of the dual variables 
        pi = [c.pi for c in LRRMP.getConstrs()]

        z_PP, pattern = solve_pricing_problem(s, B, pi)
        if LOG:
            print("pricing problem:", red_cost)

        # Add condition
        # if no more columns to add
        # break

        # new pattern
        t.append(pattern)

        # add new column to the master problem
    
    bins_created = []
    # get the solution
    return bins_created

def solve_MIP_heuristic(s, B, t):
    K = len(t)
    m = len(s)

    # Solve the restricted Master

    bins = []
    # get the solution

    return bins


def solveBinPacking(s, B):
    t, x = solve_master_problem_by_cg(s, B)
    # Finally, solve the IP
    # if LOG:
    #     master.Params.OutputFlag = 1 # verbose mode
    x = solve_MIP_heuristic.optimize(s, B, t)

    # retrieve solution
    bins = []

    return bins


if __name__ == "__main__":
    s, B = BinPackingExample()
    ffd = FFD(s, B)
    print("\n\n\nSolution of FFD:")
    print(ffd)
    print(len(ffd), "bins")

    print("\n\n\nBin Packing, column generation:")
    bins = solveBinPacking(s, B)
    print(len(bins), "bins:")
    print(bins)
