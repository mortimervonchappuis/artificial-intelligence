from propositional import *


KB = [

]


L_0_11 = Atomic(value=True) # Agent Position
P_11 = Atomic(value=True) # Pit Position
W_11 = Atomic(value=True) # Wumpus Position
WA_0 = Atomic(value=True) # Wumpus Alive
HA_0 = Atomic(value=True) # Having Arrow


def adjacent(i, j):
	if i-1 > 0:
		yield str(i-1) + str(j)
	if i+1 < 5:
		yield str(i+1) + str(j)
	if j-1 > 0:
		yield str(i) + str(j-1)
	if j+1 < 5:
		yield str(i) + str(j+1)


def other(i, j):
	for x in range(1, 5):
		for y in range(1, 5):
			if i != x or j != y:
				yield str(x) + str(y)


# Creating Variables
for i in range(1, 5):
	for j in range(1, 5):
		exec(f"(B_{i}{j} := Atomic())")
		exec(f"(S_{i}{j} := Atomic())")
		KB.append(eval(f"B_{i}{j}"))
		KB.append(eval(f"S_{i}{j}"))
		print(globals())
		if i != 1 and j != 1:
			exec(f"KB.append((W_{i}{j} := Atomic()))")
			exec(f"KB.append((P_{i}{j} := Atomic()))")

print(KB)
# Creating perception Rules
for i in range(1, 5):
	for j in range(1, 5):
		KB.append(eval(f"B_{i}{j} == {' + '.join('P_' + square for square in adjacent(i, j))}"))
		KB.append(eval(f"S_{i}{j} == {' + '.join('W_' + square for square in adjacent(i, j))}"))
		KB.append(eval(f"W_{i}{j} >> {' + '.join('-W_' + square for square in other(i, j))}"))


print(KB)
#		KB.append(f"B_{i}{j} ⇔ {' ∨ '.join('P_' + square for square in adjacent(i, j))}")
#		KB.append(f"S_{i}{j} ⇔ {' ∨ '.join('W_' + square for square in adjacent(i, j))}")
#		KB.append(f"W_{i}{j} ⇒ {' ∧ '.join('¬W_' + square for square in other(i, j))}")


