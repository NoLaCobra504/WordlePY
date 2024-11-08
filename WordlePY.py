import os
import subprocess
import tkinter as tk
from tkinter import messagebox
import hashlib
import random
import datetime
import nltk
import ssl
from nltk.corpus import words

# Ensure NLTK words corpus is available
try:
    nltk.data.find('corpora/words.zip')
except LookupError:
    try:
        _create_default_https_context = ssl._create_default_https_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = ssl._create_unverified_context
    nltk.download('words')

# Game version
CURRENT_VERSION = "1.0.0"

# Function to check for updates
def check_for_update():
    # Run the updater script
    subprocess.Popen(['python3', 'updater.py'], close_fds=True)
    exit()  # Exit the current application

valid_words = {word.upper() for word in words.words() if len(word) == 5}
target_word = random.choice(list(valid_words))

class WordleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Game")
        
        # Start the update check
        check_for_update()

        self.attempts = 6
        self.current_attempt = 0
        self.guesses = []
        self.show_start_menu()

    def show_start_menu(self):
        """Display the start menu to choose options like New Game or Upload."""
        self.start_menu = tk.Toplevel(self.root)
        self.start_menu.title("Start Menu")
        
        tk.Label(self.start_menu, text="Select an option:", font=("Helvetica", 16)).pack(pady=10)

        new_game_button = tk.Button(self.start_menu, text="New Game", command=self.start_new_game, font=("Helvetica", 14))
        new_game_button.pack(pady=5)

        upload_button = tk.Button(self.start_menu, text="Upload", command=self.upload_game, font=("Helvetica", 14))
        upload_button.pack(pady=5)

    def start_new_game(self):
        """Start a new game."""
        self.start_menu.destroy()
        self.setup_game()

    def upload_game(self):
        """Upload game (or prepare to handle this action)."""
        self.start_menu.destroy()
        self.setup_game()

    def setup_game(self):
        """Set up the game UI (grid, entry, and controls)."""
        self.result_frame = tk.Frame(self.root)
        self.result_frame.pack(pady=20)

        self.result_labels = []
        for _ in range(self.attempts):
            row = tk.Frame(self.result_frame)
            row.pack()
            self.result_labels.append([tk.Label(row, text='', font=("Helvetica", 24), width=2, height=1, relief='solid') for _ in range(5)])
            for label in self.result_labels[-1]:
                label.pack(side='left', padx=5)

        self.entry = tk.Entry(self.root, font=("Helvetica", 24), justify='center', width=10)
        self.entry.pack(pady=20)

        self.submit_button = tk.Button(self.root, text="Submit", command=self.check_guess, font=("Helvetica", 16))
        self.submit_button.pack(pady=10)

        # Display Sender information (can be adjusted for upload or other features)
        self.sender_label = tk.Label(self.root, text="Sender: None", font=("Helvetica", 12))
        self.sender_label.pack(pady=5)

    def check_guess(self):
        """Validate and process the user's guess."""
        guess = self.entry.get().upper()

        if len(guess) != 5 or not guess.isalpha():
            messagebox.showwarning("Invalid Guess", "Please enter a valid 5-letter word.")
            return
        
        if guess not in valid_words:
            messagebox.showwarning("Invalid Word", "This word is not in the dictionary.")
            return
        
        # If we're at the 6th guess, it should not allow further guessing.
        if self.current_attempt >= self.attempts:
            return

        self.entry.delete(0, tk.END)
        self.guesses.append(self.process_guess(guess))

        if guess == target_word:
            self.end_game(won=True)
        elif self.current_attempt >= self.attempts - 1:
            self.end_game(won=False)
        else:
            self.current_attempt += 1

    def process_guess(self, guess):
        """Check the guess and update grid with colors (green, yellow, gray)."""
        result = ""
        for index, letter in enumerate(guess):
            label = self.result_labels[self.current_attempt][index]
            label['text'] = letter
            
            if letter == target_word[index]:
                label['bg'] = 'green'
                result += "🟩"
            elif letter in target_word:
                label['bg'] = 'yellow'
                result += "🟨"
            else:
                label['bg'] = 'gray'
                result += "⬛️"

        return result

    def end_game(self, won):
        """Display game over message."""
        message = "Congratulations! You've guessed the word!" if won else f"Game Over! The word was: {target_word}"
        messagebox.showinfo("Game Over", message)
        self.show_end_menu(won)

    def show_end_menu(self, won):
        """Display the end menu with options for a new game, saving, or quitting."""
        self.end_menu = tk.Toplevel(self.root)
        self.end_menu.title("Game Over")
        
        tk.Label(self.end_menu, text="Select an option:", font=("Helvetica", 16)).pack(pady=10)

        new_game_button = tk.Button(self.end_menu, text="New Game", command=self.new_game, font=("Helvetica", 14))
        new_game_button.pack(pady=5)

        save_game_button = tk.Button(self.end_menu, text="Save Game", command=lambda: self.save_game(won), font=("Helvetica", 14))
        save_game_button.pack(pady=5)

        quit_button = tk.Button(self.end_menu, text="Quit", command=self.root.quit, font=("Helvetica", 14))
        quit_button.pack(pady=5)

    def new_game(self):
        """Restart the game with a new word."""
        self.end_menu.destroy()
        self.guesses = []
        self.current_attempt = 0
        self.setup_game()

    def save_game(self, won):
        """Hash the guesses and target word and save the hash to a file."""
        
        colored_guesses = []

        # Collect the guesses
        for attempt in range(self.current_attempt + 1):
            guess = ""
            for index in range(5):
                label = self.result_labels[attempt][index]
                guess += label['text']  # The guessed letter

            # Append the guess and target word to the list (no feedback)
            colored_guesses.append(f"Guess: '{guess}' Target: '{target_word}'")

        # Combine all guesses and the target word into a single string
        combined_string = "\n".join(colored_guesses)

        # Hash the combined string using SHA-256
        hashed_string = hashlib.sha256(combined_string.encode()).hexdigest()

        # Get the current date and time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Create a filename using the current date and time
        filename = f"saved_game_{current_time}.txt"

        # Open the file for writing (this will create or overwrite the file)
        with open(filename, "w") as file:
            # Write only the hash string (not the original guesses)
            file.write(f"{hashed_string}")

        # Notify the user that the game has been saved
        messagebox.showinfo("Game Saved", f"Game saved! The hash has been written to {filename}")

# Tkinter root initialization
root = tk.Tk()
game = WordleGame(root)
root.mainloop()
