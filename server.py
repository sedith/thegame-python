import zmq
from random import shuffle


class Player:
    def __init__(self, pseudo):
        self.pseudo = pseudo
        self.hand = []
        self.order = -1

    def set_order(self, order):
        self.order = order

    def get_order(self):
        return self.order

class Move:
    def __init__(self, pseudo, card, stack):
        self.pseudo = pseudo
        self.card = card
        self.stack = stack


class TheGame:
    # Initialization
    players = []
    history = []
    phase = 'registration'

    def __init__(self):
        self.deck = list(range(2, 100))
        shuffle(self.deck)
        self.stacks = [[100], [100], [1], [1]]

    # Getters
    def get_board(self):
        return [s[-1] for s in self.stacks]

    def get_deck(self):
        return len(self.deck)

    def get_score(self):
        return sum(len(p.hand) for p in self.players) + len(self.deck)

    def get_active(self):
        try:
            return self.players[[p.order for p in self.players].index(self.active)]
        except ValueError:
            return None

    def get_player(self, pseudo):
        try:
            return self.players[[p.pseudo for p in self.players].index(pseudo)]
        except ValueError:  # pseudo not in players
            return None

    # Checks
    def remain(self):
        return len(self.deck) > 0

    def check_player(self, pseudo):
        return pseudo in [p.pseudo for p in self.players]

    def check_stack(self, stack):
        return 0 <= stack < 4

    def check_card(self, card):
        return card in self.get_active().hand

    def check_move(self, move):
        prev_card = self.stacks[move.stack][-1]
        if move.stack < 2:
            return prev_card > move.card or prev_card + 10 == move.card
        else:
            return prev_card < move.card or prev_card - 10 == move.card

    def check_finished(self):
        return not self.remain() and not any(p.hand for p in self.players)

    def check_stuck(self):
        n = 2 if self.remain() else 1
        stuck = self.nb_cards - len(self.get_active().hand) < n
        for c in self.get_active().hand:
            for s in range(1, 5):
                if self.check_move(Move('', c, s)):
                    stuck = False
                    break
        return stuck

    # Register
    def register(self, pseudo):
        self.players.append(Player(pseudo))

    def close_registrations(self):
        if self.phase == 'registration':
            self.phase = 'preparation'
            if len(self.players) == 1:
                self.nb_cards = 8
            elif len(self.players) == 2:
                self.nb_cards = 7
            else:
                self.nb_cards = 6

    # History
    def restore(self):
        last_move = self.history.pop()
        self.get_active().hand.append(self.stacks[last_move.stack].pop())

    # Game
    def player_ready(self, pseudo, order):
        self.get_player(pseudo).set_order(order-1)
        if all(p.order != -1 for p in self.players):
            self.start()

    def start(self):
        self.phase = 'play'
        self.active = 0

    def first_draw(self,pseudo):
        for p in self.players:
            print(p.pseudo, p.hand)
        self.close_registrations()
        p = self.get_player(pseudo)
        if len(p.hand) == self.nb_cards:
            print('??')
            return []
        while self.remain() and len(p.hand) < self.nb_cards:
            p.hand.append(self.deck.pop())
        p.hand.sort()
        return p.hand

    def draw(self, pseudo):
        # existing cards are sorted and the rest is appended
        n = 2 if self.remain() else 1
        p = self.get_player(pseudo)
        if self.nb_cards - len(p.hand) < n:
            return []
        p = self.get_player(pseudo)
        p.hand.sort()
        while self.remain() and len(p.hand) < self.nb_cards:
            p.hand.append(self.deck.pop())
        self.end_turn()
        return p.hand

    def play(self, move):
        self.get_active().hand.remove(move.card)
        self.stacks[move.stack].append(move.card)
        self.history.append(move)
        if self.check_stuck() or self.check_finished():
            self.phase = 'end'

    def end_turn(self):
        empty = True
        while empty:
            self.active = (self.active + 1) % len(self.players)
            empty = self.get_active().hand == []


class API:
    '''
    ALLOWED ACTIONS
    * registration
        * connect(pseudo)
        * draw
    * preparation
        * draw
        * order
    * play
        * play(card,stack)
        * draw
        # who
        # expand(stack)
        # undo
        # valid_moves
    '''

    game = TheGame()

    def notify(self):
        if self.game.phase == 'play':
            return {'status':'play', 'board':self.game.get_board(), 'deck':self.game.get_deck(), 'player':self.game.get_active().pseudo}
        if self.game.phase == 'end':
            return {'status':'end', 'score':self.game.get_score()}

    def call(self, pseudo, method, args):
        try:
            return getattr(self, method)(pseudo=pseudo, *args)
        except Exception as e:
            return {'status': 'error', 'value': 'caught exception: %s' % str(e)}

    def connect(self, *args, pseudo, **kwargs):
        if self.game.phase == 'registration':
            if self.game.check_player(pseudo):
                return {'status': 'of', 'value': 'name %s already taken' % pseudo}
            self.game.register(pseudo)
            return {'status': 'ok', 'value': ''}
        if self.game.check_player(pseudo):
            return {'status': 'of', 'value': {'hand': self.game.get_player(pseudo).hand, 'board': self.game.get_board(), 'deck':self.game.get_deck()}}
        return {'status': 'error', 'value': 'game already started'}


    def draw(self, *args, pseudo, **kwargs):
        if self.game.phase != 'play':
            print('%s draws' %  pseudo)
            h = self.game.first_draw(pseudo)
        else:
            h = self.game.draw(pseudo)
        if not h:
            return {'status': 'error', 'value': '%s cannot draw now' % pseudo}
        return {'status': 'ok', 'value': h}

    def order(self, order, *args, pseudo, **kwargs):
        try:
            order = int(order)
            assert 0 < order <= len(self.game.players) and order - 1 not in [p.order for p in self.game.players]
        except ValueError:
            return {
                'status': 'error',
                'value': 'invalid argument, enter integer value'
            }
        except AssertionError:
            l = [p.order + 1 for p in self.game.players if p.order != -1]
            append_value = ', these are already taken: %s' % l if l != [] else ''
            return {
                'status': 'error',
                'value': 'correct order is between 1 and %i%s' % (len(self.game.players), ', these are already taken: %s' % l if l != [] else '')
            }

        # in theory, we cannot enter the first if due to client design
        if self.game.phase == 'registration':
            return {'status': 'error', 'value': 'draw before defining order'}
        if self.game.phase == 'play':
            return {'status': 'error', 'value': 'game already started'}
        self.game.player_ready(pseudo,order)
        return {'status': 'ok', 'value': ''}

    def play(self, card, stack, *args, pseudo, **kwargs):
        try:
            card = int(card)
            stack = int(stack)
        except ValueError:
            return {
                'status': 'error',
                'value': 'invalid argument, format is "play card stack"',
            }
        if self.game.phase != 'play':
            return {'status': 'error', 'value': 'game not started'}
        if not self.game.check_stack(stack - 1):
            return {'status': 'error', 'value': 'invalid stack number ([1-4])'}
        if not self.game.check_card(card):
            return {'status': 'error', 'value': 'card %i not in hand' % card}
        move = Move(pseudo, card, stack - 1)
        if not self.game.check_move(move):
            return {'status': 'error', 'value': 'card %i not playable on stack %i' % (card, stack)}
        self.game.play(move)
        return {'status': 'ok', 'value': self.game.get_active().hand}


### MAIN
if __name__ == '__main__':
    api = API()

    context = zmq.Context()
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind('tcp://*:5555')
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:5556")

    print('Game started')

    while True:
        req = rep_socket.recv_json()
        print('Receive request:  %s' % req)
        resp = api.call(**req)
        rep_socket.send_json(resp)
        print('Send response: %s' % resp)
        notif = api.notify()
        if notif is not None:
            pub_socket.send_json(notif)
            print('Notify: %s' % notif)
        print()
