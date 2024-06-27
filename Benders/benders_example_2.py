# %%


#get_ipython().system('pip install gurobipy')
#from gurobipy import Model, GRB, quicksum

import numpy as np
import gurobipy as gp


# %%
class Data():
    def __init__(self):
        self.c = np.array([4,5])
        self.h = np.array([2,-7,5])
        self.F = np.concatenate((np.array([[3,4]]),np.zeros((3,2))),axis=0)
        self.G = np.concatenate((np.array([[2,-2,3]]),np.eye(3)),axis=0)
        self.d = np.array([10,2,2,2])

        self.x_star=np.array([3,3])


# Solve the full model

# %%

class FullModel:
    def __init__(self, D: Data):
        self.m = gp.Model()
        data = D
        # Variables

        x = self.m.addMVar(shape=data.c.shape[0], vtype=gp.GRB.INTEGER, ub=3, name="x")
        y = self.m.addMVar(shape=data.h.shape[0], vtype=gp.GRB.CONTINUOUS, name="y")

        # Set objective
        self.m.setObjective(data.c @ x + data.h @ y, gp.GRB.MAXIMIZE)

        # Add constraints
        self.m.addConstr(data.F @ x + data.G @ y <= data.d, name="constr")
        
        self.x = x
        self.y = y

    def solve(self):
        #self.m.Params.OutputFlag=0 
        self.m.write("model.lp")
        self.m.optimize()
        
    def print_solution(self):
        print("Objective : ",self.m.objVal)        
        print("x : ", self.x.x) #[.x for x in self.x]) #self.m.x)
        print("y : ", self.y.x) #[y.x for y in self.y])
        #print("y2 : ", self.m.getAttr('x',self.y2))


# %%

data = Data()
fm = FullModel(data)
fm.solve()
fm.print_solution()


class REF:
    
    def __init__(self, D:Data):
        self.m = gp.Model()
        self.data = D
        # Variables
           # Create variables
        self.x = self.m.addMVar(shape=self.data.F.shape[1], ub=3, vtype=gp.GRB.CONTINUOUS, name="x")
        self.eta = self.m.addMVar(shape=1, ub=100, vtype=gp.GRB.CONTINUOUS, name="eta")           
        
        # Set objective
        self.m.setObjective(self.data.c @ self.x + self.eta, gp.GRB.MAXIMIZE)

                
    def solve(self):
        self.m.setParam(gp.GRB.Param.DualReductions, 0)
        self.m.Params.OutputFlag=0 
        self.m.optimize()
        
    def is_unbounded(self):
        return self.m.status == gp.GRB.status.UNBOUNDED

    def is_infeasible(self):
        return self.m.status == gp.GRB.status.INFEASIBLE

    def print_solution(self):
        print("Objective : ",self.m.objVal)
        print("x : ", self.x.x)
        print("eta : ", self.eta.x)
        
    def get_solution(self):
        return self.x.x, self.eta.x
    
    def get_objective(self):
        return self.m.objVal        
        
    def add_feasibility_cut(self, ray:np.array):
        self.m.addConstr(ray @ (self.data.d - self.data.F @ self.x)>=0, name="feasibility cut")
        
        
    def add_optimality_cut(self, point: np.array):
        self.m.addConstr(point @ (self.data.d - self.data.F @ self.x)>=self.eta, name="optimality cut")
            



# In[2]:

class DSP:
    
    def __init__(self, D: Data, x_star: np.array):
        # Model
        self.m = gp.Model("DSP")
        self.data = D

        # Create variables
        self.u = self.m.addMVar(shape=self.data.G.shape[0], vtype=gp.GRB.CONTINUOUS, name="u")

        # Set objective
        self.m.setObjective(self.u @ (self.data.d-self.data.F @ x_star), gp.GRB.MINIMIZE)

        # Add constraints
        self.m.addConstr(self.data.G.T @ self.u>= self.data.h, name="c")
      

    def solve(self):
        self.m.setParam(gp.GRB.Param.InfUnbdInfo, 1)
        self.m.Params.OutputFlag=0 
        self.m.optimize()

    def is_unbounded(self):
        return self.m.status == gp.GRB.status.UNBOUNDED
    
    def is_infeasible(self):
        return self.m.status == gp.GRB.status.INFEASIBLE
    
    def get_ray(self):
        return self.m.UnbdRay
    
    def get_objective(self):
        return self.m.objVal   
    
    def get_solution(self):
        return self.u.x

    def get_duals(self):
        return [c.Pi for c in self.m.getConstrs()]
    

# %%

  

# # Solution

# Here we implement the L-Shaped algorithm.

# In[ ]:


data = Data()
ref = REF(data)
converged = False
iteration = 0
ub = float('inf')
lb = -float('inf')
while (not converged) and (iteration < 10):
    iteration = iteration + 1
    print("Iteration #",iteration)
    
    # Solve REF
    ref.solve()
    # Get the solution X, Eta 
    if ref.is_infeasible():
        print("Instance infeasible")
        break
    elif ref.is_unbounded():
        print("Ref unbounded")        
        break
    else:          
        x_star, eta_star = ref.get_solution()
    
    dsp = DSP(data, x_star)
    dsp.solve()

    if dsp.is_infeasible():
        print("DSP Instance infeaasible")    
        break
    elif dsp.is_unbounded():
        print("Found extreme ray:", dsp.get_ray())
        ref.add_feasibility_cut(np.array(dsp.get_ray())) 
    else:            
        if dsp.get_objective() < eta_star:
            print("Found optimality cut:", ref.get_objective())    
            ref.add_optimality_cut(dsp.get_solution())
        elif dsp.get_objective() == eta_star:
            print("Problem Solved: ",
                  f"z={ref.get_objective()}, eta={eta_star},"
                  f"x={x_star}, y={dsp.get_duals()}")
            break


    print("Lower bound ",lb," upper bound ",ub)

