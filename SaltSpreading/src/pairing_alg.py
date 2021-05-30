################################################################################
# Pairing Algorithm to find routes
################################################################################
import sys

def recurr(i, path):
    global route
    global Ar
    if len(path)>=1 and i == path[0]:
        path+=[i]
        #print("loop closed %d" % i)
        return path
    else:
        path += [i]        
        for (x,y) in Ar:
            if x==i:
                try:
                    Ar.remove((x,y))
                except ValueError:
                    print("Missed removal")
                    sys.exit(0)
                recurr(y, path)
                return(path)
        print("No outgoing arc found. %d" % i)
        return([]) #sys.exit(0)



def derive_route(data,Arcs):
    for h in data.vehicles:
        print('\nRoute for veichle %d:' % h)
        s = data.depots[h]
        global Ar
        Ar = list(Arcs[h])
        global route
        route = []
        route = recurr(s, [])
        while len(Ar)>0:
            for i in range(len(route)):
                u = route[i]
                found = False
                for (x,y) in Ar:
                    if x==u:
                        cycle = recurr(u, [])
                        route[i:i] = cycle[:-1]

                        found = True
                        break
                if found:
                    break

        print(route)
    #print ' '.join(map(str,route))
