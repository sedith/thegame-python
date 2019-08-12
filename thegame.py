from random import shuffle
from copy import copy
from bisect import insort
from math import log10

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
		print('  2-99      play card of inputed value')
		print('  1-4       play on stack of inputed number')
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

	# Inputs
	def get_card(self):
		read = input('play card : ')
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
		elif read not in self.hand or read > 99 or read < 2:
			return 'merde'
		else:
			return read
	def get_stack(self):
		try:
			read = int(input('on stack  : '))
		except:
			return 0
		if read < 1 or read > 4:
			return 0
		else:
			return read

	# Game
	def draw(self):
		self.hand.sort()
		while self.remain() and len(self.hand) < self.nb_hand:
			self.hand.append(self.deck.pop())
	def play(self,card,stack):
		self.stacks[stack-1].append(card)
		self.hand.remove(card)

### MAIN
game = TheGame()
game.controls()
while not game.end():
	if game.remain and len(game.hand) <= game.nb_hand-2:
		game.draw()
	game.display()
	card = game.get_card()
	if   card == 'merde':
		continue
	elif card == 'exit':
		break
	elif card == 'restore':
		game.restore()
	elif card == 'expand':
		game.show_stacks()
	else:
		stack = game.get_stack()
		if stack:
			game.backup(stack)
			game.play(card,stack)
game.score()
