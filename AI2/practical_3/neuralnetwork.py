import warnings
import numpy as np
from tqdm import tqdm
from random import shuffle
from optimizer import Vanilla
from math import ceil
warnings.filterwarnings('ignore')



class NeuralNetwork:
	def __init__(self, input_size, loss, optimizer=Vanilla()):
		self.layers = []
		self.input_size = input_size
		self.loss = loss
		self.optimizer = optimizer
		self.error = 0

	def __str__(self):
		return "Neural Network:\n" + '\n'.join(str(layer) for layer in self)

	def __getitem__(self, idx):
		return self.layers[idx]

	def __iter__(self):
		for layer in self.layers:
			yield layer

	def __len__(self):
		return len(self.layers)
	
	def __add__(self, layer):
		if not self.layers:
			layer.set(self.input_size)
		else:
			layer.set(self[-1].output_size)
		self.layers.append(layer)

	def __call__(self, x):
		a = x.copy()
		for layer in self:
			a = layer(a)
		return a

	def Δ(self, x, y):
		# calculate Error
		p = self(x)
		self.error = float(np.mean(self.loss(p, y)))

		# calculate last layer derivative and loss derivative
		Δσ = self[-1].σ.Δ(p)
		δ = self.loss.Δ(p, y)

		# Backpropagation
		Δ = []
		for layer in self[::-1]:
			grad, δ = layer.Δ(δ)
			Δ.append(grad)
		return Δ, δ

	def SGD(self, x, y, epochs, batchsize, η=1.):
		# Setting up the training episode
		N = x.shape[-1]
		self.optimizer.reset()
		history = {'loss': [], 'grads': []}

		# Starting the training
		with tqdm(total=(N//batchsize)*epochs) as pbar:
			pbar.set_description(f"|Δ|=None\tLoss=None")
			for epoch in range(epochs):
				xs, ys = self.randomize(x.T, y.T)
				for i in range(0, N - (N % batchsize), batchsize):
					if x.ndim == 2:
						x_batch = xs[:,i:i+batchsize]
					else:
						x_batch = xs[:,:,i:i+batchsize]
					y_batch = ys[:,i:i+batchsize]
					Δ, _ = self.Δ(x_batch, y_batch)

					# Process gradient
					Δ, Δ_abs = self.optimizer(Δ)
					pbar.set_description("|Δ|={0:.2f}\tLoss={1:.3f}".format(
						round(Δ_abs, 2), round(self.error, 3)))
					history['loss'].append(self.error)
					history['grads'].append(Δ_abs)

					# Apply gradient
					for grad, layer in zip(Δ, self[::-1]):
						layer.apply_Δ(*grad, η)
					pbar.update(1)
		return history

	def predict(self, x):
		return np.argmax(self(x))

	def evaluate(self, x, y, verbose=True):
		p = self(x)
		loss = float(np.mean(self.loss(p, y)))
		acc = float(np.mean(np.argmax(p, axis=0) == np.argmax(y, axis=0)))
		if verbose:
			print("Accuracy:\t{0:.2f}%\nAverage Loss:\t{1:.3f}".format(
				round(acc*100, 2), round(loss, 3)))
		return acc, loss

	@staticmethod
	def randomize(*args):
		idx = list(range(min(len(item) for item in args)))
		shuffle(idx)
		return tuple((np.array([arg[i] for i in idx]).T for arg in args))
