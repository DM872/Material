
def BinPackingExample():
    B = 9
    w = [2, 3, 4, 5, 6, 7, 8]
    q = [4, 2, 6, 6, 2, 2, 2]
    s = []
    for j in range(len(w)):
        for i in range(q[j]):
            s.append(w[j])
    return s, B


def BinPackingLister():
    B = 300
    s = [32, 9, 118, 227, 177, 16, 125, 46, 220, 187, 17,
         243, 294, 50, 246, 178, 62, 24]
    return s, B


def CuttingStockExample1():
    """CuttingStockExample1: create toy instance for the cutting stock problem."""
    B = 110            # roll width (bin size)
    w = [20, 45, 50, 55, 75]  # width (size) of orders (items)
    q = [48, 35, 24, 10, 8]  # quantitiy of orders
    return w, q, B


def CuttingStockExample2():
    """CuttingStockExample2: create toy instance for the cutting stock problem."""
    B = 9            # roll width (bin size)
    w = [2, 3, 4, 5, 6, 7, 8]   # width (size) of orders (items)
    q = [4, 2, 6, 6, 2, 2, 2]  # quantitiy of orders
    return w, q, B

def CuttingStockExample3():
    """CuttingStockExample3: from test_pricing.py in pyscipopt."""
    # item widths
    w = [14, 31, 36, 45]
    # width demand
    q = [211, 395, 610, 97]
    # roll length
    B = 100    
    return w, q, B

def generateCuttingStockExample():
    # By Joao Dionisio
    # Generates small/medium sized instances
    from random import randint
    B = randint(30,70)
    n_orders = randint(2,5)
    w = [randint(10,B) for _ in range(n_orders)]
    q = [randint(1,10) for _ in range(n_orders)]
    return w,q,B




def mkCuttingStock(s):
    """mkCuttingStock: convert a bin packing instance into cutting stock format"""
    w, q = [], []   # list of different widths (sizes) of items, their quantities
    for item in sorted(s):
        if w == [] or item != w[-1]:
            w.append(item)
            q.append(1)
        else:
            q[-1] += 1
    return w, q


def mkBinPacking(w, q):
    """mkBinPacking: convert a cutting stock instance into bin packing format"""
    s = []
    for j in range(len(w)):
        for i in range(q[j]):
            s.append(w[j])
    return s





def FFD(s, B):
    remain = [B]
    sol = [[]]
    for item in sorted(s, reverse=True):
        for j, free in enumerate(remain):
            if free >= item:
                remain[j] -= item
                sol[j].append(item)
                break
        else:
            sol.append([item])
            remain.append(B-item)
    return sol
