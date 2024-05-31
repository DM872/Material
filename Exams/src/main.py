#! /usr/bin/python3
import os, argparse, json
from data import Data as Data
import cml_parser




def solve(options):
    
    instance = Data(os.path.dirname(options.instance), options.instance)
    ## Just for inspecting the data in nice formatting:
    #print(json.dumps(instance.config, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False))
    
    #print(json.dumps(instance.exams, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False))
    #print(json.dumps(instance.rooms, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False))
    #print(data.adj)      
    #ext = {x + " " + y: shared[(x,y)] for (x,y) in shared if adj[(x, y)] > 0}
    #ext = {x + " " + y: adj[(x,y)] for (x,y) in adj} 
    #s = json.dumps(ext, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False)
    #print(s)
    #s = json.dumps(rooms, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False)
    #print(s)

    ## Your Task
    pass    


if __name__ == "__main__":
    options = cml_parser.cml_parse()
    solve(options)