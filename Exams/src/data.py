import os, sys, codecs, json, itertools



class Data:

    def __init__(self, dirname: str, instance: str):        
        self.config = self.read_config(dirname)
        self.exams = self.read_exams(instance)
        self.adj, self.shared = self.create_adj(self.exams)

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


    def create_adj(self, exams: dict) -> dict:
        adj = {}
        shared = {}
        for (i, j) in itertools.combinations(exams.keys(), 2):
            shared[(i, j)] = [x for x in exams[i]['students'] if x in exams[j]['students'] ]
            adj[(i, j)] = len(shared[(i, j)])
    
        return adj, shared
