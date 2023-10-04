echo $'Tests with valid configuraiton files: As the timing is difficult, I have provided a description/example for each configuration file. Please see tests.txt.\n'


echo $'Tests for invalid config lines.\n==================================='

echo '' > ~/.runner.conf
echo 'configuration file empty' > expected.txt
python3 runner.py | diff - expected.txt || 'Empty config file test failed'

echo 'every Tuesday,Wednesday,Tuesday at 1200,1100 run /bin/date' > ~/.runner.conf
echo 'Error in configuration: every Tuesday,Wednesday,Tuesday at 1200,1100 run /bin/date' > expected.txt
python3 runner.py | diff - expected.txt  || 'Repeated Day test failed'

echo 'every Tues at 1100 run /bin/date' > ~/.runner.conf
echo 'Error in configuration: every Tues at 1100 run /bin/date' > expected.txt
python3 runner.py | diff - expected.txt  || 'Incorrect dayname (abbreviated) test failed'

echo 'every tuesday at 1100 run /bin/date' > ~/.runner.conf
echo 'Error in configuration: every tuesday at 1100 run /bin/date' > expected.txt
python3 runner.py | diff - expected.txt  || 'Incorrect dayname (capitailsation) test failed'

echo 'every Tuesday at 11000 run /bin/date' > ~/.runner.conf
echo 'Error in configuration: every Tuesday at 11000 run /bin/date' > expected.txt
python3 runner.py | diff - expected.txt  || 'Incorrect time format test failed'

echo 'on Tuesday at 1100 /bin/date' > ~/.runner.conf
echo 'Error in configuration: on Tuesday at 1100 /bin/date' > expected.txt
python3 runner.py | diff - expected.txt  || 'No run keyword test failed'

echo 'on every Tuesday at 1100 run /bin/date' > ~/.runner.conf
echo 'Error in configuration: on every Tuesday at 1100 run /bin/date' > expected.txt
python3 runner.py | diff - expected.txt  || 'Bad syntax test failed'

echo 'on Tuesday at 2400 run /bin/date' > ~/.runner.conf
echo 'Error in configuration: on Tuesday at 2400 run /bin/date' > expected.txt
python3 runner.py | diff - expected.txt  || 'Out of range time test failed'

echo 'on Tuesday at 1260 run /bin/date' > ~/.runner.conf
echo 'Error in configuration: on Tuesday at 1260 run /bin/date' > expected.txt
python3 runner.py | diff - expected.txt  || 'Out of range time test failed'

echo 'on Tuesday at 123 run /bin/date' > ~/.runner.conf
echo 'Error in configuration: on Tuesday at 123 run /bin/date' > expected.txt
python3 runner.py | diff - expected.txt  || 'Bad time test failed'

echo $'on Tuesday at 1100 run /bin/date\non Tuesday at 1100 run /bin/date' > ~/.runner.conf
echo 'Error in configuration: on Tuesday at 1100 run /bin/date' > expected.txt
python3 runner.py | diff - expected.txt  || 'Repeated time over multiple lines test failed'

echo 'on Tuesday at 1100 run' > ~/.runner.conf
echo 'Error in configuration: on Tuesday at 1100 run' > expected.txt
python3 runner.py | diff - expected.txt  || 'No path test failed'