from utils import *
from random import uniform


class Sarsa:
	def __init__(self, Actions, policy=EpsilonGreedy(epsilon=0.2), alpha=0.7, gamma=0.7, q_base=lambda *_: 0):
		self.Q = Function(q_base)
		self.Actions = Actions
		self.PI = policy
		self.S = None
		self.A = None
		self.a = alpha
		self.g = gamma

	def reset(self):
		self.S = None
		self.A = None

	def get_action(self, S, greedy=False):
		return self.PI(S, self.Actions, self.Q, greedy)

	def __call__(self, R, S_):
		# Initialize
		if self.S is None:
			self.S = S_
			self.A = self.PI(self.S, self.Actions, self.Q)
			return self.A
		# Mainloop
		else:
			A_ = self.PI(self.S, self.Actions, self.Q)
			self.Q[self.S, self.A] += self.a * (R + self.g * self.Q[S_, A_] - self.Q[self.S, self.A])
			self.S = S_
			self.A = A_
			return A_


class Qlearning:
	def __init__(self, Actions, policy=EpsilonGreedy(epsilon=0.2), alpha=0.7, gamma=0.7, q_base=lambda *_: 0):
		self.Q = Function(q_base)
		self.Actions = Actions
		self.PI = policy
		self.S = None
		self.A = None
		self.a = alpha
		self.g = gamma

	def reset(self):
		self.S = None
		self.A = None

	def get_action(self, S, greedy=False):
		return self.PI(S, self.Actions, self.Q, greedy)

	def __call__(self, R, S_):
		# Initialize
		if self.S is None:
			self.S = S_
			self.A = self.PI(self.S, self.Actions, self.Q)
			return self.A
		# Mainloop
		else:
			A_ = self.PI(self.S, self.Actions, self.Q)
			self.Q[self.S, self.A] += self.a * (R + self.g * max(self.Q[S_, a] for a in self.Actions(S_)) - self.Q[self.S, self.A])
			self.S = S_
			self.A = A_
			return A_


class DoubleQlearning:
	def __init__(self, Actions, policy=EpsilonGreedy(epsilon=0.2), alpha=0.7, gamma=0.7, q_base=lambda *_: 0):
		self.Q1 = Function(q_base)
		self.Q2 = Function(q_base)
		self.Actions = Actions
		self.PI = policy
		self.S = None
		self.A = None
		self.a = alpha
		self.g = gamma

	def reset(self):
		self.S = None
		self.A = None

	def get_action(self, S, greedy=False):
		if uniform(0, 1) < 0.5:
			return self.PI(S, self.Actions, self.Q1, greedy)
		else:
			return self.PI(S, self.Actions, self.Q2, greedy)

	def __call__(self, R, S_):
		# Initialize
		if self.S is None:
			self.S = S_
			self.A = self.PI(self.S, self.Actions, self.Q1) # Since the initial Q1 and Q2 are identical, the choice between them is irrelevant
			return self.A
		# Mainloop
		else:
			if uniform(0, 1) < 0.5:
				A_ = self.PI(self.S, self.Actions, self.Q1)
				self.Q1[self.S, self.A] += self.a * (R + self.g * max(self.Q2[S_, a] for a in self.Actions(S_)) - self.Q1[self.S, self.A])
			else:
				A_ = self.PI(self.S, self.Actions, self.Q2)
				self.Q2[self.S, self.A] += self.a * (R + self.g * max(self.Q1[S_, a] for a in self.Actions(S_)) - self.Q2[self.S, self.A])
			self.S = S_
			self.A = A_
			return A_

