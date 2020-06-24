class Symb:
	def __init__(self, name, value=None):
		self.name = name.replace('¬', '').replace('-', '')
		if value is None:
			self.value = not name.startswith('¬') and not name.startswith('-')
		else:
			self.value = value

	def __str__(self):
		return f"{'' if self.value else '¬'}{self.name}"

	def __repr__(self):
		return str(self)

	def __iter__(self):
		return self

	def __hash__(self):
		return hash(str(self))

	def __invert__(self):
		return Symb(self.name, not self.value)

	def __bool__(self):
		return self.value

	def __and__(self, other):
		return Expr(self, other, 'and')

	def __or__(self, other):
		return Expr(self, other, 'or')

	def __rshift__(self, other):
		return Expr(self, other, 'imp')

	def __eq__(self, other):
		return Expr(self, other, 'equiv')

	def equals(self, other):
		return self.name == other.name and self.value == other.value


class Expr(Symb):
	op_names = {
	'and': '∧', 
	'or': '∨', 
	'imp': '⊃', 
	'equiv': '≡',
	}
	def __init__(self, first, second, operator, value=True):
		self.first = first
		self.second = second
		self.operator = operator
		self.value = value

	def __bool__(self):
		calc = {
		'and': bool(self.first) and bool(self.second), 
		'or': bool(self.first) or bool(self.second), 
		'imp': not bool(self.first) or bool(self.second), 
		'equiv': not bool(self.first) or bool(self.second) and bool(self.first) or not bool(self.second),
		}
		if self.value:
			return calc[self.operator]
		else:
			return not calc[self.operator]

	def __str__(self):
		return f"{'' if self.value else '¬'}({self.first}{self.op_names[self.operator]}{self.second})"

	def __invert__(self):
		return Expr(self.first, self.second, self.operator, not self.value)

	def __repr__(self):
		return str(self)

	def __getattr__(self, attr):
		if attr == 'name':
			return str(self)

	def elim_equiv(self):
		if self.operator == 'equiv':
			return Expr((self.first >> self.second), (self.second >> self.first), 'and', self.value)
		return self

	def elim_imp(self):
		if self.operator == 'imp':
			return Expr(~self.first, self.second, 'or', self.value)
		return self

	def elim_neg(self):
		# De Morgan
		if not self.value:
			if self.operator == 'and':
				return Expr(~self.first, ~self.second, 'or', True)
			elif self.operator == 'or':
				return Expr(~self.first, ~self.second, 'and', True)
		return self

	def distribute(self):
		# only distributes AND up
		if self.operator == 'or':
			# (a*b)+c = (a+c)*(b+c) 
			if isinstance(self.first, Expr) and self.first.operator == 'and':
				return Expr(self.first.first | self.second, self.first.second | self.second, 'and', self.value)
			# a+(b*c) = (a+b)*(a+c) 
			elif isinstance(self.second, Expr) and self.second.operator == 'and':
				return Expr(self.first | self.second.first, self.first | self.second.second, 'and', self.value)
		return self


class Clause:
	def __init__(self, *args):
		self.set = set(args)

	def __str__(self):
		return f"[{', '.join(str(literal) for literal in self)}]"

	def __repr__(self):
		return str(self)

	def __hash__(self):
		return sum(hash(literal) for literal in self)

	def __iter__(self):
		for literal in self.set:
			yield literal

	def __contains__(self, key):
		return any((literal.equals(key) if isinstance(literal, Symb) else literal == key) for literal in self)

	def __len__(self):
		return len(self.set)

	def __eq__(self, other):
		if isinstance(other, Clause):
			return self.set == other.set
		elif isinstance(other, set):
			return self.set == other
		raise Exception(f'{type(other)} ARG')

	def __le__(self, other):
		return self.set <= other.set

	def __ge__(self, other):
		return self.set >= other.set

	def __lt__(self, other):
		return self.set < other.set

	def __gt__(self, other):
		return self.set > other.set

	def __mul__(self, other):
		yielded = set()
		for val_i in self:
			for val_j in other:
				if (val_j, val_i) not in yielded:
					yielded.add((val_i, val_j))
					yield val_i, val_j

	def __add__(self, other):
		return Clause(*self, *other)

	def __sub__(self, other):
		if isinstance(other, Clause):
			return Clause(*(self.set - other.set))
		elif isinstance(other, Symb):
			return Clause(*(literal for literal in self if not other.equals(literal)))

	def __iadd__(self, other):
		return self + other

	def __isub__(self, other):
		return self - other

	def __contains__(self, *literals):
		return all(literal in self.set for literal in literals)


class Conjunction(Clause):
	def __add__(self, other):
		if isinstance(other, Conjunction):
			return Conjunction(*self, *other)
		elif isinstance(other, Disjunction):
			return Conjunction(*self, other)
		elif isinstance(other, Symb):
			return Conjunction(*self, Disjunction(other))

	def __bool__(self):
		return all(bool(clause) for clause in self)


class Disjunction(Clause):
	def __add__(self, other):
		if isinstance(other, Disjunction):
			return Disjunction(*self, *other)
		elif isinstance(other, Conjunction):
			return Disjunction(*self, other)
		elif isinstance(other, Symb):
			return Disjunction(*self, other)

	def __bool__(self):
		return any(bool(clause) for clause in self)


class CNF:
	def __init__(self, sentence):
		if isinstance(sentence, Expr):
			# Eliminate EQUIVALENCE and IMPLICATIONS
			sentence = self.elim(sentence)
			# Push NEGATIONS inward, OR down and AND up
			sentence = self.flatten(sentence)
			# Convert to Clauses of Disjunctions and Conjunctions
			self.set = self.convert(sentence)
			if isinstance(self.set, Disjunction):
				self.set = Conjunction(self.set)
		elif isinstance(sentence, Conjunction):
			self.set = sentence
		elif isinstance(sentence, Disjunction):
			self.set = Conjunction(sentence)
		elif isinstance(sentence, Symb):
			self.set = Conjunction(Disjunction(sentence))
		else:
			raise Exception(f'__init__ failed {type(sentence)} {sentence}')
		

	def __str__(self):
		return '{' + ', '.join(str(clause) for clause in self) + '}'

	def __iter__(self):
		for clause in self.set:
			yield clause

	def __iadd__(self, other):
		if isinstance(other, Conjunction):
			return CNF(self.set + Conjunction(*(literal if isinstance(literal, Disjunction) else Disjunction(literal) for literal in other)))
		elif isinstance(other, Disjunction):
			return CNF(self.set + other)
		elif isinstance(other, CNF):
			return CNF(self.set + other.set)

	def elim(self, sentence):
		if isinstance(sentence, Expr):
			sentence = sentence.elim_equiv()
			sentence = sentence.elim_imp()
			sentence.first = self.elim(sentence.first)
			sentence.second = self.elim(sentence.second)
			sentence = sentence.elim_neg()
		return sentence

	def flatten(self, sentence):
		if isinstance(sentence, Expr):
			sentence = sentence.elim_neg()
			sentence.first = self.flatten(sentence.first)
			sentence.second = self.flatten(sentence.second)
			sentence = sentence.distribute()
		return sentence

	def convert(self, sentence):
		if type(sentence) == Symb:
			return Disjunction(sentence)
		first = self.convert(sentence.first)
		second = self.convert(sentence.second)
		if sentence.operator == 'or':
			if isinstance(first, Disjunction):
				if isinstance(second, Disjunction):
					# (a + b + c) + (d + e + f) = (a + b + c + d + e + f)
					return Disjunction(*first, *second)
				else:
					# (a + b + c) + (d * e * f) = (a + b + c + d) * (a + b + c + e) * (a + b + c + f)
					return Conjunction(*(Disjunction(*first, *literal) for literal in second))
			else:
				if isinstance(second, Disjunction):
					# (a * b * c) + (d + e + f) = (a + d + e + f) * (b + d + e + f) * (c + d + e + f)
					return Conjunction(*(Disjunction(*second, *literal) for literal in first))
				else:
					# (a * b * c) + (d * e * f) = (a + d) * (a + e) * (a + f) * (b + d) * (b + e) * (b + f)
					return Conjunction(*(Disjunction(x, y) for x in first for y in second))
		else:
			if isinstance(first, Disjunction):
				if isinstance(second, Disjunction):
					# (a + b + c) * (d + e + f) = (a + b + c) * (d + e + f)
					return Conjunction(first, second)
				else:
					# (a + b + c) * (d * e * f) = (a + b + c) * d * e * f
					return Conjunction(first, *second)
			else:
				if isinstance(second, Disjunction):
					# (a * b * c) * (d + e + f) = a * b * c * (d + e + f)
					return Conjunction(*first, second)
				else:
					# (a * b * c) * (d * e * f) = a * b * c * d * e * f
					return Conjunction(*first, *second)
				


def symbols(*args):
	return (Symb(symbol.strip()) for arg in args for symbol in arg.split(','))


if __name__ == '__main__':
	A, B, C = symbols('A, B, C')
	con = Conjunction(A, B, C)
	print(con - con)
