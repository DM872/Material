
def BinPackingExample():
    B = 9
    w = [2, 3, 4, 5, 6, 7, 8]
    q = [4, 2, 6, 6, 2, 2, 2]
    s = []
    for j in range(len(w)):
        for i in range(q[j]):
            s.append(w[j])
    return s, B


def Lister():
    B = 300
    s = [32, 9, 118, 227, 177, 16, 125, 46, 220, 187, 17,
         243, 294, 50, 246, 178, 62, 24]
    return s, B


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
