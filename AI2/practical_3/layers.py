import numpy as np
from activation import Identity
from numpy.lib.stride_tricks import sliding_window_view as slide
from math import ceil, prod
rot180 = lambda x: np.rot90(x, 2, axes=(0, 1))



class BaseLayer:
	def apply_Δ(self, *args):
		pass

	def set(self, size):
		pass



class Layer(BaseLayer):
	def __init__(self, size, activation=Identity(), l2=None):
		self.output_size = size
		self.b = np.random.rand(self.output_size, 1)
		self.l2 = l2
		self.σ = activation
		self.trainable = True

	def __str__(self):
		return f"Layer:\tW:\t{self.W.shape}\tb:\t{self.b.shape}"

	def set(self, input_size):
		self.input_size = input_size
		self.W = np.random.randn(self.output_size, self.input_size)

	def __call__(self, i):
		self.i = i
		self.z = np.dot(self.W, i) + self.b
		self.o = self.σ(self.z)
		return self.o

	def Δ(self, δ):
		""" returns: ΔW, Δb, δ	forward: Wi + b = z		σ(z) = o"""
		try:
			δ = δ * self.σ.Δ(self.o)
		except:
			#print(δ.shape, self.σ.Δ(self.o).shape)
			#quit()
			δ = np.einsum('ji,ilj->li', δ, self.σ.Δ(self.o))
		ΔW = np.dot(δ, self.i.T)
		Δb = np.expand_dims(np.mean(δ, axis=-1), axis=1)
		δ = np.dot(self.W.T, δ)
		return (ΔW, Δb), δ

	def apply_Δ(self, W, b, η):
		if self.trainable:
			if self.l2  is not None:
				self.W = (1 - η*self.l2) * self.W - η * W
			else:
				self.W -= η * W
			self.b -= η * b



class Perceptron(BaseLayer):
	def __init__(self, size, activation, l2=None):
		self.output_size = size
		self.σ = activation
		self.l2 = l2
		self.trainable = True

	def set(self, input_size):
		self.input_size = input_size
		self.W = np.random.randn(self.output_size, self.input_size)

	def __call__(self, i):
		self.i = i
		self.z = np.dot(self.W, i)
		self.o = self.σ(self.z)
		return self.o

	def Δ(self, δ):
		""" returns: ΔW, δ	forward: Wi = z		σ(z) = o"""
		try:
			δ = δ * self.σ.Δ(self.o)
		except:
			δ = np.einsum('ji,ijl->li', δ, self.σ.Δ(self.o))
		ΔW = np.dot(δ, self.i.T)
		δ = np.dot(self.W.T, δ)
		return (ΔW,), δ

	def apply_Δ(self, W, η):
		if self.trainable:
			if self.l2  is not None:
				self.W = (1 - η*self.l2) * self.W - η * W
			else:
				self.W -= η * W



class Conv(BaseLayer):
	def __init__(self, size, kernel, padding='same', activation=Identity()):
		self.i, self.j = self.kernel_shape = kernel
		self.size = size
		self.b = np.random.randn(1, 1, self.size, 1)
		self.padding = padding
		self.σ = activation
		self.i_start = self.i // 2
		self.j_start = self.j // 2
		self.i_end = self.i_start - (1 if self.i % 2 == 0 else 0)
		self.j_end = self.j_start - (1 if self.j % 2 == 0 else 0)
		self.trainable = True

	def __call__(self, x):
		if x.ndim == 3:
			x = np.expand_dims(x, axis=2)
		self.x = x
		xi, xj, x_size, batchsize = x.shape
		if self.padding == 'same':
			padded = self._pad(x)
		else:
			padded = x

		window = slide(padded, self.kernel_shape, axis=(0, 1))
		z = np.einsum('ijklmn,mnkop->ijol', window, rot180(self.K))
		self.o = self.σ(z + self.b)
		return self.o

	def __getitem__(self, idx):
		return self.K[idx]

	def _pad(self, x):
		if x.ndim == 4:
			xi, xj, x_size, batchsize = x.shape
			padded = np.zeros((
					self.i_start + self.i_end + xi,
					self.j_start + self.j_end + xj,
					x_size, batchsize))
			padded[self.i_start:-self.i_end,
			self.j_start:-self.j_end,:,:] = x
		else:
			xi, xj, sample, x_size, batchsize = x.shape
			padded = np.zeros((
					self.i_start + self.i_end + xi,
					self.j_start + self.j_end + xj,
					sample, x_size, batchsize))
			padded[self.i_start:-self.i_end,
			self.j_start:-self.j_end,:,:,:] = x
		return padded

	def Δ(self, δ):
		""" returns: ΔW, δ  	forward: K×i = z 	σ(z) = o"""
		try:
			δ = δ * self.σ.Δ(self.o)
		except:
			δ = np.einsum('ji,ijl->li', δ, self.σ.Δ(self.o))
		xi, xj, sample_size, batchsize = δ.shape 
		Δb = δ
		Δb = np.sum(Δb, axis=(0, 1, 3))
		Δb = np.expand_dims(Δb, axis=(0, 1, 3))
		ΔK = np.einsum('ijkl,mnklij->mnk', self.o, 
			slide(self._pad(rot180(δ)), δ.shape[:2], axis=(0, 1)))

		ΔK = np.expand_dims(ΔK, axis=(2, 4))
		δ = np.einsum('ijklm,nolpij->nokp', rot180(self.K), 
			slide(self._pad(δ), self.kernel_shape, axis=(0, 1)))
		return (ΔK, Δb), δ

	def apply_Δ(self, K, b, η):
		if self.trainable:
			self.K -= η * K
			self.b -= η * b

	def set(self, size):
		self.output_size = size[:2] + (self.size,)
		self.d = size[2]
		self.K = np.random.randn(self.i, self.j, self.d, self.size, 1)



class MaxPooling(BaseLayer):
	def __init__(self, size, activation=Identity()):
		self.σ = activation
		self.size = self.i, self.j = size
		self.trainable = True

	def __iter__(self):
		for i in range(self.i):
			for j in range(self.j):
				yield i, j

	def __call__(self, x):
		self.x = x
		self.z = np.max([x[i::self.i, j::self.j,:,:] for i, j in self], axis=0)
		self.o = self.σ(self.z)
		return self.o

	def Δ(self, δ):
		try:
			δ = δ * self.σ.Δ(self.o)
		except:
			δ = np.einsum('ji,ijl->li', δ, self.σ.Δ(self.o))
		δ = np.repeat(δ, self.i, axis=0)
		δ = np.repeat(δ, self.j, axis=1)
		z = np.repeat(self.z, self.i, axis=0)
		z = np.repeat(z, self.j, axis=1)
		δ[np.not_equal(self.x, z)] = 0.
		return (np.array([]),), δ

	def set(self, size):
		self.input_size = i, j, sample = size
		self.output_size = (ceil(i/self.i), ceil(j/self.j), sample)



class AveragePooling(BaseLayer):
	def __init__(self, size, activation=Identity()):
		self.σ = activation
		self.size = self.i, self.j = size
		self.trainable = True

	def __iter__(self):
		for i in range(self.i):
			for j in range(self.j):
				yield i, j

	def __call__(self, x):
		self.x = x
		self.z = np.mean([x[i::self.i, j::self.j,:,:] for i, j in self], axis=0)
		self.o = self.σ(self.z)
		return self.o

	def Δ(self, δ):
		try:
			δ = δ * self.σ.Δ(self.o)
		except:
			δ = np.einsum('ji,ijl->li', δ, self.σ.Δ(self.o))
		δ = np.repeat(δ, self.i, axis=0)
		δ = np.repeat(δ, self.j, axis=1)
		δ /= prod(self.size)
		return (np.array([]),), δ

	def set(self, size):
		self.input_size = i, j, sample = size
		self.output_size = (ceil(i/self.i), ceil(j/self.j), sample)



class Flatten(BaseLayer):
	def __call__(self, i):
		self.i = i
		self.i_shape = i.shape
		self.o_shape = (prod(self.i_shape[:-1]), self.i_shape[-1])
		self.o = self.i.reshape(self.o_shape)
		return self.o

	def Δ(self, δ):
		return (np.array([]),), δ.reshape(self.i_shape)

	def set(self, size):
		self.input_size = size
		if isinstance(size, int):
			self.output_size = size
		else:
			self.output_size = prod(size)
