from tqdm import trange
from os import system
from time import sleep


class Simulation:
	"""Simulation silumates multiple Episodes"""
	def __init__(self, env, agent, state_interpretation):
		self.env = env
		self.agent = agent
		self.interpretation = state_interpretation

	def __call__(self, n):
		V = 0
		Vs = []
		for i in trange(n):
			done = False
			reward = 0
			score = 0
			state = self.env.reset()
			while not done:
				#self.env.render()
				action = self.agent(reward, self.interpretation(state))
				#print('ACTION', action)
				state, reward, done, _ = self.env.step(action)
				reward = reward[0]
				score += reward
				#if state['gold']:
				#	print('\n'.join(str(t) for t in self.agent.Q.array.items()))
				#	print('Action', action)
				#	self.env.render()
				#	input('NEXT')

				#self.env.render()
				#print(self.interpretation(state))
				#print('\n'.join(str(t) for t in self.agent.Q.array.items()))
			#print('REWARD', reward)
			self.agent(reward, self.interpretation(state))
			self.agent.reset()
			#self.env.render()
			#if score > 0 and state['x'] == 0 == state['y']:
			#	#print('\n'.join(str(t) for t in self.agent.Q.array.items()))
			#	#self.env.render()
			#	system('clear')
			#	if Vs: print(sum(Vs)/len(Vs))
			#	#input(f'{i} NEXT {i - V}')
			#	if V: Vs.append(i - V)
			#	V = i
			#	#Vs = Vs[-100:]
			##print('\n'.join(str(t) for t in self.agent.Q.array.items()))
#
			##print('\nDONE\n')
		#print('SCORE', score)

	def show(self, greedy=False):
		self.env.reset()
		done = False
		state = self.env.reset()
		while not done:
			system('clear')
			self.env.render()
			action = self.agent.get_action(self.interpretation(state), greedy)
			print('Action:', action)
			state, reward, done, _ = self.env.step(action)
			sleep(0.1)
		system('clear')
		self.env.render()

