import tkinter as tk
import random
import winsound
import os
import webbrowser
from tkinter import simpledialog, messagebox, ttk, scrolledtext
from collections import defaultdict
import pyttsx3  # Text-to-speech library
import json  # For saving and loading user data

# Dictionary of quotes (English)
quotes = {
    "Courage": [
        "We, in our youth, dare to pursue our dreams, even facing hardship, we still believe in ourselves.",
        "Don't be afraid of failure, for every setback is a step towards success.",
        "Having a brave heart, youth is our greatest asset.",
        "Youth is the time to chase dreams; don't be afraid of failures.",
        "The greatest courage is to be yourself in a world that wants you to be someone else.",
        "Face your fears with determination, for that's how heroes are made.",
        "Courage isn't about being fearless, it's about facing life despite your fears.",
        "Every brave attempt is an opportunity for growth.",
        "True courage comes from perseverance in the face of difficulties."
    ],
    "Friendship": [
        "Treasure friendships, for they are the most beautiful memories of youth.",
        "A good friendship is like a precious gem, worth cherishing with all our heart.",
        "Friends from our youth often become our lifelong companions.",
        "Friendship is the foundation of happiness; treasure your friends.",
        "True friends are like stars; you don't always see them, but you know they're always there.",
        "Friendship is about finding people who understand your weirdness.",
        "Friends are the family we choose for ourselves.",
        "Sincere friendship is youth's most beautiful gift.",
        "Understanding between friends is a resonance of souls."
    ],
    "Dreams": [
        "Youth is a poem, filled with courage and dreams, though time may gradually fade it.",
        "Even when life is tough, ideals can light the way forward.",
        "Every adventure in our youth is an exploration of the future.",
        "Dreams are the whispers of your soul; listen to them.",
        "Your dreams are the blueprints of your destiny.",
        "Chase your dreams until you catch them.",
        "Dreams are today's answers to tomorrow's questions.",
        "Dreams are the compass of the soul, guiding our direction forward.",
        "The pursuit of dreams is a journey of self-realization."
    ],
    "Love": [
        "Young love is like the rising sun, filled with hope and beauty.",
        "Even if we've been hurt, love is still worth pursuing.",
        "Love is the mark of youth, forever etched in our hearts.",
        "Love is the music of the heart; let it play.",
        "Love is not about finding the perfect person, but seeing an imperfect person perfectly.",
        "True love stories never have endings.",
        "Love is the poetry of the senses.",
        "Love is the most beautiful scenery of youth.",
        "True love needs no words, only sincerity."
    ],
    "Life": [
        "Life is not easy for everyone, but we must learn to enjoy every moment.",
        "Every challenge is an opportunity for growth.",
        "Young life is like a blank canvas, waiting for us to fill it.",
        "Life is a journey; embrace every twist and turn.",
        "Life is short, but it's wide enough to hold all your dreams.",
        "Every day is a new page in your life's story.",
        "Life is about creating yourself, not finding yourself.",
        "Life is like a song, let us sing our own melody.",
        "Life is like an adventure, full of surprises and challenges."
    ],
    "Growth": [
        "Every challenge you face is an opportunity for growth.",
        "Growth is painful, change is painful, but nothing is as painful as staying stuck.",
        "The only way to grow is to step out of your comfort zone."
    ],
    "Wisdom": [
        "Knowledge comes from learning, wisdom comes from living.",
        "The greatest wisdom is knowing you have more to learn.",
        "Wisdom is not about knowing everything, but understanding what matters."
    ],
    "Success": [
        "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "The road to success is always under construction.",
        "Success is walking from failure to failure with no loss of enthusiasm."
    ],
    "Happiness": [
        "Happiness is not something ready made. It comes from your own actions.",
        "The greatest happiness comes from the smallest moments.",
        "Choose happiness, choose to smile, choose to shine."
    ],
    "Inspiration": [
        "Inspiration exists, but it has to find you working.",
        "Let your light shine so bright that others can see their way out of the dark.",
        "Be the inspiration you wish to see in the world."
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

# Load user data from file
def load_user_data():
    global users, user_quotes, quote_ratings, quote_comments, custom_quotes, achievements
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r") as file:
            data = json.load(file)
            users = data.get("users", {})
            user_quotes = defaultdict(list, data.get("user_quotes", {}))
            quote_ratings = defaultdict(list, data.get("quote_ratings", {}))
            quote_comments = defaultdict(list, data.get("quote_comments", {}))
            custom_quotes = data.get("custom_quotes", [])
            achievements = defaultdict(list, data.get("achievements", {}))

# Save user data to file
def save_user_data():
    data = {
        "users": users,
        "user_quotes": dict(user_quotes),
        "quote_ratings": dict(quote_ratings),
        "quote_comments": dict(quote_comments),
        "custom_quotes": custom_quotes,
        "achievements": dict(achievements)
    }
    with open("user_data.json", "w") as file:
        json.dump(data, file)

# Create main window
root = tk.Tk()
root.title("Youthful Quote Generator")
root.geometry("600x600")

# 移動 mood_var 的宣告至 root 初始化之後
mood_var = tk.StringVar(value=moods[0])

# 更新主題配色方案，使用更現代的配色
themes = {
    "Modern Light": {
        "bg": "#FFFFFF",
        "fg": "#2C3E50",
        "button_bg": "#ECF0F1",
        "accent": "#3498DB",
        "hover": "#2980B9",
        "card_bg": "#F8F9FA",
        "border": "#E9ECEF"
    },
    "Modern Dark": {
        "bg": "#1A1A1A",
        "fg": "#FFFFFF",
        "button_bg": "#2D2D2D",
        "accent": "#6C5CE7",
        "hover": "#5B4BC5",
        "card_bg": "#2D2D2D",
        "border": "#3D3D3D"
    },
    "Pastel": {
        "bg": "#FFF5F5",
        "fg": "#2D3436",
        "button_bg": "#FFE8E8",
        "accent": "#FF9999",
        "hover": "#FF7777",
        "card_bg": "#FFFFFF",
        "border": "#FFD1D1"
    }
}

style = ttk.Style()
current_theme = tk.StringVar(value="Light")

# 加入表情符號到按鈕文字
EMOJIS = {
    "generate": "✨",
    "share": "📤",
    "rate": "⭐",
    "register": "📝",
    "login": "🔑",
    "profile": "👤",
    "mood": "🎭",
    "voice": "🎙️",
    "search": "🔍",
    "comment": "💭",
    "custom": "✏️",
    "recommend": "🎯",
    "exit": "👋"
}

# 更新按鈕樣式
def configure_button_style():
    style.configure(
        "Custom.TButton",
        padding=(20, 12),
        relief="flat",
        background=themes[current_theme.get()]["button_bg"],
        foreground=themes[current_theme.get()]["fg"],
        font=("Segoe UI", 11),
        borderwidth=0,
        focuscolor=themes[current_theme.get()]["accent"]
    )
    
    # 新增懸停效果
    style.map("Custom.TButton",
        background=[("active", themes[current_theme.get()]["hover"])],
        foreground=[("active", "#FFFFFF")]
    )
    
    # 新增圓角卡片樣式
    style.configure(
        "Card.TFrame",
        background=themes[current_theme.get()]["card_bg"],
        relief="solid",
        borderwidth=1,
        bordercolor=themes[current_theme.get()]["border"]
    )
    
    # 更新下拉選單樣式
    style.configure(
        "TCombobox",
        background=themes[current_theme.get()]["button_bg"],
        fieldbackground=themes[current_theme.get()]["bg"],
        foreground=themes[current_theme.get()]["fg"],
        arrowcolor=themes[current_theme.get()]["accent"]
    )

# 更新主視窗設定
root.configure(bg=themes["Modern Light"]["bg"])
root.option_add('*TCombobox*Listbox.background', themes["Modern Light"]["bg"])
root.option_add('*TCombobox*Listbox.foreground', themes["Modern Light"]["fg"])

def change_theme():
    theme = current_theme.get()
    theme_colors = themes[theme]
    root.config(bg=theme_colors["bg"])
    configure_button_style()
    
    # 更新所有部件顏色
    for widget in root.winfo_children():
        update_widget_colors(widget, theme_colors)

def update_widget_colors(widget, colors):
    if isinstance(widget, (tk.Label, tk.Frame)):
        widget.configure(bg=colors["bg"], fg=colors["fg"])
    elif isinstance(widget, scrolledtext.ScrolledText):
        widget.configure(bg=colors["button_bg"], fg=colors["fg"])
    
    # 遞迴更新子部件
    for child in widget.winfo_children():
        update_widget_colors(child, colors)

# Add voice settings
def configure_voice():
    voice_window = tk.Toplevel(root)
    voice_window.title("Voice Settings")
    voice_window.geometry("300x200")
    
    # Speed adjustment
    speed_scale = ttk.Scale(voice_window, from_=0, to=200, orient="horizontal")
    speed_scale.set(engine.getProperty('rate'))
    speed_scale.pack(pady=10)
    
    # Volume adjustment
    volume_scale = ttk.Scale(voice_window, from_=0, to=1, orient="horizontal")
    volume_scale.set(engine.getProperty('volume'))
    volume_scale.pack(pady=10)
    
    def apply_settings():
        engine.setProperty('rate', speed_scale.get())
        engine.setProperty('volume', volume_scale.get())
        voice_window.destroy()
    
    ttk.Button(voice_window, text="Apply", command=apply_settings).pack(pady=10)

# Add search functionality
def search_quotes():
    search_term = simpledialog.askstring("Search", "Enter search term:")
    if search_term:
        results = []
        for category, quote_list in quotes.items():
            for quote in quote_list:
                if search_term.lower() in quote.lower():
                    results.append(quote)
        
        if results:
            result_window = tk.Toplevel(root)
            result_window.title("Search Results")
            result_text = scrolledtext.ScrolledText(result_window, width=50, height=10)
            result_text.pack(padx=10, pady=10)
            for quote in results:
                result_text.insert(tk.END, f"{quote}\n\n")
            result_text.config(state='disabled')
        else:
            messagebox.showinfo("Search", "No matching quotes found.")

# 改進主框架佈局
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# 創建更現代的滾動區域
canvas = tk.Canvas(main_frame, highlightthickness=0)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas, padding="10")

# Configure scrolling
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Pack scroll components
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Create quote type selection dropdown menu
quote_type_var = tk.StringVar(value="Courage")
quote_type_menu = tk.OptionMenu(scrollable_frame, quote_type_var, *quotes.keys())
quote_type_menu.config(font=("Arial", 12))
quote_type_menu.pack(pady=10)

# User registration and login
def register():
    username = simpledialog.askstring("Register", "Please enter your username:")
    if username:
        if username not in users:
            users[username] = True  # Register user
            save_user_data()
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

def logout():
    current_user.set("Not logged in")
    messagebox.showinfo("Success", "Logged out successfully!")

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
        save_user_data()

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
            save_user_data()
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
            save_user_data()
            messagebox.showinfo("Success", "Comment successful!")
    else:
        messagebox.showwarning("Warning", "Please generate a quote first!")

# Define function to add custom quotes
def add_custom_quote():
    custom_quote = simpledialog.askstring("Add Quote", "Please enter your custom quote:")
    if custom_quote:
        custom_quotes.append(custom_quote)
        save_user_data()
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

# Modify share functionality to support more platforms
def share_quote():
    quote = quote_label.cget("text")
    if quote:
        share_window = tk.Toplevel(root)
        share_window.title("Share Quote")
        share_window.geometry("200x200")
        
        def share_to(platform):
            if platform == "Facebook":
                webbrowser.open(f"https://www.facebook.com/sharer/sharer.php?u={quote}")
            elif platform == "Twitter":
                webbrowser.open(f"https://twitter.com/intent/tweet?text={quote}")
            elif platform == "LinkedIn":
                webbrowser.open(f"https://www.linkedin.com/sharing/share-offsite/?url={quote}")
            share_window.destroy()
        
        for platform in ["Facebook", "Twitter", "LinkedIn"]:
            ttk.Button(share_window, text=platform, 
                      command=lambda p=platform: share_to(p)).pack(pady=5)
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
            "Happy": [
                "Life is short, enjoy every moment!", 
                "Let's embrace happiness!", 
                "Happiness is most important!", 
                "Life is short, enjoy every moment! Let's embrace happiness!",
                "Happiness is when what you think, what you say, and what you do are in harmony.",
                "The best way to cheer yourself up is to try to cheer somebody else up.",
                "Joy comes from a content heart.",
                "Happiness is a choice, choose to smile at life."
            ],
            "Sad": [
                "When you're sad, remember to give yourself some time.", 
                "Sadness is part of life, learn to accept it.", 
                "Don't be afraid to feel sad, it's part of life.", 
                "It's okay to be sad, give yourself time to heal.",
                "Every cloud has a silver lining.",
                "Tears are words the heart can't express.",
                "Sadness is temporary, hope is eternal.",
                "Face sadness calmly to see hope."
            ],
            "Anxious": [
                "Don't let anxiety control you, take a deep breath, everything will be okay.", 
                "Anxiety is not scary, the key is to find solutions.", 
                "Don't let anxiety control you, take a deep breath, everything will be okay.", 
                "Anxiety is not scary, the key is to find solutions.",
                "Anxiety is temporary, but your strength is permanent.",
                "Focus on what you can control, let go of what you can't.",
                "When anxious, take deep breaths and relax.",
                "Staying calm is the best way to face anxiety."
            ],
            "Excited": [
                "Be passionate and go for it!", 
                "Pursue your dreams with passion and make them a reality!", 
                "Be passionate and go for it!", 
                "Pursue your dreams with passion and make them a reality.",
                "Channel your excitement into positive action.",
                "Let your enthusiasm light up the world.",
                "Excitement is the source of motivation.",
                "Passion is the key to success."
            ],
            "Calm": [
                "A peaceful mind is the source of happiness.", 
                "Learn to observe calmly and experience true peace.", 
                "A peaceful mind is the source of happiness.", 
                "Learn to observe calmly and experience true peace.",
                "In the midst of chaos, there is also opportunity.",
                "Peace comes from within.",
                "Tranquility is inner strength.",
                "Serenity leads to distance, take life slowly."
            ]
        }
        if selected_mood in mood_quotes:
            quote = random.choice(mood_quotes[selected_mood])
            quote_label.config(text=quote)
        else:
            messagebox.showwarning("Warning", "This mood category is not supported yet!")

# Beautify quote label
quote_label = tk.Label(
    scrollable_frame,
    text="Click generate button to start ✨",
    wraplength=500,
    font=("Segoe UI", 20),
    bg=themes["Modern Light"]["card_bg"],
    fg=themes["Modern Light"]["fg"],
    pady=40,
    padx=40,
    relief="flat",
    borderwidth=0
)
quote_label.pack(pady=40, padx=30, fill=tk.X)

# Create modern button container
def create_button_container(parent):
    container = ttk.Frame(parent, style="Card.TFrame")
    container.pack(pady=10, padx=20, fill=tk.X)
    return container

# Reorganize button layout using grid system
main_controls = create_button_container(scrollable_frame)
main_controls.columnconfigure((0,1,2), weight=1)

ttk.Button(main_controls, 
    text=f"{EMOJIS['generate']} Generate Quote",
    command=show_quote, 
    style="Custom.TButton"
).grid(row=0, column=0, padx=8, pady=8, sticky="ew")

ttk.Button(main_controls, 
    text=f"{EMOJIS['share']} Share",
    command=share_quote, 
    style="Custom.TButton"
).grid(row=0, column=1, padx=8, pady=8, sticky="ew")

ttk.Button(main_controls, 
    text=f"{EMOJIS['rate']} Rate",
    command=rate_quote, 
    style="Custom.TButton"
).grid(row=0, column=2, padx=8, pady=8, sticky="ew")

# User control panel
user_controls = create_button_container(scrollable_frame)
user_controls.columnconfigure((0,1,2), weight=1)

ttk.Button(user_controls, 
    text=f"{EMOJIS['register']} Register",
    command=register, 
    style="Custom.TButton"
).grid(row=0, column=0, padx=8, pady=8, sticky="ew")

ttk.Button(user_controls, 
    text=f"{EMOJIS['login']} Login",
    command=login, 
    style="Custom.TButton"
).grid(row=0, column=1, padx=8, pady=8, sticky="ew")

ttk.Button(user_controls, 
    text=f"{EMOJIS['profile']} Profile",
    command=show_user_data, 
    style="Custom.TButton"
).grid(row=0, column=2, padx=8, pady=8, sticky="ew")

# Mood selection area
mood_frame = create_button_container(scrollable_frame)
mood_label = tk.Label(
    mood_frame,
    text=f"{EMOJIS['mood']} How are you feeling today?",
    font=("Segoe UI", 13),
    bg=themes["Modern Light"]["card_bg"],
    fg=themes["Modern Light"]["fg"]
)
mood_label.pack(pady=(12,6))

mood_combobox = ttk.Combobox(
    mood_frame,
    textvariable=mood_var,
    values=moods,
    state="readonly",
    font=("Segoe UI", 10),
    width=30
)
mood_combobox.pack(pady=5)

ttk.Button(
    mood_frame,
    text="Get Mood Quote",
    command=show_mood_quote,
    style="Custom.TButton"
).pack(pady=(5,10))

# Settings area
settings_frame = create_button_container(scrollable_frame)
settings_frame.columnconfigure((0,1,2), weight=1)

ttk.Button(settings_frame, 
    text=f"{EMOJIS['voice']} Voice Settings",
    command=configure_voice, 
    style="Custom.TButton"
).grid(row=0, column=0, padx=8, pady=8, sticky="ew")

ttk.OptionMenu(settings_frame, current_theme, "Modern Light", *themes.keys(),
              command=lambda _: change_theme()).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

ttk.Button(settings_frame, 
    text=f"{EMOJIS['search']} Search Quote",
    command=search_quotes, 
    style="Custom.TButton"
).grid(row=0, column=2, padx=8, pady=8, sticky="ew")

# Create the "Loading..." label
loading_label = tk.Label(scrollable_frame, text="", font=("Arial", 12))
loading_label.pack()

# Create button group frame
buttons_frame = ttk.Frame(scrollable_frame)
buttons_frame.pack(fill=tk.X, pady=10)

quote_controls_frame = ttk.Frame(buttons_frame)
quote_controls_frame.pack(pady=10)

user_controls_frame = ttk.Frame(buttons_frame)
user_controls_frame.pack(pady=10)

interaction_controls_frame = ttk.Frame(buttons_frame)
interaction_controls_frame.pack(pady=10)

# Create comment quote button
comment_button = ttk.Button(scrollable_frame, 
    text=f"{EMOJIS['comment']} Add Comment",
    command=comment_quote,
    style="Custom.TButton")
comment_button.pack(pady=8)

# Create add custom quote button
add_custom_button = ttk.Button(scrollable_frame, 
    text=f"{EMOJIS['custom']} Custom Quote",
    command=add_custom_quote,
    style="Custom.TButton")
add_custom_button.pack(pady=8)

# Create recommend quote button
recommend_button = ttk.Button(scrollable_frame, 
    text=f"{EMOJIS['recommend']} Recommend Quote",
    command=recommend_quote,
    style="Custom.TButton")
recommend_button.pack(pady=8)

# Create exit button
exit_button = ttk.Button(scrollable_frame, 
    text=f"{EMOJIS['exit']} Exit",
    command=root.quit,
    style="Custom.TButton")
exit_button.pack(pady=(8,20))

# Load user data at startup
load_user_data()


configure_button_style()
change_theme()

# Start the main loop
root.mainloop()