import PDFGenerator
import random

# Task Manager handles the data and processing of tasks and questions
class TaskManager(object):
    
    def __init__ (self):
        
        # Holds all of the questions in a newly created task or imported task
        # Also referred to as the running task dictionary
        # Follows this format {"1": First Question As String, "2": Second Question}
        self.newTaskQuestions = {}
        
        self.title = "" # The worksheet title
        self.questionsPerSheet = 0
        
        # A list holding all of the layouts for each question row in the user interface
        # List is ordered, starting with row 1
        # Each row corresponds to an question in self.newTaskQuestions
        self.taskRows = []  
            
    def exportWorksheet(self, num):
        for x in range(1, num+1):
            questions_list = list(self.newTaskQuestions.values())
            random.shuffle(questions_list)
            PDFGenerator.makePDF(self.title, str(x), questions_list[:num+1], self.title + " " + str(x) + ".pdf")
            
    # Returns a boolean representing whether the current task is completed filled (no empty questions)
    def checkNone(self):
        
        if len(self.newTaskQuestions) == 0:
            return False
        
        try:
            for newTaskQuestion in self.newTaskQuestions:
                if newTaskQuestion == "":
                    return False
            if self.newTaskQuestions == None:
                return False
        except TypeError:
            return False
        return True
    
    # Deletes an question at a specific index and shift the other questions to fill the gap
    def deleteQuestion(self, index):
        try:
            for i in range(index, len(self.newTaskQuestions)):
                self.newTaskQuestions[str(i)] = self.newTaskQuestions[str(i+1)]
            del self.newTaskQuestions[str(len(self.newTaskQuestions))]
            del self.taskRows[index-1]
            
            for i in range(index-1, len(self.taskRows)):
                for widget in self.taskRows[i].children:
                    if(widget.id == "task_label"):
                        widget.text = str(int(widget.text)-1)
        except:
            self.newTaskQuestions = {}
            self.taskRows = []
        
# Creates a TaskManager object which can be used when the class is imported
TaskManager = TaskManager()