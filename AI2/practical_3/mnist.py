import numpy as np


train_file = "data/train.csv"
test_file = "data/test.csv"
# θ η λ σ Δ ∂ δ γ


def load_file(file, vectorize, limit):
    xs, ys = [], []
    for i, line in enumerate(open(file, 'r').readlines()):
        if limit is not None and i >= limit:
            break
        items = line.split(',')
        xs.append([int(item) for item in items[1:]])
        y = [0] * 10
        y[int(items[0])] = 1
        ys.append(y)
    if limit is None:
        limit = i + 1
    x = np.array(xs).T
    y = np.array(ys).T
    if not vectorize:
        x = x.reshape(28, 28, limit)
    return x, y


def load_mnist(vectorize=True, limit=None):
    return load_file(train_file, vectorize, limit), load_file(test_file, vectorize, limit)
