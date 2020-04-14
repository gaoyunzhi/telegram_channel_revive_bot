import os
import sys

def kill():
	os.system("ps aux | grep ython | grep 'revive.py' | awk '{print $2}' | xargs kill -9")

def setup(arg = ''):
	if arg == 'kill':
		return kill()

	RUN_COMMAND = 'nohup python3 -u revive.py &'

	kill()
	if arg.startswith('debug'):
		os.system(RUN_COMMAND[6:-2])
	else:
		os.system(RUN_COMMAND)

if __name__ == '__main__':
	if len(sys.argv) > 1:
		setup(sys.argv[1])
	else:
		setup('')