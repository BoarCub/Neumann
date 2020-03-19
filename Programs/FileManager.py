import os
import json
from TaskManager import *

class FileManager(object):
    def __init__(self):
        #contains the name (ex: CommandsDatabase) of the current file being imported
        self.file_name = ""
        
    #sets the default file path used in importFile   
    def setPath(self, file_path):
        self.file_path = file_path
    
    #import the current self.file_path
    def importFile(self): 
        return self.importFilePath(self.file_path)
        
    #imports file using json
    def importFilePath(self, file_path):
        for index in range(len(file_path)-1, 0, -1):
            if (file_path[index]=="/" or file_path[index] == "\\"):
                self.file_name = file_path[index+1:len(file_path)]
                break
                
        if file_path == None or file_path == "":
            return None
        try:
            with open(file_path) as file:
                selectedFile = json.load(file)
                return selectedFile
        except FileNotFoundError:
            return None
        except:
            return None
    
    #deletes the last location in a file path (ex: C:/Users/JohnDoe -> C:/Users/)
    def shortenFilePath(self, file_path):
        #counts the number of times a slash is found
        for index in range ((len(file_path)-1), 0, -1):
            if file_path[index] == "/" or file_path[index] == "\\":
                break
        file_path = file_path[0:index]
        return file_path
    
    def writeFile(self, path, filename):
        self.dict_to_save = {}
        self.dict_to_save.update({'Title': TaskManager.title})
        self.dict_to_save.update({'Questions Per Sheet': TaskManager.questionsPerSheet})
        self.dict_to_save.update({'Questions': TaskManager.newTaskQuestions})
        
        with open(os.path.join(path, filename), 'w') as file:
            json.dump(self.dict_to_save, file)
            
            
FileManager = FileManager()