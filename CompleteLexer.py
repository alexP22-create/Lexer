from os import fdopen, posix_fadvise
from typing import Iterable
from Regex_Nfa_Afd import create_expr, Regex_to_Nfa, Nfa_to_AFD
from Regex_Nfa_Afd import Afd, Nfa, Expr, Star, Symbol, Concat, Union, Plus
from Lexer import runlexer, Dfa
#	Postolache Alexandru-Gabiel 331CB	#


#						Etapa	3.1

	
precedence_score={'+':4,'*':4,'|':2,'^':2, '(':0, ')':0}

def is_operand(i):
	if i in 'abcdefghijklmnopqrstuvwxyz0123456789\\\' ':
		return True
	else:
		return False

def reverse(expr):
	rev = ""
	
	for i in expr:
		if i is '(':
			i = ')'
		elif i is ')':
			i = '('
		rev = i + rev
	
	return rev
	
def infixtoprefix (expr):
	stack = []
	
	if expr == ' ':
		return ' '
	prefix = ""

	for i in expr:
		
		if(is_operand(i)):
			prefix += i

		elif(i in "*+"):
			prefix += i

		elif(i in "|^"):
			while(len(stack) and precedence_score[i] < precedence_score[stack[len(stack)-1]]):
				prefix += stack.pop()
			stack.append(i)
		
		elif i is '(':
			stack.append(i)
		
		elif i is ')':
			el = stack.pop()
			
			while el != '(':
				prefix += el
				el = stack.pop()
	
	while len(stack):
		if(stack[len(stack)-1] == '('):
			stack.pop()
		
		else:
			prefix += stack.pop()
	
	return reverse(prefix)

	
#adauga un simbol de concat: ab => a^b	
def add_concat_symbol(regex:str):
	
	if len(regex) == 1:
		return regex
	if regex == "'\\n'":
		return "'\\n'"
	if regex == "' '":
		return "' '"
	i = 0

	finnished = False
	
	while finnished == False:
		finnished = True
		i = 0
		
		while i < len(regex)-1:
			
			if regex[i] != "|" and regex[i] != "^" and regex[i] != "(" and regex[i] != " ":
				if regex[i+1] != "|" and regex[i+1] != "*" and regex[i+1] != "+" and regex[i+1] != "^" and regex[i+1] != ")" and regex[i+1] != " ":
					regex = regex[:i+1] + "^" + regex[i+1:]
					finnished = False
					break
			
			if regex[i] in "*+":
				if regex[i+1] == "(":
					regex = regex[:i+1] + "^" + regex[i+1:]
					finnished = False
					break
			
			i += 1
	return regex

# ab* => a b STAR
def convert(regex: str):
	final = ""
	i = 0
	
	while i < len(regex):
		if regex[i] == "|":
			final += "UNION "
			i += 1
		elif regex[i] == "^":
			final += "CONCAT "
			i += 1
		elif regex[i] == "*":
			final += "STAR "
			i += 1
		elif regex[i] == "+":
			final += "PLUS "
			i += 1
		elif regex[i] == "'" and regex[i+1] == " " and regex[i+2] == "'":
			final += "SPACE "
			i = i + 3
		elif regex[i] == "'" and regex[i+1] == "n" and regex[i+2] == "\\" and regex[i+3] == "'":
			final += "NEWLINE "
			i = i + 4
		else:
			final += regex[i] + " "
			i += 1
	
	final = final[:-1]
	return final
	
#face swap la copii nodurilor unui arbore binar deoarece alg de infix la prefix le interschimba
def swap_children(tree_head: Expr) -> Expr:
	
	if isinstance(tree_head, Concat):
		aux = tree_head._expr1
		tree_head._expr1 = tree_head._expr2
		tree_head._expr2 = aux
		swap_children(tree_head._expr1) 
		swap_children(tree_head._expr2)
	
	elif isinstance(tree_head, Union):
		aux = tree_head._expr1
		tree_head._expr1 = tree_head._expr2
		tree_head._expr2 = aux 
		swap_children(tree_head._expr1)
		swap_children(tree_head._expr2)
	
	elif isinstance(tree_head, Star):
		swap_children(tree_head._expr)
	
	elif isinstance(tree_head, Plus):
		swap_children(tree_head._expr)


def read_token_regex(file):
	f = open(file,"r")
	info = f.read()
	lines = info.split("\n")
	afd_list = []

	for i in range(0, len(lines) - 1):
		words = lines[i].split(" ")
		token = words[0]
		#regex-ul este format de restul de words in afara de primul word
		regex = ""
		
		for j in range(1,len(words)):
			regex += words[j] + " "
		regex = regex[:-2]
		regex = add_concat_symbol(regex)
		regex = infixtoprefix(regex)
		
		#convertire la inputul de la etapa 2
		regex = convert(regex)
		#construire arbore regex
		tree_regex = create_expr(regex)
		#swap copii noduri
		swap_children(tree_regex)
		
		#creare AFD
		nfa = Regex_to_Nfa(tree_regex)
		afd = Nfa_to_AFD(nfa)
		afd_list.append((afd, token))
	return afd_list

#dfa si afd reprezinta acelasi lucru doar ca au configurari diferite intre etapa 2 si 1
def convert_dfa_etape(dfa: Dfa, afd: Afd):
	#stari finale
	for final_state in afd._final_states:
		state = final_state._index
		dfa._final_states.add(state)

	#alphabet
	dfa._alphabet = afd._alphabet
	dfa._max_state = 0

	#max state
	for state in afd._all_states:
		if state._index > dfa._max_state:
			dfa._max_state = state._index

	#delta
	#in imlpementarea de la etapa 2 la synk state-uri puneam -1 asa ca voi seta acum
	for fct in afd._delta:
		if fct[2] == -1:
			fct[2] = afd._nr_states - 1

		#la etapa 1 delta era dictionar iar in etapa 2 lista deci convertesc
		t = tuple([fct[0], fct[1]])
		dfa._delta[t] = fct[2]

	#gasire synk states 
	dfa.getSinkStates()


def runcompletelexer(token_regex_file: str, in_file: str, out_file:str):
	afd_list = read_token_regex(token_regex_file)
	dfa_list = []
	for el in afd_list:
		afd = el[0]
		token = el[1]
		dfa = Dfa()
		dfa._token = token
		convert_dfa_etape(dfa, afd)
		dfa_list.append(dfa)
	runlexer(token_regex_file, in_file, out_file, dfa_list)
	return

#                             Etapa		3.2

TAB = '  '  # two whitespaces

#nod creat de mine care in afara de inaltime are si string-ul pe care il reprezinta
class MyNode:
	def __init__(self, *args):
		self.height = int(args[0])  # the level of indentation required for current Node
		self.value = args[1]

	def __str__(self): 
		return self.value

	@staticmethod
	def one_tab(line):
		"""Formats the line of an argument from an expression."""
		return TAB + line + '\n'

	def final_print_str(self, print_str):
		"""Adds height number of tabs at the beginning of every line that makes up the current Node."""
		return (self.height * TAB).join(print_str)

class Node:
	def __init__(self, *args):
		self.height = int(args[0])  # the level of indentation required for current Node
		

	def __str__(self):
		return 'prog'

	@staticmethod
	def one_tab(line):
		"""Formats the line of an argument from an expression."""
		return TAB + line + '\n'

	def final_print_str(self, print_str):
		"""Adds height number of tabs at the beginning of every line that makes up the current Node."""
		return (self.height * TAB).join(print_str)


class InstructionList(Node):
	"""begin <instruction_list> end"""

	def __init__(self, *args):  # args = height, [Nodes in instruction_list]
		super().__init__(args[0])
		self.list = args[1]

	def __str__(self):
		print_str = ['[\n']
		for expr in self.list:
			print_str.append(self.one_tab(expr.__str__()))
		print_str.append(']')

		return self.final_print_str(print_str)


class Expr(Node):
	"""<expr> + <expr> | <expr> - <expr> | <expr> * <expr> | <expr> > <expr> | <expr> == <expr> | <variable> | <integer>"""

	def __init__(self, *args):  # args = height, '+' | '-' | '*' | '>' | '==' | 'v' | 'i', left_side, *right_side
		super().__init__(args[0])
		self.type = args[1]
		self.left = args[2]
		if len(args) > 3:
			self.right = args[3]
		else:
			# variable and integer have no right_side
			self.right = None

	def __str__(self):
		name = 'expr'
		if self.type == 'v':
			name = 'variable'
		elif self.type == 'i':
			name = 'integer'
		elif self.type == '+':
			name = 'plus'
		elif self.type == '-':
			name = 'minus'
		elif self.type == '*':
			name = 'multiply'
		elif self.type == '>':
			name = 'greaterthan'
		elif self.type == '==':
			name = 'equals'

		print_str = [name + ' [\n', self.one_tab(str(self.left))]
		if self.right:
			print_str.append(self.one_tab(str(self.right)))
		print_str.append(']')

		return self.final_print_str(print_str)


class While(Node):
	"""while (<expr>) do <prog> od"""

	def __init__(self, *args):  # args = height, Node_expr, Node_prog
		super().__init__(args[0])
		self.expr = args[1]
		self.prog = args[2]

	def __str__(self):
		print_str = ['while [\n',
					 self.one_tab(self.expr.__str__()),
					 self.one_tab('do ' + self.prog.__str__()),
					 ']']
		return self.final_print_str(print_str)


class If(Node):
	"""if (<expr>) then <prog> else <prog> fi"""

	def __init__(self, *args):  # args = height, Node_expr, Node_then, Node_else
		super().__init__(args[0])
		self.expr = args[1]
		self.then_branch = args[2]
		self.else_branch = args[3]

	def __str__(self):
		print_str = ['if [\n',
					 self.one_tab(self.expr.__str__()),
					 self.one_tab('then ' + self.then_branch.__str__()),
					 self.one_tab('else ' + self.else_branch.__str__()),
					 ']']
		return self.final_print_str(print_str)


class Assign(Node):
	"""<variable> '=' <expr>"""

	def __init__(self, *args):  # args = height, Node_variable, Node_expr
		super().__init__(args[0])
		self.variable = args[1]
		self.expr = args[2]

	def __str__(self):
		print_str = ['assign [\n',
					 self.one_tab(self.variable.__str__()),
					 self.one_tab(self.expr.__str__()),
					 ']']
		return self.final_print_str(print_str)


def print_trees(stack, aux):
	print("=================stack=========")
	for el in stack:
		print(el)
	print("=================aux=========")
	for el in aux:
		print(el)

def raise_if_assign(el: Assign):
	el.expr.height += 1
	el.expr.left.height += 1
	if el.expr.right != None:
		el.expr.right.height += 1

def raise_while_assign(el: Assign):
	el.expr.height += 1
	el.expr.left.height += 1
	if el.expr.right != None:
		el.expr.right.height += 1

def stack_to_tree(my_stack) -> Expr:
	#stiva axuxiliara pentru a retine operatorii care asteapta alti operatori
	aux = []

	while len(my_stack) != 0:
		#print_trees(my_stack, aux)
		el1 = my_stack.pop()

		#stop condition
		if len(my_stack) == 0:
			return el1

		#creare lista de instructiuni
		if isinstance(el1, Assign) or isinstance(el1, If) or isinstance(el1, While):
			if isinstance(aux[len(aux)-1], Assign) or isinstance(aux[len(aux)-1], If) or isinstance(aux[len(aux)-1], While):
				expr2 = aux.pop()
				l = []
				l.append(el1)
				l.append(expr2)
				instruction_list = InstructionList(el1.height-1, l)
				my_stack.append(instruction_list)
				continue

			elif isinstance(aux[len(aux)-1], InstructionList):
				list = aux.pop()
				new_list = []
				new_list.append(el1)
				new_list.extend(list.list)
				instruction_list = InstructionList(list.height, new_list)
				my_stack.append(instruction_list)
				continue

		if isinstance(el1, MyNode):
			#pregatire pt creare lista de instructiuni
			if el1.value == "begin":
				my_stack.append(el1)
				my_stack.append(aux.pop())
				continue
			
			#creare nod if
			if el1.value == "if":
				if_cond = aux.pop()
				then = aux.pop()
				ex1 = aux.pop()
				else_node = aux.pop()
				ex2 = aux.pop()
				end_if = aux.pop()
				if_cond.height += 1
				if isinstance(ex1, Assign):
					raise_if_assign(ex1)
				if isinstance(ex2, Assign):
					raise_if_assign(ex2)
				if_node = If(el1.height, if_cond, ex1, ex2)
				my_stack.append(if_node)
				continue
			
			#creare nod while
			if el1.value == "while":
				cond = aux.pop()
				do = aux.pop()
				instr = aux.pop()
				end_do = aux.pop()
				cond.height += 1
				if isinstance(instr, Assign):
					raise_while_assign(instr)
				while_node = While(el1.height, cond, instr)
				my_stack.append(while_node)
				continue
		

		el2 = my_stack.pop()
		
		if isinstance(el2, MyNode):
			if el2.value == "begin":
				my_stack.append(el2)
				my_stack.append(el1)
				my_stack.append(aux.pop())
				continue
	
		el3 = my_stack.pop()
	
		# caz (a+b) > 3
		if isinstance(el3, Expr) and isinstance(el1, MyNode):
			if el2.value == "=":
				if el1.value in "abcdefghijklmnopqrstuvwxyz":
					new_el1 = Expr(el1.height+2, "v", el1)
				else:
					new_el1 = Expr(el1.height+2, "i", el1)

				a = Assign(el3.height, el3, new_el1)
				my_stack.append(a)
				continue
				
			elif el2.value in "+-*>==":
				if el1.value in "abcdefghijklmnopqrstuvwxyz":
					new_el1 = Expr(el1.height+2, "v", el1)
				else:
					new_el1 = Expr(el1.height+2, "i", el1)

				e = Expr(el1.height, el2.value, el3, new_el1)
				my_stack.append(e)
				continue

		# caz (a+b) == (c - d)
		if isinstance(el3, Expr) and isinstance(el1, Expr): 
			if el2.value == "=":
				a = Assign(el3.height, el3, el1)
				my_stack.append(a)
				continue
				
			elif el2.value in "+-*>==":
				e = Expr(el1.height, el2.value, el3, el1)
				my_stack.append(e)
				continue
				
		
		# caz a > b + c
		if isinstance(el2, MyNode) and isinstance(el1, Expr):
			if el2.value == "=":
				if el3.value in "abcdefghijklmnopqrstuvwxyz":
					new_el3 = Expr(el3.height+2, "v", el3)
				else:
					new_el3 = Expr(el3.height+2, "i", el3)
				a = Assign(el1.height, new_el3, el1)
				my_stack.append(a)
				continue
				
			elif el2.value in "+-*>==":
				if el3.value in "abcdefghijklmnopqrstuvwxyz":
					new_el3 = Expr(el3.height+2, "v", el3)
				else:
					new_el3 = Expr(el3.height+2, "i", el3)

				e = Expr(el1.height, el2.value, new_el3, el1)
				my_stack.append(e)
				continue

		#caz a > b
		if isinstance(el2, MyNode) and isinstance(el1, MyNode):
			if el2.value == "=":
				if el1.value in "abcdefghijklmnopqrstuvwxyz":
					new_el1 = Expr(el1.height+2, "v", el1)
				else:
					new_el1 = Expr(el1.height+2, "i", el1, None)

				if el3.value in "abcdefghijklmnopqrstuvwxyz":
					new_el3 = Expr(el3.height+2, "v", el3)
				else:
					new_el3 = Expr(el3.height+2, "i", el3)

				a = Assign(el1.height, new_el3, new_el1)
				my_stack.append(a)
				continue
				
			elif el2.value in "+-*>==":
				if el1.value in "abcdefghijklmnopqrstuvwxyz":
					new_el1 = Expr(el1.height+2, "v", el1)
				else:
					new_el1 = Expr(el1.height+2, "i", el1, None)
				
				if el3.value in "abcdefghijklmnopqrstuvwxyz":
					new_el3 = Expr(el3.height+2, "v", el3)
				else:
					new_el3 = Expr(el3.height+2, "i", el3)

				e = Expr(el1.height, el2.value, new_el3, new_el1)
				my_stack.append(e)
				continue
	
		#creare lista de instructiuni intre begin si end
		if isinstance(el3, MyNode):
			if el3.value == "begin":
				if not isinstance(el2, InstructionList):
					instruction_list = InstructionList(el3.height, [el2])
					my_stack.append(instruction_list)
					continue
				else:
					my_stack.append(el2)
					continue

		#  nu s-a gasit nicio expresie deci ma deplasez pe stiva in jos
		my_stack.append(el3)
		my_stack.append(el2)

		#salvez elementele anterioare intr-o stiva
		aux.append(el1)

#elimina tab-urile inainte de caractere de pe un rand
def eliminate_before_spaces(line: str):
	nr = 0
	for i in range(0, len(line)):
		if line[i] == " ":
			nr += 1
		else:
			break
	return line[nr:]

#creaza arborele
def create_tree(s: str) -> Expr:
	lines = s.split("\n")
	my_stack = []
	#inaltimea din fisier la care se afla in momentul citirii
	height = 0
	if_height = 0

	for i in range(0, len(lines)):

		#daca linia incepe cu multe tab-uri in fata le elimin
		lines[i] = eliminate_before_spaces(lines[i])

		if lines[i] == "begin":
			n = MyNode(height, "begin")
			my_stack.append(n)
			height += 1

		elif lines[i] == "end":
			n = MyNode(height, "end")
			my_stack.append(n)
			height -= 1

		elif lines[i] == "od":
			n = MyNode(height, "od")
			my_stack.append(n)
			height -= 1
		
		elif lines[i] == "fi":
			n = MyNode(height, "fi")
			my_stack.append(n)
			height -= 1
		
		elif lines[i] == "else":
			n = MyNode(if_height, "else")
			my_stack.append(n)
		
		else:
			words = lines[i].split(" ")
			if words[1] == "=":
				for j in range(0, len(words)):
					n = MyNode(height, words[j])
					my_stack.append(n)

			elif words[0] == "while":
				words[1] = words[1][1:]
				words[len(words)-2] = words[len(words)-2][:-1]

				comparator_position = 0

				for j in range(0, len(words)):
					if words[j] in ">==":
						comparator_position = j
						break
				
				if comparator_position > 2:
					while_node = MyNode(height, "while")
					my_stack.append(while_node)
					n1 = MyNode(height, words[1])
					n2 = MyNode(height, words[3])

					if n1.value in "abcdefghijklmnopqrstuvwxyz":
						n1_expr = Expr(height+3, "v", n1)
					else:
						n1_expr = Expr(height+3, "i", n1)
					if n2.value in "abcdefghijklmnopqrstuvwxyz":
						n2_expr = Expr(height+3, "v", n2)
					else:
						n2_expr = Expr(height+3, "i", n2)

					#inseamna ca se gaseste o expresie inainte de comparator
					expr = Expr(height+2, words[2], n1_expr, n2_expr)
					my_stack.append(expr)
					
					for j in range(comparator_position, len(words)):
						n = MyNode(height, words[j])
						my_stack.append(n)
				
				else:				
					for j in range(0, len(words)):
						n = MyNode(height, words[j])
						my_stack.append(n)
				height += 1

			elif words[0] == "if":
				words[1] = words[1][1:]
				words[len(words)-2] = words[len(words)-2][:-1]

				comparator_position = 0

				for j in range(0, len(words)):
					if words[j] in ">==":
						comparator_position = j
						break

				if comparator_position > 2:
					if_node = MyNode(height, "if")
					my_stack.append(if_node)
					n1 = MyNode(height, words[1])
					n2 = MyNode(height, words[3])
					
					if n1.value in "abcdefghijklmnopqrstuvwxyz":
						n1_expr = Expr(height+3, "v", n1)
					else:
						n1_expr = Expr(height+3, "i", n1)
					
					if n2.value in "abcdefghijklmnopqrstuvwxyz":
						n2_expr = Expr(height+3, "v", n2)
					else:
						n2_expr = Expr(height+3, "i", n2)
					
					#inseamna ca se gaseste o expresie inainte de comparator
					expr = Expr(height+2, words[2], n1_expr, n2_expr)
					my_stack.append(expr)
					
					for j in range(comparator_position, len(words)):
						n = MyNode(height, words[j])
						my_stack.append(n)
				
				else:				
					for j in range(0, len(words)):
						n = MyNode(height, words[j])
						my_stack.append(n)
				
				height += 1
				if_height = height

	return stack_to_tree(my_stack)


def runparser(in_file: str, out_file: str):
	inp = open(in_file, "r")
	tree = create_tree(inp.read())
	out = open(out_file, "w")
	out.write(tree.__str__())
	return