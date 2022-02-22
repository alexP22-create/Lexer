from typing import Set, Dict
from typing import List
# Postolache Alexandru-Gabriel 331CB
class Dfa:
	_token: str
	_alphabet: Set[str]
	_initial_state: int
	_current_state: int
	_final_states: Set[int]
	_delta: dict()
	_sink_states: Set[int]
	_max_state: int
	#_max_state folosita pt determinarea sink state-urilor
	_max_state: int
	def __init__(self):
		self._initial_state = 0
		self._current_state = 0
		self._final_states = set()
		self._delta = {}
		self._alphabet = set()
		self._sink_states = set()
		self._max_state = 0
	# def __init__(self, text):
	# 	self._initial_state = 0
	# 	self._current_state = 0
	# 	self._final_states = set()
	# 	self._delta = {}
	# 	self._alphabet = set()
	# 	self._sink_states = set()
	# 	self._max_state = 0
	# 	lines = text.split('\n')
	# 	for i in range(0, len(lines)):
	# 		#alphabet
	# 		if i == 0:
	# 			for j in range(0, len(lines[0])):
	# 				if lines[0][j] == "\\" and j < len(lines[0]) - 1:
	# 					el = "\\"+lines[0][j+1]
	# 					self._alphabet.add(el)
	# 				if j > 0 and lines[0][j-1] != "\\":
	# 					self._alphabet.add(lines[0][j])
	# 				if j == 0:
	# 					self._alphabet.add(lines[0][j])
	# 		#token
	# 		if i == 1:
	# 			self._token = lines[1]
	# 		#intitial state
	# 		if i == 2:
	# 			self._initial_state = int(lines[2])
	# 			self._current_state = self._initial_state
	# 			if self._initial_state > self._max_state:
	# 				self._max_state = self._initial_state
	# 		if i > 2:
	# 			#final states
	# 			if i == len(lines) - 1:
	# 				words = lines[i].split(' ')
	# 				for word in words:
	# 					self._final_states.add(int(word))
	# 					if int(word) > self._max_state:
	# 						self._max_state = int(word)
	# 			else:#delta
	# 				words = lines[i].split(',')
	# 				#extragere ' '
	# 				words[1] = words[1][1:]
	# 				words[1] = words[1][:-1]
	# 				#starea curents si ce input poate primi
	# 				l = [int(words[0]), words[1]]
	# 				# trasform din lista mutabila in tuplu imutabil
	# 				l = tuple(l)
	# 				#hash function pt starea finala
	# 				self._delta[l] = int(words[2])
	# 				if int(words[0]) > self._max_state:
	# 					self._max_state = int(words[0])
	# 				if int(words[2]) > self._max_state:
	# 					self._max_state = int(words[2])
	
	def getSinkStates(self):
		states = []
		states_set = set()
		for i in self._final_states:
			states.append(i)
			states_set.add(i)
		while len(states) != 0:
			el = states[0]
			states = states[1:]
			for t in self._delta:
				if el == self._delta[t] and not(t[0] in states_set):
					states_set.add(t[0])
					states.append(t[0])
		for i in range(0, self._max_state+1):
			if not(i in states_set):
				self._sink_states.add(i)

	def next_config(self, inp):
		for l in self._delta.keys():
			if inp == "\n":
				if l[0] == self._current_state and l[1] == "\\n":        
					self._current_state = self._delta[l]
					return
			if l[0] == self._current_state and l[1] == inp:
				self._current_state = self._delta[l]
				return
		

	def accept_word(self, word):
		for inp in word:
			self.next_config(inp)
		if self._current_state in self._final_states:
			return True
		else:
			return False

	def reset_state(self):
		self._current_state = self._initial_state

	def accept(self):
		if self._current_state in self._final_states:
			return True
		return False

	def reached_sink(self):
		if self._current_state in self._sink_states:
			return True
		return False

	def printDFA(self):
		print(self._initial_state)
		for k in self._delta.keys():
			print(str(k[0]) + ' ' + str(k[1]) + ' ' + str(self._delta[k]))
		print(self._final_states)

	def in_alphabet(self, c):
		if c == "\n":
			return "\\n" in self._alphabet
		if len(c) == 1:
			return c in self._alphabet


class Lexer:
	_dfa_list: List[Dfa]
	#because the dfa list will be modified we need a copy
	_copy_dfa_list: List[Dfa]
	def __init__(self, dfas):
		self._dfa_list = []
		self._dfa_list = dfas
		self._copy_dfa_list = dfas.copy()

	#return the dfa with the longest prefix accepted
	def longest_prefix(self, word):
		prefix = ""
		lexem = ""
		#id-ul dfa-ului lexemului max
		max_dfa = "-1"
		#pana dau toate masinile sink
		until_sink = 0
		for c in word:
			prefix += c
			i = 0
			already_found = False
			while i <  len(self._dfa_list):
				self._dfa_list[i].next_config(c)
				#check if it goes into a sink state or ff the alphabet is invalid
				if self._dfa_list[i].reached_sink() or not(self._dfa_list[i].in_alphabet(c)):
					self._dfa_list.remove(self._dfa_list[i])
					i = i - 1
				else:
					if self._dfa_list[i].accept() and already_found == False:
						already_found = True
						max_dfa = self._dfa_list[i]._token
						lexem = prefix
				i = i + 1
			if len(self._dfa_list) == 0:
				return (max_dfa, lexem, until_sink) 
			until_sink += 1
		return (max_dfa, lexem, until_sink)

	def parse(self, word):
		lexems = ""
		c_word = word
		passed_characters = 0
		while (word != ""):
			dfa_prefix = self.longest_prefix(word)
			if (dfa_prefix[1] == "\n"):
				lexems += dfa_prefix[0] + " " + "\\n\n"
			else:
				lexems += dfa_prefix[0] + " " + dfa_prefix[1] + "\n"
			#extragere prefix
			if dfa_prefix[1] != "":
				word = word[len(dfa_prefix[1]):]
				passed_characters += len(dfa_prefix[1])
			#recreate dfa list
			self._dfa_list = self._copy_dfa_list.copy()
			#reset the current state of every dfa
			for i in range(0,len(self._dfa_list)):
				self._dfa_list[i]._current_state = self._dfa_list[i]._initial_state
			#nu se poate imparti input-ul dupa lexeme
			if (dfa_prefix[0] == "-1"):
				line = get_Line(c_word, word)
				index = passed_characters + dfa_prefix[2]
				if index == len(c_word):
					return "No viable alternative at character " + "EOF" + ", line " + line
				else:
					return "No viable alternative at character " + str(passed_characters+dfa_prefix[2]) + ", line " + line
		return lexems		

def get_Line(big_str, word):
	passed_char = 0
	lines = big_str.split("\n")
	for i in range(0, len(lines)):
		for j in range(0,len(lines[i])):
			if lines[i][j] == word[0]:
				found = True
				for k in range(0,len(word)):
					if big_str[passed_char+j+k] != word[k]:
						found = False
						break
				if found == True:
					return(str(i))
		passed_char += len(lines[i])
	return ("") 

def read_dfa_list(dfa_info):
	dfa_list = []
	dfas = dfa_info.split("\n\n")
	for i in range(0, len(dfas)):
		DFA = Dfa(dfas[i])
		DFA.getSinkStates()
		dfa_list.append(DFA)
	return dfa_list

def runlexer(lexer, finput, foutput, dfa_list): 
	f_out = open(foutput, "w")
	f_inp = open(finput, "r")
	lexer = Lexer(dfa_list)
	# print("="+f_inp.read()+"=")
	lexems = lexer.parse(f_inp.read())
	f_out.write(lexems)