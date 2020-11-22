
"""
   WALK = 0
   TURNLEFT = 1
   TURNRIGHT = 2
   GRAB = 3
   SHOOT = 4
   CLIMB = 5
"""


import gym
import fh_ac_ai_gym
from os import system

env = gym.make('Wumpus-v0')
observations = env.reset()

print(observations)
env.render()

actions = {'Forward': 0, 'Left': 1, 'Right': 2, 'Grab': 3, 'Shoot': 4, 'Climb': 5}
done = False
while not done: # (action := Agent(observations)) != 'Climb'
	action = int(input())
	system('clear')
	observations, reward, done, info = env.step(action)
	print(done, observations, reward, info)
	env.render()

