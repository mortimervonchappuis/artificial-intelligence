import gym
import fh_ac_ai_gym
from Simulation import Simulation
from Agent import *
from utils import *
from os import system
"""
    WALK = 0
    TURNLEFT = 1
    TURNRIGHT = 2
    GRAB = 3
    SHOOT = 4
    CLIMB = 5
"""
system('clear')


algorithms = {'1': 'sarsa', '2': 'q-learning', '3': 'double q-learning'}
intro = """
REINFORCEMENT LEARNING

1) SARSA
2) Q-Learning
3) Double Q-Learning

››› """


while (algorithm := input(intro)) not in algorithms:
	system('clear')
algorithm = algorithms[algorithm]

system('clear')
print("""
REINFORCEMENT LEARNING
""")


# Hyperparameters 
if algorithm == 'sarsa':
	# SARSA
	def action_function(state):
		state = {key: val for key, val in zip(['x', 'y', 'gold', 'glitter', 'direction'], state.split(', '))}
		actions = [0, 1, 2]
		if state['glitter'] == 'True':
			actions.append(3)
		if state['x'] == state['y'] == '0':
			actions.append(5)
		return actions
	
	# action_function = lambda state: [0, 1, 2, 3, 5]

	alpha = 0.6
	gamma = 1
	epsilon = 0.4
	episodes = 10000
elif algorithm == 'q-learning':
	# Q Learning
	action_function = lambda state: [0, 1, 2, 3, 5]
	alpha = 0.8
	gamma = 1.
	epsilon = 0.3
	episodes = 10000
elif algorithm == 'double q-learning':
	# Double Q Learning
	action_function = lambda state: [0, 1, 2, 3, 5]
	alpha = 0.8
	gamma = 1.
	epsilon = 0.3
	episodes = 20000


policy = EpsilonGreedy(epsilon)
interpretation = lambda obs: ', '.join(str(obs[key]) for key in ['x', 'y', 'gold', 'glitter', 'direction'])

# Environment
env = gym.make('Wumpus-v0')

# Agents
if algorithm == 'sarsa':
	agent = Sarsa(action_function, policy, alpha, gamma, lambda *_: 0)
elif algorithm == 'q-learning':
	agent = Qlearning(action_function, policy, alpha, gamma, lambda *_: 0)
elif algorithm == 'double q-learning':
	agent = DoubleQlearning(action_function, policy, alpha, gamma, lambda *_: 0)

# Simulation
Simulation = Simulation(env, agent, interpretation)
Simulation(episodes)

# Lets have a look
while input('Watch Episode? [y/n] ') != 'n':
	Simulation.show()
system('clear')
