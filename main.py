#import libraries and modules
import customtkinter as ctk
import sqlite3
import hashlib
from PIL import Image
from tkcalendar import DateEntry
import tkinter as tk
from datetime import datetime

#---define images section---
home_icon = Image.open("icons/house_icon.png") #home icon image
app_logo = Image.open("images/braintain_logo.png") #app
pomodoro_icon =Image.open("icons/stopwatch_icon.png")
flash_cards_icon=Image.open("icons/flash_cards_icon.png")
tasks_icon=Image.open("icons/tasks_icon.png")
notes_icon=Image.open("icons/notes_icon.png")
logout_icon=Image.open("icons/logout_icon.png")
task_complete_icon=Image.open("icons/task_complete_icon.png")
delete_icon=Image.open("icons/trash_icon.png")
add_icon=Image.open("icons/add_icon.png")

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


#notes table
c.execute('''CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                data TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id))''') #user_id becomes a foreign key in notes


#Create tasks table
c.execute('''CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    name TEXT,
    subject TEXT,
    due_date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)''')
conn.commit()

# Helper functions, hashing algorithm sha256 converts password into ciphertext, hiding the password in notes_app.db
def hash_password(password): #hashing function: encrypts passwords from plaintext to encoded set of characters
    return hashlib.sha256(password.encode()).hexdigest()

class App(ctk.CTk): #class for app
    def __init__(self):
        super().__init__()
        self.title("Braintrain")
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
        self.task_list = [] 
        self.on_break = False  # Initially not on break
 


    #function that clears all widgets on a page
    def clear_widgets(self):
      for widget in self.winfo_children():
        widget.destroy()
      self.sidebar = None
      self.content_frame = None

    #menu bar function
    def build_logged_in_layout(self):
      self.clear_widgets()
    
      # Sidebar menu when user is logged in
      self.sidebar = ctk.CTkFrame(self, width=60, fg_color="white")
      self.sidebar.pack(side="left", fill="y")
      
      ctk.CTkLabel(self.sidebar, text="Menu", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))

      #-- Page buttons --#

      #Put each page button in its own frame
      home_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
      home_frame.pack(fill="x", pady=5, padx=5)
      
      ctk.CTkButton(home_frame, image=ctk.CTkImage(light_image=home_icon),text="Home", 
                    command=self.home, fg_color="white", text_color="black", 
                    anchor="w", compound="left", hover_color="#e6e6e6"
                    ).pack(pady=5)
     
      #separate pomodoro frame inside sidebar
      pomodoro_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", )
      pomodoro_frame.pack(fill="x", pady=5, padx=5)
      
      #pomodoro button
      ctk.CTkButton(pomodoro_frame, image=ctk.CTkImage(light_image=pomodoro_icon),
                    text="Pomodoro", command=self.build_pomodoro, fg_color="white", 
                    text_color="black", anchor="w", compound="left", hover_color="#e6e6e6",
                    ).pack(pady=5)
      
      #separate notes frame inside sidebar 
      notes_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
      notes_frame.pack(fill="x", pady=5, padx=5)
      
      #images button 
      ctk.CTkButton(notes_frame, image=ctk.CTkImage(light_image=notes_icon), text="Notes", 
                    command=self.build_notes, fg_color="white", text_color="black",
                    anchor="w", compound="left", hover_color="#e6e6e6",
                    ).pack(pady=5)  
      
      #separate tasks frame inside sidebar
      tasks_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
      tasks_frame.pack(fill="x", pady=5, padx=5)
      
      #tasks button
      ctk.CTkButton(tasks_frame, image=ctk.CTkImage(light_image=tasks_icon),
                    text="Tasks", command=self.build_tasks_page, fg_color="white", 
                    text_color="black", anchor="w", compound="left", hover_color="#e6e6e6",
                    ).pack(pady=5)
       
      #separate login frame inside sidebar
      logout_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
      logout_frame.pack(fill="x", pady=5, padx=5)
      
      #logout button
      ctk.CTkButton(self.sidebar, image=ctk.CTkImage(light_image=logout_icon),
                    text="Logout", command=self.logout, fg_color="white", 
                    text_color="black", anchor="w", compound="left", hover_color="#e6e6e6"
                    ).pack(side="bottom",pady=20)

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
      content_frame = ctk.CTkFrame(container, fg_color="transparent", 
                                   border_color="#d0d0d0", border_width=0.4, corner_radius=10)
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

      self.app_title = ctk.CTkLabel(header_frame, text = "Braintrain", 
                                    font=ctk.CTkFont(family="Huninn", size=55, weight="bold"))
      #self.app_title(anchor="center", padx=10, pady=(0,20))
      self.app_title.pack(side="left")

       
      #welcome widgets
      self.label = ctk.CTkLabel(innercont_frame, text="Login", 
                                font=ctk.CTkFont(family="Calibri", size=40, weight="normal"))
      self.label.pack(anchor="center", padx=10, pady=(0, 20))

      self.greeting = ctk.CTkLabel(innercont_frame, text="Hi there, 👋 Welcome!", 
                                   font=ctk.CTkFont(family="Calibri", size=18))
      self.greeting.pack(anchor="center", padx=10, pady=(0, 20))
      
      #email widgets
      self.email_label= ctk.CTkLabel(innercont_frame,text="Email", 
                                     font=ctk.CTkFont(family="Calibri", size=16, weight="bold"), 
                                     text_color="black",)
      self.email_label.pack(pady=0, anchor="w")

      self.email_entry = ctk.CTkEntry(innercont_frame, placeholder_text="", 
                                      width=400, height=50, fg_color="#F6E9FF", 
                                      border_color="black", border_width=0.5, 
                                      font=ctk.CTkFont(family="Calibri", size=16))
      self.email_entry.pack(pady=10)
      
      #password widgets
      self.password_label= ctk.CTkLabel(innercont_frame,text="Password", 
                                        font=ctk.CTkFont(family="Calibri", size=16, weight="bold"), 
                                        text_color="black")
      self.password_label.pack(pady=0, anchor="w")
      

      self.password_entry = ctk.CTkEntry(innercont_frame, placeholder_text="", 
                                         show="*", width=400, height=50, fg_color="#F6E9FF", border_color="black", border_width=0.5, font=ctk.CTkFont(family="Calibri", size=16))
      self.password_entry.pack(pady=5)

      self.login_btn = ctk.CTkButton(innercont_frame, text="Login", command=self.login, width=400, 
                                     height=50, fg_color="#4B0082", text_color="white", 
                                     font=ctk.CTkFont(family="Calibri", size=16), hover_color="#ff1493")
      self.login_btn.pack(pady=15)

      self.signup_link = ctk.CTkButton(innercont_frame, text="Don't have an account? Sign up", 
                                       command=self.build_signup, width=400, height=50, 
                                       fg_color="transparent", text_color="#4B0082", 
                                       font=ctk.CTkFont(family="Calibri", size=16, underline=True), 
                                       hover_color="white")
      self.signup_link.pack(pady=5)

      self.flash_label = ctk.CTkLabel(innercont_frame, text="")
      self.flash_label.pack(pady=(10, 0))

    # --- Right panel (unchanged) --- 
      right_panel = ctk.CTkFrame(self, fg_color="#4B0082", corner_radius=0)
      right_panel.place(relx=0.4, rely=0, relwidth=0.6, relheight=1)

     
    #signup page function
    def build_signup(self): 
        self.clear_widgets()

        gradient_bg = Image.open("images/braintain_gradient_bg.png")
        self.signup_bg=ctk.CTkImage(light_image=gradient_bg,
                                    size=(self.winfo_screenwidth(),
                                          self.winfo_screenheight()))
        bg_label = ctk.CTkLabel(self, image=self.signup_bg, text="")
        bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        wrapper_frame = ctk.CTkFrame(self, fg_color="#F6E9FF")
        wrapper_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        main_frame=ctk.CTkFrame(wrapper_frame, 
                                fg_color="white", 
                                width=350, 
                                height=500, 
                                corner_radius=20,
                                ) 
        main_frame.pack()
        main_frame.pack_propagate(False)
        
        inner_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        inner_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center inside main_frame

        self.label = ctk.CTkLabel(inner_frame, text="Sign Up", font=ctk.CTkFont(size=30, weight="bold"))
        self.label.pack(pady=10)
        
        #text entries
        self.email_entry = ctk.CTkEntry(inner_frame, placeholder_text="Email")
        self.email_entry.pack(pady=(20, 10))
        self.name_entry = ctk.CTkEntry(inner_frame, placeholder_text="First Name")
        self.name_entry.pack(pady=10)
        self.password1 = ctk.CTkEntry(inner_frame, placeholder_text="Password", show="*")
        self.password1.pack(pady=10)
        self.password2 = ctk.CTkEntry(inner_frame, placeholder_text="Confirm Password", show="*")
        self.password2.pack(pady=10)

        self.signup_btn = ctk.CTkButton(inner_frame, text="Create Account", command=self.signup)
        self.signup_btn.pack(pady=10)

        self.login_link = ctk.CTkButton(inner_frame, text="Back to Login", command=self.build_login)
        self.login_link.pack(pady=10)

        self.flash_label = ctk.CTkLabel(main_frame, text="")
        self.flash_label.pack()
    
    #homepage function
    def build_notes(self):
      
      for widget in self.content_frame.winfo_children():
        widget.destroy()

      ctk.CTkLabel(self.content_frame, text="My Notes", font=ctk.CTkFont(size=50, weight="bold")).pack(pady=5)

      self.note_entry = ctk.CTkTextbox(self.content_frame, height=100, width=400)
      self.note_entry.pack(pady=10)

      self.add_btn = ctk.CTkButton(self.content_frame, text="Add Note", command=self.add_note)
      self.add_btn.pack(pady=5)

      self.notes_frame = ctk.CTkFrame(self.content_frame)
      self.notes_frame.pack(pady=50, fill="both", expand=True)

      self.load_notes()

    def home(self):

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        bg_frame = ctk.CTkFrame(self.content_frame, 
                                fg_color="#4B0082")
        bg_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(bg_frame, text=f"Welcome, {self.current_user[2]}", font=ctk.CTkFont(size=18, weight="bold"), text_color="white").pack(pady=20)
        
        overview_frame = ctk.CTkFrame(bg_frame, fg_color="#3A0066")
        overview_frame.pack(pady=10)

        ctk.CTkLabel(overview_frame, 
                     text="Today's Overview",
                     font=ctk.CTkFont(size=22, weight="bold"), 
                     text_color="white").pack(pady=10)
        

        
        # Grid for tiles
        tiles_frame = ctk.CTkFrame(overview_frame,
                                   fg_color="transparent")
        tiles_frame.pack(padx=20,pady=10)
        tiles_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)


        tasks_today = self.get_tasks_due_today()
        task_tile = self.create_summary_tile(tiles_frame, "Tasks Today", 
                                              str(tasks_today), 
                                              "#FF69B4")
        task_tile.grid(row=0, column=0, padx=15, pady=10)

        #upcoming tasks frame
        upcoming_frame = ctk.CTkFrame(bg_frame, fg_color="white")
        upcoming_frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(upcoming_frame, text="Upcoming Tasks (Next 2 Weeks)",
                    font=ctk.CTkFont(size=18, weight="bold"), text_color="black").pack(anchor="w", padx=10, pady=(10, 5))

        tasks = self.get_upcoming_tasks()
        if tasks:
            for name, subject, due_date in tasks:
                ctk.CTkLabel(upcoming_frame,
                            text=f"{name} | {subject} | Due: {due_date}",
                            text_color="black", anchor="w",
                            font=ctk.CTkFont(size=14)).pack(anchor="w", padx=15, pady=2)
        else:
            ctk.CTkLabel(upcoming_frame,
                        text="No upcoming tasks!",
                        text_color="gray", anchor="w").pack(anchor="w", padx=15, pady=5)


    def get_upcoming_tasks(self):
        from datetime import datetime, timedelta
        today = datetime.now().date()
        two_weeks = today + timedelta(days=14)
        c.execute("SELECT name, subject, due_date FROM tasks WHERE user_id=? AND due_date BETWEEN ? AND ?",
                (self.current_user[0], today.isoformat(), two_weeks.isoformat()))
        return c.fetchall()

    def create_summary_tile(self, parent, title, value, color):
        tile = ctk.CTkFrame(parent, 
                            width=150, 
                            height=100, 
                            fg_color=color,
                            corner_radius=12)
        tile.pack_propagate(False)
        ctk.CTkLabel(tile, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="black").pack(pady=(8, 0))
        ctk.CTkLabel(tile, text=value, font=ctk.CTkFont(size=26, weight="bold"), text_color="black").pack()
        return tile
    
    def get_tasks_due_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute("SELECT COUNT(*) FROM tasks WHERE user_id=? AND due_date=?", (self.current_user[0], today))
        result = c.fetchone()
        return result[0] if result else 0
    
    def get_pomodoro_count(self):
        return 2


    def get_notes_count(self):
        c.execute("SELECT COUNT(*) FROM notes WHERE user_id=?", (self.current_user[0],))
        result = c.fetchone
        return result[0] if result else 0          
        
    
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
        
        bg_frame = ctk.CTkFrame(self.content_frame, 
                                fg_color="#4B0082")
        bg_frame.pack(fill="both", expand=True)

        # Create a centered frame for all pomodoro elements
        center_frame = ctk.CTkFrame(bg_frame, width=700, height=500)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame
        center_frame.pack_propagate(False)

        # Inner content wrapper to center elements vertically and horizontally
        content_wrapper = ctk.CTkFrame(center_frame, fg_color="transparent")
        content_wrapper.pack(expand=True)  # Vertically center the wrapper


        ctk.CTkLabel(content_wrapper, text="Pomodoro Timer", font=ctk.CTkFont(size=50, weight="bold")).pack(pady=10)
        
        self.session_label = ctk.CTkLabel(content_wrapper, text="Work Session", font=ctk.CTkFont(size=18))
        self.session_label.pack(pady=5)
        
        self.timer_label = ctk.CTkLabel(content_wrapper, text="25:00", font=ctk.CTkFont(size=100), width=400,
                                        )
        self.timer_label.pack(pady=20)

        # Create a horizontal frame for the buttons
        button_row = ctk.CTkFrame(content_wrapper, fg_color="transparent")
        button_row.pack(pady=10)

        self.start_button = ctk.CTkButton(button_row, text="Start", command=self.start_timer, width=100)
        self.start_button.pack(side="left", padx=5)

        self.pause_button = ctk.CTkButton(button_row, text="Pause", command=self.pause_timer, width=100)
        self.pause_button.pack(side="left", padx=5)

        self.reset_button = ctk.CTkButton(button_row, text="Reset", command=self.reset_timer, width=100)
        self.reset_button.pack(side="left", padx=5)

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
                if not self.on_break:
                    # Work session just finished, start break
                    self.on_break = True
                    self.timer_seconds = 5 * 60  # 5-minute break
                    self.session_label.configure(text="Break Time!", text_color="green")
                    self.start_timer()  # Automatically start break
                else:
                    # Break finished, go back to work session
                    self.on_break = False
                    self.timer_seconds = 25 * 60  # 25-minute session again
                    self.session_label.configure(text="Work Time!", text_color="blue")
                    self.start_timer()

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
            ctk.CTkButton(note_row, image=ctk.CTkImage(light_image=delete_icon),text="Delete", width=70, command=lambda nid=note_id: self.delete_note(nid)).pack(side="right", padx=5)
   
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
      
      ctk.CTkLabel(self.content_frame, text="My Tasks", 
             font=ctk.CTkFont(size=50, weight="bold"), 
             text_color="black").pack(pady=(10, 0))

      self.tasks_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="#4B0082")
      self.tasks_frame.pack(fill="both", expand=True, padx=20, pady=20)

      task_header = ctk.CTkFrame(self.tasks_frame, fg_color="#4B0082")
      task_header.grid(row=0, column=0, columnspan=4, sticky="ew")
      ctk.CTkButton(task_header, text="Add Subject", command=self.add_subject_popup, 
                    fg_color="#FF69B4", text_color="black",
                    image=ctk.CTkImage(light_image=add_icon),
                    hover_color="none").pack(side="left", padx=10)
      
      ctk.CTkButton(task_header, text="New Task", command=self.add_task_popup, 
                    fg_color="#FF69B4", text_color="black",
                    image=ctk.CTkImage(light_image=add_icon),
                    hover_color="none").pack(side="right", padx=10)

      self.load_tasks_grid()

    def load_tasks_grid(self):
        for widget in self.tasks_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self.tasks_frame.winfo_children()[0]:
                widget.destroy()
        c.execute("SELECT id, name, subject, due_date FROM tasks WHERE user_id=?", (self.current_user[0],))
        tasks = c.fetchall()
        if not hasattr(self, 'task_list'):
            self.task_list = []

        for idx, task in enumerate(tasks):
            task_id, name, subject, due_date = task
            frame = ctk.CTkFrame(self.tasks_frame, border_width=1, corner_radius=10, width=300, height=150)
            frame.grid(row=(idx // 5) + 1, column=idx % 5, padx=10, pady=10, sticky="nsew")
            frame.grid_propagate(False)

            ctk.CTkLabel(frame, text=f"Name: {name}", wraplength=280).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(frame, text=f"Subject: {subject}", wraplength=280).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(frame, text=f"Due: {due_date}", wraplength=280).pack(anchor="w", padx=10, pady=2)

            

            ctk.CTkButton(frame, text="Mark Complete", 
                          command=lambda tid=task_id: self.mark_task_complete(tid), 
                          fg_color="green", border_width=1, 
                          image=ctk.CTkImage(light_image=task_complete_icon),
                          text_color="white",
                          border_color="green",
                          hover_color="none").pack(pady=2)

    def add_subject_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Add Subject")
        popup.grab_set()
        popup.attributes('-topmost', True)

        ctk.CTkLabel(popup, text="New Subject").pack(pady=10)
        subject_entry = ctk.CTkEntry(popup)
        subject_entry.pack(pady=5)

        def save_subject():
            if not hasattr(self, 'subjects'):
                self.subjects = []
            self.subjects.append(subject_entry.get())
            popup.destroy()

        ctk.CTkButton(popup, text="Save", command=save_subject, 
                      fg_color="#4B0082").pack(pady=10)

    def add_task_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Create New Task")
        popup.grab_set()
        popup.attributes('-topmost', True)

        ctk.CTkLabel(popup, text="Task Name").pack(pady=5)
        name_entry = ctk.CTkEntry(popup)
        name_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Subject").pack(pady=5)
        
        subject_combobox = ctk.CTkComboBox(popup, values=getattr(self, 'subjects', []))
        subject_combobox.set("")  # Set blank by default
        subject_combobox.pack(pady=5)

        ctk.CTkLabel(popup, text="Due Date").pack(pady=5)

        # Embed DateEntry inside a tk.Frame so it displays correctly inside a CTk popup
        calendar_frame = tk.Frame(popup)  # standard tkinter frame
        calendar_frame.pack(pady=5)

        due_entry = DateEntry(calendar_frame, width=20, background='darkblue', foreground='white',
                            borderwidth=2, date_pattern='yyyy-mm-dd')
        due_entry.pack()


        def save_task():
            new_task = {
                'name': name_entry.get(),
                'subject': subject_combobox.get(),
                'due_date': due_entry.get()
            }
            if not hasattr(self, 'task_list'):
                self.task_list = []
            c.execute("INSERT INTO tasks (user_id, name, subject, due_date) VALUES (?, ?, ?, ?)",
            (self.current_user[0], name_entry.get(), subject_combobox.get(), due_entry.get()))
            conn.commit()
            self.load_tasks_grid()

            popup.destroy()

        ctk.CTkButton(popup, text="Create Task", command=save_task, fg_color="#4B0082").pack(pady=10)

    def view_task_popup(self, task):
        popup = ctk.CTkToplevel(self)
        popup.title("View Task")
        popup.grab_set()
        popup.attributes('-topmost', True)

        ctk.CTkLabel(popup, text=f"Name: {task['name']}").pack(pady=5)
        ctk.CTkLabel(popup, text=f"Subject: {task['subject']}").pack(pady=5)
        ctk.CTkLabel(popup, text=f"Due Date: {task['due_date']}").pack(pady=5)

    def mark_task_complete(self, task):
        c.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task, self.current_user[0]))
        conn.commit()
        self.load_tasks_grid()

#runs the app continuouslyu
if __name__ == "__main__":
    app = App()
    app.mainloop()