class Sentence:
	def __mul__(self, other):
		return Complex(self, other, 'and')

	def __add__(self, other):
		return Complex(self, other, 'or')

	def __eq__(self, other):
		return Complex(self, other, 'equiv')

	def __rshift__(self, other):
		return Complex(self, other, 'implicate')



class Atomic(Sentence):
	def __init__(self, value=None, neg=False, name=None):
		self.value = value
		if name is not None:
			self.name = ('¬' if self.neg else '') + name
		self.neg = True if name is not None and (name.startswith('¬') or name.startswith('-')) else neg

	def reduce(self):
		return self

	def __call__(self, *args):
		if args:
			self.value = args[0]
		elif self.value is not None:
			return not self.value if self.neg else self.value

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.name + (f"<{self.value}>" if self.value is not None else '')

	def __getattr__(self, attr):
		""" Some trickery to let the class know the name of its
		instance without passing it as an argument. Does only work
		in global namespace."""
		if attr == 'name':
			for k, v in globals().items():
				if v is self:
					self.name = ('¬' if self.neg else '') + k
					return self.name
			self.name = ('¬' if self.neg else '') + 'VAR'
			return self.name

	def __neg__(self):
		if self.name == 'True':
			return FALSE
		elif self.name == 'False':
			return TRUE
		return Atomic(self.value, not self.neg, self.name[1:] if self.neg else '¬' + self.name)

	def equals(self, other):
		return self.name == other.name and self.neg == other.neg and self.name != 'VAR'



TRUE = Atomic(value=True, neg=False, name='True')
FALSE = Atomic(value=False, neg=False, name='False')



class Complex(Sentence):
	def __init__(self, first, second, conjunction, neg=False):
		self.first = first
		self.second = second
		self.negation = False
		self.con_name = conjunction
		self.neg = neg
		if conjunction == 'and':
			self.conjunction = lambda: self.first() and self.second()
			self.con_symbol = '∧'
		elif conjunction == 'or':
			self.conjunction = lambda: self.first() or self.second()
			self.con_symbol = '∨'
		elif conjunction == 'equiv':
			self.conjunction = lambda: self.first() == self.second()
			self.con_symbol = '⇔'
		elif conjunction == 'implicate':
			self.conjunction = lambda: not self.first() or self.second()
			self.con_symbol = '⇒'
		self.name = str(self)
		

	def __str__(self):
		return ('¬' if self.neg else '') + f"({str(self.first)} {self.con_symbol} {str(self.second)})"

	def __repr__(self):
		return ('¬' if self.neg else '') + f"({self.first} {self.con_symbol} {self.second})" + (f'<{self()}>' if self() is not None else '')

	def __call__(self):
		if self.first() is not None and self.second() is not None:
			con = self.conjunction()
			return not con if self.neg else con

	def __neg__(self):
		return Complex(self.first, self.second, self.con_name, not self.neg)

	def equals(self, other):
		return self.con_name == other.con_name and ((self.first.equals(other.first) and self.second.equals(other.second)) or  
			(self.first.equals(other.second) and self.second.equals(other.first))) and self.con_name != 'VAR' and self.neg == other.neg

	def double_elimination(self):
		
		# Elementary Values
		if self.first.name == 'True':
			if self.con_name == 'or':
				return self.first
			else:
				return self.second
		if self.second.name == 'True':
			if self.con_name in {'or', 'implication'}:
				return self.second
			else:
				return self.first
		if self.first.name == 'False':
			if self.con_name == 'and':
				return self.first
			elif self.con_name == 'implicate':
				return TRUE
			elif self.con_name == 'or':
				return self.second
			elif self.con_name == 'equiv':
				return -self.second
		if self.second.name == 'False':
			if self.con_name == 'or':
				return self.first
			elif self.con_name == 'and':
				return FALSE
			else:
				return -self.first

		# Doubles
		if self.first.equals(self.second):
			if self.con_name in {'and', 'or'}:
				return self.first
			elif self.con_name == 'implicate':
				return TRUE
			elif self.con_name == 'equiv':
				return TRUE
		elif self.first.equals(-self.second):
			if self.con_name == 'and':
				return FALSE
			elif self.con_name == 'or':
				return TRUE
			elif self.con_name == 'implicate':
				if self.first():
					return FALSE
				else:
					TRUE
			elif self.con_name == 'equiv':
				return FALSE
		raise Exception('Non double elimination possible')

	def equivalence_elimination(self):
		if self.con_name == 'equiv':
			return (self.first >> self.second) * (self.second >> self.first)
		else:
			raise Exception('Equivalence elimination is only legal for EQUIVALENCES')

	def implication_elimination(self):
		if self.con_name == 'implicate':
			return -self.first + self.second
		else:
			raise Exception('Implication elimination is only legal for IMPLICATIONS')

	def contraposition(self):
		if self.con_name == 'implicate':
			return -self.second >> -self.first
		else:
			raise Exception('Contraposition is only legal for IMPLICATIONS')

	def de_morgan(self):
		if self.con_name == 'or':
			return -(-self.first * -self.second)
		elif self.con_name == 'and':
			return -(-self.first + -self.second)
		else:
			raise Exception('De Morgan is only allowed for AND and OR conjunctions.')

	def distribute_or_down(self):
		if self.con_name != 'or':
			raise Exception('Must distribute over OR')
		if 'and' == self.second.con_name:
			return self.first * self.second.first + self.first * self.second.second
		elif 'and' == self.first.con_name:
			return self.second * self.first.first + self.second * self.first.second
		else:
			raise Exception('No distribution possible')

	def distribute_or_up(self):
		if self.con_name != 'or':
			raise Exception('Must distribute over OR')
		if self.first.con_name == 'and' == self.second.con_name:
			if self.first.first is self.second.first:
				return self.first.first * (self.first.second + self.second.second)
			elif self.first.first is self.second.second:
				return self.first.first * (self.first.second + self.second.first)
			elif self.first.second is self.second.first:
				return self.first.second * (self.first.first + self.second.second)
			elif self.first.second is self.second.second:
				return self.first.second * (self.first.first + self.second.first)
		else:
			raise Exception('No distribution possible')

	def distribute_and_down(self):
		if self.con_name != 'and':
			raise Exception('Must distribute over AND')
		if 'or' == self.second.con_name:
			return (self.first + self.second.first) * (self.first + self.second.second)
		elif 'or' == self.first.con_name:
			return (self.second + self.first.first) * (self.second + self.first.second)
		else:
			raise Exception('Non distribution possible')

	def distribute_and_up(self):
		if self.con_name != 'and':
			raise Exception('Must distribute over AND')
		if self.first.con_name == 'or' == self.second.con_name:
			if self.first.first is self.second.first:
				return self.first.first + (self.first.second * self.second.second)
			elif self.first.first is self.second.second:
				return self.first.first + (self.first.second * self.second.first)
			elif self.first.second is self.second.first:
				return self.first.second + (self.first.first * self.second.second)
			elif self.first.second is self.second.second:
				return self.first.second + (self.first.first * self.second.first)
		else:
			raise Exception('No distribution possible')



class Disjunction:
	def __init__(self, *literals):
		self.literals = []
		for literal in literals:
			if isinstance(literal, Disjunction):
				self.literals.extend(literal)
			else:
				self.literals.append(literal)
		try:
			self.literals = sorted(self.literals, key=lambda literal: literal.name.replace('¬', ''))
		except:
			pass

	def __in__(self, other):
		return other in self.literals

	def add(self, *others):
		for literal in others:
			if not any(x == literal for x in self):
				self.literals.append(literal)

	def __eq__(self, other):
		return self > other and other > self

	def __gt__(self, other): # superset >
		return all(any((ci.equals(cj) if isinstance(ci, Sentence) else ci == cj) for cj in self) for ci in other)

	def __lt__(self, other): # subset <
		return other > self

	def __getitem__(self, key):
		return self.literals[key]

	def __iter__(self):
		for literal in self.literals:
			yield literal

	def __call__(self):
		return any(literal() for literal in self)

	def __str__(self):
		return f"[{', '.join(str(literal) for literal in self)}]"

	def __getattr__(self, attr):
		if attr == 'name':
			return str(self)

	def __len__(self):
		return len(self.literals)

	def reduce(self):
		literals = []
		for x in self.literals:
			if not any(x.name == y.name for y in literals):
				literals.append(x)
		for x in literals:
			if isinstance(x, Atomic):
				for y in literals:
					if  isinstance(y, Atomic):
						if x.name == (-y).name or (-x).name == y.name:
							literals.remove(x)
							literals.remove(y)
			else:
				if not len(x):
					literals.remove(x)
		self.literals = literals



class Conjunction:
	def __init__(self, *literals):
		self.literals = []
		for literal in literals:
			if isinstance(literal, Conjunction):
				self.literals.extend(literal)
			else:
				self.literals.append(literal)
		try:
			self.literals = sorted(self.literals, key=lambda literal: literal.name.replace('¬', ''))
		except:
			pass

	def __iter__(self):
		for literal in self.literals:
			yield literal

	def __in__(self, other):
		return other in self.literals

	def add(self, *others):
		for literal in others:
			if not any(x == literal for x in self):
				self.literals.append(literal)

	def __eq__(self, other):
		return self > other and other > self

	def __gt__(self, other): # superset >
		return all(any((ci.equals(cj) if isinstance(ci, Sentence) else ci == cj) for cj in self) for ci in other)

	def __lt__(self, other): # subset <
		return other > self

	def __getitem__(self, key):
		return self.literals[key]

	def __call__(self):
		return all(literal() for literal in self)

	def __str__(self):
		return "{" + ', '.join(str(literal) for literal in self) + "}"

	def __getattr__(self, attr):
		if attr == 'name':
			return str(self)

	def __len__(self):
		return len(self.literals)

	def reduce(self):
		literals = []
		for x in self.literals:
			if not any(x.name == y.name for y in literals):
				literals.append(x)
		for x in literals:
			if isinstance(x, Atomic):
				for y in literals:
					if  isinstance(y, Atomic):
						if x.name == (-y).name or (-x).name == y.name:
							literals.remove(x)
							literals.remove(y)
			else:
				if not len(x):
					literals.remove(x)
					literals.append(Disjunction(FALSE))
		self.literals = literals



class CNF:
	def __init__(self, sentence):
		if isinstance(sentence, Sentence):
			equiv = self.simplify(sentence)
			self.clauses = self.convert(equiv)
			for clause in self.clauses:
				clause.reduce()
			self.clauses.reduce()
			if isinstance(self.clauses, Disjunction):
				self.clauses = Conjunction(self.clauses)
		elif isinstance(sentence, Conjunction):
			self.clauses = sentence
		elif isinstance(sentence, Disjunction):
			self.clauses = Conjunction(sentence)

	def __iter__(self):
		for clause in self.clauses:
			yield clause

	def __repr__(self):
		return str(self.clauses)

	def simplify(self, sentence):
		try:
			sentence = sentence.double_elimination()
		except:
			pass
		try:
			sentence = sentence.equivalence_elimination()
		except:
			pass
		try:
			sentence = sentence.implication_elimination()
		except:
			pass
		if isinstance(sentence, Atomic):
			return sentence
		sentence.first = self.simplify(sentence.first)
		sentence.second = self.simplify(sentence.second)
		if isinstance(sentence.first, Atomic) and sentence.first.name in ('True', 'False') or isinstance(sentence.second, Atomic) and sentence.second.name in ('True', 'False'):
			return self.simplify(sentence)
		return sentence

	def convert(self, sentence):
		if isinstance(sentence, Atomic):
			return Disjunction(sentence)
		if sentence.neg:
			sentence = sentence.de_morgan()
		first = self.convert(sentence.first)
		second = self.convert(sentence.second)
		if sentence.con_name == 'or':
			if isinstance(first, Disjunction):
				if isinstance(second, Disjunction):
					# (a + b + c) + (d + e + f) = (a + b + c + d + e + f)
					return Disjunction(*first, *second)
				else:
					# (a + b + c) + (d * e * f) = (a + b + c + d) * (a + b + c + e) * (a + b + c + f)
					return Conjunction(*(Disjunction(*first, literal) for literal in second))
			else:
				if isinstance(second, Disjunction):
					# (a * b * c) + (d + e + f) = (a + d + e + f) * (b + d + e + f) * (c + d + e + f)
					return Conjunction(*(Disjunction(*second, literal) for literal in first))
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



