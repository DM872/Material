#! /usr/bin/python3

import os, argparse, json
from data import Data as Data

def read_input():

    example_text = '''example:
    python3 src/main.py -i data/E21/biologi.json
    '''
    
    parser = argparse.ArgumentParser(prog='exam_scheduler',
                                 description='Scheduling Exams for DM872',
                                 epilog=example_text,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i','--instance', dest='instance', metavar='INSTANCE', type=str, required=True,help='the path to the instance')
    args = parser.parse_args()

    return Data(os.path.dirname(args.instance), args.instance)


def solve(data):
    ## Just for inspecting the data in nice formatting:
    #s = json.dumps(config, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False)
    #print(s)
    #s = json.dumps(exams, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False)
    #print(s)

    print(data.adj)      
    #ext = {x + " " + y: shared[(x,y)] for (x,y) in shared if adj[(x, y)] > 0}
    #ext = {x + " " + y: adj[(x,y)] for (x,y) in adj} 
    #s = json.dumps(ext, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False)
    #print(s)
    print(f"exams to schedule: {len(data.exams)}")

    ## Your Task
    


if __name__ == "__main__":
    data = read_input()
    solve(data)