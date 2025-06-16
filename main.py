
import customtkinter as ctk
import sqlite3
import hashlib


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")



# Initialize DB
conn = sqlite3.connect("notes_app.db") #connect sqlite to .db file
c = conn.cursor()
#Creates users table, define fields for users table
c.execute('''CREATE TABLE IF NOT EXISTS users ( 
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE,
                first_name TEXT,
                password TEXT)''')
#Creates notes table, storing user info and the notes they types
c.execute('''CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                data TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id))''') #user_id becomes a foreign key in notes
conn.commit()

# Helper functions, hashing algorithm sha256 converts password into ciphertext, hiding the password in notes_app.db
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Notes App")
        self.geometry("500x500")
        self.current_user = None
        self.build_login()
        self.sidebar = None
        self.content_frame = None
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_paused = False
        self.timer_id = None


    def clear_widgets(self):
      for widget in self.winfo_children():
        widget.destroy()
      self.sidebar = None
      self.content_frame = None

    #sidebar shown when logged in
    def build_logged_in_layout(self):
      self.clear_widgets()
    
      # Sidebar menu
      self.sidebar = ctk.CTkFrame(self, width=120)
      self.sidebar.pack(side="left", fill="y")

      ctk.CTkLabel(self.sidebar, text="Menu", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))

      ctk.CTkButton(self.sidebar, text="Home", command=self.build_home).pack(pady=5)
      ctk.CTkButton(self.sidebar, text="Pomodoro", command=self.build_pomodoro).pack(pady=5)
      ctk.CTkButton(self.sidebar, text="Logout", command=self.logout).pack(pady=5)

      # Content frame
      self.content_frame = ctk.CTkFrame(self)
      self.content_frame.pack(side="left", fill="both", expand=True)


    
    #login page function
    def build_login(self):
        self.clear_widgets()

        
        container = ctk.CTkFrame(self)#Creates a frame that will hold all login widgets
        container.place(relx=0.5, rely=0.5, anchor="center")  # center the frame in the window

        self.label = ctk.CTkLabel(container, text="Login", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=50, padx=150)

        self.email_entry = ctk.CTkEntry(container, placeholder_text="Email", width=300, height=40) #email entry box
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(container, placeholder_text="Password", show="*", width=300, height=40) #password entry box
        self.password_entry.pack(pady=5)

        self.login_btn = ctk.CTkButton(container, text="Login", command=self.login, width=300, height=40)
        self.login_btn.pack(pady=10)

        self.signup_link = ctk.CTkButton(container, text="Sign Up", command=self.build_signup, width=300, height=40)
        self.signup_link.pack(pady=5)

        self.flash_label = ctk.CTkLabel(container, text="")
        self.flash_label.pack()

    #signup page function
    def build_signup(self): 
        self.clear_widgets()
        self.label = ctk.CTkLabel(self, text="Sign Up", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=10)
        
        #text entries
        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email")
        self.email_entry.pack(pady=5)
        self.name_entry = ctk.CTkEntry(self, placeholder_text="First Name")
        self.name_entry.pack(pady=5)
        self.password1 = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password1.pack(pady=5)
        self.password2 = ctk.CTkEntry(self, placeholder_text="Confirm Password", show="*")
        self.password2.pack(pady=5)

        self.signup_btn = ctk.CTkButton(self, text="Create Account", command=self.signup)
        self.signup_btn.pack(pady=10)

        self.login_link = ctk.CTkButton(self, text="Back to Login", command=self.build_login)
        self.login_link.pack(pady=5)

        self.flash_label = ctk.CTkLabel(self, text="")
        self.flash_label.pack()
    
    #homepage function
    def build_home(self):
      for widget in self.content_frame.winfo_children():
        widget.destroy()

      ctk.CTkLabel(self.content_frame, text=f"Welcome, {self.current_user[2]}", font=ctk.CTkFont(size=18)).pack(pady=5)

      self.note_entry = ctk.CTkTextbox(self.content_frame, height=100, width=400)
      self.note_entry.pack(pady=10)

      self.add_btn = ctk.CTkButton(self.content_frame, text="Add Note", command=self.add_note)
      self.add_btn.pack(pady=5)

      self.notes_frame = ctk.CTkFrame(self.content_frame)
      self.notes_frame.pack(pady=10, fill="both", expand=True)

      self.load_notes()



    #pomodoro timer   
    def build_pomodoro(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create a centered frame for all pomodoro elements
        center_frame = ctk.CTkFrame(self.content_frame)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

        ctk.CTkLabel(center_frame, text="Pomodoro Timer", font=ctk.CTkFont(size=18)).pack(pady=10)

        self.timer_label = ctk.CTkLabel(center_frame, text="25:00", font=ctk.CTkFont(size=36), width=400)
        self.timer_label.pack(pady=20)

        self.start_button = ctk.CTkButton(center_frame, text="Start", command=self.start_timer)
        self.start_button.pack(pady=5)

        self.pause_button = ctk.CTkButton(center_frame, text="Pause", command=self.pause_timer)
        self.pause_button.pack(pady=5)

        self.reset_button = ctk.CTkButton(center_frame, text="Reset", command=self.reset_timer)
        self.reset_button.pack(pady=5)


    #time format using f string
    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    #start timer function
    def start_timer(self):
        if not self.timer_running:
            if self.timer_seconds == 0 or self.timer_seconds == 25 * 60:
                self.timer_seconds = 25 * 60  # Reset to full session if starting fresh
            self.timer_running = True
            self.timer_paused = False
            self.update_timer() #loops for every second

    #pause timer function
    def pause_timer(self):
        if self.timer_running:
            self.timer_paused = True
            self.timer_running = False
            if self.timer_id:
                self.after_cancel(self.timer_id)

   #update timer function
    def update_timer(self):
        if self.timer_running and not self.timer_paused:
            if self.timer_seconds >= 0:
                self.timer_label.configure(text=self.format_time(self.timer_seconds))
                self.timer_seconds -= 1
                self.timer_id = self.after(1000, self.update_timer)
            else:
                self.timer_running = False

    #reset timer function
    def reset_timer(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
        self.timer_running = False #timer not running
        self.timer_paused = False #not pausing either
        self.timer_seconds = 25 * 60 #converts 25 minutes to seconds
        self.timer_label.configure(text="25:00") #sets timer to 25 minutes when reset button is hit







    def flash(self, msg, color="red"):
        self.flash_label.configure(text=msg, text_color=color)
    #login page function
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
      
        if user and user[3] == hash_password(password):  #sends user to homepage when login credentials are correct
          self.current_user = user
          self.build_logged_in_layout()
          self.build_home()
        else: #if credentials are invalid, this message is flashed
          self.flash("Invalid login credentials") 
    
    #signup page function
    def signup(self):
        email = self.email_entry.get()
        name = self.name_entry.get()
        p1 = self.password1.get()
        p2 = self.password2.get()
        
        if p1 != p2: #if passwords match, signup
            self.flash("Passwords do not match")
            return
        if len(p1) < 7:#if password is less than 7 characters, the user is not logged in and this message is flashed
            self.flash("Password must be 7+ characters")
            return

        try:
            c.execute("INSERT INTO users (email, first_name, password) VALUES (?, ?, ?)",
                      (email, name, hash_password(p1)))
            conn.commit()
            self.flash("Account created!", color="green")
        except sqlite3.IntegrityError:
            self.flash("Email already exists")
   
    #add note function
    def add_note(self):
        data = self.note_entry.get("1.0", "end").strip()
        if len(data) < 1:
            return
        c.execute("INSERT INTO notes (user_id, data) VALUES (?, ?)", (self.current_user[0], data))
        conn.commit()
        self.note_entry.delete("1.0", "end")
        self.load_notes()
  
    def load_notes(self):  #load notes function
        for widget in self.notes_frame.winfo_children():
            widget.destroy()

        c.execute("SELECT id, data FROM notes WHERE user_id=?", (self.current_user[0],))
        notes = c.fetchall()
        
        for note_id, data in notes:#for every note created, format the note with:
            note_row = ctk.CTkFrame(self.notes_frame)
            note_row.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(note_row, text=data, wraplength=350).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(note_row, text="Delete", width=70, command=lambda nid=note_id: self.delete_note(nid)).pack(side="right", padx=5)
   
    def delete_note(self, note_id): #delete function, deletes notes
        c.execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id, self.current_user[0]))
        conn.commit()
        self.load_notes()
    
    def logout(self):#logout function, logs the user out
      self.current_user = None
      self.clear_widgets()
      self.build_login()

#runs the app continuouslyu
if __name__ == "__main__":
    app = App()
    app.mainloop()
