def turn(current, target):
	directions = {'West': 0, 'North': 1, 'East': 2, 'South': 3}
	turning_number = (directions[current] - directions[target]) % len(directions)
	if turning_number < 3:
		return ['Left'] * turning_number
	else:
		return ['Right']

def direction(current, target):
	ci, cj = current
	ti, tj = target
	if cj - tj == 1:
		return 'South'
	elif cj - tj == -1:
		return 'North'
	elif ci - ti == 1:
		return 'East'
	elif ci - ti == -1:
		return 'West'

import signal

def handler(signum, frame):
    print('Signal handler called with signal', signum)
    exit()

# Set the signal handler and a 5-second alarm
signal.signal(signal.SIGINT, handler)
while True:
	pass