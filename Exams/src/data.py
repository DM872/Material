import os, sys, codecs, json, itertools
import datetime 
from functools import reduce
from collections import Counter
import pandas as pd
import random

class Data:

    def __init__(self, dirname: str, instance: str):        
        self.config = self.read_config(dirname)
        self.exams = self.read_exams(instance)
        self.adj, self.shared = self.create_adj(self.exams)
        self.rooms = self.read_rooms(dirname)        
        self.preanalysis()
        binned_rooms, binned_exams = self.preanalysis_rooms()
        self.sample_rooms(binned_exams)

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
            if exams[key]["stype"]=="u" or exams[key]["stype"]=="o":
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

    def preanalysis(self):        
        exam_days = reduce((lambda x, y: x + y), [self.exams[r]["rdays"] for r in self.exams])        
        print(f"exams to schedule: {len(self.exams)}, exam days to allocate: {exam_days}")
        room_days=0
        for r in self.rooms:
            #print(r, len(self.rooms[r]["available"]))
            room_days += len(self.rooms[r]["available"])
        print("Room days: ", room_days)
        students = set({x for i in self.exams for x in self.exams[i]['students'] })
        print("Students: ", len(students))


    def preanalysis_rooms(self):
        print("Rooms available binned per size:")
        counts_dict = {}
        for day in self.config["DAYS"]:
            counts=[]            
            for key,room in self.rooms.items():
                if day in room["available"]:
                    counts += [room["seats"]]
            counts_dict[day]=counts
        
        results_df=[]
        for day, count_vec in counts_dict.items(): 
            bins = pd.cut(count_vec, bins=[0,10,20,30,50,100,150,200,300,400])
            # Count the number of outcomes in each interval
            binned_counts = bins.value_counts().sort_index()
            
            # Convert the dictionary to a DataFrame for better readability
            binned_counts_df = pd.DataFrame(binned_counts).transpose()
            binned_counts_df["day"] = day
            results_df.append(binned_counts_df)
        final_results_df = pd.concat(results_df)
        print(final_results_df.reset_index().drop('index', axis=1))
        
        print("Written exams binned per size:")
        sizes=[]
        counts=0
        for key,exam in self.exams.items():  
            if exam["nstds"]==0 and len(exam["students"])==0:
                print(key)
            if exam["stype"]=="s":
                sizes+=[exam["nstds"]]
            else:
                counts+=1
            
        bins = pd.cut(sizes, bins=[0,10,20,30,50,100,150,200,300,400])
        # Count the number of outcomes in each interval
        binned_counts = pd.Series(bins.value_counts().sort_index())
        binned_counts.columns=["count"]
        print(binned_counts)
        print("Oral exams: ",counts, "average per day ",round(counts/len(self.config["DAYS"]),2))

        return final_results_df.reset_index().drop('index', axis=1), binned_counts

    def sample_rooms(self, binned_exams):
        counts_dict = {}
        raw_rooms_df = []
        for day in self.config["DAYS"]:            
            for key,room in self.rooms.items():
                if day in room["available"]:
                    raw_rooms_df.append((day,key,room["seats"]))
        final_raw_rooms_df = pd.DataFrame(raw_rooms_df, columns=['Day', 'Room', 'Size'])
        #print(final_raw_rooms_df)

        # Group by the categorical column
        grouped = final_raw_rooms_df.groupby('Day')
        result_dfs = []
        result_dict = {}
        # Iterate through each group
        for group_name, group_df in grouped:
            # Create a dictionary to hold the counts for the current group
            binned_counts = {}
            
            # Iterate through each numerical column in the group
        
            # Bin the data into intervals
            bins = pd.cut(group_df["Size"], bins=[0,10,20,30,50,100,150,200,300,400])

            result_dict[group_name]={}
            # Iterate through each unique bin
            for bin_interval in bins.cat.categories:
                # Filter the DataFrame for rows where 'A' falls within the current bin
                filtered_df = group_df[bins == bin_interval]
                
                # Group the filtered DataFrame by the categorical column 'C' and aggregate the results
                #grouped = filtered_df.groupby('Room')['Room'].apply(list)
                # Add the results to the dictionary
                result_dict[group_name][bin_interval] = set(filtered_df["Room"]) #grouped.to_dict()


            # Count the number of outcomes in each interval
            binned_counts["Size"] = bins.value_counts().sort_index()
        
            # Convert the dictionary to a DataFrame
            binned_counts_df = pd.DataFrame(binned_counts)
            
            # Add the categorical column to the DataFrame
            binned_counts_df['Day'] = group_name
            
            # Append the result DataFrame to the list
            result_dfs.append(binned_counts_df)

        # Concatenate all the result DataFrames into a single DataFrame
        final_result_df = pd.concat(result_dfs).reset_index().rename(columns={'index': 'Interval'})
        #print(final_result_df)
        #print(result_dict)
        #print(binned_exams)
        nscenarios = range(30)
        for scenario in nscenarios:
            for day in self.config["DAYS"]:
                # Loop through each category
                for index, value in binned_exams.items():
                    sample_size = min(len(result_dict[day][index]),value)
                    r = random.sample(result_dict[day][index], sample_size)
        


    def create_adj(self, exams: dict) -> dict:
        adj = {}
        shared = {}
        for (i, j) in itertools.combinations(exams.keys(), 2):
            shared[(i, j)] = [x for x in exams[i]['students'] if x in exams[j]['students'] ]
            adj[(i, j)] = len(shared[(i, j)])
    
        return adj, shared
