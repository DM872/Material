#!/usr/bin/python

import sys
import getopt
import data
import pairing_alg



if __name__ == "__main__":
    # Parse command line options
    filename = ""
    outfile = ""
    
    # Read input data
    instance = data.Data()

    try:                                
        opts, args = getopt.getopt(sys.argv[1:], "hf:", ["help", "file="]) 
    except getopt.GetoptError:
        usage()          
        sys.exit("Parsing error in command line options")                     
        
    if (len(opts)<1):
        #instance.load_example_BelBen()
        instance.load_example_Gualandi()

    for opt, arg in opts:                
        if opt in ("-h", "--help"):      
            print("-f, --filename missing")
            sys.exit(0)                  
        elif opt in ("-f", "--filename"): 
            filename = arg
            instance.read_from_file(filename)



    instance.statistics()
    instance.draw_instance()
    print("vehicles=",instance.vehicles)
    print("depots=",instance.depots)
    print("A=",instance.A)
    print("A_R=",instance.A_R)
    print("E_R",instance.E_R)

    #Arcs = solve(instance)
    #
    #for h in instance.vehicles:
    #    print('\nDraw route for veichle %d:' % h)
    #    draw.draw_route(data,Arcs,h)
    #
    #pairing_alg.derive_route(data,Arcs)
