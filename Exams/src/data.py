import os, sys, codecs, json, itertools
import datetime 

from preanalysis import Preanalysis

class Data(Preanalysis):

    def __init__(self, dirname: str, instance: str):        
        self.config = self.read_config(dirname)
        self.exams = self.read_exams(instance)
        self.adj, self.shared = self.create_adj(self.exams)
        self.room_details = self.read_rooms(dirname)        
        self.preanalysis(self.exams)
        binned_exams = self.preanalysis_exams()        
        self.room_scenarios = self.sample_rooms(binned_exams, self.room_details, self.config)
        #binned_rooms = self.preanalysis_rooms()
        self.preanalysis_room_scenario(self.room_scenarios,0,self.room_details, self.config)

    def read_config(self, dirname: str) -> dict:
        filename = os.path.join(dirname, "config.json")
        print("Reading: ",filename)
        with open(filename,  "r") as filehandle:
            try:
                config = json.load(filehandle)
                #json.dump(self.config, fp=filehandle, sort_keys=False, indent=4, separators=(',', ': '),  encoding="utf-8")
            except ValueError as e:
                sys.exit('try to read config file: {}'.format(e))
        return(config)

    def read_exams(self, instance: str) -> dict:
        # filename = os.path.join(dirname, instance+".json")
        filename = instance
        print("Reading: ",filename)
        with open(filename,  "r") as filehandle:
            try:
                exams = json.load(filehandle)
            except ValueError as e:
                sys.exit('try to read exams file: {}'.format(e))
        keys = list(exams.keys())
        
        for key in keys:
            if exams[key]["nstds"]==0 and len(exams[key]["students"])==0: ## TODO would be better not here but in the output to here
                del exams[key]
            elif exams[key]["stype"]=="u" or exams[key]["stype"]=="o":
                del exams[key]
        return(exams)

    def read_rooms(self, dirname: str) -> dict:
        filename = os.path.join(dirname, "rooms.json")
        print("Reading: ",filename)
        with open(filename,  "r") as filehandle:
            try:
                rooms = json.load(filehandle) # a dictionary
                #json.dump(self.config, fp=filehandle, sort_keys=False, indent=4, separators=(',', ': '),  encoding="utf-8")
            except ValueError as e:
                sys.exit('try to read rooms file: {}'.format(e))

        filename = os.path.join(dirname, "room_unavailabilities.json")
        print("Reading: ",filename)
        with open(filename,  "r") as filehandle:
            try:
                room_unavailabilities = json.load(filehandle) # a list
                #json.dump(self.config, fp=filehandle, sort_keys=False, indent=4, separators=(',', ': '),  encoding="utf-8")
            except ValueError as e:
                sys.exit('try to read room_unavailabilities file: {}'.format(e))
        
        for r in rooms:
            rooms[r]["available"] = self.config["DAYS"]
        
        
        for u in room_unavailabilities:
            #print(u['from'])
            day=datetime.date.fromisoformat(u['from'][:10])
            yday = day.timetuple().tm_yday
            room_id="room."+u["roomCode"].lower().replace(" ","")
            if room_id in rooms:
                rooms[room_id]["available"] = list(set(rooms[room_id]["available"]) - set([yday]))

        
        return(rooms)

    def create_adj(self, exams: dict) -> dict:
        adj = {}
        shared = {}
        for (i, j) in itertools.combinations(exams.keys(), 2):
            shared[(i, j)] = [x for x in exams[i]['students'] if x in exams[j]['students'] ]
            adj[(i, j)] = len(shared[(i, j)])
    
        return adj, shared

    def room_capacity(self, room: str):
        return self.room_details[room]["seats"] 