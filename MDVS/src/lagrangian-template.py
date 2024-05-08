import sys
import random

import pyomo.environ as po


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


def solveSubproblem(h, S, N, D, Arcs, Lambda):
    global n, m, k
    # Model
    model = po.ConcreteModel("VS-Subproblem")
    # The objective is to minimize the total costs

    #########################################
    # TODO: Introduce the arc variables
    ########################################

    ########################################
    # TODO: Introduce the constraints
    ########################################

    # Optimize

    print 'The optimal subproblem value is', model.objVal()

    # Check number of depots and of vehicles
    x_star = model.x()

    sol = {}
    R = {}
    for i, j, k, _ in Arcs if k == h
        if x_star[i, j] > 0.99:
            R[i, j, h] = 1.0

    return model.objVal(), R


def subgradient_optimization(S, N, D, Arcs):
    # This parameter should be reduced with increasing iterations
    mu = 2.0
    Z_UB = sum(map(lambda a: a[3], Arcs))
    Z_LB = 0.0
    for k in range(1):
        print "-------------------------------------------------"
        ######################################################
        # TODO: Compute lower bound and put in z_LB_k
        ######################################################

        #####################################################
        # TODO: Update lower bound
        #####################################################

        # Update subgradients
        g = {}
        for i in S:
            g[i] = 1.0
            for s, j, h, _ in Arcs if s == i:
                if (i, j, h) in x_bar:
                    g[i] -= 1.0
        # Update step size
        T = mu*100000/sum(map(lambda z: z*z, g.values()))
        #T = f*(Z_UB-Z_LB)/sum(map(lambda z: z*z, g.values()))
        # Update Lagrangian multipliers
        for i in S:
            Lambda[i] = Lambda[i] + T*g[i]
        # Logging
        print "Current LB: %.2f" % Z_LB_k, " Best LB: %.2f" % Z_LB, " Step size: %.3f" % T


def lagrangian_heuristic(x_bar, Arcs, N, D):
    global n, m, k
    x_heu = {}

    Q1 = set()
    Q2 = set()
    for i in S:
        cover = 0
        h0 = -1
        for s, j, h, c in Arcs if s == i:
            if (i, j, h) in x_bar:
                cover += 1
                h0 = h

        if cover == 1:
            x_heu[i] = h0
        elif cover > 1:
            Q1.add(i)
        else:
            Q2.add(i)
        # Try to empty Q1

        # Try to empty Q2

    # TODO:
    return None


def main():
    parser = argparse.ArgumentParser(description='MILP solver for timetabling.')
    parser.add_argument(dest="filename", type=str, help='filename')
    parser.add_argument("-e", "--example", type=str, dest="example",
                        default="value", metavar="[value1|value2]", help="Explanation [default: %default]")

    args = parser.parse_args()  # by default it uses sys.argv[1:]

    n, m, k, Arcs = readData(args.filename)

    # Determine the set of trips S and of depots D
    S = set([i+m for i in range(n)])
    N = set(range(2*(n+m)))
    D = set(range(len(k)))
    print "Number of trips:", len(S), " Number of depots:", len(D)

    # Set random multipliers for testing
    Lambda = {}
    #####################################################
    # TODO: set values for lambda here:
    #####################################################
    for i in S:
        Lambda[i] = random.randint(100, 5000)
    #####################################################
    # TODO:  Compute corresponding lower bound
    #####################################################


if __name__ == "__main__":
    main()
