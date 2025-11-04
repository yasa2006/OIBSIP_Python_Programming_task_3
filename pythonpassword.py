import random
import string
import tkinter as tk
from tkinter import messagebox
import json
import os 


HISTORY_FILE = 'password_history.json'
MAX_HISTORY = 5
AMBIGUOUS_CHARS = 'lIOi01'
MAIN_BG = "#93b2b7"
ANIMATION_DELAY = 50

DARK_COLORS = [
    "#00796B",  
    "#1976D2",  
    "#388E3C",  
    "#5D4037", 
    "#455A64",  
    "#6A1B9A",  
    "#7B1FA2",  
    "#C0392B"   
]

def generate_password(length, use_letters, use_numbers, use_symbols, exclude_ambiguous=False):
    """
    Generates a random password based on specified criteria.
    Ensures at least one of each selected character type is included.
    """

    character_pool = " "
    
   
    letters = string.ascii_letters
    numbers = string.digits
    
    if exclude_ambiguous:
        letters = ''.join(c for c in letters if c not in AMBIGUOUS_CHARS)
        numbers = ''.join(c for c in numbers if c not in AMBIGUOUS_CHARS)

    if use_letters:
        character_pool += letters
    if use_numbers:
        character_pool += numbers
    if use_symbols:
       
        character_pool += string.punctuation

    if not character_pool:
        return "Error: No character types selected. Cannot generate password."
    
    
    password_list = []
    if use_letters:
        password_list.append(random.choice(letters))
    if use_numbers:
        password_list.append(random.choice(numbers))
    if use_symbols:
        password_list.append(random.choice(string.punctuation))
        
   
    remaining_length = length - len(password_list)
    if remaining_length > 0:
        password_list.extend(random.choice(character_pool) for _ in range(remaining_length))

    
    random.shuffle(password_list)
    return "".join(password_list)

def assess_strength(password):
    """
    Assesses the strength of a password based on length and character type diversity.
    Returns a tuple: (strength_rating, color)
    """
    length = len(password)
    types = 0
    if any(c.islower() for c in password):
        types += 1
    if any(c.isupper() for c in password):
        types += 1
    if any(c.isdigit() for c in password):
        types += 1
    if any(c in string.punctuation for c in password):
        types += 1

    
    score = length + types * 5
    
   
    random_dark_color = random.choice(DARK_COLORS)

    if score < 15:
        return "Very Weak", random_dark_color
    elif score < 20:
        return "Weak", random_dark_color
    elif score < 25:
        return "Moderate", random_dark_color
    elif score < 30:
        return "Strong", random_dark_color
    else:
        return "Very Strong", random_dark_color

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Generator")
        
       
        self.root.geometry("450x650") 
        self.root.resizable(False, False) 
        self.root.config(bg='#cccccc')

        self.history = []
        self.load_history()

       
        self.animated_circles = [] 
        self.circle_data = [] 

       
        self.choice_var = tk.StringVar(value='random')
        self.length_var = tk.StringVar(value='12')
        self.letters_var = tk.BooleanVar(value=True)
        self.numbers_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.ambiguous_var = tk.BooleanVar(value=False)
        self.password_output = tk.StringVar(value="[Password will appear here]")

        self._setup_ui()
        self._animate_background() 

    def _initialize_circles(self, count):
        """Creates initial circle elements for the background animation."""
       
        canvas_width = 450
        canvas_height = 650 - 50 

       
        circle_color = '#b2ebf2' 
        
        for _ in range(count):
            radius = random.randint(10, 20)
            x = random.randint(0, canvas_width)
            y = random.randint(0, canvas_height)
            speed = random.uniform(0.3, 0.7) 
            
            
            circle_id = self.bg_canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                outline=circle_color, fill=circle_color, width=1, tags="bg_circle"
            )
            
            
            self.animated_circles.append(circle_id)
            self.circle_data.append({
                'id': circle_id, 
                'radius': radius, 
                'speed': speed, 
                'x': x, 
                'y': y
            })

    def _animate_background(self):
        """Moves the circles and wraps them around the canvas for a subtle animation effect."""
        if not hasattr(self, 'bg_canvas'):
            return

        canvas_width = self.bg_canvas.winfo_width()
        canvas_height = self.bg_canvas.winfo_height()
        
       
        if canvas_width == 1 and canvas_height == 1:
             canvas_width = 450
             canvas_height = 600

        for data in self.circle_data:
            data['y'] -= data['speed'] 

           
            if data['y'] + data['radius'] < 0:
                data['y'] = canvas_height + data['radius']
                data['x'] = random.randint(0, canvas_width)
                
                # Update canvas coordinates
                x1 = data['x'] - data['radius']
                y1 = data['y'] - data['radius']
                x2 = data['x'] + data['radius']
                y2 = data['y'] + data['radius']
                self.bg_canvas.coords(data['id'], x1, y1, x2, y2)
            else:
                # Move the circle relative to its old position
                self.bg_canvas.move(data['id'], 0, -data['speed'])

       
        self.root.after(ANIMATION_DELAY, self._animate_background)

    def _recenter_content(self, event):
        """Recenter the main content frame when the canvas is resized (or on startup)."""
        canvas_width = event.width
        canvas_height = event.height
        
       
        self.bg_canvas.coords(self.content_window, canvas_width / 2, canvas_height / 2)


    def _setup_ui(self):
        # --- 1. Canvas for Header/Title ---
        self.header_canvas = tk.Canvas(self.root, height=50, bg="#2c3e50", highlightthickness=0)
        self.header_canvas.pack(fill='x')
        self.header_canvas.create_text(
            225, 25, 
            text="🔐 ADVANCED PASSWORD GENERATOR 🔐", 
            fill="white", 
            font=("Arial", 14, "bold")
        )

        # --- 2. Background Canvas (replaces direct packing of main_frame) ---
        self.bg_canvas = tk.Canvas(self.root, bg=MAIN_BG, highlightthickness=0)
        self.bg_canvas.pack(fill='both', expand=True)
        
        # Initialize background circles
        self._initialize_circles(10)

        # Create a frame to hold all existing widgets (placed ON the canvas)
        main_frame = tk.Frame(self.bg_canvas, padx=15, pady=10, bg=MAIN_BG)
        
        # Place the content frame centrally on the canvas
        self.content_window = self.bg_canvas.create_window(
            225, 300, # Initial estimated center
            window=main_frame, anchor="center"
        )
        
        # Bind event to center the content frame on resize/startup
        self.bg_canvas.bind('<Configure>', self._recenter_content)

        # --- 3. Widget Layout (All widgets placed inside 'main_frame') ---
        tk.Label(main_frame, text="Choose generation method:", font=("Arial", 10, "underline"), bg=MAIN_BG).pack(pady=(10, 5))
        
        tk.Radiobutton(main_frame, text="Random (Secure)", variable=self.choice_var, value='random', bg=MAIN_BG).pack(anchor='w', padx=20)
        tk.Radiobutton(main_frame, text="Personalized (Not Recommended for high security)", variable=self.choice_var, value='personalized', bg=MAIN_BG).pack(anchor='w', padx=20)

        # Username and DOB inputs
        tk.Label(main_frame, text="Username:", bg=MAIN_BG).pack(pady=(5,0))
        self.username_entry = tk.Entry(main_frame, width=30)
        self.username_entry.pack()

        tk.Label(main_frame, text="Date of Birth (YYYY-MM-DD):", bg=MAIN_BG).pack(pady=(5,0))
        self.dob_entry = tk.Entry(main_frame, width=30)
        self.dob_entry.pack()

        # --- 3. Length and Character Types ---
        tk.Label(main_frame, text="Password Length (Min 6):", bg=MAIN_BG).pack(pady=(10, 0))
        tk.Entry(main_frame, textvariable=self.length_var, width=10, justify='center').pack()

        tk.Label(main_frame, text="Character Sets:", font=("Arial", 10, "underline"), bg=MAIN_BG).pack(pady=(10, 5))
        
        # Checkboxes in a smaller frame for better grouping
        check_frame = tk.Frame(main_frame, bg=MAIN_BG)
        check_frame.pack()
        tk.Checkbutton(check_frame, text="Letters (a, A)", variable=self.letters_var, bg=MAIN_BG).grid(row=0, column=0, sticky='w')
        tk.Checkbutton(check_frame, text="Numbers (0-9)", variable=self.numbers_var, bg=MAIN_BG).grid(row=0, column=1, sticky='w')
        tk.Checkbutton(check_frame, text="Symbols (!@#$)", variable=self.symbols_var, bg=MAIN_BG).grid(row=1, column=0, sticky='w')
        tk.Checkbutton(check_frame, text=f"Exclude Ambiguous ({AMBIGUOUS_CHARS})", variable=self.ambiguous_var, bg=MAIN_BG).grid(row=1, column=1, sticky='w')

        # --- 4. Generation and Output ---
        tk.Button(main_frame, text="GENERATE PASSWORD", command=self.generate_password_gui, 
                  bg='#4CAF50', fg='white', width=30, font=("Arial", 10, "bold")).pack(pady=15)
        
        # Password Display (Read-only Entry for easy copying)
        tk.Entry(main_frame, textvariable=self.password_output, width=40, font=('Courier', 12), state='readonly', justify='center').pack(pady=(0, 5))
        
        # Strength Indicator
        tk.Label(main_frame, text="Strength:", bg=MAIN_BG).pack(pady=(5, 0))
        self.strength_label = tk.Label(main_frame, text="N/A", font=("Arial", 12, "bold"), bg=MAIN_BG)
        self.strength_label.pack()

        # Copy and History Buttons
        button_frame_top = tk.Frame(main_frame, bg=MAIN_BG)
        button_frame_top.pack(pady=(10, 5))
        tk.Button(button_frame_top, text="Copy Password", command=self.copy_to_clipboard, width=18).pack(side='left', padx=10)
        tk.Button(button_frame_top, text="View History", command=self.view_history, width=18).pack(side='left', padx=10)

        # New Security Info Button (placed below the main buttons)
        tk.Button(main_frame, text="Security Info: Why Random?", command=self.show_security_info, 
                  bg='#2980b9', fg='white', width=40, font=("Arial", 10)).pack(pady=5)


    # --- History and File I/O Methods ---
    def load_history(self):
        try:
            if os.path.exists(HISTORY_FILE) and os.path.getsize(HISTORY_FILE) > 0:
                 with open(HISTORY_FILE, 'r') as f:
                    self.history = json.load(f)
        except Exception:
            self.history = []

    def save_history(self):
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f)

    def add_to_history(self, pwd):
        self.history.append(pwd)
        if len(self.history) > MAX_HISTORY:
            self.history.pop(0) 
        self.save_history()

    # --- Action Methods ---
    def generate_password_gui(self):
        try:
            # 1. Input Validation
            try:
                length = int(self.length_var.get())
                if length < 6:
                    messagebox.showwarning("Warning", "Password length should be at least 6 for security.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive integer for length.")
                return

            use_letters = self.letters_var.get()
            use_numbers = self.numbers_var.get()
            use_symbols = self.symbols_var.get()
            exclude_ambiguous = self.ambiguous_var.get()

            if not (use_letters or use_numbers or use_symbols):
                messagebox.showerror("Error", "You must select at least one character type.")
                return

            # 2. Random Seed Handling (as per user's request for personalized)
            choice = self.choice_var.get()
            if choice == 'personalized':
                username = self.username_entry.get()
                dob = self.dob_entry.get()
                if not username or not dob:
                    messagebox.showerror("Error", "Please enter both username and date of birth for personalized password.")
                    return
                random.seed(username + dob)
            else:
                random.seed() 

            # 3. Generation, Display, and History
            generated_pwd = generate_password(length, use_letters, use_numbers, use_symbols, exclude_ambiguous)
            self.password_output.set(generated_pwd)
            
            # Update Strength Indicator
            strength, color = assess_strength(generated_pwd)
            self.strength_label.config(text=f"Strength: {strength}", fg=color)

            # Update History
            self.add_to_history(generated_pwd)
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def copy_to_clipboard(self):
        password = self.password_output.get()
        if password and not password.startswith("["):
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Copied", "Password successfully copied to clipboard!")
        else:
            messagebox.showwarning("Copy Error", "Please generate a password first.")

    def view_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Password History")
        history_window.geometry("350x250")
        
        tk.Label(history_window, text="Last 5 Passwords:", font=("Arial", 10, "bold")).pack(pady=5)
        
        if self.history:
            for i, pwd in enumerate(reversed(self.history), 1):
                tk.Label(history_window, text=f"• {pwd}", wraplength=300).pack(anchor='w', padx=10)
        else:
            tk.Label(history_window, text="No history available.", fg='gray').pack()

    def show_security_info(self):
        info_window = tk.Toplevel(self.root)
        info_window.title("Password Security Information")
        info_window.geometry("450x300")
        info_window.transient(self.root) 

        # Config background for the info window
        info_window.config(bg=MAIN_BG)

        # All labels in the info window now have an explicit background
        tk.Label(info_window, 
                 text="Password Generation Security", 
                 font=("Arial", 12, "bold", "underline"), 
                 fg="#2c3e50", bg=MAIN_BG).pack(pady=10)

        tk.Label(info_window, 
                 text="Random (Secure):",
                 font=("Arial", 10, "bold"), bg=MAIN_BG).pack(anchor='w', padx=15)
        
        tk.Label(info_window, 
                 text="Generates unique, high-entropy passwords based on system time and true randomness. This is the recommended choice for maximum security, as it is impossible to guess the input (seed).", 
                 wraplength=420, 
                 justify='left', bg=MAIN_BG).pack(anchor='w', padx=15, pady=(0, 10))

        tk.Label(info_window, 
                 text="Personalized (Insecure):",
                 font=("Arial", 10, "bold"),
                 fg="red", bg=MAIN_BG).pack(anchor='w', padx=15)
        
        tk.Label(info_window, 
                 text="Uses personal data (Username/DOB) to 'seed' the random generator. This makes the password *predictable* by anyone who can guess or find your personal information (social engineering), severely compromising security.", 
                 wraplength=420, 
                 justify='left', bg=MAIN_BG).pack(anchor='w', padx=15)

        tk.Button(info_window, text="Close", command=info_window.destroy, width=10).pack(pady=15)


if __name__ == "__main__":
    random.seed() 
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
