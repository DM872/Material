import pyomo.environ as po
from data import BinPackingExample, Lister, FFD
import itertools


def bpp(s, B):
    n = len(s)
    U = len(FFD(s, B))
    
    # Your Gurobi model for the compact formulation

    return model


def solveBinPacking(s, B):
    n = len(s)
    U = len(FFD(s, B))
    model = bpp(s, B)
    model.optimize()
    bins = [[] for i in range(U)]
    # Get the contents of the bins from your model 
    for i in range(bins.count([])):
        bins.remove([])
    for b in bins:
        b.sort()
    bins.sort()
    return bins


if __name__ == '__main__':
    # s, B = BinPackingExample()
    s, B = Lister()
    bins = solveBinPacking(s, B)
    print(len(bins))
    for b in bins:
        print((b, sum(b)))
