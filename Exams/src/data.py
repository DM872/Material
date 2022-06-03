import os, sys, codecs, json, itertools
import datetime 
from functools import reduce



class Data:

    def __init__(self, dirname: str, instance: str):        
        self.config = self.read_config(dirname)
        self.exams = self.read_exams(instance)
        self.adj, self.shared = self.create_adj(self.exams)
        self.rooms = self.read_rooms(dirname)
        self.preanalysis()

    def read_config(self, dirname: str) -> dict:
        filename = os.path.join(dirname, "config.json")
        print("Reading: ",filename)
        with codecs.open(filename,  "r", "utf-8") as filehandle:
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
        with codecs.open(filename,  "r", "utf-8") as filehandle:
            try:
                exams = json.load(filehandle)
            except ValueError as e:
                sys.exit('try to read exams file: {}'.format(e))
        return(exams)

    def read_rooms(self, dirname: str) -> dict:
        filename = os.path.join(dirname, "rooms.json")
        print("Reading: ",filename)
        with codecs.open(filename,  "r", "utf-8") as filehandle:
            try:
                rooms = json.load(filehandle) # a dictionary
                #json.dump(self.config, fp=filehandle, sort_keys=False, indent=4, separators=(',', ': '),  encoding="utf-8")
            except ValueError as e:
                sys.exit('try to read rooms file: {}'.format(e))

        filename = os.path.join(dirname, "room_unavailabilities.json")
        print("Reading: ",filename)
        with codecs.open(filename,  "r", "utf-8") as filehandle:
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

        #print(json.dumps(rooms, sort_keys=False, indent=4, separators=(',', ': '), ensure_ascii=False))
        return(rooms)

    def preanalysis(self):        
        exam_days = reduce((lambda x, y: x + y), [self.exams[r]["rdays"] for r in self.exams])        
        print(f"exams to schedule: {len(self.exams)}, exam days: {exam_days}")
        room_days=0
        for r in self.rooms:
            #print(r, len(self.rooms[r]["available"]))
            room_days += len(self.rooms[r]["available"])
        print("Room days: ", room_days)


    def create_adj(self, exams: dict) -> dict:
        adj = {}
        shared = {}
        for (i, j) in itertools.combinations(exams.keys(), 2):
            shared[(i, j)] = [x for x in exams[i]['students'] if x in exams[j]['students'] ]
            adj[(i, j)] = len(shared[(i, j)])
    
        return adj, shared
