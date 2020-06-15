from logic import *
from itertools import count


class LogicAgent:
	def __init__(self, KB, function, mode='resolution', **kwargs):
		self.KB = KB
		self.mode = mode
		self.function = function
		for k, v in kwargs.items():
			setattr(self, k, v)

	def __call__(self, percepts):
		return self.function(percepts)

	def hornify(self):
		definite = lambda clause: sum(literal.value for literal in clause) == 1
		self.KB = [clause for clause in self.KB if definite(clause)]


	def tell(self, sentence):
		if isinstance(sentence, Disjunction) or isinstance(sentence, Conjunction) or isinstance(sentence, CNF):
			self.KB += sentence
		elif isinstance(sentence, Expr) or isinstance(sentence, Symb):
			self.KB += CNF(sentence)
		elif isinstance(sentence, list):
			for clause in sentence:
				self.tell(clause)
		elif isinstance(sentence, str):
			self.tell(Symb(sentence))
		else:
			raise Exception(f'Sentence {sentence} of type {type(sentence)} could not be told')
		if self.mode == 'forwardchaining':
			self.hornify()

	def ask(self, query, status=False):
		if isinstance(query, str):
			query = Symb(query)
		if self.mode == 'resolution':
			return self.smh_resolution(query, status)
		elif self.mode == 'forwardchaining':
			return self.forward_chaining(query)


	def resolution(self, query, status=True):
		clauses = Conjunction(*self.KB, *CNF(~query).set)
		new = Conjunction()
		if status:
			print(f'Resolution query: {str(query)}')
		for c in count():
			for ci in clauses:
				for cj in clauses:
					if (resolvent := self.resolve(ci, cj)) is None:
						continue
					elif not len(resolvent):
						return True
					new += resolvent
			if new < clauses:
				return False
			clauses += new


	def smh_resolution(self, query, status=True):
		"""
SUPER MEGA HYPER RESOLUTION - comes with extensions for better performance like:
1. Ignoring clauses, that cannot lead to an empty clause (under assumption that KB is satisfiable)
2. Disregarding clauses, that subsume others.
3. Alot more containers to loose track of the functionality
Resulting in a slightly better performance and headache while debugging"""
		clauses = Conjunction(*self.KB)
		if type(query) == Symb:
			new = Conjunction(Disjunction(~query))
		elif type(query) == Expr:
			new = CNF(~query).set
		relevant = Conjunction()
		if status:
			print(f'Resolution query: {str(query)}')
		for c in count():
			if status:
				print(f"""
Resolution round {c}
Length of clauses {len(clauses)}
Length of new {len(new)}
Length of relevant {len(relevant)}
""")
			resolvents = Conjunction()
			for ci in new:
				for cj in clauses:
					if (resolvent := self.resolve(ci, cj)) is None:
						continue
					elif not len(resolvent):
						return True
					resolvents += resolvent
			if resolvents < clauses + relevant:
				return False
			new = resolvents - relevant
			new = Conjunction(*(ci for ci in new if not any(cj < ci for cj in new)))
			relevant += resolvents

	def resolve(self, ci, cj):
		if ci == cj:
			return
		flag = False
		clause = Disjunction()
		for li in ci:
			if ~li in cj:
				if not flag:
					flag = True
				else:
					return
			else:
				clause += li
		for lj in cj:
			if ~lj not in ci and lj not in clause:
				clause += lj
		if flag:
			return clause

	def forward_chaining(self, query):
		def premise(clause):
			return [literal for literal in clause if not literal.value]

		def conclusion(clause):
			for literal in clause:
				if literal.value:
					return literal

		count = {clause: sum(not symbol.value for symbol in clause) for clause in self.KB}
		inferred = {symbol: False for clause in self.KB for symbol in clause}
		agenda = [symbol for clause, counter in count.items() if counter == 0 for symbol in clause]
		print(self.KB)
		while agenda:
			p = agenda.pop(0)
			print(p)
			if p.equals(query):
				return True
			if not inferred[p]:
				inferred[p] = True
				for c in self.KB:
					if p in premise(c):
						count[c] -= 1
					if count[c] == 0:
						agenda.append(conclusion(c))
		print(self.KB)
		return False