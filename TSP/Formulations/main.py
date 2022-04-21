from dfj_gurobi import solve_DFJ
from mtz import solve_MTZ
from svestka import solve_Svestka
from dantzig import solve_Dantzig
import time 
import tsputil



##################################################
_SIZE = 15
_SEED = 25  # YOUR_ID
##################################################


def timer(func):
    """Decorator for printing the type of output a function returns"""
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        sol = func(*args, **kwargs) # Call the decorated function.# solve_MTZ(points)
        t1 = time.perf_counter()
        print("Computation time {:.2f}".format(t1-t0))
        #print(model.ObjBoundC,model.nodeCount )
        #tsputil.plot_situation(points, sol)
        #output = print("output type:", type(output)) # Process before finishing.
        return sol # Return the function output.
    return wrapper


solve_DFJ=timer(solve_DFJ)
solve_MTZ=timer(solve_MTZ)
solve_Svestka=timer(solve_Svestka)
solve_Dantzig=timer(solve_Dantzig)


if __name__ == '__main__':

    points = tsputil.Cities(_SIZE, seed=_SEED)
    #plot_situation(points)
    sol = solve_DFJ(points)    
    sol = solve_MTZ(points)  
    sol = solve_Svestka(points)  
    sol = solve_Dantzig(points)  
    
    


    # cutting_plane_alg(points)