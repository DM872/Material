import pyomo
import pyomo.opt
import pyomo.environ as pe
import networkx
import tsputil
import time


class TSPCuttingPlane:
    """A class to solve the TSP using a cutting plane (row-generation) algorithm."""

    def __init__(self, points):
        """The input is a CSV file describing the undirected network's edges."""
        self.points = points

        self.createRelaxedModel()

    def createRelaxedModel(self):
        """Create the relaxed model, without any subtour elimination constraints."""
        node_set = set(range(len(self.points)))
        edge_set = set((i, j) for i in node_set for j in node_set if i < j)
        cost = {e: tsputil.distance(points[e[0]], points[e[1]]) for e in edge_set}

        # Create the model and sets
        m = pe.ConcreteModel()

        m.node_set = pe.Set(initialize=node_set)
        m.edge_set = pe.Set(initialize=edge_set, dimen=2)

        # Define variables
        m.x = pe.Var(m.edge_set, domain=pe.Binary)  # <= BINARY!

        # Objective
        def obj_rule(m):
            return sum(m.x[e] * cost[e] for e in m.edge_set)
        m.OBJ = pe.Objective(rule=obj_rule, sense=pe.minimize)

        # Add the n-1 constraint
        def mass_balance_rule(m, v):
            return sum(m.x[(v, i)] for i in node_set if (v, i) in edge_set) + sum(m.x[(i, v)] for i in node_set if (i, v) in edge_set) == 2
        m.mass_balance = pe.Constraint(node_set, rule=mass_balance_rule)

        # Empty constraint list for subtour elimination constraints
        # This is where the generated rows will go
        m.subtour_elimination_cc = pe.ConstraintList()

        self.m = m

    def convertXsToNetworkx(self):
        """Convert the model's x variables into a networkx object."""
        ans = networkx.Graph()
        edges = [e for e in self.m.edge_set if self.m.x[e].value > .99]
        ans.add_edges_from(edges)
        return ans

    def solve(self):
        """Solve for the TSP, using row generation for subtour elimination constraints."""
        def createConstForCC(m, S):
            S = dict.fromkeys(S)
            return sum(m.x[e] for e in m.edge_set if ((e[0] in S) and (e[1] in S))) <= len(S) - 1

        if not hasattr(self, 'solver'):
            solver = pyomo.opt.SolverFactory('gurobi')

        done = False
        while not done:
            # Solve once and add subtour elimination constraints if necessary
            # Finish when there are no more subtours
            results = solver.solve(self.m, tee=False, keepfiles=False,
                                   options_string="mip_tolerances_integrality=1e-9 mip_tolerances_mipgap=0")
            # Construct a graph from the answer, and look for subtours
            graph = self.convertXsToNetworkx()
            ccs = list(networkx.connected_component_subgraphs(graph))
            for cc in ccs:
                print('Adding constraint for connected component (subtour):')
                print(cc.nodes())
                print(createConstForCC(self.m, cc))
                print('--------------\n')
                self.m.subtour_elimination_cc.add(createConstForCC(self.m, cc))
            if ccs[0].number_of_nodes() == len(self.m.node_set):
                done = True


if __name__ == "__main__":
    # points = tsputils.read_instance("data/dantzig42.dat")
    points = list(tsputil.Cities(n=20, seed=35))
    # plot_situation(ran_points)
    t0 = time.perf_counter()
    tsp = TSPCuttingPlane(points)
    tsp.solve()
    t1 = time.perf_counter()
    print(tsp.m.OBJ())
    print("Computation time {:.2f}".format(t1-t0))

    # tsp.m.x.pprint()
    tsputil.plot_situation(points, {e: pe.value(tsp.m.x[e]) for e in tsp.m.edge_set})
