import numpy as np
from tqdm import trange


class Perceptron():
	"""Simple Perceptron Model to demonstrate the Functionality of one step Backpropagation"""
	def __init__(self, input_size, output_size):
		self.input_size = input_size
		self.output_size = output_size
		self.W = np.random.randn(output_size, input_size)
		
	# sigmoid function
	def sigmoid(self, x):
		return 1/(1 + np.exp(-x))

	# derivative of sigmoid function
	def sigmoid_derivative(self, x):
		return self.sigmoid(x) * (1 - self.sigmoid(x))

	# one step backpropagation
	def gradient(self, x, t):
		o = self(x)
		return np.dot((t - o) * self.sigmoid_derivative(o), t) 
	
	# training loop
	def train(self, xs, ts, epochs, eta=0.1):
		for i in trange(epochs):
			ΔW = np.zeros(self.W.shape)
			for x, t in zip(xs, ts):
				ΔW += self.gradient(x, t)
			self.W += eta/len(xs) * ΔW
	
	# one calculation step of the perceptron
	def __call__(self, x):
		return self.sigmoid(np.dot(self.W, x))
		
		
if __name__ == "__main__":
	# model
	input_size = 3
	output_size = 1
	P = Perceptron(input_size, output_size)
	
	# data
	xs = [np.array([0, 0, 1]), np.array([1, 1, 1]), np.array([1, 0, 0]), np.array([0, 1, 1])]
	ts = [np.array([0]), np.array([1]), np.array([1]), np.array([0])]

	# training
	epochs = 100
	eta = 1
	P.train(xs, ts, epochs, eta)

	# test
	print(f"Prediction: {P(np.array([1, 1, 0]))}")
