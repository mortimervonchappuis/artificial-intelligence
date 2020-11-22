from random import uniform, choice


class Function:
	"""Function is a Class for implementing tabular functions.
It stores values in an array like structure, which can be 
assigned and called for via F[x]. x must be hashable"""
	def __init__(self, base_function=None):
		self.base_function = base_function
		self.array = {}

	def __getitem__(self, x):
		if x in self.array:
			return self.array[x]
		elif self.base_function is not None:
			return self.base_function(x)
		else:
			return None

	def __setitem__(self, key, val):
		self.array[key] = val


class EpsilonGreedy:
	def __init__(self, epsilon=0.2):
		self.e = epsilon

	def __call__(self, S, A, Q, greedy=False):
		actions = A(S)
		if uniform(0, 1) < self.e and not greedy:
			return choice(actions)
		else:
			return max(actions, key=lambda a: Q[S, a])
