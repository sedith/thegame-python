import zmq
import json
from math import log10


class GameBoard:
    board = []
    hand = []

    def __init__(self, pseudo):
        self.pseudo = pseudo

    def display(self):
        print('')
        print('----------------------------------')
        print(
            'v',
            int(log10(self.board[0])) * ' ',
            ' v',
            int(log10(self.board[1])) * ' ',
            ' ʌ',
            int(log10(self.board[2])) * ' ',
            ' ʌ',
            sep='',
        )
        print(
            self.board[0], self.board[1], self.board[2], self.board[3],
        )
        print('')
        for i in range(len(self.hand)):
            print(self.hand[i], end=' ')
        print('\n')

    def end(score):
        print('----------------------------------')
        print('Final score :', score)
        if score == 0:
            print('Congratulations!! :D')
        else:
            print('Maybe next time ;)')
        exit(0)


### MAIN
if __name__ == '__main__':
    print('Welcome to ConoraTheGame ^o^')

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:5555')

    table = GameBoard(input('Whats your name? '))

    # Registration
    socket.send_json({'method': 'connect', 'pseudo': table.pseudo, 'args': []})
    resp = socket.recv_json()
    if resp['status'] == 'error':
        print('Oops. %s' % resp['value'])
        exit(1)
    else:
        print('You are in The Game!')
        print('Possible actions are : %s' % resp['value'])
        print('Input format: [action] [arg1] [arg2]')
        print('')

    while True:
        tokens = input('action : ').split()
        socket.send_json(
            {'pseudo': table.pseudo, 'method': tokens[0], 'args': tokens[1:] or []}
        )
        resp = socket.recv_json()
        if resp['status'] == 'error':
            print('Oops, %s' % resp['value'])
        elif tokens[0] in ['play', 'draw', 'start']:
            table.hand = resp['value'][0]
            table.board = resp['value'][1]
            table.display()
