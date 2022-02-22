import sys
from typing import Set

# POSTOLACHE ALEXANDRU-GABRIEL 331CB

class Nfa:
	_nr_states: int
	_alphabet: Set[str]
	_initial_state: int
	_final_state: int
	_delta: list()
	_max_state: int
	def __init__(self):
		self._nr_states = 0
		self._initial_state = 0
		self._final_state = 0
		self._delta = []
		self._alphabet = set()

	def print_Nfa(self):
		print("\n===================NFA====================")
		nfa = self
		print("Stare initiala "+ str(nfa._initial_state)) 
		print("Stare finala " + str(nfa._final_state))
		print("Nr stari: " + str(nfa._nr_states))
		print("Alfabet: ")
		print(nfa._alphabet)
		print("Tranzitii ")
		print(nfa._delta)

	#daca exista un drum de tranzitii epsilon de la starile din found_state la final state
	def connection_to_final(self, found_state):
		found_state = list(found_state)
		ok = False
		i = 0
		while i != len(found_state):
			state = found_state[i]
			for fct in self._delta:
				if fct[0] == state and fct[1] == "Epsilon":
					if not(fct[2] in found_state):
						found_state.append(fct[2])
							
			i += 1
		if self._final_state in found_state:
			ok = True
		return ok

	#verifica daca 2 state-uri simplificate de dfa sunt aceleasi gasindu-le valorile vechi
	def same_state(self, state1, state2):
		i = 0
		state1 = list(state1)
		state2 = list(state2)
		while i != len(state1):
			state = state1[i]
			for fct in self._delta:
				if fct[0] == state and fct[1] == "Epsilon":
					if not(fct[2] in state1): 
						state1.append(fct[2])
	
							
			i += 1
		
		i = 0
		while i != len(state2):
			state = state2[i]
			for fct in self._delta:
				if fct[0] == state and fct[1] == "Epsilon":
					if not(fct[2] in state2): 
						state2.append(fct[2])
							
			i += 1
		if set(state1) == set(state2):
			return True

		return False


class Expr:
	pass

# expresie regulata care e doar un symbol
class Symbol(Expr):
	_char: str

	def __init__(self, c: str):
		self._char = c

	def __str__(self):
		return self._char

# expresie regulata care se ridica la *
class Star(Expr):
	_expr: Expr

	def __init__(self, expr: Expr):
		self._expr = expr

	def __str__(self):
		if isinstance(self._expr, Union):
			return str(self._expr) + "*"
		if isinstance(self._expr, Symbol):
			return str(self._expr) + "*"
		return "(" + str(self._expr) + ")" + "*"

# Expr(Expr)*
class Plus(Expr):
	_expr: Expr

	def __init__(self, expr: Expr):
		self._expr = expr

	def __str__(self):
		if isinstance(self._expr, Union):
			return str(self._expr) + str(self._expr) + "*"
		if isinstance(self._expr, Symbol):
			return str(self._expr) + str(self._expr) + "*"
		return str(self._expr) + "(" + str(self._expr) + ")" + "*"		

#expr reg formata din concatenarea a 2 alte expresii
class Concat(Expr):
	_expr1: Expr
	_expr2: Expr

	def __init__(self, expr1: Expr, expr2: Expr):
		self._expr1 = expr1
		self._expr2 = expr2

	def __str__(self):
		return str(self._expr1) + str(self._expr2)

#expr reg formata din uniunea a 2 alte expresii
class Union(Expr):
	_expr1: Expr
	_expr2: Expr

	def __init__(self, expr1: Expr, expr2: Expr):
		self._expr1 = expr1
		self._expr2 = expr2

	def __str__(self):
		return "(" + str(self._expr1) + "U" + str(self._expr2) + ")"


def check_stack(my_stack) -> Expr:
	#stiva axuxiliara pentru a retine operatorii care asteapta alti operatori
	aux = []

	while len(my_stack) != 0:
		el1 = my_stack.pop()

		#stop condition
		if len(my_stack) == 0:
			return el1

		#adaug un element de pe aux pe stiva princp pt STAR
		if el1 == "STAR":
			my_stack.append(el1)
			my_stack.append(aux.pop())
			continue

		#adaug un element de pe aux pe stiva princp pt Plus
		if el1 == "PLUS":
			my_stack.append(el1)
			my_stack.append(aux.pop())
			continue

		el2 = my_stack.pop()

		if el2 == "STAR" and isinstance(el1, Expr):
			my_stack.append(Star(el1))
			continue

		if el2 == "PLUS" and isinstance(el1, Expr):
			my_stack.append(Plus(el1))
			continue

		#adaug un element de pe aux pe stiva princp pt Union, concat 
		if el2 == "UNION" or el2 == "CONCAT":
			my_stack.append(el2)
			my_stack.append(el1)
			my_stack.append(aux.pop())
			continue

		el3 = my_stack.pop()
		if el3 == "UNION":
			my_stack.append(Union(el2, el1))
			continue
		if el3 == "CONCAT":
			my_stack.append(Concat(el2, el1))
			continue

		#nu s-a gasit nicio expresie deci ma deplasez pe stiva in jos
		my_stack.append(el3)
		my_stack.append(el2)

		#salvez elementele anterioare intr-o stiva
		aux.append(el1)


def create_expr(s: str) -> Expr:
	words = s.split(" ")
	my_stack = []

	for i in range(0, len(words)):
		if len(words[i]) == 1:
			my_stack.append(Symbol(words[i]))
		elif words[i] == "SPACE":
			my_stack.append(Symbol(" "))
		elif words[i] == "NEWLINE":
			my_stack.append(Symbol("\\n"))
		else:
			my_stack.append(words[i])

	return check_stack(my_stack)


#renumeroteaza starile si le adauga nfa-ului de returnat
def merge_nfas_concat(nfa1: Nfa, nfa2: Nfa, nfa: Nfa):
	nfa2._final_state += nfa1._nr_states
	nfa2._initial_state += nfa1._nr_states

	#modificare lista transformati	
	new_delta = []
	new_delta.append([nfa1._final_state, "Epsilon",nfa2._initial_state])

	for key in nfa2._delta:
		new_key = []
		#creare transf noua
		new_key = [key[0] + nfa1._nr_states, key[1], key[2] + nfa1._nr_states]
		# print(new_key)
		new_delta.append(new_key)# = nfa2._delta[key] + nfa1._nr_states

	nfa2._delta = new_delta

	nfa._alphabet.update(nfa1._alphabet)
	nfa._alphabet.update(nfa2._alphabet)
	nfa._nr_states += nfa1._nr_states + nfa2._nr_states
	nfa._initial_state = nfa1._initial_state
	nfa._final_state = nfa2._final_state
	nfa._delta = nfa1._delta
	nfa._delta.extend(nfa2._delta)

def merge_nfas_union(nfa1: Nfa, nfa2: Nfa, nfa: Nfa):
	nfa1._initial_state += 1
	nfa1._final_state += 1
	nfa2._final_state = nfa1._final_state + nfa2._nr_states
	nfa2._initial_state = nfa1._initial_state + nfa1._nr_states

	nfa._initial_state = nfa1._initial_state - 1
	nfa._final_state = nfa2._final_state + 1

	#modificare lista transformari	
	new_delta = []

	new_delta.append([nfa._initial_state, "Epsilon", nfa1._initial_state]) 
	new_delta.append([nfa._initial_state, "Epsilon", nfa2._initial_state])

	#starile din 1 + 1
	for key in nfa1._delta:
		new_key = []
		new_key = [key[0]+1, key[1], key[2] + 1]
		new_delta.append(new_key)


	#starile din 2 + nr elem nfa1 + 1
	for key in nfa2._delta:
		new_key = []
		new_key = [key[0]+nfa1._nr_states+1, key[1], key[2]+nfa1._nr_states+1]
		new_delta.append(new_key)

	new_delta.append([nfa1._final_state, "Epsilon", nfa._final_state])
	new_delta.append([nfa2._final_state, "Epsilon", nfa._final_state])

	nfa._alphabet.update(nfa1._alphabet)
	nfa._alphabet.update(nfa2._alphabet)
	nfa._nr_states = nfa1._nr_states + nfa2._nr_states + 2
	nfa._delta = new_delta

def merge_nfa_star(before: Nfa, after: Nfa):
	before._initial_state += 1
	before._final_state += 1

	after._initial_state = before._initial_state - 1
	after._final_state = before._final_state + 1

	new_delta = []
	new_delta.append([after._initial_state, "Epsilon", before._initial_state])
	new_delta.append([after._initial_state, "Epsilon", after._final_state])
	new_delta.append([before._final_state, "Epsilon", before._initial_state])
	new_delta.append([before._final_state, "Epsilon", after._final_state])

	for key in before._delta:
		new_key = [key[0] + 1, key[1], key[2] + 1]
		new_delta.append(new_key)

	after._delta = new_delta
	after._alphabet.update(before._alphabet)
	after._nr_states = before._nr_states + 2

	#am nevoie de valorile lor initiale pt PLUS
	before._initial_state -= 1
	before._final_state -= 1

#combina 2 nfa-uri diferite in unul singur
def combine_nfa(nfa1: Nfa, nfa2: Nfa, op: str):
	nfa = Nfa()
	if op == "CONCAT":
		merge_nfas_concat(nfa1, nfa2, nfa)
		
			
	if op == "UNION":
		merge_nfas_union(nfa1, nfa2, nfa)

	if op == "STAR":
		merge_nfa_star(nfa1, nfa)

	if op == "PLUS":
		aux = Nfa()
		merge_nfa_star(nfa1, aux)
		merge_nfas_concat(nfa1, aux, nfa)

	return nfa

#build the nfa by browsing the regex tree recursively
def build_nfa(regex: Expr):
	if isinstance(regex, Union):
		nfa1 = build_nfa(regex._expr1)
		nfa2 = build_nfa(regex._expr2)
		return combine_nfa(nfa1, nfa2, "UNION")
	
	if isinstance(regex, Concat):
		nfa1 = build_nfa(regex._expr1)
		nfa2 = build_nfa(regex._expr2)
		return combine_nfa(nfa1, nfa2, "CONCAT")
	
	if isinstance(regex, Star):
		nfa = build_nfa(regex._expr)
		return combine_nfa(nfa, nfa, "STAR")

	if isinstance(regex, Plus):
		nfa = build_nfa(regex._expr)
		return combine_nfa(nfa, nfa, "PLUS")
	
	if isinstance(regex, Symbol):
		nfa = Nfa()
		nfa._alphabet.add(regex._char)
		nfa._nr_states = 2
		nfa._initial_state = 0
		nfa._final_state = 1
		nfa._delta.append([0, regex._char,1])
		return nfa

def read_Prenex(in_file):
	f = open(in_file, "r")
	str = f.read()
	return str

def Regex_to_Nfa(regex: Expr):
	nfa = build_nfa(regex)
	return nfa 

#clasa pt o stare de dfa
class Afd_State:
	_index: int
	_delta: list()
	_old_name: set()
	_even_older_name: set()
	def __init__(self):
		self._index = 0
		self._delta = []
		_old_name = []
		_even_older_name = []

class Afd:
	_nr_states: int
	_alphabet: Set[str]
	_initial_state: Afd_State
	_final_states: list()
	_all_states: list()
	_delta: list()
	def __init__(self):
		self._nr_states = 0
		self._initial_state = Afd_State()
		self._initial_state._index = -1
		self._final_states = []
		self._delta = []
		self._alphabet = set()
		self._all_states = []

	def print_AFD(self):
		print("\n====================AFD=======================")
		afd = self
		print("Stare initiala: "+ str(afd._initial_state._index))
		print("Stari finale: ")
		for state in afd._final_states:
			print(state._index) 
		print("Alphabet:")
		print(afd._alphabet)
		print("Nr states: " + str(afd._nr_states))
		print("DELTA")
		print(afd._delta)


	def write_in_file(self, out_file):
		f = open(out_file, "w")
		line = ""
		for el in self._alphabet:
			line += el
		f.write(line+"\n")
		
		f.write(str(self._nr_states)+"\n")
		f.write(str(self._initial_state._index)+"\n")
		
		line = ""
		self._final_states = sorted(self._final_states, key = lambda x: x._index, reverse= True)
		for final in self._final_states:
			line += " " + str(final._index)
		f.write(line[1:] + "\n")

		for fct in self._delta:
			line = "" + str(fct[0]) + ",'"
			line += fct[1] + "',"
			#synk state
			if (fct[2] == -1):
				fct[2] = self._nr_states - 1
			line += str(fct[2]) + "\n"
			f.write(line)

	#checks if found_state is already an added state, meanining it's a cycle
	def cycle(self, found_state):
		for state in self._all_states:
			if set(found_state) == state._old_name:
				#se returneaza si index-ul starii
				return [True, state._index]
		return [False, -1]

	#gaseste starile afd-ului si il construieste
	def get_States(self, nfa: Nfa, start):
		#pt indexarea starilor gasite
		state_index = 0

		# o stare de afd o reprezint ca o lista de stari de nfa
		
		#gasire prima stare, initiala
		start_state = [start]
		i = 0
		
		while i != len(start_state):
			state = start_state[i]
			for fct in nfa._delta:
				if fct[0] == state and fct[1] == "Epsilon":
					#nu se adauga starile de la transf lui Epsilon cand trece in niste stari deja parcurse
					if not(fct[2] in start_state): 
						start_state.append(fct[2])
							
			i += 1

		#adaugare stare initiala
		initial_state = Afd_State()
		initial_state._old_name = set(start_state)
		initial_state._even_older_name = set(start_state)
		initial_state._index = state_index
		self._initial_state = initial_state
		self._all_states.append(initial_state)

		state_index += 1

		#poate fi stare finala
		if nfa._final_state in self._initial_state._old_name:
			self._final_states.append(self._initial_state)

		#ne spune la a cata stare de parcurs am ajuns
		parse_state = 0

		while parse_state != len(self._all_states):
			#starea de unde se pleaca
			c_s = self._all_states[parse_state]
			current_state = list(c_s._old_name)
			parse_state += 1

			for op in self._alphabet:
				found_state = []
				i = 0
				#valid ne spune daca se gaseste o stare valida, adica mai sunt si alte transf in afara de epsilon
				valid = False
				epsilon_states = []
				while i !=  len(current_state):
					start = current_state[i]
					
					for fct in nfa._delta:
						#cred ca e degeaba
						if fct[0] == start and fct[1] == "Epsilon":
							#nu se adauga starile de la transf lui Epsilon cand trece in niste stari deja existente sau stari ce apartin starii de la care a plecat
							if not(fct[2] in found_state) and not(fct[2] in current_state):
								found_state.append(fct[2])
								epsilon_states.append(fct[2])
							
						if fct[0] == start and fct[1] == op:
							#nu se adauga starile deja parcurse sau de la care se pleaca
							if not(fct[2] in found_state) and not(fct[2] in current_state):
								found_state.append(fct[2])
								valid = True
					i += 1
				
				#se cauta si celelalte epsilon-uri pt starile adaugate recent
				i = 0
				go_on = True
				#cat timp se mai gasesc alte stari
				while go_on == True:
					go_on = False
					while i != len(found_state):
						start = found_state[i]
						
						for fct in nfa._delta:
							
							if fct[0] == start and fct[1] == "Epsilon":
								if not(fct[2] in found_state) and not(fct[2] in current_state): 
									found_state.append(fct[2])
									epsilon_states.append(fct[2])
									go_on = True

							if fct[0] == start and fct[1] == op:
								if not(fct[2] in found_state): 
									found_state.append(fct[2])
									go_on = True
									valid = True	 
						i += 1

				#elimin starile prin care se ajunge cu transf epsilon
				found_state = [x for x in found_state if x not in epsilon_states]
				
				if valid:
					#verificam daca cicleaza
					res = self.cycle(found_state)
					if res[0] == True:
						self._delta.append([c_s._index, op, res[1]])
				
					#s-a gasit o stare noua
					else:
						already_exists = False

						#daca starea gasita a fost adaugata deja
						for state2 in self._all_states:
							if nfa.same_state(found_state.copy(), state2._old_name.copy()):

								self._delta.append([c_s._index, op, state2._index])
								already_exists = True
								break
						
						if already_exists == True: 
							continue

						s_to_add = Afd_State()
						s_to_add._old_name = set(found_state.copy())
						s_to_add._index = state_index
						state_index += 1

						#print(s_to_add._index)
						#print(found_state)

						#delta
						self._delta.append([c_s._index,op,s_to_add._index])

						#este stare finala
						if nfa._final_state in s_to_add._old_name or nfa.connection_to_final(s_to_add._old_name.copy()):
							self._final_states.append(s_to_add)
 
						self._all_states.append(s_to_add)

				#daca nu se ajunge nicaieri valid intra in synk
				else:
					#pt synk momentan pun -1 caci nu stiu cat e
					self._delta.append([c_s._index, op, -1])

		#se adauga synk
		self._nr_states = len(self._all_states) + 1
		synk = self._nr_states - 1
		for op in  self._alphabet:
			self._delta.append([synk, op, synk])


def Nfa_to_AFD(nfa: Nfa):
	afd = Afd()
	afd._alphabet.update(nfa._alphabet)
	#sortare alfabet
	afd._alphabet = sorted(afd._alphabet)

	#se incepe parcurgerea nfa-ului
	start = nfa._initial_state
	afd.get_States(nfa, start)

	return afd

# prenex = read_Prenex(sys.argv[1])
# regex_tree = create_expr(prenex)
# nfa = Regex_to_Nfa(regex_tree)
# # nfa.print_Nfa()
# afd = Nfa_to_AFD(nfa)
# afd.write_in_file(sys.argv[2])
# # afd.print_AFD()