from logic import *
from logicagent import *
from KB import *
from graph import *
from search import *
from os import system


class HybridWumpusAgent:
	def __init__(self, mode='resolution', t=0):
		self.t = t
		self.agent = LogicAgent(KB, function=self, mode=mode)
		self.visited = set()

	def __call__(self, percepts):
		current = percepts['x'], percepts['y']
		self.visited.add(current)
		#print(f'Found position {current}')
		self.agent.tell(self.make_percept_sentence(percepts))
		#print('Made percept sentences')
		self.agent.tell(self.physics(current))
		#print('Made physics sentences')
		safe, plan = list(self.visited), None
		orientation = str(percepts['direction']).replace('Direction.', '').title()
		gold = percepts['gold']
		#print(f'Found orientation {orientation}')
		for i, j in set([*(pos for i, j in  self.visited for pos in adjacent(i, j))]) - self.visited:
			if self.agent.ask(OK(self.t, i, j)):
				safe.append((i, j))
		print(f'Updated safe positions {safe}')
		if gold:
			plan = self.route(current, [(0, 0)], safe, orientation) + ['Climb']
		if plan is None and self.agent.ask(f'Glitter_{self.t}'):
			print('Found Gold')
			plan = ['Grab'] + self.route(current, [(0, 0)], safe, orientation) + ['Climb']
		if plan is None:
			print('Updating unvisited positions')
			unvisited = [(i, j) for i in range(4) for j in range(4) 
			if not any(self.agent.ask(f'L_{t}_{i}{j}') for t in range(self.t+1))]
			plan = self.route(current, [node for node in unvisited if node in safe], safe, orientation)
		if plan is None:
			print('Updating possible wumpus positions')
			possible_wumpus = [(i, j) for i in range(4) for j in range(4) if not self.agent.ask(f'¬W_{i}{j}')]
			#plan = plan_shot(cuurent, possible_wumpus, safe)
		if plan is None:
			print('Exploring new positions')
			not_unsafe = [(i, j) for i in range(4) for j in range(4) if not self.agent.ask(~OK(self.t, i, j))]
			plan = self.route(current, [node for node in unvisited if node in not_unsafe], safe, orientation)
		if plan is None:
			print('Leaving dungeon')
			plan = self.route(current, [(0, 0)], safe, orientation) + ['Climb']
		action = plan.pop(0)
		#self.agent.tell(make_action_sentence(action))
		self.t += 1
		return action

	def route(self, current, goals, nodes, orientation):
		def turn(current, target):
			directions = {'West': 0, 'North': 1, 'East': 2, 'South': 3}
			turning_number = (directions[current] - directions[target]) % len(directions)
			if turning_number < 3:
				return ['Left'] * turning_number
			else:
				return ['Right']

		def direction(current, target):
			ci, cj = current
			ti, tj = target
			if cj - tj == 1:
				return 'South'
			elif cj - tj == -1:
				return 'North'
			elif ci - ti == 1:
				return 'West'
			elif ci - ti == -1:
				return 'East'

		graph = Grid('\n'.join(''.join(' ' if (i, j) in nodes else '#' for j  in range(4)) for i in range(3, -1, -1)))
		path_finder = A_STAR(graph)
		for goal in goals:
			problem = Problem(graph[str(current)], graph[str(goal)])
			if (result := path_finder(problem, manhatten)):
				cost, path = result
				if len(path) == 1:
					return []
				path = [eval(node.name) for node in path]
				plan, current_direction = [], orientation
				for current, target in zip(path[:-1], path[1:]):
					target_direction = direction(current, target)
					plan.extend(turn(current_direction, target_direction) + ['Forward'])
					current_direction = target_direction
				return plan

	def make_percept_sentence(self, percepts):
		return [f"{'' if value else '¬'}{key.title()}_{self.t}" for key, value in percepts.items()
		 if key.title() in {'Stench', 'Breeze', 'Glitter', 'Bump', 'Scream'}] + [f"L_{self.t}_{percepts['x']}{percepts['y']}", 
		 f"{'' if percepts['arrow'] else '¬'}HA_{self.t}", f"Facing{str(percepts['direction']).replace('Direction.', '').title()}_{self.t}"]
	
	def physics(self, current):
		sentences = []
		x, y = current
		sentences.append(Symb(f'Breeze_{self.t}') == Symb(f'B_{x}{y}'))
		sentences.append(Symb(f'Stench_{self.t}') == Symb(f'S_{x}{y}'))
		sentences.append(Symb(f'B_{x}{y}') == disjunc(*(Symb(f'P_{i}{j}') for i, j in adjacent(x, y))))
		sentences.append(Symb(f'S_{x}{y}') == disjunc(*(Symb(f'W_{i}{j}') for i, j in adjacent(x, y))))
		#sentences.append(Symb(f'W_{x}{y}') == conjunc(*(Symb(f'¬W_{i}{j}') for i, j in other(x, y))))
		
		# General Successor State Axioms
		if self.t > 0:
			sentences.append(Symb(f'WA_{self.t}') == Symb(f'WA_{self.t-1}') & ~Symb(f'Scream_{self.t}'))
		return sentences
	

	def make_action_sentence(self, action):
		return Symb(f'{action}_{self.t}')


class SupportWumpusAgent:
	def __init__(self, mode='resolution', t=0):
		self.t = t
		self.agent = LogicAgent(KB, function=self, mode=mode)

	def __call__(self, percepts):
		clear = lambda: system('clear') # cls for Windows
		clear()

		current = percepts['x'], percepts['y']
		x, y = current
		current = percepts['x'], percepts['y']
		self.agent.tell(self.make_percept_sentence(percepts))
		self.agent.tell(self.physics(current))
		directions = {'West': '←', 'North': '↑', 'East': '→', 'South': '↓'}
		orientation = str(percepts['direction']).replace('Direction.', '').title()
		gold = percepts['gold']

		commands = {'F': 'Forward', 'L': 'Left', 'R': 'Right', 'G': 'Grab', 'S': 'Shoot', 'C': 'Climb'}
		while (command := input("""
Breeze: {}
Stench: {}
Bump:   {}
Scream: {}
Glitter:{}
+--+--+--+--+
{}+--+--+--+--+
Gold: {}

(F) Forward
(L) Left Turn
(R) Right Turn
(G) Grab
(S) Shoot
(C) Climb
(A) Ask the KB

»»»""".format(
	percepts['breeze'],
 	percepts['stench'], 
 	percepts['bump'], 
 	percepts['scream'], 
 	percepts['glitter'], 
 	'+--+--+--+--+\n'.join('|' + '|'.join(('L' + directions[orientation] if j == x and 3-i == y else '  ') 
	for j in range(4))  + '|\n' for i in range(4)), gold)).upper()) not in commands:
			clear()
			if command == 'A':
				query = input("""
Negation        ~
Conjunction     &
Disjunction     |
Equivalence     ==
Implication     >>
Brackets        ()

Enter your query
»»»""")
				try:
					sentence = self.querify(query)
				except:
					continue
				input(f"""Answer to {sentence}: {self.agent.ask(sentence)}
PRESS ENTER TO CONTINUE""")
		self.t += 1
		return commands[command]
		
	def querify(self, query):
		variables = set(var.strip() for var in query.replace('~', '').replace('&', ':').replace('|', ':').replace('==', ':').replace('>>', ':').replace('(', '').replace(')', '').split(':'))
		for var in variables:
			query = query.replace(var, f"Symb('{var}')")
		return eval(query)

	def make_percept_sentence(self, percepts):
		return [f"{'' if value else '¬'}{key.title()}_{self.t}" for key, value in percepts.items()
		 if key.title() in {'Stench', 'Breeze', 'Glitter', 'Bump', 'Scream'}] + [f"L_{self.t}_{percepts['x']}{percepts['y']}", 
		 f"{'' if percepts['arrow'] else '¬'}HA_{self.t}", f"Facing{str(percepts['direction']).replace('Direction.', '').title()}_{self.t}"]
	
	def physics(self, current):
		sentences = []
		x, y = current
		sentences.append(Symb(f'Breeze_{self.t}') == Symb(f'B_{x}{y}'))
		sentences.append(Symb(f'Stench_{self.t}') == Symb(f'S_{x}{y}'))
		sentences.append(Symb(f'B_{x}{y}') == disjunc(*(Symb(f'P_{i}{j}') for i, j in adjacent(x, y))))
		sentences.append(Symb(f'S_{x}{y}') == disjunc(*(Symb(f'W_{i}{j}') for i, j in adjacent(x, y))))
		sentences.append(Symb(f'W_{x}{y}') == conjunc(*(Symb(f'¬W_{i}{j}') for i, j in other(x, y))))
		# General Successor State Axioms
		if self.t > 0:
			sentences.append(Symb(f'WA_{self.t}') == Symb(f'WA_{self.t-1}') & ~Symb(f'Scream_{self.t}'))
		return sentences


if __name__ == '__main__':
	slayer = SupportWumpusAgent()
	print(slayer.querify('P_11 | P_01 | ~P_10 == (B_0 | S_00) & (B_0 >> B_0)'))
