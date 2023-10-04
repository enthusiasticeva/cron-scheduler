# cron-scheduler
- A basic version of the Linux 'cron' command, implemented in Python
- This program reads in a file that gives programs with when they need to be run.

## Files
### `runner.py`
- Reads in the config file
- Runs in the background (daemon), running the specified programs at the correct times
- keeps information about what and when programs will run, and when they last ran
- At startup, the program will writes it's `PID` to `$HOME/.runner.pid`, and create the `$HOME/.runner.status` file if it doesnt already exist.

### `runstatus.py`
- Gets the current status of `runner.py`, and prints it to standard output
- When run, it 
  - sends a `SIGUSR1` signal to `runner.py`, 
  - opens and outputs the `$HOME/.runner.status` file
  - clears the `$HOME/.runner.status` file

### `.runner.conf`
- The config file will be located at `$HOME/.runner.conf`
- Contains a list of programs to start, their parameters, what time to start them, and if and when to repeat them
- The lines should follow the below structure
```
timespec program-path parameters
```
  - `timespec` specifies the time and repetition of the program, it should be in the following structure
      ```
      [[​every​|​on​] [​day​[,​day...​ ]]] ​ at​ ​HHMM[​ ,​HHMM​...] ​run
      ```
      - times are in 24 hour time
      - `every`, `on`, `at` and `run` are keywords
  - `program-path` should be the full path to the program you want to run
  - `parameters` are the parameters for the program

Examples:
```
at 1355 run /bin/echo wooooow hi
every Tuesday at 1100 run /bin/echo hello
on Tuesday at 1100 run /bin/echo hello
every Monday,Wednesday,Friday at 0900,1200,1500 run /home/bob/myscript.sh
at 0900,1200 run /home/bob/myprog
```


### `.runner.status`
- Contains lines on the status of already run programs, and details of future programs.
- The format is as follows
```
ran date-time program-path parameters
error date-time program-path parameters
will run at date-time program-path parameters
```

## Error Handling
- Checks for errors in
  - config file
  - the fork/exec process
  - missing files e.g. `$HOME/.runner.pid` or `$HOME/.runner.status`
  - status taking more than 5 seconds to arrive in `$HOME/.runner.status`


## Testing
- While there are on automated tests written for this program, [this file](/tests.txt) outlines a number of 'test cases' with their expected functionality