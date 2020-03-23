import zmq
from random import shuffle


class Player:
    hand = []

    def __init__(self, pseudo):
        self.pseudo = pseudo


class Move:
    def __init__(self, pseudo, card, stack):
        self.pseudo = pseudo
        self.card = card
        self.stack = stack


class TheGame:
    # Initialization
    players = []
    history = []
    active = -1

    def __init__(self):
        self.deck = list(range(2, 100))
        shuffle(self.deck)
        self.stacks = [[100], [100], [1], [1]]

    # Getters
    def get_board(self):
        return [s[-1] for s in self.stacks]

    def nb_cards(self):
        if len(self.players) == 1:
            return 8
        elif len(self.players) == 2:
            return 7
        else:
            return 6

    def n_to_play(self):
        return 2 if self.remain() else 1

    def n_card_played(self):
        return self.nb_cards() - len(self.active().hand)

    def get_active(self):
        return self.players[self.active]

    def find_player(self, pseudo):
        return self.get_pseudos().index(pseudo)

    def get_player(self, pseudo):
        return self.players[self.find_player(pseudo)]

    def get_pseudos(self):
        return [p.pseudo for p in self.players]

    def remain(self):
        return len(self.deck) > 0

    def finished(self):
        return not self.remain() and not any(p.hand for p in self.players)

    # Checks
    def check_player(self, pseudo):
        return pseudo in self.get_pseudos()

    def check_active(self, pseudo):
        return pseudo == self.get_active().pseudo

    def check_card(self, card):
        return card in self.get_active().hand

    def check_stack(self, stack):
        return 0 <= stack < 4

    def check_started(self):
        return self.active != -1

    def check_playable(self, move):
        prev_card = self.stacks[move.stack][-1]
        if move.stack < 2:
            return prev_card > move.card or prev_card + 10 == move.card
        else:
            return prev_card < move.card or prev_card - 10 == move.card

    def check_stuck(self):
        struck = self.n_card_played() < self.n_to_play()
        for c in self.get_active().hand:
            for s in range(1, 5):
                if self.check_playable(Move('', c, s)):
                    struck = False
                    break
        return stuck

    # Register
    def register(self, pseudo):
        self.players.append(Player(pseudo))

    # History
    def restore(self):
        last_move = self.history.pop()
        self.get_active().hand.append(self.stacks[last_move.stack].pop())

    # Game
    def start(self, pseudo):
        for p in self.get_pseudos():
            self.draw(p)
            self.get_player(p).hand.sort()
        self.active = self.find_player(pseudo)

    def draw(self, pseudo):
        print(pseudo)
        p = self.get_player(pseudo)
        print(p.hand)
        print(self.remain())
        p.hand.sort()
        n = self.nb_cards()
        while self.remain() and len(p.hand) < n:
            p.hand.append(self.deck.pop())
        return p.hand

    def play(self, move):
        self.get_active().hand.remove(move.card)
        self.stacks[move.stack].append(move.card)
        self.history.append(move)
        return self.get_active().hand

    def end_turn(self):
        self.draw(self.get_active().pseudo)
        self.active = (self.active + 1) % len(self.players)
        return self.get_active().pseudo

    def score(self):
        return sum(len(p.hand) for p in self.players) + len(self.deck())


class API:
    '''
    ALLOWED ACTIONS
    * connect(pseudo)
    * start
    * controls
    * play(card,stack)
    * draw
    #    * who
    #    * expand(stack)
    #    * undo
    #    * valid_moves
    '''

    game = TheGame()

    def call(self, pseudo, method, args):
        try:
            return getattr(self, method)(pseudo=pseudo, *args)
        except:
            return {'status': 'error', 'value': 'invalid request'}

    def connect(self, *args, pseudo, **kwargs):
        if self.game.check_started():
            return {'status': 'error', 'value': 'game already started'}
        if self.game.check_player(pseudo):
            return {'status': 'error', 'value': 'player already registered'}
        else:
            self.game.register(pseudo)
            return {'status': 'ok', 'value': self.controls()['value']}

    def start(self, pseudo, *args, **kwargs):
        if self.game.check_started():
            return {'status': 'error', 'value': 'game already started'}
        if not self.game.check_player(pseudo):
            return {'status': 'error', 'value': 'player not registered'}
        else:
            self.game.start(pseudo)
            return {
                'status': 'ok',
                'value': (self.game.get_active().hand, self.game.get_board()),
            }

    def controls(self, *args, **kwargs):
        return {
            'status': 'ok',
            'value': 'controls, start, play(card[2-98],stack[1-4]), draw',
        }

    def play(self, card, stack, *args, pseudo, **kwargs):
        try:
            card = int(card)
            stack = int(stack)
        except:
            return {
                'status': 'error',
                'value': 'invalid arguement for method play (format is "play card stack", card and stack are integers)',
            }
        if not self.game.check_started():
            return {'status': 'error', 'value': 'game not started'}
        if not self.game.check_player(pseudo):
            return {'status': 'error', 'value': 'player not registered'}
        if not self.game.check_active(pseudo):
            return {'status': 'error', 'value': 'player not active'}
        if not self.game.check_card(card):
            return {'status': 'error', 'value': 'card %i not in hand' % card}
        if not self.game.check_stack(stack - 1):
            return {'status': 'error', 'value': 'invalid stack %i' % stack}
        move = Move(pseudo, card, stack - 1)
        if not self.game.check_playable(move):
            return {'status': 'error', 'value': 'card not playable'}
        return {'status': 'ok', 'value': (self.game.play(move), self.game.get_board())}

    def draw(self, *args, pseudo, **kwargs):
        if not self.game.check_started():
            return {'status': 'error', 'value': 'game not started'}
        if not self.game.check_player(pseudo):
            return {'status': 'error', 'value': 'player not registered'}
        if not self.game.check_active(pseudo):
            return {'status': 'error', 'value': 'player not active'}
        return {
            'status': 'ok',
            'value': (self.game.draw(pseudo), self.game.get_board()),
        }


### MAIN
if __name__ == '__main__':
    api = API()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://*:5555')

    print('Game started')

    while True:
        req = socket.recv_json()
        print('Got request:  %s' % req)
        resp = api.call(**req)
        socket.send_json(resp)
        print('Sending response: %s\n' % resp)
