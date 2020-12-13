import numpy as np
from utils import diag


class Identity:
	@staticmethod
	def __call__(x):
		return x

	@staticmethod
	def Δ(x):
		return np.ones(x.shape)



class Sigmoid:
	@staticmethod
	def __call__(x):
		return 1/(1 + np.exp(-x))

	@staticmethod
	def Δ(x):
		return np.exp(-x)/((1 + np.exp(x))**2)



class ReLU:
	def __init__(self, leaky=0):
		self.leaky = leaky

	def __call__(self, x):
		y = x.copy()
		y[x <= 0] *= self.leaky 
		return y

	def Δ(self, x):
		y = np.ones(x.shape)
		y[x <= 0] = self.leaky
		return y



class SoftMax:
	@staticmethod
	def __call__(x):
		exps = np.exp(x - np.max(x))
		return exps/np.sum(exps)

	def Δ(self, x):
		vec = self(x)
		return diag(vec) - np.dot(vec, vec.T)
