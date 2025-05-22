"""
Final Project

Python GUI Blackjack Game

This is a graphical user interface (GUI) implementation of the classic card game Blackjack, written in Python using the Tkinter library.
It includes basic game play as well as double down and split features using object-oriented programming (OOP) principles. The game uses
card images provided in the "Images" folder.

Created by Cody Pimentel for CS202-1001, Truckee Meadows Community College 
Date: 7 May 2023

"""

import os
import tkinter as tk
from tkinter import messagebox
import random
import pickle

# Get the absolute directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARD_DIR = os.path.join(BASE_DIR, "card1")

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = self._get_value()

    def _get_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

class Deck:
    def __init__(self):
        self.cards = [Card(s, r) for s in ["S", "C", "H", "D"] for r in ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]]
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        self.value += card.value
        if card.rank == 'A':
            self.aces += 1
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

class Player:
    def __init__(self, name, bankroll):
        self.name = name
        self.hand = Hand()
        self.bankroll = bankroll
        self.bet = 0
        
    def place_bet(self, bet):
        if bet > self.bankroll:
            return False
        else:
            self.bankroll -= bet
            self.bet = bet
            return True
    
    def win_bet(self):
        self.bankroll += 2 * self.bet
        self.bet = 0
        
    def push_bet(self):
        self.bankroll += self.bet
        self.bet = 0

    def hit(self, deck):
        self.hand.add_card(deck.draw_card())

    def double_down(self, deck):
        self.hit(deck)
        self.stand()

    def split(self, deck):
        if len(self.hand.cards) == 2 and self.hand.cards[0].value == self.hand.cards[1].value:
            new_hand = Hand()
            new_hand.add_card(self.hand.cards.pop())
            self.hand.value = self.hand.cards[0].value
            new_hand.add_card(deck.draw_card())
            self.hand.add_card(deck.draw_card())
            return new_hand

class Blackjack:
    def __init__(self, bankroll):
        self.deck = Deck()
        self.player = Player('Player', bankroll)
        self.dealer = Player('Dealer', float('inf'))
        self.player.hit(self.deck)
        self.dealer.hit(self.deck)
        self.player.hit(self.deck)
        self.dealer.hit(self.deck)

    def play(self):
        while True:
            # Player turn
            player_choice = messagebox.askquestion("Hit or Stand?", "Do you want to hit?")
            if player_choice == 'yes':
                self.player.hit(self.deck)
                self.player_hand_value = self.player.hand.value
                if self.player_hand_value > 21:
                    self.dealer_wins()
                    self.player.push_bet()
                    break
                elif self.player_hand_value == 21:
                    break
            else:
                break

        if self.player_hand_value == 21:
            self.player_wins()
            self.player.win_bet()
        else:
            # Dealer turn
            while self.dealer.hand.value < 17:
                self.dealer.hit(self.deck)
                self.dealer_hand_value = self.dealer.hand.value
                if self.dealer_hand_value > 21:
                    self.player_wins()
                    self.player.win_bet()
                    break

            if self.dealer_hand_value <= 21 and self.dealer_hand_value >= self.player_hand_value:
                self.dealer_wins()
                self.player.push_bet()
            elif self.dealer_hand_value < self.player_hand_value:
                self.player_wins()
                self.player.win_bet()
            else:
                self.push()
                self.player.push_bet()
    
            self.update_bankroll_label()
            return self.player.bankroll

    def player_wins(self):
        self.player.bankroll += 2 * self.player.bet
        print("Player wins!")
        messagebox.showinfo("Result", "You win!")
        
    def dealer_wins(self):
        print("Dealer wins!")
        messagebox.showinfo("Result", "Dealer wins!")

    def push(self):
        self.player.bankroll += self.player.bet
        print("Push!")
        messagebox.showinfo("Result", "Push!")

class BlackjackGUI(tk.Tk):
    def __init__(self):

        self.dealer_hand_ids = []
        self.player_hand_images = []
        self.dealer_hand_images = []
        
        super().__init__()
        self.title('Blackjack')
        self.geometry('800x600')
        self.resizable(False, False)

        self.canvas = tk.Canvas(self, width=800, height=600)
        self.canvas.pack()

        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        self.game_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label='Game', menu=self.game_menu)
        self.game_menu.add_command(label='New Game', command=self.start_game)
        self.game_menu.add_command(label='Exit', command=self.quit)
        self.game_menu.add_command(label='Save Game', command=self.save_game)

        self.help_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label='Help', menu=self.help_menu)
        self.help_menu.add_command(label='Rules', command=self.show_rules)
        self.help_menu.add_command(label='About', command=self.show_about)

        self.start_button = tk.Button(self, text='Start Game', command=self.start_game)
        self.canvas.create_window(400, 300, window=self.start_button)

        self.player_bankroll = 1000
        self.player_bet = 0

        self.player_bankroll_label = tk.Label(self.canvas, text='Bankroll: $' + str(self.player_bankroll))
        self.player_bankroll_label.place(relx=0.01, rely=0.95)

        self.bet_label = tk.Label(self.canvas, text='Bet: $' + str(self.player_bet))
        self.bet_label.place(relx=0.8, rely=0.95)

        self.bet_entry = tk.Entry(self.canvas)
        self.canvas.create_window(400, 500, window=self.bet_entry)

        self.bet_button = tk.Button(self.canvas, text='Place Bet', command=self.place_bet)
        self.canvas.create_window(400, 550, window=self.bet_button)

        self.mainloop()

    def place_bet(self):
        try:
            bet_bet = int(self.bet_entry.get())
            if bet_bet > 0 and bet_bet <= self.player_bankroll:
                self.player_bet = bet_bet
                self.update_bankroll(-bet_bet)
                self.bet_label.config(text='Bet: $' + str(self.player_bet))
        except ValueError:
            pass

    def start_game(self):
        self.blackjack = Blackjack(self.player_bankroll)
        self.canvas.delete('all')
        self.canvas.create_text(400, 50, text=f"{self.blackjack.player.name}'s Hand", font=('Arial', 16))
        self.canvas.create_text(400, 350, text=f"{self.blackjack.dealer.name}'s Hand", font=('Arial', 16))

        self.player_hand_images = []
        self.player_hand_value = self.blackjack.player.hand.value
        for i, card in enumerate(self.blackjack.player.hand.cards):
            img_path = os.path.join(CARD_DIR, f"{card.suit}{card.rank}.png")
            img = tk.PhotoImage(file=img_path).subsample(2, 2)
            self.player_hand_images.append(img)
            self.canvas.create_image(100 + i * 70, 200, image=img)

        self.dealer_hand_images = []
        self.dealer_hand_value = self.blackjack.dealer.hand.value
        for i, card in enumerate(self.blackjack.dealer.hand.cards):
            if i == 0:
                # First card is face up
                img_path = os.path.join(CARD_DIR, f"{card.suit}{card.rank}.png")
            else:
                # Second card is face down (use a back-of-card image)
                img_path = os.path.join(CARD_DIR, "back.png")  # Use your own back-of-card image here

            img = tk.PhotoImage(file=img_path).subsample(2, 2)
            self.dealer_hand_images.append(img)
            image_id = self.canvas.create_image(100 + i * 70, 450, image=img)
            self.dealer_hand_ids.append(image_id)

        self.player_value_text = self.canvas.create_text(400, 250, text=f"Value: {self.player_hand_value}", font=('Arial', 16))
        self.dealer_value_text = self.canvas.create_text(400, 500, text=f"Value: {self.dealer_hand_value}", font=('Arial', 16))

        self.hit_button = tk.Button(self, text='Hit', command=self.hit)
        self.canvas.create_window(200, 550, window=self.hit_button)
        self.stand_button = tk.Button(self, text='Stand', command=self.stand)
        self.canvas.create_window(300, 550, window=self.stand_button)
        self.double_down_button = tk.Button(self, text='Double Down', command=self.double_down)
        self.canvas.create_window(400, 550, window=self.double_down_button)
        self.split_button = tk.Button(self, text='Split', command=self.split)
        self.canvas.create_window(500, 550, window=self.split_button)

    def show_dealer_hand(self):
        # Reveal all of the dealer's cards
        for i, card in enumerate(self.blackjack.dealer.hand.cards):
            img_path = os.path.join(CARD_DIR, f"{card.suit}{card.rank}.png")
            img = tk.PhotoImage(file=img_path).subsample(2, 2)
            self.dealer_hand_images[i] = img  # Replace the back with the actual image
            self.canvas.itemconfig(self.dealer_hand_ids[i], image=img)
        
        # Update the dealer's hand value
        self.dealer_hand_value = self.blackjack.dealer.hand.value
        self.canvas.itemconfig(self.dealer_value_text, text=f"Value: {self.dealer_hand_value}")

    def hit(self):
        self.blackjack.player.hit(self.blackjack.deck)
        self.player_hand_value = self.blackjack.player.hand.value
        
        # Display the new card in the player's hand
        card = self.blackjack.player.hand.cards[-1]
        img_path = os.path.join(CARD_DIR, f"{card.suit}{card.rank}.png")
        img = tk.PhotoImage(file=img_path).subsample(2, 2)
        self.player_hand_images.append(img)
        self.canvas.create_image(50 + len(self.player_hand_images) * 60, 200, image=img)
        self.canvas.itemconfig(self.player_value_text, text=f"Value: {self.player_hand_value}")
        
        # Check if the player busts or wins
        if self.player_hand_value > 21:
            self.blackjack.dealer_wins()
            self.show_dealer_hand()
            self.hit_button.config(state='disabled')
            self.stand_button.config(state='disabled')
        elif self.player_hand_value == 21:
            self.stand()
            self.hit_button.config(state='disabled')
            self.stand_button.config(state='disabled')

    def stand(self):
        # Reveal the dealer's first card
        first_card = self.blackjack.dealer.hand.cards[0]
        img_path = os.path.join(CARD_DIR, f"{first_card.suit}{first_card.rank}.png")
        img = tk.PhotoImage(file=img_path).subsample(2, 2)
        self.dealer_hand_images[0] = img
        self.canvas.create_image(100, 450, image=img)

        # Draw cards until the dealer's hand value is at least 17
        while self.blackjack.dealer.hand.value < 17:
            self.blackjack.dealer.hit(self.blackjack.deck)
            self.dealer_hand_value = self.blackjack.dealer.hand.value
            card = self.blackjack.dealer.hand.cards[-1]
            img_path = os.path.join(CARD_DIR, f"{card.suit}{card.rank}.png")
            img = tk.PhotoImage(file=img_path).subsample(2, 2)
            self.dealer_hand_images.append(img)
            self.canvas.create_image(50 + len(self.dealer_hand_images) * 60, 450, image=img)

        # Determine the winner
        if self.blackjack.dealer.hand.value > 21:
            self.blackjack.player_wins()
        elif self.blackjack.dealer.hand.value == self.player_hand_value:
            self.blackjack.push()
        elif self.blackjack.dealer.hand.value > self.player_hand_value:
            self.blackjack.dealer_wins()
        else:
            self.blackjack.player_wins()

        self.hit_button.config(state='disabled')
        self.stand_button.config(state='disabled')
        self.show_dealer_hand()

    def double_down(self):
        pass  # implement double down logic here

    def split(self):
        pass  # implement split logic here

    def update_player_hand(self):
        self.canvas.delete(self.player_value_text)
        self.player_hand_value = self.blackjack.player.hand.value
        for i, card in enumerate(self.blackjack.player.hand.cards):
            img_path = os.path.join(CARD_DIR, f"{card.suit}{card.rank}.png")
            img = tk.PhotoImage(file=img_path).subsample(2, 2)
            self.player_hand_images.append(img)  # Keep reference alive
            self.canvas.create_image(100 + i * 70, 200, image=img)

        for i, card in enumerate(self.blackjack.dealer.hand.cards):
            img_path = os.path.join(CARD_DIR, f"{card.suit}{card.rank}.png")
            img = tk.PhotoImage(file=img_path).subsample(2, 2)
            self.dealer_hand_images.append(img)  # Keep reference alive

            # If first card is to be shown face down
            if i == 0:
                hidden_img = tk.PhotoImage(file=os.path.join(CARD_DIR, 'back.png')).subsample(2, 2)
                self.dealer_hand_images.append(hidden_img)  # Keep reference
                self.canvas.create_image(100 + i * 70, 450, image=hidden_img)
            else:
                self.canvas.create_image(100 + i * 70, 450, image=img)

    def update_bankroll(self, bet):
        self.player_bankroll += bet
        self.player_bankroll_label.config(text='Bankroll: $' + str(self.player_bankroll))

    def show_rules(self):
        messagebox.showinfo('Rules', 'The goal of blackjack is to beat the dealer by having a hand value of 21 or as close to 21 as possible without going over. Face cards are worth 10, Aces are worth 1 or 11, and all other cards are worth their face value.')

    def show_about(self):
        messagebox.showinfo('About', 'This game was created by Cody Pimentel using Python and Tkinter.')
    
    def save_game(self):
        game_state = {
            'player': self.blackjack.player,
            'dealer': self.blackjack.dealer,
            'deck': self.blackjack.deck,
        }
        with open('blackjack.sav', 'wb') as f:
            pickle.dump(game_state, f)

if __name__ == '__main__':
    app = BlackjackGUI()