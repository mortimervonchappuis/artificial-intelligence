import numpy as np


class Loss:
	"""Calculates the loss, and keeps a rolling average discounted by λ"""
	def __init__(self, function, derivative):
		self.function = function
		self.derivative = derivative


	def __call__(self, p, y):
		return self.function(p, y)

	def Δ(self, p, y):
		return self.derivative(p, y)



class MSE:
	"""Calculates the loss, and keeps a rolling average discounted by λ"""
	def __call__(self, p, y):
		return 0.5 * np.sum((p - y)**2, axis=0)

	def Δ(self, p, y):
		return p - y



class MSE_Attention(Loss):
	def __init__(self, γ=2):
		super().__init__(self.attention_loss, self.attention_derivative)
		self.γ = γ

	def attention_loss(self, p, y):
		if np.argmax(p) == np.argmax(y):
			return 0.5 * np.dot((p - y).T, p - y)
		else:
			return (0.5 + self.γ/len(p)) * np.dot((p - y).T, p - y)

	def attention_derivative(self, p, y):
		if np.argmax(p) == np.argmax(y):
			return p - y
		else:
			return (1 + self.γ/len(p)) * (p - y)
