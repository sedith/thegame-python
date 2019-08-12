from random import shuffle
from copy import copy
from bisect import insort
from math import log10
from time import sleep

class TheGame:
	# Initialization
	nb_hand = 8
	nb_show_stack = 5

	def __init__(self):
		self.deck = [i for i in range(2,100)]
		shuffle(self.deck)
		self.hand = []
		self.draw()
		self.hand.sort()
		self.stacks = [[100], [100], [1], [1]]
		self.history = []

	# Tests
	def remain(self): return len(self.deck) > 0
	def end(self): return len(self.hand) == 0

	# History
	def backup(self, stack):
		self.history.append(stack-1)
	def restore(self):
		if len(self.history) > 0 :
			if len(self.hand) == self.nb_hand:
				self.deck.append(self.hand.pop())
				if self.remain(): self.deck.append(self.hand.pop())
			insort(self.hand, self.stacks[self.history[-1]].pop())
			self.history.pop()

	# Display
	def controls(self):
		print('Controls :')
		print('  ENTER     exit game')
		print('  SPACE     display the lasts cards on each stack')
		print('  0         restore previous state')
		print('  1         display list of valid movesa')
		print('  2-99      play card of inputed value')
		print('Stacks are numbered 1 to 4')
		print('Enjoy :)')
	def display(self):
		print('----------------------------------')
		print('v',int(log10(self.stacks[0][-1]))*' ',' v',int(log10(self.stacks[1][-1]))*' ',' ʌ',int(log10(self.stacks[2][-1]))*' ',' ʌ', sep='')
		print(self.stacks[0][-1], self.stacks[1][-1], self.stacks[2][-1], self.stacks[3][-1])
		print('')
		for i in range(len(self.hand)):
			print(self.hand[i],end=' ')
		print('\n')
	def score(self):
		score = len(self.deck) + len(self.hand)
		print('----------------------------------')
		print('Final score :', score)
		if   score == 0:  print('Congratulations !! :)')
		elif score <= 10: print('Nice one ! :)')
		elif score <= 20: print('Not bad ! :)')
		elif score <= 30: print('Meh :(')
		exit(0)
	def show_stacks(self):
		print()
		for stack in range(4):
			nb_show = min(len(self.stacks[stack]),self.nb_show_stack)
			print(nb_show,'last cards of stack', stack+1, ':\n  ', end='')
			for i in range(nb_show, 0, -1):
				print(self.stacks[stack][-i], end = ' ')
			print()
	def show_valid_moves(self):
		print('\nList of valid moves :')
		for c in self.hand:
			valid = self.check_valid_card(c)
			if len(valid) > 0: print(c, ':', valid)

	# Inputs
	def get_action(self):
		read = input('action : ')
		if 	 read == '':
			return 'exit'
		if   read == ' ':
			return 'expand'
		try:
			read = int(read)
		except:
			return 'merde'
		if   read == 0:
			return 'restore'
		elif read == 1:
			return 'help'
		elif read not in self.hand or read > 99 or read < 2:
			return 'merde_int'
		else:
			return read
	def get_stack(self):
		try:
			read = int(input('stack  : '))
		except:
			return 0
		if read < 1 or read > 4:
			return 0
		else:
			return read

	# Game
	def is_valid(self, card, stack):
		prev_card = self.stacks[stack-1][-1]
		if stack < 3:
			return prev_card > card or prev_card+10 == card
		else:
			return prev_card < card or prev_card-10 == card
	def check_valid_card(self, card):
		valid = []
		for s in range(1,5):
			if self.is_valid(card, s): valid.append(s)
		return valid
	def check_stuck(self):
		nb_valid_moves = 0
		for c in self.hand:
			nb_valid_moves += len(self.check_valid_card(c))
		if nb_valid_moves == 0: self.score()
	def draw(self):
		self.hand.sort()
		while self.remain() and len(self.hand) < self.nb_hand:
			self.hand.append(self.deck.pop())
	def play(self,card,stack):
		print('\nYou played card ', card, ' on stack ', stack,'.', sep='')
		self.stacks[stack-1].append(card)
		self.hand.remove(card)

### MAIN
game = TheGame()
game.controls()
while not game.end():
	if game.remain and len(game.hand) <= game.nb_hand-2:
		game.draw()
	game.display()
	game.check_stuck()
	card = game.get_action()
	if   card == 'merde':		print('\nInvalid action.') ; continue
	elif card == 'merde_int':	print('\nInvalid card number.') ; continue
	elif card == 'exit':		break
	elif card == 'help':		game.show_valid_moves()
	elif card == 'restore': 	game.restore()
	elif card == 'expand':  	game.show_stacks()
	else:
		valid_moves = game.check_valid_card(card)
		if   len(valid_moves) == 0:	print('\nYou cannot play this card.') ; continue
		elif len(valid_moves) == 1: stack = valid_moves[0]
		else:						stack = game.get_stack()
		if stack in valid_moves:
			game.backup(stack)
			game.play(card,stack)
		else:
			print('\nYou cannot play this card here.')
game.score()
