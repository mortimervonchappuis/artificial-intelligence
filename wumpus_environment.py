import gym
import fh_ac_ai_gym
from fh_ac_ai_gym.wumpus import Location
from WumpusAgents import *
from os import system


clear = lambda: system('clear') # cls for Windows
clear()

env = gym.make('Wumpus-v0')
observations = env.reset()

inferences = {'R': 'resolution', 'F': 'forwardchaining'}
while (inference := input(f"""How should be reasond?
(R) Resolution
(F) Forwardchaining
»»»""").upper()) not in inferences:
	clear()
inference = inferences[inference]

if inference == 'resolution':
	players = {'H': 'human', 'M': 'machine'}
	while (player := input(f"""Who should play?
(H) Human - Your humble self
(M) Machine - the Computer WARNING! Runs really slow with resolution 
»»»""").upper()) not in players:
		clear()
	player = players[player]
else:
	player = 'human'


if player == 'human':
	WumpusSlayer = SupportWumpusAgent(inference)
else:
	WumpusSlayer = HybridWumpusAgent(inference)

clear()
env.render()

actions = {'Forward': 0, 'Left': 1, 'Right': 2, 'Grab': 3, 'Shoot': 4, 'Climb': 5}
action, reward = True, 0

if player == 'machine':
	env.render()
while (action := WumpusSlayer(observations)) != 'Climb':
	observations, reward, done, info = env.step(actions[action])
	clear()
	env.render()
print('Reward', reward)