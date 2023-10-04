#!/usr/bin/env python3
# -*- coding: ascii -*-

import os, sys, signal,time

# open the pidfile and read the process id
#    give an error message if file not found or bad pid
try:
  with open("/home/.runner.pid", "r") as f:
    pid = f.readline().strip()
except FileNotFoundError:
  print("File not found.")

# send the USR1 signal to runner.py
try:
  os.kill(int(pid.strip()), signal.SIGUSR1)
except:
  print("signal failed!")
  sys.exit(1)

# Checks the contents of the status file every second for 5 seconds until something appears.
f = open("/home/.runner.status", "r")
lines = f.readlines()
if len(lines) == 0:
  for i in range(5):
    if len(lines) == 0:
      time.sleep(1)
      lines = f.readlines()
    else: 
      break

# If the file is still empty after 5 seconds, "status timeout" is printed.
if len(lines) == 0:
  print("status timeout")
  sys.exit()
else:
  for line in lines:
    print(line, end = "")
f.close()


# Clears the status file
f = open("/home/.runner.status", "w")
f.write("")
f.close()