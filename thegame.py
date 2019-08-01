from random import shuffle
from copy import copy

deck = [i for i in range(2,100)]

shuffle(deck)

nb_hand = 8
hand = []

for i in range(nb_hand):
	hand += [deck.pop()]
hand.sort()

stacks = [100, 100, 1, 1]

old_stacks = stacks
old_hand = hand
old_deck = deck

while len(hand) != 0:
	if len(deck) > 0: mandatory = 2
	else: 		  mandatory = 1

	if (nb_hand - len(hand)) >= mandatory and len(deck) > 0:
		hand.sort()
		for i in range(nb_hand - len(hand)):
			hand += [deck.pop()]
	print ' v   v   ^   ^ '
	print stacks
	print ''
	print hand
	try:
		card = input('card: ')
	except:
		card = 'merde'
	if card == '':
		print 'score :', (len(deck) + len(hand))
		exit(0)
	elif card == 0:
		deck = old_deck
		hand = old_hand
		stacks = old_stacks
	elif (card not in hand) or (card > 99) or (card < 2):
		1
	else:
		try:
			stack = input('stack: ')
		except:
			continue
		if stack < 1 or stack > 4:
			continue
		old_stacks = copy(stacks)
		old_hand = copy(hand)
		old_deck = copy(deck)
		stacks[stack-1] = card
		hand.remove(card)
	print '----------------------------------'

print 'score :', 0,'!!!'
