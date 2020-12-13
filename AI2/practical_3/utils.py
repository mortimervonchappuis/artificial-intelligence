import numpy as np


def diag(x):
	return np.array([np.diag(r) for r in x.T])