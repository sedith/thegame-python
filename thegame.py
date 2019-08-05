from random import shuffle
from copy import copy

class TheGame:
	nb_hand = 8

	def __init__(self):
		self.mandatory = 2
		self.deck = [i for i in range(2,100)]
		shuffle(self.deck)
		self.hand = []
		self.draw()
		self.hand.sort()
		self.stacks = [100, 100, 1, 1]
		self.backup()

	def remain(self): return len(self.deck) > 0
	def end(self): return len(self.hand) == 0

	def backup(self):
		self.old_stacks = copy(self.stacks)
		self.old_hand = copy(self.hand)
		self.old_deck = copy(self.deck)
	def restore(self):
		self.deck = self.old_deck
		self.hand = self.old_hand
		self.stacks = self.old_stacks

	def draw(self):
		self.hand.sort()
		while self.remain() and len(self.hand) < self.nb_hand:
			self.hand += [self.deck.pop()]
		if not self.remain():
			self.mandatory = 1

	def display(self):
		print('----------------------------------')
		print(' v   v   ^   ^  ')
		print(self.stacks)
		print('')
		print(self.hand)

	def score(self):
		score = len(self.deck) + len(self.hand)
		print('----------------------------------')
		print('Final score :', score)
		if   score == 0:  print('Congratulations !! :)')
		elif score <= 10: print('Nice one ! :)')
		elif score <= 20: print('Not bad ! :)')
		elif score <= 30: print('Meh :(')
		exit(0)

	def get_card(self):
		read = input('card: ')
		if 	read == '':
			return 'exit'
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
		read = input('stack: ')
		try:
			read = int(read)
		except:
			return 'merde'
		if read < 1 or read > 4:
			return 'merde'
		else:
			return read

	def play(self,card,stack):
		self.stacks[stack-1] = card
		self.hand.remove(card)

### MAIN
game = TheGame()

while not game.end():
	if (game.nb_hand - len(game.hand)) >= game.mandatory:
		game.draw()
	game.display()
	card = game.get_card()
	if   card == 'merde':
		continue
	elif card == 'exit':
		break
	elif card == 'restore':
		game.restore()
	else:
		stack = game.get_stack()
		if stack != 'merde':
			game.backup()
			game.play(card,stack)
game.score()
