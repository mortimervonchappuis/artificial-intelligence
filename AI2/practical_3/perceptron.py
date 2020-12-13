import numpy as np
from tqdm import trange


np.random.seed(42)


class Perceptron:
	"""Simple Perceptron Model to demonstrate the Functionality of one step Backpropagation"""
	def __init__(self, input_size, output_size):
		self.input_size = input_size
		self.output_size = output_size
		self.W = np.random.randn(output_size, input_size)
		
	# sigmoid function
	def σ(self, x):
		return 1/(1 + np.exp(-x))

	# derivative of sigmoid function
	def σ_(self, x):
		return self.σ(x) * (1 - self.σ(x))

	# one step backpropagation
	def Δ(self, x, t):
		o = self(x)
		x = np.expand_dims(x, axis=0).T
		return np.dot((t - o) * self.σ_(o), x.T)
	
	# training loop
	def train(self, xs, ts, epochs, η=0.1):
		for i in trange(epochs):
			ΔW = np.zeros(self.W.shape)
			for x, t in zip(xs, ts):
				ΔW += self.Δ(x, t)
			self.W += η/len(xs) * ΔW
	
	# one calculation step of the perceptron
	def __call__(self, x):
		return self.σ(np.dot(self.W, x))
		

if __name__ == "__main__":
	# model
	input_size = 3
	output_size = 1
	P = Perceptron(input_size, output_size)
	
	# data
	xs = [
		np.array([0, 0, 1]), 
		np.array([1, 1, 1]), 
		np.array([1, 0, 0]), 
		np.array([0, 1, 1])
		]
	ts = [
		np.array([0]), 
		np.array([1]), 
		np.array([1]), 
		np.array([0])
		]

	# training
	epochs = 1000
	η = .1

	print(P.W)
	P.train(xs, ts, epochs, η)

	# test
	print(P.W)
	for x in (np.array([0, 1, 0]), np.array([0, 1, 1]), np.array([1, 1, 1]), np.array([1, 1, 0])):
		print(f"Prediction: x = {x}		p = {P(x)}")
