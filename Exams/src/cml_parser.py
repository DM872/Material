import argparse
from pathlib import Path
import yaml

def cml_parse() -> dict:

    example_text = '''example:
    python3 src/__main__.py -i data/E21/biologi.json -s sol/sol.txt
    '''
    parser = argparse.ArgumentParser(
        prog='optiexam',
        description='''Optimal exam scheduler
        for SDU NAT''',
        epilog=example_text + '''
        Run in interactive mode to be asked for approval of data corrections
        ''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--pairings', action='store_true', default=False, help='Pairings must be attempted automatically?')
    parser.add_argument('-s', '--schedule', action='store_true', default=False, help='Make the schedule') 
    parser.add_argument('-a','--solution', dest='solution_file', metavar='SOLUTION', type=str, required=False,help='the solution file in json or txt extension')
    parser.add_argument('-t', '--time_limit', type=int, default=60, help="The time limit for the solver")
    parser.add_argument('-o', '--outdir', type=str, required=True, action="store")
    parser.add_argument('instance',action="store")
   
    options = parser.parse_args()
    
    print(yaml.dump(options))
    return options
 