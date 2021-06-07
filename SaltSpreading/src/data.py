import csv
import os,sys
#import gurobipy
import networkx as nx
import matplotlib.pyplot as plt
import math

class Data:
    def __init__(self):

        self.nodes = {}

        self.vehicles = {} # with home and capacity
        self.depots = {} # with refill amount

        self.A = {} # all arcs with "len"
        
        self.E_R = {} # required edges (listed only in version _from > _to) 
        self.A_R = {} # required arcs
              



    def is_req_edge(self, edge):
        return (edge[0],edge[1]) in self.E_R or (edge[1],edge[0]) in self.E_R

        
    def u_turn_set(self):
        U = set()
        for node in self.nodes:
            a_u = set()
            a_plus_u = set()
            a_minus_u = set()
            for edge in self.E_R:
                if edge[0]==node: 
                    a_u.add(edge[1])
                elif edge[1]==node:
                    a_u.add(edge[0])
            for arc in list(self.A.keys()) + list(self.A_R.keys()):
                if arc[0]==node:
                    a_plus_u.add(arc[1])
                if arc[1]==node:
                    a_minus_u.add(arc[0])
            if len(a_u)==1 and len(a_minus_u)==0 and len(a_plus_u)==0:
                U.add(node)
            if len(a_u)==0 and len(a_minus_u)==1 and a_minus_u==a_plus_u:
                U.add(node)
            #print(a_u,a_minus_u,a_plus_u)
        return U




    def read_from_file(self,filename):
        self.outfile = os.path.split(filename)[-1].split(".")[0]
        reader = csv.reader(open(filename, "r"),delimiter=",")
        sys.stdout.write("Read " + filename + "\n")

        m3_of_salt_per_m2 = 30*10**(-6) # m^3/m^2
        capacity_in_m3 = 2 * 12.3 # in m^3
        capacity = capacity_in_m3 / (m3_of_salt_per_m2 * 1.0) # capacity in m^2

        self.vehicles = {1: {"home": 2,"capacity": capacity},
                         2: {"home": 130,"capacity": capacity}} # start and end location for vehicle 1 and 2

        self.depots = {1: {"refill": capacity}, 179: {"refill":capacity}}
        # process data
        # note: it assumes that edges are listed in the data in both directions
        for elem in reader:
            try:
                _fro = int(elem[0].strip())
                self.nodes[_fro] = () # no coordinates given :(
                for k in range(1,len(elem),4):
                    _to = int(elem[k].strip())
                    length = int(elem[k+2].strip())
                    width = float(elem[k+3].strip())
                    status = int(elem[k+1].strip())
                    demand = length * width
                                 

                    if status == 1: # saltes i valgfri retning
                        #self.R.append((_fro, _to))
                        if not self.is_req_edge( (_fro,_to) ):
                            if _fro < _to:
                                self.E_R.update( {(_fro, _to): {"dem":demand, "len": length}} )
                            else:
                                self.E_R.update( {(_to, _fro): {"dem":demand, "len": length}} )
                    elif status == 2:# saltes i denne retning
                        #self.R.append((_fro, _to))
                        if (_fro,_to) not in self.A_R:
                            self.A_R.update( {(_fro, _to): {"dem":demand, "len": length}} )
                    ## status 3 is redundant: if an arc is named but not declared with status 1 or 2 then
                    ## no need _to visit it
                    elif status == 3:# can be left out ## POSSIBLE ERROR: can we visit this in both directions???
                        if (_fro,_to) not in self.A:
                            self.A.update({(_fro, _to): {"dem":demand, "len": length}})
                        if (_to,_fro) not in self.A:
                            self.A.update({(_to, _fro): {"dem":demand, "len": length}})

                    else:
                        sys.exit("Status of arc not recognised")
            except ValueError:
                pass
        
        self.U = self.u_turn_set()
        #print(self.U)




    def load_example_BelBen(self):
        
        self.nodes = {1:(10,50), 2: (20,90), 3:(20,60), 4: (20,40), 5: (20,10), 6: (30,60), 7: (30,40)}

        self.vehicles = {1: {"home":1,"capacity":25.0},
                         2: {"home":1,"capacity":25.0}}

        self.depots = {}

        multidict = { 
                (1,2): [1,3],
                (1,3): [1,4],
                (1,4): [1,4],
                (1,5): [1,3],
                (2,3): [1,1],
                (3,4): [1,1],
                (3,6): [1,5],
                (4,5): [1,1],
                (4,7): [1,0],
                (6,7): [1,14]
                }

        #E = [(i,j) for (i,j) in multidict]
        self.A = {(i,j): {"len": multidict[(i,j)][0]} for (i,j) in multidict if multidict[(i,j)][1]==0}
        self.A.update({(j,i): {"len": multidict[(i,j)][0]} for (i,j) in multidict if multidict[(i,j)][1]==0})
                 
        self.E_R = {(i,j): {"len": multidict[(i,j)][0], "dem": multidict[(i,j)][1]} for (i,j) in multidict if multidict[(i,j)][1]>0}

        self.U = self.u_turn_set()



    def load_example_mixed(self):
        
        self.nodes = {1:(10,50), 2: (10,40), 3:(20,40), 4: (30,40), 5: (20,50)}

        self.vehicles = {1: {"home":1,"capacity":10.0},
                         2: {"home":1,"capacity":10.0}}

        self.depots = {}

        multidict_edges = {
            (1,2): [1,4],
            (1,5): [1,3],
            (2,3): [1,3],
            (3,4): [1,1],
            (3,5): [1,2]
            }

        multidict_arcs = {
            (1,3): [1,5],
            (4,5): [1,0]
            }

        #E = [(i,j) for (i,j) in multidict]
        self.A = {(i,j): {"len": multidict_edges[(i,j)][0]} for (i,j) in multidict_edges}
        self.A.update({(j,i): {"len": multidict_edges[(i,j)][0]} for (i,j) in multidict_edges})
        self.A.update({(i,j): {"len": multidict_arcs[(i,j)][0]} for (i,j) in multidict_arcs})
        
        self.E_R = {(i,j): {"dem": multidict_edges[(i,j)][1]} for (i,j) in multidict_edges if multidict_edges[(i,j)][1]>0}
        self.A_R = {(i,j): {"dem": multidict_arcs[(i,j)][1]} for (i,j) in multidict_arcs if multidict_arcs[(i,j)][1]>0}

        self.U = u_turn_set()
 

    def load_example_multivisit(self):
        
        self.nodes = {1:(10,60), 2: (20,80), 3:(20,60), 4: (20,40), 5: (30,80), 6: (30,60), 7: (30,40)}

        self.vehicles = {1: {"home":1,"capacity":15.0},
                         2: {"home":1,"capacity":15.0}}

        self.depots = {}

        multidict_edges = { 
            (1,2): [1,4],
            (1,3): [1,3],
            (2,5): [1,3],
            (5,6): [1,1],
            (6,7): [1,2],
            (3,4): [1,4]
            }
        multidict_arcs = { 
            (3,2): [1,5],
            (4,1): [1,1],
            (6,3): [1,2],
            (7,4): [1,3]
            }

        self.A = {(i,j): {"len": multidict[(i,j)][0]} for (i,j) in multidict_edges}
        self.A.update({(j,i): {"len": multidict[(i,j)][0]} for (i,j) in multidict_edges})
        self.A.update({(i,j): {"len": multidict[(i,j)][0]} for (i,j) in multidict_arcs})
        
        self.E_R = {(i,j): {"dem": multidict_edges[(i,j)][1]} for (i,j) in multidict_edges if multidict_edges[(i,j)][1]>0}
        self.A_R = {(i,j): {"dem": multidict_arcs[(i,j)][1]} for (i,j) in multidict_arcs if multidict_arcs[(i,j)][1]>0}




    def load_example_Gualandi(self):
        
        self.nodes = {0:(0,12), 1: (4,8), 2:(12,8), 3: (4,3), 4: (12,3), 5: (17,12), 6: (17,17), 7:(20,3)}

        self.vehicles = {1: {"home":0,"capacity":50.0}}

        self.depots = {7: {"refill":50.0}}

        E = {(0,1), (1,2), (2,4), (2,3), (1,3), (3,4), (2,5), (5,7), (4,7), (5,7), (5,6)}
        A_R = {(3,4): 20,(6,5): 30}
        E_R={(1,2): 30}
        def distance(node1,node2):
            return math.ceil(math.sqrt(math.pow(node1[0]-node2[0],2) + math.pow(node1[1]-node2[1],2)))

        self.A = {(i,j): {"len": distance(self.nodes[i],self.nodes[j])} for (i,j) in E}
        self.A.update({(j,i): {"len": distance(self.nodes[i],self.nodes[j])} for (i,j) in E})
        
        self.A_R = {(i,j): {"len": distance(self.nodes[i],self.nodes[j]), "dem": A_R[(i,j)]} for (i,j) in A_R}
        self.E_R = {(i,j): {"len": distance(self.nodes[i],self.nodes[j]), "dem": E_R[(i,j)]} for (i,j) in E_R}

        self.U = self.u_turn_set()
        #print(self.U)



        


    def statistics(self):
        print("%d nodes %d arcs of which %d required and %d alternative pairs required " % 
              (len(self.nodes), len(self.A), len(self.A_R), len(self.E_R)))

        tot_length = sum(self.A[(i,j)]["len"] for (i,j) in self.A)/2
        print(tot_length, "total sum of lengths of the arcs")

        tot_demand = sum(self.A_R[(i,j)]["dem"] for (i,j) in self.A_R) + sum(self.E_R[i,j]["dem"] for (i,j) in self.E_R)
        print(tot_demand, "total required demand")

        capacity = sum(self.vehicles[v]["capacity"] for v in self.vehicles)
        print(capacity, "total capacity")





    def draw_instance(self):
        
        G = nx.Graph()
        H = nx.DiGraph()

        G.add_nodes_from([(v,dict(pos=self.nodes[v])) for v in self.nodes])
        H.add_nodes_from([(v,dict(pos=self.nodes[v])) for v in self.nodes])

        G.add_edges_from(self.E_R.keys())
        H.add_edges_from(self.A.keys())
        H.add_edges_from(self.A_R.keys())

        edge_labels = {(i,j):(self.E_R[(i,j)]["dem"],self.E_R[(i,j)]["len"]) for (i,j) in self.E_R}

        pos = {v:self.nodes[v] for v in self.nodes}
        if not all(map(lambda x: True if any(pos[x]) else False, pos)):
            pos = nx.drawing.layout.kamada_kawai_layout(G)

        nx.draw_networkx(G, pos=pos, with_labels = True)
        nx.draw_networkx_edge_labels(G,pos=pos,edge_labels = edge_labels,font_size = 12)

        edge_labels = {(i,j): (self.A_R[(i,j)]["dem"],self.A_R[(i,j)]["len"]) for (i,j) in self.A_R}
        nx.draw_networkx_edges(H, pos=pos,  arrows = True)
        nx.draw_networkx_edge_labels(H,pos=pos,edge_labels = edge_labels,font_size = 12)

        plt.savefig("instance.png")
        plt.show()
