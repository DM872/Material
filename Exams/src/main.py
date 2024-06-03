#! /usr/bin/python3
import os, argparse, json
from data import Data as Data
import cml_parser




def solve(options):
    
    instance = Data(os.path.dirname(options.instance), options.instance)
    ## Just for inspecting the data in nice formatting:
    #print(json.dumps(instance.config, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False))
    
    #print(json.dumps(instance.exams, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False))
    #print(json.dumps(instance.room_scenarios, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False))
    #print(instance.adj)      
    #ext = {x + " " + y: shared[(x,y)] for (x,y) in shared if adj[(x, y)] > 0}
    #ext = {x + " " + y: adj[(x,y)] for (x,y) in adj} 
    #s = json.dumps(ext, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False)
    #print(s)
    #s = json.dumps(instance.room_details, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False)
    #print(s)

    ## Your Task
    pass    


if __name__ == "__main__":
    options = cml_parser.cml_parse()
    solve(options)