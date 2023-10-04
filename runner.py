#!/usr/bin/env python3
# -*- coding: ascii -*-

import os, time, datetime, sys, copy, signal

home_path = ""

"""
The configuration file for runner.py will contain one line for each program that is to be run.   Each line has the following parts: 

timespec program-path parameters

where program-path is a full path name of a program to run and the specified time(s), parameters are the parameters for the program,
timespec is the specification of the time that the program should be run.

The timespec has the following format:

[every|on day[,day...]] at HHMM[,HHMM] run

Square brackets mean the term is optional, vertical bar means alternative, three dots means repeated.

Examples:

every Tuesday at 1100 run /bin/echo hello
	every tuesday at 11am run "echo hello"
on Tuesday at 1100 run /bin/echo hello
	on the next tuesday only, at 11am run "echo hello"
every Monday,Wednesday,Friday at 0900,1200,1500 run /home/bob/myscript.sh
	every monday, wednesday and friday at 9am, noon and 3pm run myscript.sh
at 0900,1200 run /home/bob/myprog
	runs /home/bob/myprog once  at 9am and noon


"""

"""
The task class, is where all the information for each task is held, this includes whether it is repeated, 
the time (as a date time and in seconds) the task should be run, and its path and parameters.

It also contains 2 main methods (as well as various getters and setters), the static parseLine() method, 
which takes in a line form the config file and creates a list of task objects, and the parseDate() method, 
which translates the date and time given in the config file to a datetime and raw time form.
"""
class Task:
  def __init__(self,r,d,t,pa,par,l):
    self.repeat = r
    self.day = d
    self.time = t
    self.path = pa
    self.parameters = par
    self.line = l

    self.result = None
    self.formattedTime = None
    self.rawTime = None

  # GETTERS AND SETTERS
  def getRepeat(self):
    return self.repeat

  def getDay(self):
    return self.day
  
  def getTime(self):
    return self.time
  
  def getPath(self):
    return self.path
  
  def getParameters(self):
    return self.parameters

  def getParsedDate(self):
    return self.parsedDate

  def setParsedDate(self,x):
    self.parsedDate = x

  def getRawTime(self):
    return self.rawTime

  def setRawTime(self,r):
    self.rawTime = r

  def getResult(self):
    return self.result

  def getLine(self):
    return self.line

  @staticmethod
  def parseLine(line):
    # takes a config line, removes formatting characters and splits it by whitespace
    line = line.strip()
    parts = line.split()

  # Checks if the line is an "at" or an "ever/on" line, and extracts the informaiton accordingly
    if line.startswith("at"):
      try:
        repeat = ""
        times = parts[1].split(",")
        days = [""] * len(times)
        path = parts[3]

        # The task may or may not have parameters.
        try:
          parameters = parts[4:]
          parameters[-1].strip()
        except IndexError:
          parameters = []

      except IndexError:
        print("Error in configuration: " + line)
        sys.exit()
    
    else:
      try:
        repeat = parts[0]
        days = parts[1].split(",")
        times = parts[3].split(",")
        path = parts[5]

        # The task may or may not have parameters.
        try:
          parameters = parts[6:]
          parameters[-1].strip()
        except IndexError:
          parameters = []

      except IndexError:
        print("Error in configuration: " + line)
        sys.exit()

    # With the information retrieved above, a new task object is made for each day time 
    # combo (there will be |days|*|times| combinations)
    ls = []
    for i in range(len(days)):
      # Checks each day only appears once
      if days.count(days[i]) > 1:
        print("Error in configuration: " + line)
        sys.exit()

      for t in range(len(times)):
        # Checks the time string is the right length
        if len(times[t]) != 4:
          print("Error in configuration: " + line)
          sys.exit()
        
        # Creates a new object
        x = Task(repeat,days[i],times[t],path,parameters,line)
        # Calls the parseDate function to produce a datetime and rawtime based on the day and time.
        x.parseDate()
        ls.append(x)
    
    return ls


  def parseDate(self):
    dayInts = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}

    # If the repeat attribute is empty, the line begin with "at", 
    # and should be run at the time today or tomorrow if it has passed today
    if self.repeat == "":
      # Creates a datetime object with the current date, and the inputted time
      now = time.localtime(time.time())
      s = "{}-{}-{} {}:{}:00".format(now.tm_year,now.tm_mon,now.tm_mday, self.time[0:2], self.time[2:])
      ttr = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

      # Checks if the time has already passed, in which case 1 day is added.
      if ttr < datetime.datetime.now():
        d = datetime.timedelta(days=1)
        ttr = ttr + d
      
      # Saves the calculated time
      self.parsedDate = ttr
      self.rawTime = int(time.mktime(ttr.timetuple()))
      return

    # If repeat was not "", the config line was either an "every" or an "on" line, which are treated the same way.
    # Gets the current day as an integer (Monday = 0, Sunday = 6)
    currentDay = time.localtime(time.time()).tm_wday

    # Uses mod 7 to check how many days in the future the task is.
    try:
      if currentDay < dayInts[self.day]:
        dayGap = dayInts[self.day]-currentDay
      else:
        dayGap = (dayInts[self.day]-currentDay) %7
    except KeyError:
      print("Error in configuration: " + self.getLine())
      sys.exit()

    # finds the DATE to run the task at (time will be wrong here, will just be the same as the current time.)
    timeDateNow = datetime.datetime.now()
    timeDelta = datetime.timedelta(days=dayGap)
    dateToRun = timeDateNow + timeDelta

    #Combines the date found above with the correct time into a datetime object.
    st = "{} {}:{}:00".format(str(dateToRun).split(" ")[0], self.time[0:2], self.time[2:])
    try:
      timeToRun = datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S")
    # Deals with a time out of range like 2460
    except ValueError:
      print("Error in configuration: " + self.line)
      sys.exit()

    # If the task is meant to be run on the weekday it is currently but at a time already passed, a week is added.
    if (timeDateNow > timeToRun):
      delta = datetime.timedelta(days=7)
      timeToRun = timeToRun+delta

    # Saves the datetime found and the raw time version (seconds since epoch) to the object.
    self.parsedDate = timeToRun
    self.rawTime = int(time.mktime(timeToRun.timetuple()))



""" Main Thread of runner.py
Takes the configuration file, parses it into task objects, and runs them at the appropriate times."""

toDoSorted = []

# Setting up the signal catcher
caught = False #Used to ensure that sleeps are recaluculated if an interrupt has occured.

def catch(signum, frame):
  caught = True

  # Checks the file exists, opens it
  try:
    f = open(home_path + ".runner.status", "a")
  except Exception as e:
    print("File ~/.runner.status {}".format(str(e)))
    sys.exit()

  # Goes through each task in toDoSorted, checks if they are past or future, 
  # and if they are passed, whether they produced an erre
  for task in toDoSorted:
    line = ""
    now = time.time()

    if task.getRawTime() < now:
      if task.getResult() == 1:
        line += "error "
      else: 
        line += "ran "

    else:
      line += "will run at "
    
    # Creates the appropriate string for each task, and writes it to the file.
    line += "{} ".format(time.ctime(task.getRawTime()))
    line += "{} ".format(task.getPath())
    line += "{}\n".format(",".join(task.getParameters()))
    f.write(line)

  f.close()

# Links the SIGUSR1 signal with the catch function.
signal.signal(signal.SIGUSR1, catch)

# Writes PID into $HOME/.runner.pid
try:
  with open(home_path + ".runner.pid", "w") as f:
    pid = os.getpid()
    f.write(str(pid))
except Exception as e:
  print("file ~/.runner.pid {}".format(str(e)))
  sys.exit()

# Check that the status file $HOME/.runner.status exists.
# If the status file does not exist, create it.
try:
  f = open(home_path + ".runner.status")
  f.close()
except FileNotFoundError as e:
  f = open(home_path + ".runner.status","w").close()

# Parse config file into record from $HOME/.runner.conf
# Attempts to open file
try:
  specFile = open(home_path + ".runner.conf", "r")
except FileNotFoundError as e:
  print("configuration file not found")
  sys.exit()

# Stores the task objects (unsorted)
toDo = []
fileLines = specFile.readlines()

# Checks if the config file is empty
if len(fileLines) == 0:
  print("configuration file empty")
  sys.exit()

if len(fileLines) == 1 and fileLines[0].strip() == "":
  print("configuration file empty")
  sys.exit()

# Calles the parseLine method on each of the lines in the file, and appends them to an unsorted task list.
for line in fileLines:
  toDo += Task.parseLine(line)

# Basic insertion sort of tasks in toDo
for t in toDo:
  if len(toDoSorted) == 0:
    toDoSorted.append(t)
    continue

  beforeLen = len(toDoSorted)

  for i in range(len(toDoSorted)):

    # Checks for duplicate times
    if toDoSorted[i].getParsedDate() == t.getParsedDate():
      print("Error in configuration: "+ t.getLine())
      sys.exit()
    
    # Loops through until it finds an element in the sorted list that is bigger, and inserts it before that one.
    if toDoSorted[i].getParsedDate() < t.getParsedDate():
      toDoSorted.insert(i, t)
      break
  
  # If the time being added was bigger than all the times currently in the list, it is added to the end.
  if len(toDoSorted) == beforeLen:
    toDoSorted.append(t)

# Flips the list to be earliest first.
toDoSorted.reverse()

#Sleeps until the first task
timeNow = int(time.time())
initialGap = toDoSorted[0].rawTime-timeNow
time.sleep(initialGap)

#Loops through the variables 
num = 0
while num < len(toDoSorted):
  # Takes the next process to run
  process = toDoSorted[num]
  path = process.getPath()

  # forks the parent process
  retVal = os.fork()
  # If the child is running, the specified path is executed with arguments
  if retVal == 0:
    try:
      os.execv(path, [path]+process.parameters)
    except Exception:
      # If an error occurs in the child process, the exit signal 1 is given
      sys.exit(1)
  else:
    # In the parent, waits for a signal
    code = os.wait()
    # Isolatesates and saves the exit state
    process.result = code[1]>>8
  
  # If the process is an "every" process, it needs to be duplicated and added again.
  if process.getRepeat() == "every":
    newProcess = copy.deepcopy(process)

    # Takes the old time, adds a week, and saves that time to the new object.
    oldTime = newProcess.getParsedDate()
    timeDelta = datetime.timedelta(days=7)
    newTime = oldTime+timeDelta
    newProcess.setParsedDate(newTime)

    # Ensures the rawtime is also updated
    newRawTime = int(time.mktime(newTime.timetuple()))
    newProcess.setRawTime(newRawTime)

    toDoSorted.append(newProcess)

  # If the last process was just run, the loop should break, otherwise, the next sleep time should be calculated.
  if num == len(toDoSorted)-1:
    break
  else:
    # Calculates the amount of time to sleep
    first = toDoSorted[num].getRawTime()
    second = toDoSorted[num+1].getRawTime()
    timeToSleep = second-first
    time.sleep(timeToSleep)

    if caught:
      # If a signal has been caught, the sleep time is recalculated, and a new sleep begins.
      first = toDoSorted[num].getRawTime()
      second = toDoSorted[num+1].getRawTime()
      timeToSleep = second-first
      caught = False
      time.sleep(timeToSleep)


  num += 1

print("nothing left to run")