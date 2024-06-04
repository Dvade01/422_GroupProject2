"""
CS 422/522 Software Engineering Project: PDF Active-Reading Assistant (ARA)
Authors: Ryan Helms, William Qiu, Nikhar Ramlakhan, Abie Safdie, Caleb Sutherland
Released: 4/29/2024

This file, ARA.py, is the main driver for loading our Active-Reading Assistant app. 

The ARA app is designed to support SQ3R reading methods on PDFS. The user can view pre-loaded pdfs and take notes on them using these methods.
Their notes are able to be stored on a database to allow transfer of notes across machines. 
There are 3 pre-defined users that the user can log in as, however they may add as many users as they wish.
User storing and loading of notes dependent on a working communication to the database.

To set up the database and more information on how to use this software see our Installation Instruction pdf 
    and our programmer and user documentation pdfs located in our submission

Have fun applying SQ3R!!!

"""

import tkinter as tk    # GUI library
from tkinter import messagebox   # Messagebox: enables pop up window to display on errors
import fitz  # PyMuPDF: allows PDFS to be loaded into tkinter gui
import re   # regular expression library that allows advanced parsing of text. Used for keeping indentation in notes
import os   # os for file navigation

import database     # our defined database class that creates the communication with the database

# Get directory containing ARA for file navigation purposes
wd = os.path.dirname(os.path.realpath(__file__))
# Change directory to this for same reasons as above
os.chdir(wd)

# Configure databases
db_global = None

class PDFViewer:
    """
        PDF Viewer Class: The main page for viewing pdfs, taking notes, and saving them to the database.
                            Hide/Display buttons to support self-quizzing and sq3r reading method.
                            Pulls pdfs from local directory and pulls notes from database
    """
    def __init__(self, root, path, user, user_id, file_id, file_name):
        """
            Initializes the PDF viewer window.

            Parameters:
                root (Tk): Root Tkinter window.
                path (str): Path to the PDF file.
                user (str): Current user name.
                user_id (int): Current user ID.
                file_id (int): ID of the PDF file.
                file_name (str): Name of the PDF file.

        """
        self.root = root
        self.user = user
        self.root.title("Active-Reading Assistant")   # sets title of application
        self.root.geometry("1920x1080") # sets native resolution
        self.user_id = user_id
        self.file_id = file_id
        self.file_name = file_name
        self.is_example = False     # defaults PDF that is viewed to not one of the examples

        # List of 'Example' PDFS that have pre-loaded notes associated with it
        examples = ["Somerville Chapter 5 System Modeling.pdf"] 

        # Finds if the file that was passed was an example PDF w/ notes. If so, set is_example to true
        if self.file_name in examples:
            self.is_example = True

        # define the gui canvas for placing objects on it
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(side="left", fill="both", expand=True)

        # define the scrollbar for navigating through the pdf
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        # places the scrollbar on the canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # inits list of images for the pdf viewing
        self.image_refs = []

        # defaults the current file were viewing to None
        self.current_file = None

        # Initialize scroll region
        self.scrollregion = (0, 0, 0, 0)  

        # binds keyboard buttons to call associated functions
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        # defaults notes to None
        self.notes = None

        # defaults the sq3r label, which aids user through sq3r to none, and sets the status of it showing on the screen to false
        self.sQ3R_label = None
        self.q3r_info = None
        self.sq3r_showing = False

        self.load_menu_bar()        # call menu bar
        self.open_pdf(path)         # call open pdf 

    def open_pdf(self, file_path):
        """
            Checks to see if the file path is legitimate to open the pdf

            Parameters:
                file_path (str): Path to the PDF file.
        """

        # if the file path is blank or doesnt exist, go back to the menu, else load the pdf
        if (file_path == "" or file_path is None):
            self.back_to_menu()
        else:
            self.load_pdf(file_path)


    def load_pdf(self, file_path):
        """
            Load and display the PDF file.

            Parameters:
                file_path (str): Path to the PDF file.
        """

        # Error check to ensure no empty (None) file path
        if not file_path:
            return


        # if the file isnt already the one loaded, load the notes
        if self.current_file is not file_path:
            self.load_notetaking_area()
        else:
            self.current_file = file_path

        # deletes the canvas and sets images to none to make space for the pdf images
        self.canvas.delete("all")
        self.image_refs = []

        # calls fitz library package to put pdfs into gui
        doc = fitz.open(file_path)
        canvas_width = self.canvas.winfo_width()  # Get the width of the canvas
        y = 0  # Initialize y coordinate
        x = 0  # initialize x coordinate
        max_page_width = 0  # Initialize maximum page width
        total_height = 0  # Initialize total height
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()

            max_page_width = max(max_page_width, pix.width)
            total_height += pix.height

            img = tk.PhotoImage(data=pix.tobytes("ppm"))
            self.image_refs.append(img)
            self.canvas.create_image(x, y, anchor="nw", image=img)
            y += pix.height + 20  # Add 20 pixels of space between each page

        # Calculate the new scroll region
        self.scrollregion = (0, 0, max_page_width, total_height)
        self.canvas.config(scrollregion=self.scrollregion)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Re-add the binding for two-finger scroll

    def on_canvas_resize(self, event):
        """
            Event handler for canvas resize.
            Reloads the PDF when the canvas is resized.

            Parameters:
                event: Canvas resize event.
        """
        if not self.root.attributes("-fullscreen"):
            self.load_pdf(self.current_file)

    def on_mouse_wheel(self, event):
        """
            Event handler for mouse wheel scroll.
            Scrolls the canvas when the mouse wheel is scrolled.

            Parameters:
                event: Mouse wheel scroll event.
        """
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def toggle_fullscreen(self, event=None):
        """
            Toggle fullscreen mode. Reloads the pdf when entered full screen

            Parameters: event Canvas resize event: defaulted to None
        """
        fullscreen_state = not self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", fullscreen_state)
        if fullscreen_state:
            self.load_pdf(self.current_file)  # Reload PDF when entering fullscreen mode
        else:
            self.canvas.config(scrollregion=self.scrollregion)  # Restore scroll region when exiting fullscreen mode

    def exit_fullscreen(self, event=None):
        """
            Toggle fullscreen mode. Reloads the pdf when entered full screen

            Parameters: event Canvas resize event: defaulted to None
        """
        # reconfig canvas size and scroll region
        self.root.attributes("-fullscreen", False)
        self.canvas.config(scrollregion=self.scrollregion)  # Restore scroll region when exiting fullscreen mode
    
    def load_menu_bar(self):
        """
            instantiates and places all labels and buttons on the user interface for user interaction
        """
        # Label showing username
        username_label = tk.Label(self.canvas, text=f"User: {self.user}")
        username_label.place(x=650, y=25)   

        # back to main menu button
        back_button = tk.Button(self.canvas, text="Back to Menu", command=self.back_to_menu)   
        back_button.place(x=750, y=20)

        # save text to database button
        save_button = tk.Button(self.canvas, text="Save Notes", command=self.save_notes)   
        save_button.place(x=700, y=70)

        # hide the notes from the screen button
        hide_notes_button = tk.Button(self.canvas, text="Hide Notes", command=self.hide_notes)   
        hide_notes_button.place(x=650, y=120)

        # show notes to the screen button
        show_notes_button = tk.Button(self.canvas, text="Show Notes", command=self.show_notes)   
        show_notes_button.place(x=750, y=120)

        # hide/show sq3r buttons that explain the sq3r reading method
        hide_sq3r = tk.Button(self.canvas, text="Hide SQ3R", command=self.hide_instructions)   
        hide_sq3r.place(x=650, y=150)
        show_sq3r = tk.Button(self.canvas, text="Show SQ3R", command=self.show_instructions)   
        show_sq3r.place(x=750, y=150)


    def show_instructions(self):
        """
            shows sq3r instructins
        """
        # if the instructions are not showing, show the instructions
        if self.sq3r_showing is False:
            self.sQ3R_label = tk.Label(self.canvas, text=f"SQ3R Instructions: ")
            self.sQ3R_label.place(x=615, y=200)

            q3r_info = "Survey: Skim over all the important\nheadings/subheadings.\n\nQuestion: Form questions based\non surveying. \n\nRead: Critically read over the document. \n\nRecite: Rehearse and write down\nthe important information\nthat was gathered. \n\nReview: Answer your questions and\nexamine your notes on the text."
            self.q3r = tk.Label(self.canvas, text=q3r_info)
            self.q3r.place(x = 615, y = 225)
            self.sq3r_showing = True

    def hide_instructions(self):
        """
            hides sq3r instructins
        """
        # if the instructions are showing, hide the instructions
        if self.sq3r_showing:
            self.sQ3R_label.destroy()
            self.q3r.destroy()
            self.sq3r_showing = False

    def load_notetaking_area(self):
        """
            Loads the notetaking region and scans the database for pre-existing notes and loads them in if found
        """
        self.notes = tk.Text(self.root)
        self.notes.pack(fill="both", expand=True)
        self.notes.bind("<Return>", self.auto_indent)

        exists = db_global.check_note_existence(self.user_id, self.file_id)
        if exists and not self.is_example:
            text = db_global.display_note(self.user_id, self.file_id)
            if text is not None:
                self.notes.insert(tk.END, text)
        else:
            db_global.add_note(self.user_id, self.file_id)
            if self.is_example:
                txt_file = self.file_name.replace(".pdf", ".txt")
                path = os.getcwd()
                path += f"/Notes/{txt_file}"
                with open(path) as f:
                    input_txt = f.read()
                    self.notes.insert(tk.END, input_txt)


    def save_notes(self):
        """
            Saves notes to database
        """
        text = self.notes.get("1.0", tk.END)
        db_global.modify_note(self.user_id, self.file_id, text)
    
    def back_to_menu(self):
        """
            Back to main menu homepage
        """
        self.destroy_current_frame()
        HomePage(self.root, self.user_id, self.user)

    def hide_notes(self):
        """
            hide the user notes
        """
        self.notes.pack_forget()

    def show_notes(self):
        """
            show the user notes
        """
        self.notes.pack(fill="both", expand=True)


    def destroy_current_frame(self):
        """
            removes all widgets in the frame to prepare for loading of new widgets
        """
        # Destroy all widgets within the current frame
        for widget in self.root.winfo_children():
            widget.destroy()

    def auto_indent(self, event):
        """
            Uses regular expressions to auto-indent the next line to ensure hieararchy of notes

            Parameters: canvas event that will hold the text
        """
        text = event.widget

        # get leading whitespace from current line
        line = text.get("insert linestart", "insert")
        match = re.match(r'^(\s+)', line)
        whitespace = match.group(0) if match else ""

        # insert the newline and the whitespace
        text.insert("insert", f"\n{whitespace}")

        # return "break" to inhibit default insertion of newline
        return "break"


class Login:
    """
        Login Class: Main page for getting the user to login with their inteneded user. 
            Allows an admin set-up to create a connection to the database that holds all the users and their information
    """
    def __init__(self, root):
        """
            Initializes the login window.

            Parameters:
                root (Tk): the root window of the tkinter gui
        """

        self.root = root
        self.root.title("Active-Reading Assistant") # set title of window
        self.root.geometry("1920x1080")     # set resolution
                
        self.load_login()       # calls load login

    def load_login(self):
        """
            loads the users, labels, admin, and other 'welcome to' information needed for user to load app

        """
        # welcome to our app!
        welcome_label = tk.Label(self.root, text="Welcome to Active-Reading Assistant!")
        welcome_label.pack(anchor="n", padx=10)
        welcome_label.config(font=("Arial", 20))

        # select user label
        username_label = tk.Label(self.root, text="Select User:")
        username_label.pack(anchor="n", padx=30)

        
        global db_global    # get our db to pull our users from there

        # informal comment: this is a crazy if... but im actually proud of this logic haha
            # if we have no global database them we force user to press admin to set up server
            # or, if there is a global database and there's no connection to that database, then force user to press admin to connect to server
        if db_global is None or (db_global is not None and db_global.connection is None):
            username_label.config(text="Please set up server")
            admin_button = tk.Button(self.root, text="Admin Settings", command=self.admin_config_window)
            admin_button.pack(anchor="n", pady=50, padx=60)

        else:       # else load the 3 predefined users and all other users in database to dropdown

            options = ["User1", "User2", "User3"]
            current_users = db_global.print_users()

            # load default users into db if needed
            for u in options:
                if u not in current_users:
                    db_global.add_user(u)

            names = db_global.print_users()     # gets all of our usernames


            selected_option = tk.StringVar(self.root)   # get the values of the selected option
            selected_option.set(names[0])  # Set the default option

            # dropdown window showing all the users
            dropdown = tk.OptionMenu(self.root, selected_option, *names, command=self.on_select)
            dropdown.pack(anchor="n", padx=50)

            # button to add new user
            new_user_button = tk.Button(self.root, text="Add New User", command=self.add_user)
            new_user_button.pack(anchor="n")

            # button to load admin window
            admin_button = tk.Button(self.root, text="Admin Settings", command=self.admin_config_window)
            admin_button.pack(anchor="n", pady=50, padx=60)


    def add_user(self):
        """
            loads the window to type in username to add
        
        """
        # new window for username input
        user_win = tk.Toplevel(self.root)
        user_win.title("Add User")
        user_win.geometry("400x300") 

        # user label
        text_label = tk.Label(user_win, text=f"User: ")
        text_label.pack(side="left", anchor="nw")  

        # user input
        entry = tk.Entry(user_win, width=30)
        entry.pack(pady=10) 

        # button that loads the new user into the db
        apply_btn = tk.Button(user_win, text="Apply", command=lambda: self.get_new_user(entry, user_win))
        apply_btn.pack()

    def get_new_user(self, user, user_win):
        """
        Adds the new users to the database

        Parameters:
            user : canvas entry widget for user input.
            user_win: Toplevel window for adding a new user.
        """
        u = user.get()      # get the value from the user entry widget
        current_users = db_global.print_users()     # get all curent users in database
        if u in current_users:
            messagebox.showerror("Cannot add user", "User already exists")      # throw error if new user inputted already exists
        else:
            db_global.add_user(u)       # add the user to the database!
            user_win.destroy()          # destroys the pop up window
            self.destroy_current_frame()    # destroys all widgets in frame
            Login(self.root)                # reloads login page so new user will appear


    def on_select(self, user):
        """
            Called when user clicks on the user they want to sign in as.
            Builds their pdf table and changes to the homepage
        """
        self.destroy_current_frame()            # destroy widgets in frame
        user_id = db_global.get_user_id(user)   # get our user id, so we know where to look in database


        db_global.delete_files()        # delete all the pdfs, in case user added/removed
        db_global.build_pdf_table()     # rebuild the pdf table
        HomePage(self.root, user_id, user)      # load homepage



    def admin_config_window(self):
        """
            loads admin config window to set up database
        """
        self.db_config_window()


    def destroy_current_frame(self):
        """ 
            removes all widgets on the screen to prepare space for new widgets
        """
        # Destroy all widgets within the current frame
        for widget in self.root.winfo_children():
            widget.destroy()

    def db_config_window(self):
        """
            load window to input information to connect to a database
        
        """
    # Create a new top-level window
        config_win = tk.Toplevel(self.root)
        config_win.title("Database Configuration")
        config_win.geometry("400x300")  # Width x Height

        # Labels and entries for each database configuration parameter
        labels = ['Host', 'Port', 'User', 'Password', 'Database']
        entries = {}
        for idx, label in enumerate(labels):
            tk.Label(config_win, text=label).grid(row=idx, column=0)
            entry = tk.Entry(config_win)
            entry.grid(row=idx, column=1)
            entries[label.lower()] = entry

        # Pre-fill the entries with the current configuration
        if db_global is not None:
            entries['host'].insert(0, db_global.host)
            entries['port'].insert(0, db_global.port)
            entries['user'].insert(0, db_global.user)
            entries['password'].insert(0, db_global.password)
            entries['database'].insert(0, db_global.database)
        else:   # else fill with our default server
            entries['host'].insert(0, 'ix-dev.cs.uoregon.edu')
            entries['port'].insert(0, 3932)
            entries['user'].insert(0, 'group7')
            entries['password'].insert(0, 'KBAcriaT')
            entries['database'].insert(0, 'sq3r_db')

        # Apply Button to connect to database
        apply_btn = tk.Button(config_win, text="Apply", command=lambda: self.apply_db_config(entries))
        apply_btn.grid(row=len(labels), column=1, sticky="e")

    def apply_db_config(self, entries):
        """
            instantiates our new database with the user entries
        """
        # Update the db_config dictionary with values from the entries
        host = entries['host'].get()
        port = int(entries['port'].get())
        user = entries['user'].get()
        password = entries['password'].get()
        db = entries['database'].get()

        # Build the config file
        config = [host, port, user, password, db]

        db_new = database.Database(config)      # create new database
        global db_global
        db_global = db_new      # point our global db to the new db for ease of refeerence
        self.destroy_current_frame()        # remove widgets in  current frame
        Login(self.root)           # reload the login page, but now with a connection to a db!




class HomePage:
    """
        Homepage Class: Main page for viewing all the pdfs that can be loaded and viewed
    """

    def __init__(self, root, user_id=None, username=None):
        """
            Initializes the main homepage window.

            Parameters:
                root : root window of gui
                user_id : ID of the logged-in user
                username: Username of the logged-in user
        """
        self.root = root
        self.user_id = user_id
        self.username = username
        self.root.title("Active-Reading Assistant")     # set window title
        self.root.geometry("1920x1080")                 # set resolution

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.menu()     # load the menu of the homepage
            
        # load the pdfs
        self.example_pdf_shelf()
        self.user_pdfs()
        self.example_with_notes()

    def menu(self):
        """
            creates the labels and buttons needed for menu navigation
        """
        # username label to display!
        username_label = tk.Label(self.canvas, text=f"User: {self.username}")
        username_label.pack(side="left", anchor="nw")  

        # log out button for switching users!
        log_out_button = tk.Button(self.canvas, text="Log Out", command=self.log_out) 
        log_out_button.pack(side="right", anchor="ne")   

    def example_with_notes(self):
        """
            creates the example pdf with the pre-loaded notes button to load that pdf
        """
        # create a frame to display the pdf button
        self.pdfs_frame = tk.Frame(self.root)
        self.pdfs_frame.place(x=100, y=100) 
        text_label = tk.Label(self.pdfs_frame, text="Example PDF w/ SQ3R Sample Notes")
        text_label.pack()
        self.pdfs = []

        # change our directory to find our correct pdf
        os.chdir("PDFs")
        os.chdir("Examples")
        directory = os.getcwd()
        # Reset directory to root folder containing .py file
        os.chdir(wd)
        # loop thorugh out files and find the sommerville ch 5 that has our example notes and then displau the button to load it
        for filename in os.listdir(directory):
            if filename == "Somerville Chapter 5 System Modeling.pdf":
                dir_str = f"{directory}/{filename}"
                pdf_frame = tk.Frame(self.pdfs_frame)
                pdf_frame.pack(side="left", padx=5)
                pdf = tk.Button(pdf_frame, text=f"{filename[:-4]}", wraplength=100, justify='left', width=10, height=5, relief="raised")
                pdf.config(command=lambda path=dir_str: self.loadPDF(path))
                pdf.pack()

    def example_pdf_shelf(self):
        """
            creates the example pdf buttons to load those pdfs
        """
        # create a frame to display the pdf buttons
        self.pdfs_frame = tk.Frame(self.root)
        self.pdfs_frame.place(x=100, y=250) 
        text_label = tk.Label(self.pdfs_frame, text="Example PDFs")
        text_label.pack()
        self.pdfs = []
        
        # change our directory to find our correct pdf
        os.chdir("PDFs")
        os.chdir("Examples")
        directory = os.getcwd()
        # Reset directory to root folder containing .py file
        os.chdir(wd)

        # loop thorugh out files and find all example pdfs and then display the buttons to load them
        for filename in os.listdir(directory):
            if filename != "Somerville Chapter 5 System Modeling.pdf":
                dir_str = f"{directory}/{filename}"
                pdf_frame = tk.Frame(self.pdfs_frame)
                pdf_frame.pack(side="left", padx=5)
                pdf = tk.Button(pdf_frame, text=f"{filename[:-4]}", wraplength=100, justify='left', width=10, height=5, relief="raised")
                pdf.config(command=lambda path=dir_str: self.loadPDF(path))
                pdf.pack()
                # self.pdfs.append(pdf)

    def user_pdfs(self):
        """
            creates the uesr pdf buttons to load those pdfs
        """
        # create a frame to display the pdf buttons
        self.pdfs_frame = tk.Frame(self.root)
        self.pdfs_frame.place(x=100, y=400) 
        text_label = tk.Label(self.pdfs_frame, text="User PDFs")
        text_label.pack()
        self.pdfs = []
        
        # change our directory to find our correct pdf 
        os.chdir("PDFs")
        directory = os.getcwd()
        # Reset directory to root folder containing .py file
        os.chdir(wd)

        # loop thorugh our files and find all the user pdfs and then display the buttons to load them
        for filename in os.listdir(directory):
            if (filename != "Examples"):
                dir_str = f"{directory}/{filename}"
                pdf_frame = tk.Frame(self.pdfs_frame)
                pdf_frame.pack(side="left", padx=5)
                pdf = tk.Button(pdf_frame, text=f"{filename[:-4]}", wraplength=100, justify='left', width=10, height=5, relief="raised")
                pdf.config(command=lambda path=dir_str: self.loadPDF(path))
                pdf.pack()


    def log_out(self):
        """
            logs the user out and returns to the login page
        """
        self.destroy_current_frame()
        Login(self.root)

    def destroy_current_frame(self):
        """
            removes all widgets in the frame to make space for new ones to be loaded
        """
        # Destroy all widgets within the current frame
        for widget in self.root.winfo_children():
            widget.destroy()

    def loadPDF(self, file_path):
        """
            calls the pdfviewer class to load the window to display the pdf that we wished to load
        """ 
        file_name = os.path.basename(file_path)     # gets the specific name of the file
        file_id = db_global.get_file_id(file_name)   # gets the file id

        self.destroy_current_frame()    # remove widgets
        
        # load our pdf viewer!
        PDFViewer(self.root, file_path, self.username, self.user_id, file_id, file_name)



        

def main():
    """
        main function loop that creates and keeps the tkinter gui alive
    """
    root = tk.Tk()          # creates tkinter gui window
    login = Login(root)     # loads our login page
    root.mainloop()         # loop to keep window alive


if __name__ == "__main__":
    main()

