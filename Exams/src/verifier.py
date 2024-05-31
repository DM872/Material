#! /usr/bin/python3

import os
import argparse
import json
from data import Data as Data
import cml_parser
from enum import Enum
# import utils
import codecs
import sys
import yaml
from collections import OrderedDict, defaultdict 

class Session(Enum):
    ORDINARY = 0
    REEXAM = 1


def calculate_distance(self, l1, l2):
    return max([abs(i-j) for i in l1 for j in l2])


class analyze:

    def __init__(self, instance, schedule, outdir):
        self.instance=instance
        self.schedule=schedule
    
        self.fixed = []
        self.free = []
        for exam in instance.exams.keys():
            if 'schedule' in self.instance.exams[exam]:
                self.fixed += [exam]
            else:
                self.free += [exam]
        
        self.evaluation=OrderedDict()
        self.evaluation["viol_unassigned"] = self.viol_unassigned()
        self.evaluation["viol_improper"] = self.viol_improper()
        self.evaluation["viol_requested"] = self.viol_requested()
        self.evaluation["viol_unknown"] = self.viol_unknown_exams()
        self.evaluation["viol_consecutive"] = self.viol_consecutive()
        self.evaluation["viol_available"] = self.viol_available()
        self.evaluation["viol_forbidden"] = self.viol_forbidden()
        self.evaluation["viol_joining"] = self.viol_joining()
        self.evaluation["viol_conflicting"] = self.viol_conflicting("conflicting")    
        #self.evaluation["viol_conflicting_2"] = self.viol_conflicting("conflicting_2")    
        self.evaluation["viol_seats"] = self.viol_seats()    
        self.evaluation["viol_rooms"] = self.viol_rooms()    
    

    def viol_unassigned(self):
        viol_unassigned = 0
        for exam in self.free:
            if exam not in self.schedule and self.instance.exams[exam]['nstds']>0: # added requirement that nstds > 0 for DM841
                print("#  UNASSIGNED: ",exam)
                viol_unassigned += 1   
        return viol_unassigned 

    def viol_improper(self):
        viol_improper = 0
        for exam in self.schedule:
            if not set(self.schedule[exam]).issubset(self.instance.config["DAYS"]):
                print("# IMPROPER: ",exam, self.schedule[exam], self.instance.config["DAYS"])
                viol_improper += 1
        return viol_improper 

    def viol_requested(self):
        viol_req = 0
        for exam in self.free:
            if exam in self.schedule and len(set(self.schedule[exam])) != self.instance.exams[exam]['rdays']:
                print("# REQUESTED: ",exam,self.schedule[exam],self.instance.exams[exam]['rdays'] )
                viol_req+=1

        for exam in self.fixed:
            if exam in self.schedule and len(self.instance.exams[exam]["schedule"]) != self.instance.exams[exam]['rdays']:
                print("# REQUESTED FIXED: ",exam,self.instance.exams[exam]["schedule"],self.instance.exams[exam]['rdays'] )
                viol_req+=1
        return viol_req

    def viol_unknown_exams(self):
        viol_unkn=0 
        for exam in self.schedule.keys():
            if exam not in self.instance.exams:
                print("# UNKNOWN: ",exam)
                viol_unkn+=1
        return viol_unkn
                
    def viol_consecutive(self):
        viol_consec=0
        for exam in self.schedule.keys():            
            if exam in self.instance.exams and self.instance.exams[exam]["rdays"]>1 and self.instance.exams[exam]["rdays"]<=5:
                for i in range(len(self.schedule[exam])-1):
                    if self.schedule[exam][i]+1 != self.schedule[exam][i+1]:
                        print("# CONSECUTIVE:",exam,self.schedule[exam])
                        viol_consec+=1
        return viol_consec
    

    def viol_available(self):
        viol_available=0
        for exam in self.schedule.keys():
            if "available" not in self.instance.exams[exam]:
                continue
            available = {x[0] for x in self.instance.exams[exam]["available"]}
            assigned = set(self.schedule[exam])
            if not assigned.issubset(available):
                print("# UNAVAILABLE:", exam, self.schedule[exam], available )
                viol_available+=1
        return viol_available

    def viol_forbidden(self):
        viol_forbidden=0
        for exam in self.schedule.keys():
            if "forbidden" not in self.instance.exams[exam]:
                continue
            forbidden = {x[0] for x in self.instance.exams[exam]["forbidden"]}
            assigned = set(self.schedule[exam])
            if not assigned.isdisjoint(forbidden):
                print("# FORBIDDEN:", exam, self.schedule[exam], forbidden )
                viol_forbidden+=1
        return viol_forbidden

    def viol_joining(self):
        joining=set()
        for exam in self.schedule.keys():
            if "joining" in self.instance.exams[exam]:
                for e in self.instance.exams[exam]["joining"]:
                    # it can be joining with some exam not to schedule
                    if e in self.instance.exams and (e,exam) not in joining:
                        joining.add((exam,e))

        viol_joining=0
        for (e1, e2) in joining:
            viol_before=viol_joining
            if e2 in self.schedule:
                if self.schedule[e1][0] != self.schedule[e2][0]:
                    print("# JOINING: ", e1, e2, self.schedule[e1], self.schedule[e2])                    
                    viol_joining+=1                    
            elif "schedule" in self.instance.exams[e2]:
                if self.schedule[e1][0] != self.instance.exams[e2]["schedule"][0]:
                    print("# JOINING: ", e1, e2, self.schedule[e1], [y[0] for y in self.instance.exams[e2]["schedule"]])
                    viol_joining+=1
        return viol_joining

    
    def viol_conflicting(self, which="conflicting"):
        conflicting=set()
        for exam in self.schedule.keys():
            if which in self.instance.exams[exam]:
                for e in self.instance.exams[exam][which]:
                    # it can be conflicting with some exam not to schedule
                    if e in self.instance.exams and (e,exam) not in conflicting:
                        conflicting.add((exam,e))

        viol_conflict=0
        pen_conflict=0
        for (e1, e2) in conflicting:
            if e2 in self.schedule:
                if not set(self.schedule[e1]).isdisjoint(set(self.schedule[e2])):
                    print("# ",which.upper(),": ", e1, e2, self.schedule[e1], self.schedule[e2])               
                    viol_conflict+=1
            elif "schedule" in self.instance.exams[e2]:
                schedule_e2 = {x[0] for x in self.instance.exams[e2]["schedule"]}
                if not set(self.schedule[e1]).isdisjoint(schedule_e2):
                    print("# ",which.upper(),": ", e1, e2, self.schedule[e1], schedule_e2)               
                    viol_conflict+=1
            if which=="conflicting":
                if (e1 in self.fixed or e1 in self.schedule) and (e2 in self.fixed or e2 in self.schedule ):
                    s1=self.instance.exams[e1]["schedule"][0][0] if e1 in self.fixed else self.schedule[e1][0]
                    s2=self.instance.exams[e2]["schedule"][0][0] if e2 in self.fixed else self.schedule[e2][0]            
        if which == "conflicting":         
            return viol_conflict
        elif which == "conflicting_2":
            return viol_conflict

    #   "MAX_SEATS_PER_DAY": 300,
    #"MAX_ROOMS_PER_DAY": 15,
    #"MAX_STUDENTS_PER_DAY": 16,
    #"WEIGHT_PROGRAMS": 100,
    #"YEAR": 2023,
    #"MAX_EXAMS": 17,
    #"MAX_ECTS": 40,

 
    def viol_seats(self):
        viol_seats=0
        if self.instance.config["SESSION"] == Session.ORDINARY:
            distribution=defaultdict(list)
            for x in self.free:
                if self.instance.exams[x]["stype"]=="s" and x in self.schedule:
                    for y in self.schedule[x]:
                        distribution[y].append(x)
            
            for d, exams in sorted(distribution.items()):
                S = sum([self.instance.exams[x].nstds for x in exams])
                if S>self.instance.config["MAX_SEATS_PER_DAY"]:
                    print("#  MAX_SEATS:", d, S, self.instance.config.MAX_SEATS_PER_DAY)
                    viol_seats+=1
        return viol_seats
    

    def viol_rooms(self):
        distribution=defaultdict(list)
        for x in self.free:
            if x in self.schedule:
                for y in self.schedule[x]:
                    if self.instance.exams[x]["stype"]=="m":
                        distribution[y].append(x)
        viol_rooms=0
        for d, exams in sorted(distribution.items()):
            if len(exams)>self.instance.config["MAX_ROOMS_PER_DAY"]:
                print("#  MAX_ROOMS:", d, len(exams), self.instance.config["MAX_ROOMS_PER_DAY"])
                viol_rooms+=1
        return viol_rooms

    
    def total_penalty(self):
        penalty=0
        for (e1, e2) in self.instance.adj.keys():
            try:
                if (e1 in self.fixed or e1 in self.schedule) and (e2 in self.fixed or e2 in self.schedule ):
                    s1=self.instance.exams[e1]["schedule"][0][0] if e1 in self.fixed else self.schedule[e1][0]
                    s2=self.instance.exams[e2]["schedule"][0][0] if e2 in self.fixed else self.schedule[e2][0]            
                    penalty += self.instance.adj[(e1, e2)] * self.default_values[(s1, s2)]
            except KeyError as ke:
                print("KeyError in penalty:",ke," (fixed schedule outside period, ok not to account for)")
        return penalty



def read_solution(filename: str):
    if os.path.exists(filename):
        if filename[-4:] == ".txt":
            return read_txt_solution_file(filename)
        elif filename[-5:] == ".json":
            return read_json_solution_file(filename)
        else:
            print("")
            raise SystemError("solution name not compliant: "+filename)
    else:        
        print("")
        raise SystemError("solution file not found: "+filename)

def read_json_solution_file(filename):
    with open(filename,  "r") as filehandle:
        try:
            content=json.load(filehandle)
        except ValueError as e:
            sys.exit(f'reading solution file: {filename} {e}')
    return content

def read_txt_solution_file(filename):
    schedule={}
    with open(filename,  "r") as filehandle:
        try:
            content=filehandle.readlines()
        except ValueError as e:
            sys.exit(f'reading solution file: {filename} {e}')
        
    for line in content:
        terms=line.split(",")
        schedule[terms[0]]=[int(t.strip()) for t in terms[1:]]
    return schedule

    # Just for inspecting the data in nice formatting:
    # s = json.dumps(config, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False)
    # print(s)
    # s = json.dumps(exams, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False)
    # print(s)
    # print(data.adj)
    # ext = {x + " " + y: shared[(x,y)] for (x,y) in shared if adj[(x, y)] > 0}
    # ext = {x + " " + y: adj[(x,y)] for (x,y) in adj}
    # s = json.dumps(ext, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False)
    # print(s)
    # s = json.dumps(rooms, sort_keys=False,  indent=4, separators=(',', ': '), ensure_ascii=False)
    # print(s)


def process(options):
    instance=Data(os.path.dirname(options.instance), options.instance)
    solution=read_solution(options.solution_file)
    analysis = analyze(instance, solution, options.outdir)
    #print(yaml.dump(analysis.evaluation))
    print("\n".join([f"{k}: {v}" for k, v in analysis.evaluation.items()]))
    hvalue=0; svalue=0; value=0
    for k,v in analysis.evaluation.items():
        if "viol" in k:
            hvalue+=v
        elif k=="penalty":
            svalue+=v
    hvalue_prime = hvalue-analysis.evaluation["viol_conflicting"]
    svalue_prime = svalue  #+instance.config["WEIGHT_PROGRAMS"]*analysis.evaluation["pen_conflicting"]
    print(hvalue, svalue, 
          hvalue_prime, svalue_prime,          
          1000000000*hvalue_prime+svalue_prime)

if __name__ == "__main__":
    options=cml_parser.cml_parse()
    process(options)
