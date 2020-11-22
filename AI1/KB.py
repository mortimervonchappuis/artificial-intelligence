from logic import *


def adjacent(i, j):
	if i-1 >= 0:
		yield (i-1, j)
	if i+1 < 4:
		yield (i+1, j)
	if j-1 >= 0:
		yield (i, j-1)
	if j+1 < 4:
		yield (i, j+1)


def other(i, j):
	for x in range(4):
		for y in range(4):
			if i != x or j != y:
				yield str(x) + str(y)


facts = [
	Symb('¬P_00'),
	Symb('¬W_00'),
	Symb('WA_0'),
]

def conjunc(*args):
	sentence = args[0]
	for literal in args[1:]:
		sentence = sentence & literal
	return sentence


def disjunc(*args):
	sentence = args[0]
	for literal in args[1:]:
		sentence = sentence | literal
	return sentence


OK = lambda t, i, j: ~Symb(f'P_{i}{j}') & (~Symb(f'W_{i}{j}') | ~Symb(f'WA_{t}'))
KB = CNF(conjunc(*facts))
if __name__ == '__main__':
	print(KB)