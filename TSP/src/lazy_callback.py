#!/usr/bin/env python3.7

# Copyright 2022, Gurobi Optimization, LLC

# Solve a traveling salesman problem on a randomly generated set of
# points using lazy constraints.   The base MIP model only includes
# 'degree-2' constraints, requiring each node to have exactly
# two incident edges.  Solutions to this model may contain subtours -
# tours that don't visit every city.  The lazy constraint callback
# adds new constraints to cut them off.

import sys
import math
import random
from itertools import combinations
import gurobipy as gp
from gurobipy import GRB
import time
import tsputil


# Callback - use lazy constraints to eliminate sub-tours
def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        vals = model.cbGetSolution(model._vars)
        # find the shortest cycle in the selected edge list
        tour = subtour(vals, model._n)
        if len(tour) < model._n:
            # add subtour elimination constr. for every pair of cities in tour
            model.cbLazy(gp.quicksum(model._vars[i, j]
                                     for i, j in combinations(tour, 2))
                         <= len(tour)-1)


# Given a tuplelist of edges, find the shortest subtour

def subtour(vals, n):
    # make a list of edges selected in the solution
    edges = gp.tuplelist((i, j) for i, j in vals.keys()
                         if vals[i, j] > 0.5)
    unvisited = list(range(n))
    cycle = range(n+1)  # initial length has 1 more city
    while unvisited:  # true if list is non-empty
        thiscycle = []
        neighbors = unvisited
        while neighbors:
            current = neighbors[0]
            thiscycle.append(current)
            unvisited.remove(current)
            neighbors = [j for i, j in edges.select(current, '*')
                         if j in unvisited]
        if len(cycle) > len(thiscycle):
            cycle = thiscycle
    return cycle


def solve_DFJ_lazy(points):
    points = list(points)
    n = len(points)
    V = range(n)
    E = [(i, j) for i in range(n) for j in range(i) if i<j]
    dist = {e: tsputil.distance(points[e[0]], points[e[1]]) for e in E}

    m = gp.Model()
    
    # Create variables
    vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='e')
    for i, j in E: #vars.keys():
        vars[j, i] = vars[i, j]  # edge in opposite direction
    
    # You could use Python looping constructs and m.addVar() to create
    # these decision variables instead.  The following would be equivalent
    # to the preceding m.addVars() call...
    #
    # vars = tupledict()
    # for i,j in dist.keys():
    #   vars[i,j] = m.addVar(obj=dist[i,j], vtype=GRB.BINARY,
    #                        name='e[%d,%d]'%(i,j))
    
    
    # Add degree-2 constraint
    
    m.addConstrs(vars.sum(i, '*') == 2 for i in range(n))
    
    # Using Python looping constructs, the preceding would be...
    #
    # for i in range(n):
    #   m.addConstr(sum(vars[i,j] for j in range(n)) == 2)
    
    
    # Optimize model
    m._n = n
    m._vars = vars
    m.Params.LazyConstraints = 1
    m.optimize(subtourelim)
    
    if m.status == GRB.status.OPTIMAL:
        vals = m.getAttr('X', vars)
        tour = subtour(vals, m._n)
        assert len(tour) == n
        print('Optimal tour: %s' % str(tour))
        print('Optimal cost: %g' % m.objVal)
    
        return vals
        #return {e: vals[e].x for e in vals}
    else:
        print("Something wrong in solve_tsp")
        exit(0)

    
    
    





if __name__ == "__main__":
    points = tsputil.read_instance("data/dantzig42.dat")
    # points = tsputil.read_instance("data/dantzig42.tsp")
    # points = list(tsputil.Cities(n=20, seed=35))
    #tsputil.plot_situation(points)
    t0 = time.perf_counter()
    tsp = solve_DFJ_lazy(points)
    
    t1 = time.perf_counter()
    
    print("Computation time {:.2f}".format(t1-t0))

    tsputil.plot_situation(points, tsp)
    
