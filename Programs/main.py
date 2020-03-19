import os
os.environ["KIVY_NO_CONSOLELOG"] = "1" # Prevents Kivy from leaving debug messages in the console

#Disables multitouch emulation
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout

from TaskManager import TaskManager
from FileManager import *

# InterfaceManager acts as a container for all of the Screens in the app
class InterfaceManager(ScreenManager):
    pass


# The container for the StartScreen Screen
class StartScreen(Screen):
    pass


# The container for the SaveFile Screen
class SaveFileScreen(Screen):
    
    # Takes a parameter of path, which is the path the file will be saved to
    # Takes the parameter filename, which will be the name of the file
    # Saves the current task to that file
    def save(self, path, filename):
        FileManager.writeFile(path, filename) # Writes the task to the file
        self.refresh() # Refreshes all of the files displayed in the filechooser
        self.parent.current = "Task Creator Screen" # Switches to the Task Creator Screen
        self.makeCustomPopup("Worksheet Successfully\nSaved!") # Displays a popup to the user that tells the user that the task saved

    # Returns the path of the Tasks folder, which stores all of the saved Tasks
    def getPath(self):
        return FileManager.shortenFilePath(os.path.dirname(os.path.realpath(__file__))) + "/Worksheets"
    
    # Refreshes the filechooser so that new files are displayed
    def refresh(self):
        self.filechooser._update_files()
        
    # Callback function that closes the custom popup
    def closeCustomPopup(self, instance):
        self.customPopup.dismiss()
            
    # Opens a custom popup which displays the text in the parameter
    def makeCustomPopup(self, textParameter):
        self.customPopup = Popup(title = "Alert",
                                 content = FloatLayout(size = self.size),
                                 size_hint = (0.5, 0.8))
        
        # Creates a label that will display the message in the textParameter to the user
        messageLabel = Label(
            size_hint = (0.5, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.7},
            text = textParameter,
            halign = 'center',
            font_size = "20sp"
        )
        
        # Creates an "Okay" button
        okayButton = Button(
            size_hint = (0.5, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.3},
            text = "Okay"
        )
        
        # Binds the Okay Button to self.closeCustomPopup which will close the popup
        okayButton.bind(on_release = self.closeCustomPopup)
        
        # Adds the label and button to the popup
        self.customPopup.content.add_widget(messageLabel)
        self.customPopup.content.add_widget(okayButton)
        
        # Opens popup
        self.customPopup.open()
    
    
# The container for the TaskCreator Screen
class TaskCreatorScreen(Screen):
    
    # Super Init (Allows for the initialization of class variables
    def __init__(self, **kwargs):
        super(TaskCreatorScreen, self).__init__(**kwargs)
        self.deleteToggled = False # A boolean representing whether delete mode is toggled
    
    # Toggles whether "deleteToggled" is toggled. This value determines whether the detail buttons are in edit mode or delete mode.
    def toggleDelete(self):
        self.deleteToggled = not self.deleteToggled # Toggles delete
        
        if self.deleteToggled: # Delete is active
            self.delete_button.text = "Cancel" # Changes Delete Button text to Cancel
            self.setDetailsButtonColor((1, 0, 0, 1)) # Changes Detail Buttons to red in color
        else: # Delete is inactive
            self.delete_button.text = "Delete Question" # Changes Delete Button text to Delete Question
            self.setDetailsButtonColor((1, 1, 1, 1)) # Changes back color of Detail Buttons to white/gray
    
    # Sets the color of all detail buttons to the color given in the parameter, which is a tuple in the following format: (R, G, B, A)
    def setDetailsButtonColor(self, color):
        for layout in TaskManager.taskRows:
            for widget in layout.children: # Searches for the Detail Button in each layout
                if widget.id == "details_button":
                    widget.background_color = color # Sets the color of Details Button to the parameter
                    break
    
    # Resets the task by deleting all questions in the task
    def resetTask(self):
        while len(TaskManager.newTaskQuestions) > 0: # Deletes questions at the first index of the task until no questions are left
            self.deleteQuestion(1)
            
        if self.deleteToggled: # Makes sure delete is untoggled
            self.toggleDelete()
    
    # Deletes the question at the given index corresponding to TaskManager.newTaskQuestions, starting at 1
    def deleteQuestion(self, index):
        layoutToDelete = TaskManager.taskRows[index-1] # Gets the layout representing the question
        TaskManager.deleteQuestion(index) # Deletes the question from the task
        self.questions_layout.remove_widget(layoutToDelete) # Removes the layout representing the question for the scrollable GridLayout
        self.toggleDelete() # Toggled delete
    
    #Replaces all the questions in the task with those in the parameter, given as a dictionary in the same format as TaskManager.newTaskQuestions
    def replaceTask(self, taskDictionary):
        self.resetTask() # Resets the task so that the task is empty to begin with
        
        for i in range (1, len(taskDictionary) + 1): # Iterates through each question in the given dictionary
            layout = self.addEmptyQuestion() # An empty question is created
                    
            # Sets the value of the detail button to description of the question
            for widget in layout.children:
                if widget.id == "details_button":
                    widget.text = taskDictionary.get(str(i))
    
    #Checks if the task is ready to save
    #If the task is ready to save, the next screen is opened
    #Otherwise, a popup is opened that tells the user "Some Questions are Incomplete"
    def saveFileScreen(self, nextScreen, currentScreen):
        
        # Returns True if none of questions are empty and none of the parameters of the question are empty
        checkNone = TaskManager.checkNone()
        titlePresent = not TaskManager.title == ""
        
        # No issues, the task and all of its questions are valid
        if checkNone and TaskManager.questionsPerSheet <= len(TaskManager.newTaskQuestions) and TaskManager.questionsPerSheet > 0 and titlePresent:
            return nextScreen # Returns the nextScreen to continue to
        else: #There are some issues with the task, displaying error to the user through a notification
            self.customPopup = Popup(title = "Warning",
                                     content = FloatLayout(size = self.size),
                                     size_hint = (0.5, 0.8))
            
            #labelText is the string that will be displayed to the user
            if not checkNone: #One or more questions are empty or have empty parameters
                labelText = "Some Questions Are\nIncomplete"
            elif not titlePresent: #Since no questions are empty, the error must be that the pump goes out of bounds
                labelText = "The Title Is\nEmpty"
            else:
                labelText = "Questions Per\nSheet are Invalid"
            
            # Creates a label that will display the message to the user
            messageLabel = Label(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.7},
                text = labelText,
                halign = 'center',
                font_size = "20sp"
            )
            
            # Creates an "Okay" Button
            okayButton = Button(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.3},
                text = "Okay"
            )
            
            # Binds the button to the self.closeCustomPopup function so that pressing the button will close the popup
            okayButton.bind(on_release = self.closeCustomPopup)
            
            # Adds the button and label widgets to the popup
            self.customPopup.content.add_widget(messageLabel)
            self.customPopup.content.add_widget(okayButton)
            
            # Opens the popup
            self.customPopup.open()
            
            return currentScreen
        
    # Called by pressing the Execute Task button
    # Checks if it's possible to execute the task (device is connected/the task is applicable)
    # Opens the appropriate popups
    def executeTask(self):
        
        if TaskManager.checkNone(): # None of questions are empty or have empty parameters
            
            titlePresent = not TaskManager.title == ""
            inBounds = TaskManager.questionsPerSheet <= len(TaskManager.newTaskQuestions) and TaskManager.questionsPerSheet > 0
        
            if not inBounds: # The task causes the pump to go out of bounds and the appropriate error message is displayed
                self.makeCustomPopup("Questions Per\nSheet are Invalid")
            elif titlePresent: # Since the task is valid, an attempt is made at making a connection
                self.executionPopup = self.makeExecutionPopup() # Connection was successful, opening execution popup
            else: # Connection was unsuccessful
                self.makeCustomPopup("The Title Is\nEmpty") 
        else: # At least on question is empty or has empty parameters
            self.makeCustomPopup("Some Questions Are\nIncomplete")
            
    # Generates a custom popup with the text given in the parameter
    def makeCustomPopup(self, textParameter):
        self.customPopup = Popup(title = "Warning",
                                 content = FloatLayout(size = self.size),
                                 size_hint = (0.5, 0.8))
        
        # Creates a label that will display the message in the textParameter to the user
        messageLabel = Label(
            size_hint = (0.5, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.7},
            text = textParameter,
            halign = 'center',
            font_size = "20sp"
        )
        
        # Creates an "Okay" button
        okayButton = Button(
            size_hint = (0.5, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.3},
            text = "Okay"
        )
        
        # Binds the Okay Button to self.closeCustomPopup which will close the popup
        okayButton.bind(on_release = self.closeCustomPopup)
        
        # Adds the label and button to the popup
        self.customPopup.content.add_widget(messageLabel)
        self.customPopup.content.add_widget(okayButton)
        
        # Opens popup
        self.customPopup.open()
        
    # Creates a popup that is opened when a task is executed
    def makeExecutionPopup(self):
        popup = Popup(title = "Exporting Worksheet", # Sets the title of popup so it looks like this: "Editing Step 11"
                      content = FloatLayout(size = self.size),
                      size_hint = (0.5, 0.8))
        
        # Creates a Text Input to input the volume of liquid to used for the question
        volumeInput = TextInput(
            size_hint = (0.95, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.6},
            hint_text = "Type the number of copies...",
            multiline = False,
            input_filter = 'int'
            )
        volumeInput.bind(text = self.executionTextInputCallback) # self.volumeTextCallback is called on selection so that self.currentPopupValues is updated
               
        # Creates a confirm button
        # Button checks if the values that user selected for the parameters are correct
        # If the values are correct, self.currentPopupValues is inserted into the main Task Dictionary (self.newTaskQuestions)
        # In addition, the popup is closed and the Details Button displays a description of the values in a human-readable form
        confirmButton = Button(
            size_hint = (0.45, 0.1),
            pos_hint = {'center_x': 0.25, 'center_y': 0.3},
            text = "Confirm"
            )
        confirmButton.bind(on_release = self.executionPopupConfirmCallback) # Calls self.defaultPopupConfirmCallback on press
        
        # Creates a cancel button which closes the popup
        cancelButton = Button(
            size_hint = (0.45, 0.1),
            pos_hint = {'center_x': 0.75, 'center_y': 0.3},
            text = "Cancel"
            )
        cancelButton.bind(on_release = self.defaultPopupCancelCallback) # Calls self.defaultPopupCancelCallback which closes the popup
        
        # Adds all of the widgets created in this function to the popup
        popup.content.add_widget(volumeInput)
        popup.content.add_widget(confirmButton)
        popup.content.add_widget(cancelButton)
        
        popup.open() # Opens the popup
        
        return popup # Returns the popup, so it can be saved to a variable if needed
        
    # A callback function that is called whenever the message label in the execution popup changes text
    def messageLabelCallback(self, instance, text):
        if text == "Task Completed" or text == "Task Stopped": # Activates option to Close Window once the task is either completed or stopped
            for widget in instance.parent.children:
                if widget.id == "stop_button":
                    widget.bind(on_release = self.executionPopup.dismiss)
                    widget.text = "Close Window"
        
    # A callback function that is called whenever the stop task button is pressed in the execution popup
    def stopTaskButton(self, instance):
        SerialManager.stopTask()
    
    # Creates an empty question and adds it to the task and screen
    # A new row is added to the Scrollable Layout accordingly
    def addEmptyQuestion(self):
        
        # A row in the Scrollable Layout, which represents the properties of a single task
        layout = FloatLayout(
            )
        
        # Creates a label to display the position of the task (1, 2, etc...)
        taskLabel = Label(
            id = "task_label",
            text = str(len(TaskManager.newTaskQuestions)+1),
            size_hint = (0.15, 1),
            pos_hint = {'center_x': 0.08, 'center_y': 0.5}
            )
        
        # Adds a details button which both opens a popup on press
        # Allows the user to edit the details of the question (valve, volume, etc...)
        # After details are set, the popup will display a summary of the details
        detailsButton = Button(
            id = "details_button",
            text = "Choose the Question Text",
            size_hint = (0.7, 1),
            pos_hint = {'center_x': 0.55, 'center_y': 0.5}
            )
        
        # Bind the button to self.editButtonCallback so that edit details popup is opened on pressing the button
        detailsButton.bind(on_release = self.editButtonCallback)
        
        # Adds the label, spinner, and button to the row
        layout.add_widget(taskLabel)
        layout.add_widget(detailsButton)
        
        # Adds the newly created row to the list of rows in TaskManager.taskRows, for easy reference later on
        TaskManager.taskRows.append(layout)
        
        # Adds the row to the main Scrollable Layout, which stores all of the questions/rows
        self.questions_layout.add_widget(layout)
        
        # Updates the running task dictionary in TaskManager with a new, empty element
        TaskManager.newTaskQuestions.update({str(len(TaskManager.newTaskQuestions)+1): ""})
        
        return layout
            
    # A callback function that is called when the edit button is pressed
    # If "deletedToggled" is true, the question associated with the button is deleted
    # Otherwise, the detail editor is opened
    def editButtonCallback(self, button):
        if(self.deleteToggled):
            self.deleteQuestion(TaskManager.taskRows.index(button.parent)+1)
        else:
            self.openDetailEditor(button)
            
    # Called to initialize popup for detail editor
    # Initializes the values in self.currentPopupValues depending on the mode of the associated question
    # self.currentPopupValues keeps track of the values inputed by the user
    def openDetailEditor(self, button):
        index = str(TaskManager.taskRows.index(button.parent) + 1)
    
        self.currentQuestion = TaskManager.newTaskQuestions[index]
        self.popup = self.getDefaultPopup(index)
        
    def openPropertiesEditor(self):
        self.currentTitle = TaskManager.title;
        self.currentQuestionsPerSheet = TaskManager.questionsPerSheet
        
        self.popup = self.getPropertiesPopup()
               
    # A callback function that is called when volume textinput of the popup changes value
    # Changes values in self.currentPopupValues based on what the value of the text of the widget is
    def volumeTextInputCallback(self, instance, value):
        try:
            self.currentQuestion = value
        except:
            self.currentQuestion = ""
            
    def executionTextInputCallback(self, instance, value):
        try:
            self.exportNumber = int(value)
        except:
            self.exportNumber = None
            
    def titleTextInputCallback(self, instance, value):
        try:
            self.currentTitle = value;
        except:
            self.currentTitle = ""
            
    def valveSpinnerCallback(self, instance, value):
        try:
            self.currentQuestionsPerSheet = int(value)
        except:
            self.currentQuestionsPerSheet = 0
    
    def executionPopupConfirmCallback(self, instance):
        
        if self.exportNumber == None:
            self.customPopup = Popup(title = "Warning",
                                     content = FloatLayout(size = self.size),
                                     size_hint = (0.5, 0.8))
            
            # Label which will display "Your Input Was Invalid"
            messageLabel = Label(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.7},
                text = "Your Input Was\nEmpty",
                halign = 'center',
                font_size = "20sp"
            )
            
            # Okay Button which will close the popup
            okayButton = Button(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.3},
                text = "Okay"
            )
            okayButton.bind(on_release = self.closeCustomPopup) # Binds the Okay Button to self.closeCustomPopup()
            
            # Adds the label and the button to the popup
            self.customPopup.content.add_widget(messageLabel)
            self.customPopup.content.add_widget(okayButton)
            
            self.customPopup.open() # Opens the popup
            
        elif self.exportNumber <= 0:
            self.customPopup = Popup(title = "Warning",
                                     content = FloatLayout(size = self.size),
                                     size_hint = (0.5, 0.8))
            
            # Label which will display "Your Input Was Invalid"
            messageLabel = Label(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.7},
                text = "Your Input Was\nInvalid",
                halign = 'center',
                font_size = "20sp"
            )
            
            # Okay Button which will close the popup
            okayButton = Button(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.3},
                text = "Okay"
            )
            okayButton.bind(on_release = self.closeCustomPopup) # Binds the Okay Button to self.closeCustomPopup()
            
            # Adds the label and the button to the popup
            self.customPopup.content.add_widget(messageLabel)
            self.customPopup.content.add_widget(okayButton)
            
            self.customPopup.open() # Opens the popup
    
        else:
            TaskManager.exportWorksheet(self.exportNumber)
            self.executionPopup.dismiss()
            self.makeCustomPopup("Worksheet Successfully\nSaved!") # Displays a popup to the user that tells the user that the task saved
    
    def propertiesPopupConfirmCallback(self, instance):
        
        if self.currentTitle == "":
            self.customPopup = Popup(title = "Warning",
                                     content = FloatLayout(size = self.size),
                                     size_hint = (0.5, 0.8))
            
            # Label which will display "Your Input Was Invalid"
            messageLabel = Label(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.7},
                text = "Your Title Was\nEmpty",
                halign = 'center',
                font_size = "20sp"
            )
            
            # Okay Button which will close the popup
            okayButton = Button(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.3},
                text = "Okay"
            )
            okayButton.bind(on_release = self.closeCustomPopup) # Binds the Okay Button to self.closeCustomPopup()
            
            # Adds the label and the button to the popup
            self.customPopup.content.add_widget(messageLabel)
            self.customPopup.content.add_widget(okayButton)
            
            self.customPopup.open() # Opens the popup
            
        elif self.currentQuestionsPerSheet == 0:
            self.customPopup = Popup(title = "Warning",
                                     content = FloatLayout(size = self.size),
                                     size_hint = (0.5, 0.8))
            
            # Label which will display "Your Input Was Invalid"
            messageLabel = Label(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.7},
                text = "Needs At Least\nOne Question\nPer Sheet",
                halign = 'center',
                font_size = "20sp"
            )
            
            # Okay Button which will close the popup
            okayButton = Button(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.3},
                text = "Okay"
            )
            okayButton.bind(on_release = self.closeCustomPopup) # Binds the Okay Button to self.closeCustomPopup()
            
            # Adds the label and the button to the popup
            self.customPopup.content.add_widget(messageLabel)
            self.customPopup.content.add_widget(okayButton)
            
            self.customPopup.open() # Opens the popup
        
        else:
            TaskManager.title = self.currentTitle
            TaskManager.questionsPerSheet = self.currentQuestionsPerSheet
            
            self.popup.dismiss()
    
    # A callback function that is called when the confirm button is pressed on the default popup
    # If the inputed values are invalid, a new popup is opened to warn the user about it.
    # Otherwise, the values are accepted into the TaskManager.newTaskQuestions dictionary
    def defaultPopupConfirmCallback(self, instance):
        
        # Gets the index of the popup (in terms of its step in the task) by splicing the title of its popup (great-great-grandparent widget)
        index = instance.parent.parent.parent.parent.title[17:]
        
        # Checks if the details/parameters entered by the user are valid
        if(self.currentQuestion != ""): # The inputs are valid
            TaskManager.newTaskQuestions[index] = self.currentQuestion # The details/parameters in the main task dictionary are set to the ones inputed
            
            self.popup.dismiss() # Closes the popup and returns to the main Task Creator
            
            # Finds the details button matching the question
            for widget in TaskManager.taskRows[int(index)-1].children:
                if widget.id == "details_button":
                    widget.text = TaskManager.newTaskQuestions[index] # Changes the details text to a generated description
        else: # The user inputs are invalid
            # A popup is generated to notify the user that the input is invalid
            self.customPopup = Popup(title = "Warning",
                                     content = FloatLayout(size = self.size),
                                     size_hint = (0.5, 0.8))
            
            # Label which will display "Your Input Was Invalid"
            messageLabel = Label(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.7},
                text = "Your Input Was\nInvalid",
                halign = 'center',
                font_size = "20sp"
            )
            
            # Okay Button which will close the popup
            okayButton = Button(
                size_hint = (0.5, 0.1),
                pos_hint = {'center_x': 0.5, 'center_y': 0.3},
                text = "Okay"
            )
            okayButton.bind(on_release = self.closeCustomPopup) # Binds the Okay Button to self.closeCustomPopup()
            
            # Adds the label and the button to the popup
            self.customPopup.content.add_widget(messageLabel)
            self.customPopup.content.add_widget(okayButton)
            
            self.customPopup.open() # Opens the popup
    
    # Callback button the cancels the Edit Popup
    def defaultPopupCancelCallback(self, instance):
        self.popup.dismiss()
    
    # Callback function that closes the notify popup
    def closeCustomPopup(self, instance):
        self.customPopup.dismiss()
    
    # Returns a newly generated popup
    # Contains the following widgets:
        #Valve Spinner
        #Volume Text Input
        #Speed Text Input
    def getDefaultPopup(self, index):
        
        popup = Popup(title = "Editing Question " + index, # Sets the title of popup so it looks like this: "Editing Step 11"
                      content = FloatLayout(size = self.size),
                      size_hint = (0.5, 0.8))
        
        # Creates a Text Input to input the volume of liquid to used for the question
        volumeInput = TextInput(
            size_hint = (0.95, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.6},
            hint_text = "Type the question...",
            multiline = False,
            )
        if self.currentQuestion != "": # Updates the text in the text input if values are already entered for that parameter
            volumeInput.text = self.currentQuestion
        volumeInput.bind(text = self.volumeTextInputCallback) # self.volumeTextCallback is called on selection so that self.currentPopupValues is updated
               
        # Creates a confirm button
        # Button checks if the values that user selected for the parameters are correct
        # If the values are correct, self.currentPopupValues is inserted into the main Task Dictionary (self.newTaskQuestions)
        # In addition, the popup is closed and the Details Button displays a description of the values in a human-readable form
        confirmButton = Button(
            size_hint = (0.45, 0.1),
            pos_hint = {'center_x': 0.25, 'center_y': 0.3},
            text = "Confirm"
            )
        confirmButton.bind(on_release = self.defaultPopupConfirmCallback) # Calls self.defaultPopupConfirmCallback on press
        
        # Creates a cancel button which closes the popup
        cancelButton = Button(
            size_hint = (0.45, 0.1),
            pos_hint = {'center_x': 0.75, 'center_y': 0.3},
            text = "Cancel"
            )
        cancelButton.bind(on_release = self.defaultPopupCancelCallback) # Calls self.defaultPopupCancelCallback which closes the popup
        
        # Adds all of the widgets created in this function to the popup
        popup.content.add_widget(volumeInput)
        popup.content.add_widget(confirmButton)
        popup.content.add_widget(cancelButton)
        
        popup.open() # Opens the popup
        
        return popup # Returns the popup, so it can be saved to a variable if needed
    
    def getPropertiesPopup(self):
        
        popup = Popup(title = "Editing Properties", # Sets the title of popup
                      content = FloatLayout(size = self.size),
                      size_hint = (0.5, 0.8))
        
        # Creates a Text Input to input the volume of liquid to used for the question
        volumeInput = TextInput(
            size_hint = (0.5, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.6},
            hint_text = "Type the title...",
            multiline = False,
            )
        if self.currentTitle != "": # Updates the text in the text input if values are already entered for that parameter
            volumeInput.text = self.currentTitle
        volumeInput.bind(text = self.titleTextInputCallback) # self.volumeTextCallback is called on selection so that self.currentPopupValues is updated
               
        nums = []
        for i in range(1, len(TaskManager.newTaskQuestions) + 1):
            nums.append(str(i))

        nums = tuple(nums)
               
        valve = Spinner(
            size_hint = (0.6, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.75},
            text = "Questions Per Sheet",
            values = nums # The valves that the user can select are numbered 1-6
            )
        if self.currentQuestionsPerSheet != 0: # Updates the text in the spinner if values are already entered for that parameter
            valve.text = str(self.currentQuestionsPerSheet)
        valve.bind(text = self.valveSpinnerCallback) # self.valveSpinnerCallback is called on selection so that self.currentPopupValues is updated
               
        # Creates a confirm button
        # Button checks if the values that user selected for the parameters are correct
        # If the values are correct, self.currentPopupValues is inserted into the main Task Dictionary (self.newTaskQuestions)
        # In addition, the popup is closed and the Details Button displays a description of the values in a human-readable form
        confirmButton = Button(
            size_hint = (0.45, 0.1),
            pos_hint = {'center_x': 0.25, 'center_y': 0.3},
            text = "Confirm"
            )
        confirmButton.bind(on_release = self.propertiesPopupConfirmCallback) # Calls self.defaultPopupConfirmCallback on press
        
        # Creates a cancel button which closes the popup
        cancelButton = Button(
            size_hint = (0.45, 0.1),
            pos_hint = {'center_x': 0.75, 'center_y': 0.3},
            text = "Cancel"
            )
        cancelButton.bind(on_release = self.defaultPopupCancelCallback) # Calls self.defaultPopupCancelCallback which closes the popup
        
        # Adds all of the widgets created in this function to the popup
        popup.content.add_widget(volumeInput)
        popup.content.add_widget(valve)
        popup.content.add_widget(confirmButton)
        popup.content.add_widget(cancelButton)
        
        popup.open() # Opens the popup
        
        return popup # Returns the popup, so it can be saved to a variable if needed    
    
     
#Acts as a container for the Debug Screen
class DebugScreen(Screen):

    # Called by pressing the Execute Task button
    # Checks if the device is connected
    # Opens the appropriate popups
    def executeRawCommands(self):
        if self.rawCommandText.text != "":
            
            if SerialManager.makeConnection():
                response = SerialManager.executeRawCommand(self.rawCommandText.text)
                self.rawCommandConsole.text = response
            else:
                self.makeCustomPopup("No Connected\nDevice Found")
        else:
            self.makeCustomPopup("Input is Empty")
            
    # Generates a notification popup with the text given in the parameter
    def makeCustomPopup(self, textParameter):
        self.popup = Popup(title = "Warning",
                                 content = FloatLayout(size = self.size),
                                 size_hint = (0.5, 0.8))
        
        okayLabel = Label(
            size_hint = (0.5, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.7},
            text = textParameter,
            halign = 'center',
            font_size = "20sp"
        )
        
        okayButton = Button(
            size_hint = (0.5, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.3},
            text = "Okay"
        )
        okayButton.bind(on_release = self.closePopup)
        
        self.popup.content.add_widget(okayLabel)
        self.popup.content.add_widget(okayButton)
        
        self.popup.open()
     
     # Closes the current open popup
    def closePopup(self, instance):
        self.popup.dismiss()
     
#Allows the reader to load a previously saved file and use that
class PreviousFileScreen(Screen):
    def getPath(self):
        return  FileManager.shortenFilePath(os.path.dirname(os.path.realpath(__file__)))+ "/Worksheets"
    #recieves the file path from the file chooser
    def selectFile(self, *args):
        try:
            FileManager.setPath(args[1][0])
        except:
            pass
        
    # Refreshes the filechooser so that new files are displayed
    def refresh(self):
        self.filechooser._update_files()
    
    #signals the widgets to update based on the selected file
    def updateDisplay(self, object):
        current_dict = FileManager.importFile() # Imports file
        if current_dict!= None: # Imported dictionary is applicable
            try:
                questions_dict = current_dict.get('Questions')
                title = current_dict.get('Title')
                questionsPerSheet = current_dict.get('Questions Per Sheet')
                object.replaceTask(questions_dict) # Replace the task in Task Creator with the imported task
                TaskManager.newTaskQuestions = questions_dict
                TaskManager.title = title
                TaskManager.questionsPerSheet = questionsPerSheet
                self.parent.current = "Task Creator Screen" # Switch to the task creator screen
            except:
                self.makeCustomPopup("The Selected File\nis Not Compatible")
        else:
            self.makeCustomPopup("The Selected File\nis Not Compatible") # Open a popup notifying the user that the file was not compatible
            
    # Callback function that closes the custom popup
    def closeCustomPopup(self, instance):
        self.customPopup.dismiss()
            
    # Opens a custom popup which displays the text in the parameter
    def makeCustomPopup(self, textParameter):
        self.customPopup = Popup(title = "Warning",
                                 content = FloatLayout(size = self.size),
                                 size_hint = (0.5, 0.8))
        
        # Creates a label that will display the message in the textParameter to the user
        messageLabel = Label(
            size_hint = (0.5, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.7},
            text = textParameter,
            halign = 'center',
            font_size = "20sp"
        )
        
        # Creates an "Okay" button
        okayButton = Button(
            size_hint = (0.5, 0.1),
            pos_hint = {'center_x': 0.5, 'center_y': 0.3},
            text = "Okay"
        )
        
        # Binds the Okay Button to self.closeCustomPopup which will close the popup
        okayButton.bind(on_release = self.closeCustomPopup)
        
        # Adds the label and button to the popup
        self.customPopup.content.add_widget(messageLabel)
        self.customPopup.content.add_widget(okayButton)
        
        # Opens popup
        self.customPopup.open()


# Loads the .kv file needed
kv = Builder.load_file("Interface.kv")


# Builds the app
class MainApp(App):

    def build(self):
        return kv


# Main Function which runs the app
if __name__ == "__main__":
    MainApp().run()