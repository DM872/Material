import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import random
import time
import itertools
import urllib
import csv





# Part of this script is taken from the very nice tutorial by Peter Norvig:
# http://nbviewer.ipython.org/url/norvig.com/ipython/TSPv3.ipynb

# Cities are represented as Points, which are represented as complex numbers
Point = complex
City  = Point

def X(point): 
    "The x coordinate of a point."
    return point.real

def Y(point): 
    "The y coordinate of a point."
    return point.imag

def distance(A, B): 
    "The distance between two points."
    return abs(A - B)

def Cities(n, width=900, height=600, seed=42):
    "Make a set of n cities, each with random coordinates within a (width x height) rectangle."
    random.seed(seed * n)
    return frozenset(City(random.randrange(width), random.randrange(height))
                     for c in range(n))

def plot_tour(tour): 
    "Plot the cities as circles and the tour as lines between them."
    plot_lines(list(tour) + [tour[0]])
    
def plot_lines(points, style='bo-'):
    "Plot lines to connect a series of points."
    plt.plot(list(map(X, points)), list(map(Y, points)), style)
    plt.axis('scaled'); plt.axis('off')


def tour_length(points, edges):
    "The total of distances between each pair of vertices."
    points=list(points)
    return sum(edges[i,j]*distance(points[i], points[j]) for i,j in edges)

def plot_tsp(algorithm, cities):
    "Apply a TSP algorithm to cities, plot the resulting tour, and print information."
    # Find the solution and time how long it takes
    t0 = time.clock()
    tour = algorithm(cities)
    t1 = time.clock()
    assert valid_tour(tour, cities)
    plot_tour(tour); plt.show()
    print("{} city tour with length {:.1f} in {:.3f} secs for {}"
          .format(len(tour), tour_length(tour), t1 - t0, algorithm.__name__))
    

def valid_tour(tour, cities):
    "Is tour a valid tour for these cities?"
    return set(tour) == set(cities) and len(tour) == len(cities)


def plot_labeled_lines(points, args, length ):
    """Plot individual points, labeled with an index number.
    Then, args describe lines to draw between those points.
    An arg can be a matplotlib style, like 'ro--', which sets the style until changed,
    or it can be a list of indexes of points, like [0, 1, 2], saying what line to draw."""
    # Draw points and label them with their index number
    points=list(points)
    plot_lines(points, 'bo')
    for (label, p) in enumerate(points):
        plt.text(X(p), Y(p), '  '+str(label))
    # Draw lines indicated by args
    style = 'bo-'
    for elem in args:
        for arg in elem:
            if isinstance(arg, str):
                style = arg
            else: # arg is a list of indexes into points, forming a line                
                Xs = [X(points[i]) for i in arg]
                Ys = [Y(points[i]) for i in arg]
                plt.plot(Xs, Ys, style)

    blue_line_full = plt.plot([], [], color='blue', lw=2,
                              markersize=5, label='$x_{ij}=1$')
    red_line_dashed = plt.plot([], [], color='red', ls="--",lw=2,
                              markersize=5, label='$0.64\leq x_{ij}<1$')
    red_line_dotted = plt.plot([], [], color='red', ls="-.",lw=2,
                              markersize=5, label='$0.32\leq x_{ij}<0.64$')
    red_line_dd = plt.plot([], [], color='red', ls=':',lw=2,
                              markersize=5, label='$0.01<x_{ij}<0.32$')
    
    plt.axis('scaled'); plt.axis('off'); 
    plt.legend(ncol=4,
               loc='upper center', bbox_to_anchor=(0.5, 1), bbox_transform=plt.gcf().transFigure, 
               frameon=None,framealpha=None,fancybox=True)
    #fontsize='small')
    if length:
        plt.text(0.95, 0.03, length,
                verticalalignment='bottom', horizontalalignment='right',
                transform=plt.gcf().transFigure, style='italic',
                bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})
#            color='green', fontsize=15)
    #plt.legend(loc=1)#handles=[blue_line])
    plt.show()    



def plot_situation(cities,x=[]):    
    edge_style_list=[]
    for (i,j) in x:
        if x[i,j] > 0.98:
            edge_style_list.append(['b-', (i,j) ])
        elif x[i,j] >  0.64:
            edge_style_list.append(['r--', (i,j) ])
        elif x[i,j] >  0.32:
            edge_style_list.append(['r-.', (i,j) ])
        elif x[i,j] > 0.02:
            edge_style_list.append(['r:', (i,j) ])
        else:
            edge_style_list.append([' ', (i,j) ])
    if len(x)>0:
        length = "Tour length {:.1f}".format(tour_length(cities, x))
    else:
        length=None
    plot_labeled_lines(cities, edge_style_list, length)


def read_instance(filename):
    inputDataFile = open(filename,"r")
    lines = inputDataFile.readlines()
    inputDataFile.close()
    Xs=[]
    Ys=[]
    for line in lines:
        if line[0]=="#": continue
        parts = line.split()
        Xs.append(float(parts[1]))
        Ys.append(float(parts[2]))
    return frozenset(City(Xs[c], Ys[c]) for c in range(len(Xs)))

