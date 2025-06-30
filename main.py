
import customtkinter as ctk
import sqlite3
import hashlib
from PIL import Image
#ajsbdibasjkdsabdj
#---define images section---
home_icon = Image.open("icons/home_1946488.png") #home icon image
app_logo = Image.open("images/braintain_logo.png") #app
pomodoro_icon =Image.open("icons/stopwatch_icon.png")
flash_cards_icon=Image.open("icons/flash_cards_icon.png")

ctk.set_appearance_mode("Light") #sets the appearance mode
ctk.set_default_color_theme("themes/purple.json") #sets the default colour theme from purple.json file

#adding full fules
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

c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                name TEXT,
                subject TEXT,
                due_date TEXT,
                details TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id))''')
conn.commit()

c.execute('''CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                data TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id))''') #user_id becomes a foreign key in notes
conn.commit()

# Helper functions, hashing algorithm sha256 converts password into ciphertext, hiding the password in notes_app.db
def hash_password(password): #hashing function: encrypts passwords from plaintext to encoded set of characters
    return hashlib.sha256(password.encode()).hexdigest()

class App(ctk.CTk): #class for app
    def __init__(self):
        super().__init__()
        self.title("Braintain")
        self.after(100, lambda: self.state('zoomed'))

        self.current_user = None
        self.build_login()
        self.sidebar = None
        self.content_frame = None
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_paused = False
        self.timer_id = None
        self.app_font = ctk.CTkFont(family="Inter", size=20, weight="bold")


    def clear_widgets(self):
      for widget in self.winfo_children():
        widget.destroy()
      self.sidebar = None
      self.content_frame = None

    #sidebar shown when logged in
    def build_logged_in_layout(self):
      self.clear_widgets()
    
      # Sidebar menu
      self.sidebar = ctk.CTkFrame(self, width=120, fg_color="white")
      self.sidebar.pack(side="left", fill="y")
      

      ctk.CTkLabel(self.sidebar, text="Menu", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))

      ctk.CTkButton(self.sidebar, image=ctk.CTkImage(light_image=home_icon),text="Home", command=self.home, fg_color="white", text_color="black").pack(pady=5)
      ctk.CTkButton(self.sidebar, image=ctk.CTkImage(light_image=pomodoro_icon),text="Pomodoro", command=self.build_pomodoro, fg_color="white", text_color="black").pack(pady=5)
      ctk.CTkButton(self.sidebar, image=ctk.CTkImage(light_image=flash_cards_icon),text="Flashcards", command=self.build_flashcards, fg_color="white", text_color="black").pack(pady=5)
      ctk.CTkButton(self.sidebar, text="Notes", command=self.build_notes, fg_color="white", text_color="black").pack(pady=5)
      ctk.CTkButton(self.sidebar, text="Logout", command=self.logout, fg_color="white", text_color="black").pack(pady=5)
      ctk.CTkButton(self.sidebar, text="Tasks", command=self.build_tasks_page, fg_color="white", text_color="black").pack(pady=5)


      # Content frame
      self.content_frame = ctk.CTkFrame(self)
      self.content_frame.pack(side="left", fill="both", expand=True)


    
    #login page function
    def build_login(self):
      self.clear_widgets()

    # Fullscreen background
      background = ctk.CTkFrame(self, fg_color="#4B0082", corner_radius=0)
      background.place(relx=0, rely=0, relwidth=1, relheight=1)

    # --- Left side: Full-height container ---
      container = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
      container.place(relx=0, rely=0, relwidth=0.5, relheight=1)
      

    # Inner frame centered inside the left container
      content_frame = ctk.CTkFrame(container, fg_color="transparent", border_color="#d0d0d0", border_width=0.4, corner_radius=10)
      content_frame.place(relx=0.4, rely=0.5, anchor="center")
      content_frame.configure(fg_color="#fafafa")
      
      header_frame= ctk.CTkFrame(content_frame, fg_color="#fafafa")
      header_frame.pack(anchor="center", padx=20, pady=20)

      innercont_frame= ctk.CTkFrame(content_frame,fg_color="#fafafa")
      innercont_frame.pack(anchor="center", padx=20, pady=20)
      
      #Logo Image
      app_logo = Image.open("images/braintain_logo.png") #app
      self.logo = ctk.CTkImage(light_image=app_logo, size=(120, 120))
      
      logo_label = ctk.CTkLabel(header_frame, image=self.logo, text="")
      logo_label.pack(side="left", padx=(0, 10))  # Logo on the left

      self.app_title = ctk.CTkLabel(header_frame, text = "Braintrain", font=ctk.CTkFont(family="Huninn", size=55, weight="bold"))
      #self.app_title(anchor="center", padx=10, pady=(0,20))
      self.app_title.pack(side="left")

       
      #welcome widgets
      self.label = ctk.CTkLabel(innercont_frame, text="Login", font=ctk.CTkFont(family="Calibri", size=40, weight="normal"))
      self.label.pack(anchor="center", padx=10, pady=(0, 20))

      self.greeting = ctk.CTkLabel(innercont_frame, text="Hi there, 👋 Welcome!", font=ctk.CTkFont(family="Calibri", size=18))
      self.greeting.pack(anchor="center", padx=10, pady=(0, 20))
      
      #email widgets
      self.email_label= ctk.CTkLabel(innercont_frame,text="Email", font=ctk.CTkFont(family="Calibri", size=16, weight="bold"), text_color="black",)
      self.email_label.pack(pady=0, anchor="w")

      self.email_entry = ctk.CTkEntry(innercont_frame, placeholder_text="", width=400, height=50, fg_color="#F6E9FF", border_color="black", border_width=0.5, font=ctk.CTkFont(family="Calibri", size=16))
      self.email_entry.pack(pady=10)
      
      #password widgets
      self.password_label= ctk.CTkLabel(innercont_frame,text="Password", font=ctk.CTkFont(family="Calibri", size=16, weight="bold"), text_color="black")
      self.password_label.pack(pady=0, anchor="w")
      

      self.password_entry = ctk.CTkEntry(innercont_frame, placeholder_text="", show="*", width=400, height=50, fg_color="#F6E9FF", border_color="black", border_width=0.5, font=ctk.CTkFont(family="Calibri", size=16))
      self.password_entry.pack(pady=5)

      self.login_btn = ctk.CTkButton(innercont_frame, text="Login", command=self.login, width=400, height=50, fg_color="#4B0082", text_color="white", font=ctk.CTkFont(family="Calibri", size=16), hover_color="#ff1493")
      self.login_btn.pack(pady=15)

      self.signup_link = ctk.CTkButton(innercont_frame, text="Don't have an account? Sign up", command=self.build_signup, width=400, height=50, fg_color="transparent", text_color="#4B0082", font=ctk.CTkFont(family="Calibri", size=16, underline=True), hover_color="white")
      self.signup_link.pack(pady=5)

      self.flash_label = ctk.CTkLabel(innercont_frame, text="")
      self.flash_label.pack(pady=(10, 0))

    # --- Right panel (unchanged) --- 
      right_panel = ctk.CTkFrame(self, fg_color="#4B0082", corner_radius=0)
      right_panel.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

      gradient_bg = Image.open("images/braintain_gradient_bg.png")
      self.bg = ctk.CTkImage(light_image=gradient_bg, size= (800, 600))

      bg_label = ctk.CTkLabel(right_panel, image=self.bg, text="")
      bg_label.pack()  # Logo on the left
      

    def build_flashcards(self):
        for widget in self.content_frame.winfo_children():
          widget.destroy()

        ctk.CTkLabel(self.content_frame, text=f"Welcome, {self.current_user[2]}", font=ctk.CTkFont(size=18)).pack(pady=5)

        self.note_entry = ctk.CTkTextbox(self.content_frame, height=100, width=400)
        self.note_entry.pack(pady=10)

        self.add_btn = ctk.CTkButton(self.content_frame, text="Add Note", command=self.add_note)
        self.add_btn.pack(pady=5)

        self.notes_frame = ctk.CTkFrame(self.content_frame)
        self.notes_frame.pack(pady=10, fill="both", expand=True)
      
      
     
      
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
    def build_notes(self):
      
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

    def home(self):

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.content_frame, text=f"Welcome, {self.current_user[2]}", font=ctk.CTkFont(size=18)).pack(pady=5)

        
    
 #login event function
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
      
        if user and user[3] == hash_password(password):  #sends user to homepage when login credentials are correct
          self.current_user = user
          self.build_logged_in_layout()
          self.home()
        else: #if credentials are invalid, this message is flashed
          self.flash("Invalid login credentials") 
    

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

   
    #signing up event function
    def signup(self):
        email = self.email_entry.get()
        name = self.name_entry.get()
        p1 = self.password1.get()
        p2 = self.password2.get()
        
        if p1 != p2: #if passwords match, signup
            self.flash("Passwords do not match")
            return
        
        elif len(p1) < 7:#if password is less than 7 characters, the user is not logged in and this message is flashed
            self.flash("Password must be 7+ characters")
            return
        
        elif "@" not in p1 and "@" not in p2:
            self.flash("Invalid email: missing '@' symbol")
            
        elif not email.endswith(".com"):
            self.flash("Email must have a valid domain")

        try:
            c.execute("INSERT INTO users (email, first_name, password) VALUES (?, ?, ?)",
                      (email, name, hash_password(p1)))
            conn.commit()
            self.flash("Account created!", color="green")
        except sqlite3.IntegrityError:
            self.flash("Email already exists")
   
    #add note event function
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


    def build_tasks_page(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        top_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=10)

        # New Task button
        new_task_btn = ctk.CTkButton(top_frame, text="New Task", fg_color="#4B0082", text_color="white",
                                    command=self.open_new_task_popup)
        new_task_btn.pack(side="right")

        # Grid for tasks
        grid_frame = ctk.CTkFrame(self.content_frame)
        grid_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Fetch tasks from DB
        c.execute("SELECT id, name, subject, due_date FROM tasks WHERE user_id=?", (self.current_user[0],))
        tasks = c.fetchall()

        columns = 3  # Number of boxes per row
        for index, (task_id, name, subject, due_date) in enumerate(tasks):
            row = index // columns
            col = index % columns

            task_frame = ctk.CTkFrame(grid_frame, width=200, height=150, corner_radius=12)
            task_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

            ctk.CTkLabel(task_frame, text=f"Name: {name}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 2))
            ctk.CTkLabel(task_frame, text=f"Subject: {subject}").pack()
            ctk.CTkLabel(task_frame, text=f"Due: {due_date}").pack(pady=(0, 10))

            view_btn = ctk.CTkButton(task_frame, text="View Task", fg_color="#4B0082", text_color="white",
                                    command=lambda tid=task_id: self.show_task_details(tid))
            view_btn.pack(pady=(5, 10))

            delete_btn = ctk.CTkButton(
                task_frame,
                text="Delete",
                fg_color="red",
                text_color="white",
                hover_color="#8B0000",
                command=lambda tid=task_id: self.delete_task(tid)
            )
            delete_btn.pack(pady=(0, 10))

    def open_new_task_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("New Task")
        popup.geometry("400x400")

        ctk.CTkLabel(popup, text="Task Name").pack(pady=5)
        name_entry = ctk.CTkEntry(popup)
        name_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Subject").pack(pady=5)
        subject_entry = ctk.CTkEntry(popup)
        subject_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Due Date (e.g., 2025-07-05)").pack(pady=5)
        due_date_entry = ctk.CTkEntry(popup)
        due_date_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Details").pack(pady=5)
        details_entry = ctk.CTkTextbox(popup, height=100)
        details_entry.pack(pady=5)

        def save_task():
            name = name_entry.get()
            subject = subject_entry.get()
            due_date = due_date_entry.get()
            details = details_entry.get("1.0", "end").strip()

            if name and subject and due_date:
                c.execute("INSERT INTO tasks (user_id, name, subject, due_date, details) VALUES (?, ?, ?, ?, ?)",
                        (self.current_user[0], name, subject, due_date, details))
                conn.commit()
                popup.destroy()
                self.build_tasks_page()

        ctk.CTkButton(popup, text="Save Task", fg_color="#4B0082", text_color="white", command=save_task).pack(pady=10)
    
    def show_task_details(self, task_id):
        details_popup = ctk.CTkToplevel(self)
        details_popup.title("Task Details")
        details_popup.geometry("400x300")

        c.execute("SELECT name, subject, due_date, details FROM tasks WHERE id=? AND user_id=?", (task_id, self.current_user[0]))
        task = c.fetchone()

        if task:
            name, subject, due_date, details = task
            ctk.CTkLabel(details_popup, text=name, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
            ctk.CTkLabel(details_popup, text=f"Subject: {subject}").pack()
            ctk.CTkLabel(details_popup, text=f"Due: {due_date}").pack()
            ctk.CTkLabel(details_popup, text="Details:").pack(pady=(10, 2))

            detail_box = ctk.CTkTextbox(details_popup, height=100)
            detail_box.insert("1.0", details)
            detail_box.configure(state="disabled")
            detail_box.pack(pady=5)

    def delete_task(self, task_id):
        c.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, self.current_user[0]))
        conn.commit()
        self.build_tasks_page()  # Refresh the page after deletion





#runs the app continuouslyu
if __name__ == "__main__":
    app = App()
    app.mainloop()
