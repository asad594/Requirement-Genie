import tkinter as tk
from tkinter import Frame, Canvas, Scrollbar, BOTH, LEFT, RIGHT, Y, X, CENTER, Label, Button, BOTTOM
from tkinter.simpledialog import askstring
from datetime import datetime
from backend import Backend
from auth import Auth
import pathlib
import math
import random
import os


class RequirementGenieUI:

    BG_COLOR = "#2C2F33"
    SIDEBAR_COLOR = "#23272A"
    ACCENT_COLOR = "#00A8FC"
    TEXT_COLOR = "#FFFFFF"
    SUBTEXT_COLOR = "#B9BBBE"
    
    # Message Bubbles
    USER_BUBBLE_COLOR = "#00A8FC" # Blue
    BOT_BUBBLE_COLOR = "#FFFFFF"
    USER_TEXT_COLOR = "#FFFFFF"
    BOT_TEXT_COLOR = "#2C2F33"

    def __init__(self, master):
        self.master = master
        self.master.title("Requirement Genie - Desktop Assistant")
        self.master.geometry("1100x800")
        self.master.configure(bg=self.BG_COLOR)

        self.chat_sessions = []

        self.backend = Backend("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")

        self.auth = Auth()
        self.current_user = None

        self.setup_login_ui()

    def setup_splash_ui(self):
        self.master.configure(bg=self.BG_COLOR)
        
        self.splash_canvas = Canvas(self.master, bg=self.BG_COLOR, highlightthickness=0)
        self.splash_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._draw_constellations(self.splash_canvas)

        cx = 550 # Center of 1100
        cy = 400 # Center of 800
        
        self.splash_canvas.create_oval(cx - 150, cy - 250, cx + 150, cy + 50, fill="#23272A", outline="", tags="center_content")
        
        self._draw_genie_icon(self.splash_canvas, cx, cy - 120)

        self.splash_canvas.create_text(cx, cy + 20, text="Requirement Genie", font=("Inter", 36, "bold"), fill="white", tags="center_content")

        self.splash_canvas.create_text(cx, cy + 70, text="Your Smart Requirement Engineering Assistant", font=("Inter", 12), fill=self.SUBTEXT_COLOR, tags="center_content")

        self._draw_gradient_button(self.splash_canvas, cx, cy + 130)

        self.master.bind("<Configure>", self._on_resize_splash)

        self.pulse_step = 0
        self._animate_pulse()

    def _draw_constellations(self, canvas):
        width = 1200
        height = 900
        canvas.create_line(0, 100, 200, 300, fill=self.ACCENT_COLOR, width=1, dash=(4, 4))
        canvas.create_oval(195, 295, 205, 305, fill="white", outline="")
        
        canvas.create_line(width, 150, width - 250, 250, fill=self.ACCENT_COLOR, width=1, dash=(4, 4))
        
        for _ in range(30):
            x = random.randint(0, width)
            y = random.randint(0, height)
            if x < 300 or x > width - 300:
                r = random.randint(1, 3)
                canvas.create_oval(x, y, x+r, y+r, fill=self.ACCENT_COLOR, outline="")

    def _draw_genie_icon(self, canvas, x, y):
        r_pulse = 50
        canvas.create_oval(x-r_pulse, y-r_pulse, x+r_pulse, y+r_pulse, 
                           outline=self.ACCENT_COLOR, width=2, 
                           tags=("center_content", "pulse_ring"))

        canvas.create_oval(x-40, y-40, x+40, y+40, fill="#2C2F33", outline=self.ACCENT_COLOR, width=3, tags="center_content")
        
        canvas.create_oval(x-25, y-10, x-10, y+10, fill="#00E6FF", outline="", tags="center_content")
        canvas.create_oval(x+10, y-10, x+25, y+10, fill="#00E6FF", outline="", tags="center_content")
        
        canvas.create_line(x, y-40, x, y-60, fill=self.ACCENT_COLOR, width=2, tags="center_content")
        canvas.create_oval(x-5, y-65, x+5, y-55, fill="#FF0055", outline="", tags="center_content") # Red Sensor Tip

        canvas.create_line(x-15, y+25, x+15, y+25, fill="white", width=2, tags="center_content")

    def _animate_pulse(self):
        if hasattr(self, 'splash_canvas') and self.splash_canvas.winfo_exists():
            import math
            self.pulse_step += 0.1
            scale = 50 + 5 * math.sin(self.pulse_step) # Radius oscillates between 45 and 55
            

            coords = self.splash_canvas.coords("pulse_ring")
            if coords:
                x1, y1, x2, y2 = coords
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                
                self.splash_canvas.coords("pulse_ring", cx-scale, cy-scale, cx+scale, cy+scale)
                
                w = 2 + 1.5 * math.sin(self.pulse_step)
                self.splash_canvas.itemconfigure("pulse_ring", width=w)

            self.master.after(50, self._animate_pulse)

    def _draw_gradient_button(self, canvas, x, y):
        w, h = 200, 50
        x1, y1 = x - w // 2, y - h // 2
        x2, y2 = x + w // 2, y + h // 2
        r = 25
        btn_bg = canvas.create_line(x1+r, y, x2-r, y, width=h, capstyle=tk.ROUND, fill=self.ACCENT_COLOR, tags=("start_btn", "center_content"))
        
        canvas.create_text(x, y, text="Start Session", font=("Inter", 12, "bold"), fill="white", tags=("start_btn", "center_content"))
        
        canvas.tag_bind("start_btn", "<Button-1>", lambda e: self.start_main_session())
        canvas.tag_bind("start_btn", "<Enter>", lambda e: canvas.itemconfig(btn_bg, fill="#008ED6"))
        canvas.tag_bind("start_btn", "<Leave>", lambda e: canvas.itemconfig(btn_bg, fill=self.ACCENT_COLOR))

    def _on_resize_splash(self, event):
        if hasattr(self, 'splash_canvas') and self.splash_canvas.winfo_exists():
            w, h = event.width, event.height
            self.splash_canvas.config(width=w, height=h)

            self.splash_canvas.delete("center_content")
            cx, cy = w/2, h/2
            self.splash_canvas.create_oval(cx - 150, cy - 250, cx + 150, cy + 50, fill="#23272A", outline="", tags="center_content")
            self._draw_genie_icon(self.splash_canvas, cx, cy - 120)
            self.splash_canvas.create_text(cx, cy + 20, text="Requirement Genie", font=("Inter", 36, "bold"), fill="white", tags="center_content")
            self.splash_canvas.create_text(cx, cy + 70, text="Your Smart Requirement Engineering Assistant", font=("Inter", 12), fill=self.SUBTEXT_COLOR, tags="center_content")
            self._draw_gradient_button(self.splash_canvas, cx, cy + 130)

    def start_main_session(self):
        if hasattr(self, 'splash_canvas'): self.splash_canvas.destroy()
        
        project_name = askstring("New Project", "Enter project name for this session:")
        if not project_name:
            project_name = "Untitled_" + datetime.now().strftime("%H%M%S")
            
        self.backend.project_name = project_name.strip().replace(" ", "_")
        desktop = pathlib.Path.home() / "Desktop"
        try:
            if self.backend.file_path.exists(): os.remove(self.backend.file_path)
        except: pass
        self.backend.file_path = desktop / f"Requirements_{self.backend.project_name}.txt"
        
        with open(self.backend.file_path, "w", encoding="utf-8") as f:
            f.write(f"Project: {project_name}\n")
            f.write("=" * 40 + "\n")
            
        self.chat_sessions.append({"title": project_name, "backend": self.backend})
        self.setup_main_ui()

    def setup_main_ui(self):
        self.master.configure(bg=self.BG_COLOR)

        sidebar = Frame(self.master, bg=self.SIDEBAR_COLOR, width=280)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)

        logo_frame = Frame(sidebar, bg=self.SIDEBAR_COLOR, height=80)
        logo_frame.pack(fill=X, pady=(40, 10), padx=20)
        
        center_container = Frame(logo_frame, bg=self.SIDEBAR_COLOR)
        center_container.pack() # Defaults to center

        logo_icon = Label(center_container, text="🤖", font=("Segoe UI Emoji", 22), fg=self.TEXT_COLOR, bg=self.SIDEBAR_COLOR)
        logo_icon.pack(side=LEFT, padx=(0, 10))

        logo_lbl = Label(center_container, text="REQ.AI", font=("Inter", 22, "bold"), fg=self.TEXT_COLOR, bg=self.SIDEBAR_COLOR)
        logo_lbl.pack(side=LEFT)

        new_chat_btn = tk.Button(
            sidebar,
            text="+ New Chat",
            font=("Inter", 14, "bold"),
            bg=self.ACCENT_COLOR,
            fg="white",
            activebackground="#008ED6", # Slightly darker blue
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.start_new_chat
        )
        new_chat_btn.pack(fill=X, padx=20, pady=15, ipady=8) 

        hist_lbl = Label(sidebar, text="Previous Chats", font=("Inter", 10, "bold"), fg=self.SUBTEXT_COLOR, bg=self.SIDEBAR_COLOR)
        hist_lbl.pack(anchor="w", padx=20, pady=(10, 5))

        hist_container = Frame(sidebar, bg=self.SIDEBAR_COLOR)
        hist_container.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        self.hist_canvas = Canvas(hist_container, bg=self.SIDEBAR_COLOR, highlightthickness=0)
        self.hist_scrollbar = Scrollbar(hist_container, orient="vertical", command=self.hist_canvas.yview)
        self.hist_frame = Frame(self.hist_canvas, bg=self.SIDEBAR_COLOR)

        self.hist_frame.bind("<Configure>", lambda e: self.hist_canvas.configure(scrollregion=self.hist_canvas.bbox("all")))
        self.hist_canvas.create_window((0, 0), window=self.hist_frame, anchor="nw", width=240) # Fixed width for scroll
        self.hist_canvas.configure(yscrollcommand=self.hist_scrollbar.set)
        
        self.hist_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.hist_scrollbar.pack(side=RIGHT, fill=Y)

        self.load_previous_chats()


        main_content = Frame(self.master, bg=self.BG_COLOR)
        main_content.pack(side=RIGHT, fill=BOTH, expand=True)

        header_frame = Frame(main_content, bg=self.BG_COLOR, height=80)
        header_frame.pack(fill=X, pady=(20, 0))
        
        title_lbl = Label(header_frame, text="Requirement Genie", font=("Inter", 24, "bold"), fg=self.TEXT_COLOR, bg=self.BG_COLOR)
        title_lbl.pack()
        subtitle_lbl = Label(header_frame, text="Your Smart Requirement Engineering Assistant", font=("Inter", 11), fg=self.SUBTEXT_COLOR, bg=self.BG_COLOR)
        subtitle_lbl.pack()

        sep_line = Frame(main_content, bg=self.ACCENT_COLOR, height=2)
        sep_line.pack(fill=X, pady=(15, 0), padx=0)


        chat_container = Frame(main_content, bg=self.BG_COLOR)
        chat_container.pack(fill=BOTH, expand=True, padx=10, pady=20)

        CHAT_BOX_BG = "#36393F"
        
        self.chat_canvas = Canvas(chat_container, bg=CHAT_BOX_BG, highlightthickness=0)
        self.chat_scrollbar = Scrollbar(chat_container, orient="vertical", command=self.chat_canvas.yview)
        self.chat_frame = Frame(self.chat_canvas, bg=CHAT_BOX_BG)

        self.chat_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw", width=950) # Approx width
        
        self.chat_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.chat_scrollbar.pack(side=RIGHT, fill=Y, padx=5)

        self.chat_canvas.bind("<Enter>", lambda e: self.chat_canvas.bind_all("<MouseWheel>", self.mouse_scroll))
        self.chat_canvas.bind("<Leave>", lambda e: self.chat_canvas.unbind_all("<MouseWheel>"))


        input_container = Frame(main_content, bg=self.BG_COLOR, height=80)
        input_container.pack(fill=X, side=BOTTOM, pady=5, padx=10)
        
        self._draw_input_pill(input_container)


        self.add_message("Bot", self.backend.initial_greeting)


    def _draw_input_pill(self, parent):
        """Creates a rounded pill-shaped input area"""
        input_bg = "#40444B"
        
        self.send_btn = Button(
            parent, text="➔", font=("Inter", 16, "bold"),
            bg=self.ACCENT_COLOR, fg="white",
            activebackground="#008ED6", activeforeground="white",
            relief="flat", bd=0, highlightthickness=0,
            cursor="hand2",
            width=3, command=self.send_message
        )
        self.send_btn.pack(side=RIGHT, padx=(10, 0), pady=0, fill=Y)

        self.entry = tk.Text(
            parent, height=2, font=("Inter", 12),
            bg=input_bg, fg="white", insertbackground="white",
            relief="flat", bd=0, highlightthickness=0, 
            padx=10, pady=10, wrap="word"
        )
        self.entry.pack(side=LEFT, fill=BOTH, expand=True)
        self.entry.bind("<Return>", self.enter_send)
        self.entry.bind("<Shift-Return>", self.newline)


    def send_message(self):
        user_text = self.entry.get("1.0", "end-1c").strip()
        if not user_text:
            return
        self.entry.delete("1.0", tk.END)
        self.add_message("User", user_text)
        bot_reply = self.backend.get_response(user_text)
        self.add_message("Bot", bot_reply)

    def newline(self, event):
        return

    def enter_send(self, event):
        user_text = self.entry.get("1.0", tk.END).strip()
        if not user_text:
            return "break"
        self.entry.delete("1.0", tk.END)
        self.add_message("User", user_text)
        bot_reply = self.backend.get_response(user_text)
        self.add_message("Bot", bot_reply)
        return "break"

    def mouse_scroll(self, event):
        self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def start_new_chat(self):
        project_name = askstring("New Project", "Enter project name:")
        if not project_name:
            return
        new_backend = Backend("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")
        new_backend.project_name = project_name.strip().replace(" ", "_")
        desktop = pathlib.Path.home() / "Desktop"
        try:
            if new_backend.file_path.exists():
                os.remove(new_backend.file_path)
        except: pass
        new_backend.file_path = desktop / f"Requirements_{new_backend.project_name}.txt"

        with open(new_backend.file_path, "w", encoding="utf-8") as f:
            f.write(f"Project: {project_name}\n")
            f.write(f"Created On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 40 + "\n")
        
        self.chat_sessions.append({"title": project_name, "backend": new_backend})
        self.backend = new_backend
        
        # Clear chat
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        
        self.add_message("Bot", self.backend.initial_greeting)
        self.refresh_chat_history()

    def refresh_chat_history(self):
        for widget in self.hist_frame.winfo_children():
            widget.destroy()
            
        for idx, session in enumerate(self.chat_sessions):
            btn = Button(
                self.hist_frame, text="📄 " + session["title"],
                font=("Inter", 10), anchor="w",
                bg=self.SIDEBAR_COLOR, fg=self.SUBTEXT_COLOR,
                activebackground=self.BG_COLOR, activeforeground="white",
                relief="flat", bd=0, padx=10, pady=5,
                command=lambda i=idx: self.load_chat(i)
            )
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#36393F", fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.SIDEBAR_COLOR, fg=self.SUBTEXT_COLOR))
            btn.pack(fill=X, pady=1)

    def load_chat(self, index):
        session = self.chat_sessions[index]
        self.backend = session["backend"]
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        for msg in self.backend.message_history:
            self.add_message(msg["sender"], msg["text"])

    def load_previous_chats(self):
        desktop = pathlib.Path.home() / "Desktop"
        files = sorted(desktop.glob("Requirements_*.txt"), reverse=True)
        for file in files:
            btn = Button(
                self.hist_frame, text="📄 " + file.stem,
                font=("Inter", 10), anchor="w",
                bg=self.SIDEBAR_COLOR, fg=self.SUBTEXT_COLOR,
                activebackground=self.BG_COLOR, activeforeground="white",
                relief="flat", bd=0, padx=10, pady=5,
                command=lambda f=file: self.open_previous_chat(f)
            )
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#36393F", fg="white"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.SIDEBAR_COLOR, fg=self.SUBTEXT_COLOR))
            btn.pack(fill=X, pady=1)

    def open_previous_chat(self, file_path):
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line or line.startswith("="): continue
                if line.startswith("User: "): self.add_message("User", line.replace("User: ", ""))
                elif line.startswith("Bot: "): self.add_message("Bot", line.replace("Bot: ", ""))
                elif line.startswith("Question: "): self.add_message("User", line.replace("Question: ", ""))
                elif line.startswith("Answer: "): self.add_message("Bot", line.replace("Answer: ", ""))
                else: self.add_message("Bot", line)
        except Exception as e:
            self.add_message("Bot", f"Error: {e}")

    def add_message(self, sender, text):
        timestamp = datetime.now().strftime("%I:%M %p")
        is_user = sender == "User"
        
        bg_col = self.USER_BUBBLE_COLOR if is_user else self.BOT_BUBBLE_COLOR
        txt_col = self.USER_TEXT_COLOR if is_user else self.BOT_TEXT_COLOR
        align = RIGHT if is_user else LEFT
        
        container_bg = "#36393F" 

        msg_frame = Frame(self.chat_frame, bg=container_bg)
        msg_frame.pack(fill=X, pady=10, padx=20)

        icon_char = "👤" if is_user else "🤖"
        icon_lbl = Label(msg_frame, text=icon_char, font=("Segoe UI Emoji", 24), bg=container_bg, fg="white")
        
        if is_user:
            icon_lbl.pack(side=RIGHT, padx=(5, 0), anchor="ne")
        else:
            icon_lbl.pack(side=LEFT, padx=(0, 10), anchor="nw")

        bubble_frame = Frame(msg_frame, bg=bg_col, padx=15, pady=8)
        bubble_frame.pack(side=align, anchor="e" if is_user else "w")

        content_lbl = Label(
            bubble_frame, text=text,
            font=("Inter", 12),
            bg=bg_col, fg=txt_col,
            wraplength=780, justify=LEFT,
            relief="flat" 
        )
        content_lbl.pack(anchor="w", fill=X)

        # Timestamp (Inside the box, bottom right)
        # Adjust timestamp color for readability on different backgrounds
        ts_fg = "#E0E0E0" if is_user else "#888888" 
        ts_lbl = Label(
            bubble_frame, text=timestamp, 
            font=("Inter", 8), 
            bg=bg_col, fg=ts_fg
        )
        ts_lbl.pack(anchor="e", pady=(2, 0))

        self.master.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)



    def clear_frame(self):
        """Destroys all children of the master window to switch screens."""
        for widget in self.master.winfo_children():
            widget.destroy()

    def setup_login_ui(self):
        self.clear_frame()
        self.master.configure(bg=self.BG_COLOR)

        # Background Canvas
        bg_canvas = Canvas(self.master, bg=self.BG_COLOR, highlightthickness=0)
        bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._draw_constellations(bg_canvas)
        
        # Center Card Frame
        card_frame = Frame(self.master, bg=self.SIDEBAR_COLOR, highlightthickness=2, highlightbackground=self.ACCENT_COLOR)
        card_frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=400, height=500)
        
        # Title
        Label(card_frame, text="Welcome Back", font=("Inter", 24, "bold"), bg=self.SIDEBAR_COLOR, fg="white").pack(pady=(50, 5))
        Label(card_frame, text="Please log in to continue", font=("Inter", 12), bg=self.SIDEBAR_COLOR, fg=self.SUBTEXT_COLOR).pack(pady=(0, 30))

        # Content Container (for padding)
        form_frame = Frame(card_frame, bg=self.SIDEBAR_COLOR)
        form_frame.pack(fill=BOTH, expand=True, padx=50)

        # Username
        Label(form_frame, text="Username", bg=self.SIDEBAR_COLOR, fg="white", font=("Inter", 10)).pack(anchor="w", pady=(0, 5))
        self.login_user_entry = tk.Entry(form_frame, font=("Inter", 12), bg=self.BG_COLOR, fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground=self.ACCENT_COLOR)
        self.login_user_entry.pack(fill=X, pady=(0, 20), ipady=5)

        # Password
        Label(form_frame, text="Password", bg=self.SIDEBAR_COLOR, fg="white", font=("Inter", 10)).pack(anchor="w", pady=(0, 5))
        self.login_pass_entry = tk.Entry(form_frame, font=("Inter", 12), bg=self.BG_COLOR, fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground=self.ACCENT_COLOR, show="•")
        self.login_pass_entry.pack(fill=X, pady=(0, 30), ipady=5)

        login_btn = Button(
            form_frame, text="Login", font=("Inter", 12, "bold"),
            bg=self.ACCENT_COLOR, fg="white", activebackground="#008ED6", activeforeground="white",
            relief="flat", cursor="hand2", command=self.perform_login
        )
        login_btn.pack(fill=X, ipady=5)

        link_lbl = Label(form_frame, text="Don't have an account? Sign Up", bg=self.SIDEBAR_COLOR, fg=self.ACCENT_COLOR, font=("Inter", 10, "underline"), cursor="hand2")
        link_lbl.pack(pady=20)
        link_lbl.bind("<Button-1>", lambda e: self.setup_signup_ui())
        
        self.status_lbl = Label(form_frame, text="", bg=self.SIDEBAR_COLOR, fg="red", font=("Inter", 10))
        self.status_lbl.pack(pady=5)

    def setup_signup_ui(self):
        self.clear_frame()
        self.master.configure(bg=self.BG_COLOR)

        # Background Canvas
        bg_canvas = Canvas(self.master, bg=self.BG_COLOR, highlightthickness=0)
        bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._draw_constellations(bg_canvas)

        # Center Card Frame
        card_frame = Frame(self.master, bg=self.SIDEBAR_COLOR, highlightthickness=2, highlightbackground=self.ACCENT_COLOR)
        card_frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=400, height=500)
        
        # Title
        Label(card_frame, text="Create Account", font=("Inter", 24, "bold"), bg=self.SIDEBAR_COLOR, fg="white").pack(pady=(50, 5))
        Label(card_frame, text="Join Requirement Genie today", font=("Inter", 12), bg=self.SIDEBAR_COLOR, fg=self.SUBTEXT_COLOR).pack(pady=(0, 30))

        # Content Container
        form_frame = Frame(card_frame, bg=self.SIDEBAR_COLOR)
        form_frame.pack(fill=BOTH, expand=True, padx=50)

        Label(form_frame, text="Choose Username", bg=self.SIDEBAR_COLOR, fg="white", font=("Inter", 10)).pack(anchor="w", pady=(0, 5))
        self.signup_user_entry = tk.Entry(form_frame, font=("Inter", 12), bg=self.BG_COLOR, fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground=self.ACCENT_COLOR)
        self.signup_user_entry.pack(fill=X, pady=(0, 20), ipady=5)

        Label(form_frame, text="Choose Password", bg=self.SIDEBAR_COLOR, fg="white", font=("Inter", 10)).pack(anchor="w", pady=(0, 5))
        self.signup_pass_entry = tk.Entry(form_frame, font=("Inter", 12), bg=self.BG_COLOR, fg="white", insertbackground="white", relief="flat", highlightthickness=1, highlightbackground=self.ACCENT_COLOR, show="•")
        self.signup_pass_entry.pack(fill=X, pady=(0, 30), ipady=5)

        signup_btn = Button(
            form_frame, text="Sign Up", font=("Inter", 12, "bold"),
            bg=self.ACCENT_COLOR, fg="white", activebackground="#008ED6", activeforeground="white",
            relief="flat", cursor="hand2", command=self.perform_signup
        )
        signup_btn.pack(fill=X, ipady=5)

        link_lbl = Label(form_frame, text="Already have an account? Login", bg=self.SIDEBAR_COLOR, fg=self.ACCENT_COLOR, font=("Inter", 10, "underline"), cursor="hand2")
        link_lbl.pack(pady=20)
        link_lbl.bind("<Button-1>", lambda e: self.setup_login_ui())

        self.status_lbl = Label(form_frame, text="", bg=self.SIDEBAR_COLOR, fg="red", font=("Inter", 10))
        self.status_lbl.pack(pady=5)

    def perform_login(self):
        username = self.login_user_entry.get().strip()
        password = self.login_pass_entry.get().strip()
        
        success, msg = self.auth.login(username, password)
        if success:
            self.current_user = username
            self.clear_frame()
            self.setup_splash_ui()
        else:
            self.status_lbl.config(text=msg, fg="#FF5555")

    def perform_signup(self):
        username = self.signup_user_entry.get().strip()
        password = self.signup_pass_entry.get().strip()
        
        success, msg = self.auth.signup(username, password)
        if success:
            # Auto login or ask to login? Let's just go to login page with success msg
            self.setup_login_ui()
            self.status_lbl.config(text=msg, fg="#55FF55") # Success color
        else:
            self.status_lbl.config(text=msg, fg="#FF5555")
