import tkinter as tk
import random
import winsound
import os
import webbrowser
from tkinter import simpledialog, messagebox, ttk
from collections import defaultdict
import pyttsx3  # Text-to-speech library

# Dictionary of quotes (English)
quotes = {
    "Courage": [
        "We, in our youth, dare to pursue our dreams, even facing hardship, we still believe in ourselves.",
        "Don't be afraid of failure, for every setback is a step towards success.",
        "Having a brave heart, youth is our greatest asset.",
        "Youth is the time to chase dreams; don't be afraid of failures."
    ],
    "Friendship": [
        "Treasure friendships, for they are the most beautiful memories of youth.",
        "A good friendship is like a precious gem, worth cherishing with all our heart.",
        "Friends from our youth often become our lifelong companions.",
        "Friendship is the foundation of happiness; treasure your friends."
    ],
    "Dreams": [
        "Youth is a poem, filled with courage and dreams, though time may gradually fade it.",
        "Even when life is tough, ideals can light the way forward.",
        "Every adventure in our youth is an exploration of the future.",
        "Dreams are the whispers of your soul; listen to them."
    ],
    "Love": [
        "Young love is like the rising sun, filled with hope and beauty.",
        "Even if we've been hurt, love is still worth pursuing.",
        "Love is the mark of youth, forever etched in our hearts.",
        "Love is the music of the heart; let it play."
    ],
    "Life": [
        "Life is not easy for everyone, but we must learn to enjoy every moment.",
        "Every challenge is an opportunity for growth.",
        "Young life is like a blank canvas, waiting for us to fill it.",
        "Life is a journey; embrace every twist and turn."
    ]
}

# User data
users = {}
user_quotes = defaultdict(list)  # User-generated quotes
quote_ratings = defaultdict(list)  # Quote ratings
quote_comments = defaultdict(list)  # Quote comments
custom_quotes = []  # Custom quotes
achievements = defaultdict(list)  # User achievements
colors = ["#FFB6C1", "#87CEEB", "#98FB98", "#FFD700", "#FF69B4", "#DDA0DD", "#FF6347"]
moods = ["Happy", "Sad", "Anxious", "Excited", "Calm"]

# Text-to-speech initialization
engine = pyttsx3.init()

# Create main window
root = tk.Tk()
root.title("Youthful Quote Generator")
root.geometry("600x600")

# Create quote type selection dropdown menu
quote_type_var = tk.StringVar(value="Courage")
quote_type_menu = tk.OptionMenu(root, quote_type_var, *quotes.keys())
quote_type_menu.config(font=("Arial", 12))
quote_type_menu.pack(pady=10)

# User registration and login
def register():
    username = simpledialog.askstring("Register", "Please enter your username:")
    if username:
        if username not in users:
            users[username] = True  # Register user
            messagebox.showinfo("Success", "Registration successful! Please log in.")
        else:
            messagebox.showerror("Error", "Username already exists!")

def login():
    username = simpledialog.askstring("Log In", "Please enter your username:")
    if username:
        if username in users:
            current_user.set(username)
            messagebox.showinfo("Success", f"Log in successful, welcome {username}!")
        else:
            messagebox.showerror("Error", "Username does not exist!")

# Current user
current_user = tk.StringVar(value="Not logged in")

# Define function to display quotes
def show_quote():
    loading_label.config(text="Loading...")
    root.update()

    # Randomly select a quote
    quote_list = quotes[quote_type_var.get()] + custom_quotes
    quote = random.choice(quote_list)

    # Sound effect
    winsound.Beep(1000, 500)

    # Update the quote and background color
    quote_label.config(text=quote)
    new_color = random.choice(colors)
    root.config(bg=new_color)
    quote_label.config(bg=new_color)

    # Text-to-speech for the quote
    engine.say(quote)
    engine.runAndWait()

    # Record history
    if current_user.get() != "Not logged in":
        user_quotes[current_user.get()].append(quote)

    loading_label.config(text="")

# Define function to rate quotes
def rate_quote():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first!")
        return

    quote = quote_label.cget("text")
    if quote:
        rating = simpledialog.askinteger("Rate", "Please rate this quote (1-5):", minvalue=1, maxvalue=5)
        if rating:
            quote_ratings[quote].append((current_user.get(), rating))
            messagebox.showinfo("Success", "Rating successful!")
    else:
        messagebox.showwarning("Warning", "Please generate a quote first!")

# Define function to comment on quotes
def comment_quote():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first!")
        return

    quote = quote_label.cget("text")
    if quote:
        comment = simpledialog.askstring("Comment", "Please comment on this quote:")
        if comment:
            quote_comments[quote].append((current_user.get(), comment))
            messagebox.showinfo("Success", "Comment successful!")
    else:
        messagebox.showwarning("Warning", "Please generate a quote first!")

# Define function to add custom quotes
def add_custom_quote():
    custom_quote = simpledialog.askstring("Add Quote", "Please enter your custom quote:")
    if custom_quote:
        custom_quotes.append(custom_quote)
        messagebox.showinfo("Success", "Custom quote added successfully!")

# Define function to recommend quotes
def recommend_quote():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first!")
        return

    if quote_ratings:
        recommended_quote = random.choice(list(quote_ratings.keys()))
        quote_label.config(text=f"Recommended Quote: {recommended_quote}")
    else:
        messagebox.showwarning("Warning", "No rating records yet, unable to recommend a quote!")

# Define function to share quotes
def share_quote():
    quote = quote_label.cget("text")
    if quote:
        webbrowser.open(f"https://www.facebook.com/sharer/sharer.php?u={quote}")
        messagebox.showinfo("Share", "Quote shared to Facebook!")
    else:
        messagebox.showwarning("Warning", "Please generate a quote first!")

# Define function to display user data page
def show_user_data():
    if current_user.get() == "Not logged in":
        messagebox.showerror("Error", "Please log in first!")
        return

    user_data_window = tk.Toplevel(root)
    user_data_window.title(f"{current_user.get()}'s Data")
    user_data_window.geometry("400x300")

    # Display generation history
    history_label = tk.Label(user_data_window, text="Generated Quotes:", font=("Arial", 12))
    history_label.pack(pady=5)
    history_text = "\n".join(user_quotes[current_user.get()])
    history_listbox = tk.Listbox(user_data_window, width=40, height=5)
    history_listbox.insert(tk.END, *history_text.split("\n"))
    history_listbox.pack(pady=5)

    # Display achievements
    achievements_label = tk.Label(user_data_window, text="Unlocked Achievements:", font=("Arial", 12))
    achievements_label.pack(pady=5)
    achievements_listbox = tk.Listbox(user_data_window, width=40, height=5)
    achievements_listbox.insert(tk.END, *achievements[current_user.get()])
    achievements_listbox.pack(pady=5)

# Define function to generate quotes based on mood
def show_mood_quote():
    selected_mood = mood_var.get()
    if selected_mood:
        # Use a simple dictionary to map mood and quotes
        mood_quotes = {
            "Happy": ["Life is short, enjoy every moment!", "Let's embrace happiness!", "Happiness is most important!", "Life is short, enjoy every moment! Let's embrace happiness!"],
            "Sad": ["When you're sad, remember to give yourself some time.", "Sadness is part of life, learn to accept it.", "Don't be afraid to feel sad, it's part of life.", "It's okay to be sad, give yourself time to heal."],
            "Anxious": ["Don't let anxiety control you, take a deep breath, everything will be okay.", "Anxiety is not scary, the key is to find solutions.", "Don't let anxiety control you, take a deep breath, everything will be okay.", "Anxiety is not scary, the key is to find solutions."],
            "Excited": ["Be passionate and go for it!", "Pursue your dreams with passion and make them a reality!", "Be passionate and go for it!", "Pursue your dreams with passion and make them a reality."],
            "Calm": ["A peaceful mind is the source of happiness.", "Learn to observe calmly and experience true peace.", "A peaceful mind is the source of happiness.", "Learn to observe calmly and experience true peace."]
        }
        if selected_mood in mood_quotes:
            quote = random.choice(mood_quotes[selected_mood])
            quote_label.config(text=quote)
        else:
            messagebox.showwarning("Warning", "This mood category is not supported yet!")

# Create the label to display the quote
quote_label = tk.Label(root, text="", wraplength=500, font=("Arial", 16), bg=root.cget("bg"))
quote_label.pack(pady=20)

# Create the "Loading..." label
loading_label = tk.Label(root, text="", font=("Arial", 12))
loading_label.pack()

# Create buttons
generate_button = tk.Button(root, text="Generate Quote", command=show_quote, font=("Arial", 12))
generate_button.pack(pady=10)

# Create share button
share_button = tk.Button(root, text="Share Quote", command=share_quote, font=("Arial", 12))
share_button.pack(pady=10)

# Create register and login buttons
register_button = tk.Button(root, text="Register", command=register, font=("Arial", 12))
register_button.pack(pady=10)

login_button = tk.Button(root, text="Log In", command=login, font=("Arial", 12))
login_button.pack(pady=10)

# Create rate quote button
rate_button = tk.Button(root, text="Rate Quote", command=rate_quote, font=("Arial", 12))
rate_button.pack(pady=10)

# Create comment quote button
comment_button = tk.Button(root, text="Comment on Quote", command=comment_quote, font=("Arial", 12))
comment_button.pack(pady=10)

# Create add custom quote button
add_custom_button = tk.Button(root, text="Add Custom Quote", command=add_custom_quote, font=("Arial", 12))
add_custom_button.pack(pady=10)

# Create recommend quote button
recommend_button = tk.Button(root, text="Recommend Quote", command=recommend_quote, font=("Arial", 12))
recommend_button.pack(pady=10)

# Create show user data button
user_data_button = tk.Button(root, text="View Profile", command=show_user_data, font=("Arial", 12))
user_data_button.pack(pady=10)

# Create mood selection dropdown menu
mood_var = tk.StringVar(value="")
mood_label = tk.Label(root, text="Select Mood:", font=("Arial", 12))
mood_label.pack(pady=5)
mood_combobox = ttk.Combobox(root, textvariable=mood_var, values=moods)
mood_combobox.pack(pady=5)
mood_button = tk.Button(root, text="Generate Quote", command=show_mood_quote, font=("Arial", 12))
mood_button.pack(pady=5)

# Create exit button
exit_button = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12))
exit_button.pack(pady=10)

# Start the main loop
root.mainloop()