import numpy as np
from math import prod


class Optimizer:
	"""A class that is managing the transformation of all partial derivatives
of the gradient to a single vector. This vector can then be further used for 
Optimization through an inhereting class"""
	def __call__(self, Δ):
		Δθ = self.flatten(Δ)
		Δθ_abs = np.linalg.norm(Δθ)
		Δθ = self.update(Δθ)
		return self.reshape(Δθ), Δθ_abs

	def __getattr__(self, key):
		return None

	def reset(self):
		saved = self.saved if self.saved is not None else {}
		for key in list(self.__dict__.keys()):
			if key not in saved and key != 'saved':
				self.__dict__.pop(key)

	def save(self):
		self.saved = {val: key for val, key in self.__dict__.items()}

	def flatten(self, Δ):
		if self.shapes is None:
			self.shapes = []
			full_size = 0
			for layer in Δ:
				layer_shapes = []
				for grad in layer:
					grad_size = prod(grad.shape)
					full_size += grad_size
					layer_shapes.append((grad.shape, grad_size))
				self.shapes.append(tuple(layer_shapes))
			self.Δ = np.zeros(full_size)
		return np.concatenate([np.concatenate(grad, axis=None) for grad in Δ], axis=None)

	def reshape(self, Δθ):
		Δ, idx = [], 0
		for layer in self.shapes:
			layer_Δ = []
			for shape, size in layer:
				layer_Δ.append(Δθ[idx:idx+size].reshape(shape))
				idx += size
			Δ.append(layer_Δ)
		return Δ



class Vanilla(Optimizer):
	@staticmethod
	def update(Δθ):
		return Δθ



class Adam(Optimizer):
	def __init__(self, β1=0.9, β2=0.999, ϵ=1e-8):
		self.β1 = β1
		self.β2 = β2
		self.ϵ = ϵ
		self.save()

	def update(self, Δθ):
		# Initilize states
		if self.m is None:
			self.m = np.zeros(Δθ.shape)
		if self.v is None:
			self.v = np.zeros(Δθ.shape)

		# update states
		self.m = self.β1 * self.m + (1 - self.β1) * Δθ
		self.v = self.β2 * self.v + (1 - self.β2) * Δθ**2
		
		# calculate interim results
		m = self.m/(1 - self.β1)
		v = self.v/(1 - self.β2)

		return m/(np.sqrt(v) + self.ϵ)