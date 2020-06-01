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



facts = [
	Atomic(name=f'L_0_11'),
	Atomic(name=f'¬P_11'),
	Atomic(name=f'¬W_11'),
	Atomic(name=f'WA_0'),
	Atomic(name=f'HA_0'),
	Atomic(name=f'FacingEast_0'),
]


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


def conjunc(*args):
	sentence = TRUE
	for literal in args:
		sentence = sentence * literal
	return sentence


def disjunc(*args):
	sentence = FALSE
	for literal in args:
		sentence = sentence + literal
	return sentence


# Creating perception Rules
for i in range(1, 5):
	for j in range(1, 5):
		facts.append(Atomic(name=f'B_{i}{j}') == disjunc(*(Atomic(name='P_' + square) for square in adjacent(i, j))))
		facts.append(Atomic(name=f'S_{i}{j}') == disjunc(*(Atomic(name='W_' + square) for square in adjacent(i, j))))
		facts.append(Atomic(name=f'W_{i}{j}') == -disjunc(*(Atomic(name='W_' + square) for square in adjacent(i, j))))



KB = CNF(conjunc(*facts))


class LogicAgent:
	def __init__(self, KB, function, mode='resolution', **kwargs):
		self.KB = KB
		self.mode = mode
		self.function = function
		for k, v in kwargs.items():
			setattr(self, k, v)

	def __call__(self, percepts):
		return self.function(percepts)

	def tell(self, sentence):
		if isinstance(sentence, Disjunction):
			self.KB.clauses.append(sentence)
		elif isinstance(sentence, Sentence):
			self.tell(CNF(sentence))
		elif isinstance(sentence, list):
			for clause in sentence:
				self.tell(clause)
		elif isinstance(sentence, Conjunction):
			self.KB.clauses.extend(sentence.literals)
		elif isinstance(sentence, CNF):
			self.KB.clauses.extend(sentence.clauses)
		else:
			raise Exception(f'Sentence {sentence} of type {type(sentence)} could not be told')

	def ask(self, query):
		if isinstance(query, str):
			query = Atomic(name=query)
		if self.mode == 'resolution':
			return self.pl_resolution(query)
		elif self.mode == 'forwardchaining':
			return self.forwardchaining(query)

	def pl_resolution(self, query):
		clauses = Conjunction(*self.KB, Disjunction(-query))
		new = []
		while True:
			for i, ci in enumerate(clauses):
				for j, cj in enumerate(clauses):
					if i != j:
						resolvent = self.pl_resolve(ci, cj)
						#print(resolvent)
						if not len(resolvent):
							return True
						new.append(resolvent)
			if set(new) - set(clauses):
				return False
			clauses.append(new)

	def pl_resolve(self, ci, cj):
		flag = False
		clause = []
		for li in ci:
			for lj in cj:
				if li.equals(-lj) and not flag:
					flag = True
				else:
					clause.extend([li, lj])
		return Disjunction(*clause)

	def route(self, current, goals, nodes):
		pass


"""
TO DO:

physics -> succesor state axioms:
	OK_t_ij = ¬P_ij * ¬(W_ij * WA_t)

make percept sequence
make action sentence
plan shot
route

"""

def make_percept_sentence(percepts, t):
	return [f"{'¬' if value else ''}{key}_{t}" for key, value in percepts.items()]


def physics(t):
	sentences = []
	for i in range(1, 5):
		for j in range(1, 5):
			# Position depending Successor State Axioms
			sentences.append(Atomic(name=f'OK_{t}_{i}{j}') == Atomic(name=f'¬P_{i}{j}') * -(Atomic(name=f'W_{i}{j}') * Atomic(name=f'WA_{t}')))
			sentences.append(Atomic(name=f'Breeze_{t}') * Atomic(name=f'L_{t}_{i}{j}') == (disjunc(*(Atomic(name=f'P_{x}') for x in adjacent(i, j)))))
			sentences.append(Atomic(name=f'Stench_{t}') * Atomic(name=f'L_{t}_{i}{j}') == (disjunc(*(Atomic(name=f'W_{x}') for x in adjacent(i, j)))))
		
			# Movement
			sentences.append(Atomic(name=f'L_{t}_{i, j}') == Atomic(name=f'L_{t-1}_{i}{j}') * (- Atomic(name=f'Forward_{t-1}') + Atomic(name=f'Bump_{t}')) + Atomic(name=f'Forward_{t-1}') * (Atomic(name=f'L_{t-1}_{i+1}{j}') * Atomic(name=f'South_{t-1}') + Atomic(name=f'L_{t-1}_{i-1}{j}') * Atomic(name=f'North_{t-1}') + Atomic(name=f'L_{t-1}_{i}{j+1}') * Atomic(name=f'West_{t-1}') + Atomic(name=f'L_{t-1}_{i}{j-1}') * Atomic(name=f'East_{t-1}')))

	# General Successor State Axioms
	if t:
		# Wumpus Alive
		sentences.append(Atomic(name=f'Scream_{t}') >> Atomic(name=f'¬WA_{t}'))

		# Direction
		sentences.append(Atomic(name=f'FacingEast_{t}') == Atomic(name=f'FacingNorth_{t-1}') * Atomic(name=f'TurnRight_{t-1}') + Atomic(name=f'FacingSouth_{t-1}') * Atomic(name=f'TurnLeft_{t-1}') + (Atomic(name=f'FacingEast_{t-1}') * -(Atomic(name=f'TurnLeft_{t-1}') + Atomic(name=f'TurnRight_{t-1}'))))
		sentences.append(Atomic(name=f'FacingSouth_{t}') == Atomic(name=f'FacingEast_{t-1}') * Atomic(name=f'TurnRight_{t-1}') + Atomic(name=f'FacingWest_{t-1}') * Atomic(name=f'TurnLeft_{t-1}') + (Atomic(name=f'FacingSouth_{t-1}') * -(Atomic(name=f'TurnLeft_{t-1}') + Atomic(name=f'TurnRight_{t-1}'))))
		sentences.append(Atomic(name=f'FacingWest_{t}') == Atomic(name=f'FacingSouth_{t-1}') * Atomic(name=f'TurnRight_{t-1}') + Atomic(name=f'FacingNorth_{t-1}') * Atomic(name=f'TurnLeft_{t-1}') + (Atomic(name=f'FacingWest_{t-1}') * -(Atomic(name=f'TurnLeft_{t-1}') + Atomic(name=f'TurnRight_{t-1}'))))
		sentences.append(Atomic(name=f'FacingNorth_{t}') == Atomic(name=f'FacingWest_{t-1}') * Atomic(name=f'TurnRight_{t-1}') + Atomic(name=f'FacingEast_{t-1}') * Atomic(name=f'TurnLeft_{t-1}') + (Atomic(name=f'FacingNorth_{t-1}') * -(Atomic(name=f'TurnLeft_{t-1}') + Atomic(name=f'TurnRight_{t-1}'))))



	print(*sentences, sep='\n')
	return sentences

physics(1)


def wumpus_agent(self, percepts):
	self.tell(make_percept_sentence(percepts, t))
	self.tell(physics(t))
	safe, current = [], None
	for i in range(1, 5):
		for j in range(1, 5):
			if self.ask(f'L_{self.t}_{i}{j}'):
				current = (i, j)
			if self.ask(f'OK{i}{j})'):
				safe.append((i, j))
	if current is None:
		raise Exception('No current position could be found.')
	if self.ask(f'Glitter_{self.t}'):
		plan = ['Grab'] + self.route(current, (1, 1), safe) + ['Climb']
	if plan is None:
		unvisited = [(i, j) for i in range(1, 5) for j in range(1, 5) 
		for t in range(self.t+1) if self.ask(f'¬L_{t}_{i}{j}')]
		plan = self.route(current, [node for node in unvisited if node in safe], safe)
	if plan is None:
		possible_wumpus = [(i, j) for i in range(1, 5) for j in range(1, 5) if not self.ask(f'¬W_{i}{j}')]
		plan = plan_shot(cuurent, possible_wumpus, safe)
	if plan is None:
		not_unsafe = [(i, j) for i in range(1, 5) for j in range(1, 5) if not self.ask(f'¬OK_{self.t}_{i}{j}')]
		plan = self.route(current, [node for node in unvisited if node in not_unsafe], safe)
	if plan is None:
		plan = self.route(current, (1, 1), safe) + ['Climb']
	action = plan.pop(0)
	self.tell(make_action_sentence(action, t))
	self.t += 1
	return action


slayer = LogicAgent(KB, wumpus_agent)
print(slayer.ask('W_11'))
