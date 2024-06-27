from functools import reduce
from collections import Counter
import pandas as pd
import random



class Preanalysis:

    def preanalysis(self, exams):        
        exam_days = reduce((lambda x, y: x + y), [exams[r]["rdays"] for r in exams])        
        print(f"exams to schedule: {len(exams)}, exam days to allocate: {exam_days}")        
        students = set({x for i in exams for x in exams[i]['students'] })
        print("Students: ", len(students))


    def preanalysis_room_scenario(self, room_scenarios, scenario: int, room_details, config):
        #print(room_scenarios[0])
        print("Rooms available binned per size:")
        counts_dict = {}
        for day in config["DAYS"]:
            counts=[]
            for room in room_scenarios[scenario][day]:
                counts += [room_details[room]["seats"]]
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
        return final_results_df.reset_index().drop('index', axis=1) 
    

    def preanalysis_rooms(self, room_details, config):
        print("Rooms available binned per size:")
        counts_dict = {}
        for day in config["DAYS"]:
            counts=[]            
            for key,room in room_details.items():
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
        return final_results_df.reset_index().drop('index', axis=1) 
    
    def preanalysis_exams(self):
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

        return binned_counts

    def sample_rooms(self, binned_exams, room_details, config):
        counts_dict = {}
        raw_rooms_df = []
        for day in config["DAYS"]:            
            for key,room in room_details.items():
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
                result_dict[group_name][bin_interval] = list(filtered_df["Room"]) #grouped.to_dict()


            # Count the number of outcomes in each interval
            binned_counts["Size"] = bins.value_counts().sort_index()
        
            # Convert the dictionary to a DataFrame
            binned_counts_df = pd.DataFrame(binned_counts)
            
            # Add the categorical column to the DataFrame
            binned_counts_df['Day'] = group_name
            
            # Append the result DataFrame to the list
            result_dfs.append(binned_counts_df)

        # Concatenate all the result DataFrames into a single DataFrame
        #print(result_dfs[0].reset_index(drop=True))
        
        #print(pd.concat(result_dfs))
        #raise SystemError
        final_result_df = pd.concat(result_dfs)
        final_result_df.index.names = ['Interval']
        
        # print(final_result_df)
        #print(result_dict)
        #print(binned_exams)
        random.seed(2024)
        nscenarios = range(30)
        room_scenarios = {}
        for scenario in nscenarios:
            room_scenarios[scenario]={}
            for day in self.config["DAYS"]:
                # Loop through each category
                room_scenarios[scenario][day]=[]
                for index, value in binned_exams.items():
                    sample_size = min(len(result_dict[day][index]), value)
                    #print(result_dict[day][index], value)
                    if sample_size>0:
                        room_scenarios[scenario][day]+=random.sample(result_dict[day][index], sample_size)
                        #room_scenarios[scenario][day]+=result_dict[day][index]
        #print(room_scenarios)
        return room_scenarios


