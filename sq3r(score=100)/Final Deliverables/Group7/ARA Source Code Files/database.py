"""
CS 422/522 Software Engineering Project: PDF Active-Reading Assistant (ARA)
Authors: Ryan Helms, William Qiu, Nikhar Ramlakhan, Abie Safdie, Caleb Sutherland
Released: 4/29/2024

This file, database.py, defines functions that communicate directly to our database

See ara.py for information on this software as a whole. As well as our other documentation that was apart of our submission

Have fun applying SQ3R!!!

"""

import mysql.connector  # to communicate with our mysql database
from tkinter import messagebox  # tkinter gui pop up window for errors
import os  # os for file navigation

# our defualt database config.
# NOTE: the preloaded db when loading our app is hardcoded. Changing these values will not change what gets pre-loaded
db_default_config = ['ix-dev.cs.uoregon.edu', 3932, 'group7', 'KBAcriaT',
                     'test_db']


class Database():
    """
        Database Class: Main class for defining a database. Holds values defining what database it is and creates the connection to the
        mysql database
    """

    def __init__(self, db_info):
        """
            Initializes the connection and required info of the database

        """
        self.host = db_info[0]  # host - in our case ix-dev!
        self.port = db_info[1]  # port num
        self.user = db_info[2]  # the user
        self.password = db_info[3]  # password to connect
        self.database = db_info[4]  # database name
        self.connection = self.connect_to_database()  # creates the connection to the database!

    def config_db(self):
        """
            Changes the requried info to load database into readable format for server

            returns: dictionary of config information
        """
        config = {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'database': self.database
        }
        return config

    def connect_to_database(self):
        """
            Attempts to connect to database
            Returns: the status of the connection
        """
        # try to connect to mysql, else throw error and set the connection to none
        try:
            self.connection = mysql.connector.connect(**self.config_db())
            return self.connection
        except mysql.connector.Error as err:
            messagebox.showerror("SERVER CONNECTION FAIL",
                                 "Server settings are incorrect. Please review settings.")
            self.connection = None
            return None

    def add_user(self, username):
        """
            Adds a user to the database
        """
        insert_data = [(username,)]  # username to insert
        if self.connection:  # if there is a connection add the user via sql query
            try:
                cursor = self.connection.cursor()
                insert_query = "INSERT INTO user (username) VALUES (%s)"
                cursor.executemany(insert_query, insert_data)
                self.connection.commit()
                print("Added user successfully!")
            except mysql.connector.Error as err:
                print("Error adding user:", err)
                self.connection.rollback()
            finally:
                cursor.close()

    def print_users(self):
        """
            Gets all the users to the database
            Returns: a list of users
        """
        names = []  # inits users to empty list
        if self.connection:  # if there is a connection call the sql query to get all the usernames
            try:
                cursor = self.connection.cursor()
                select_query = "SELECT username FROM user"
                cursor.execute(select_query)
                list = cursor.fetchall()
                for name in list:
                    names.append(name[0])
                return names
            except mysql.connector.Error as err:
                print("Error printing usernames:", err)
            finally:
                cursor.close()

    def get_user_id(self, username):
        """
            Gets the id of the user
            Returns: user id (int)
        """
        select_data = (username,)  # username to pull from
        if self.connection:  # if there is a connection call the sql query to get user id
            try:
                cursor = self.connection.cursor()
                select_query = "SELECT user_id FROM user WHERE username = %s"
                cursor.execute(select_query, select_data)
                list = cursor.fetchall()
                final_user_id = list[0][0]
                return int(final_user_id)

            except mysql.connector.Error as err:
                print("Error printing usernames:", err)
            finally:
                cursor.close()

    def build_pdf_table(self):
        """
            Build the table that will hold the pdf ids in the database
        """
        # Get directory containing ARA for file navigation purposes
        wd = os.path.dirname(os.path.realpath(__file__))
        # Change directory to this for same reasons as above
        os.chdir(wd)
        os.chdir("PDFs")
        directory = os.getcwd()
        os.chdir("Examples")
        examples_directory = os.getcwd()
        # Reset directory to root folder containing .py file
        os.chdir(wd)
        pdf_names = []  # inits list of all the pdf names

        # appends all the names to the list
        for filename in os.listdir(directory):
            if filename == "Examples":
                for f in os.listdir(examples_directory):
                    pdf_names.append(f)
            else:
                pdf_names.append(filename)

        pdf_names.sort()  # sorts in alphabetical order for ease of use

        file_data = []  # inits empty list that will hold id and name

        for i in range(len(pdf_names)):
            file_data.append((i + 1, pdf_names[i]))

        if self.connection:  # if there is a connection call the sql query to insert pdf id and name
            try:
                cursor = self.connection.cursor()
                insert_query = "INSERT INTO files (file_id, file_name) VALUES (%s, %s)"
                cursor.executemany(insert_query, file_data)
                self.connection.commit()
                print("Files loaded successfully!")
            except mysql.connector.Error as err:
                print("Error loading files:", err)
                self.connection.rollback()
            finally:
                cursor.close()

    def get_file_id(self, file_name):
        """
            Get the id of the pdf that you wish to access

            Returns: file id (int)
        """
        select_data = (file_name,)  # filename to search for
        if self.connection:  # if there is a connection call the sql query to get the file id
            try:
                cursor = self.connection.cursor()
                select_query = "SELECT file_id FROM files WHERE file_name = %s"
                cursor.execute(select_query, select_data)
                list = cursor.fetchall()
                final_id = list[0][
                    0]  # sql query gets a list so we have to dereference
                return int(final_id)  # and then cast to an int

            except mysql.connector.Error as err:
                print("Error printing usernames:", err)
            finally:
                cursor.close()

    def delete_files(self):
        """
            Delets all the file ids and names
        """
        if self.connection:  # if there is a connection call the sql query to delete the files
            try:
                cursor = self.connection.cursor()
                delete_query = f"DELETE FROM files WHERE 1"
                cursor.execute(delete_query)
                self.connection.commit()
                print("All records deleted successfully!")
            except mysql.connector.Error as err:
                print("Error deleting records:", err)
                self.connection.rollback()
            finally:
                cursor.close()

    def check_note_existence(self, user_id, file_id):
        """
            Checks to see if the user has a note associated with a specific file

            param: user id: specifying user
                   file id: specifies file

            returns: true if exists, false otherwise
        """
        if self.connection:  # if there is a connection call the sql query to check existence
            try:
                cursor = self.connection.cursor()
                select_query = """
                    SELECT EXISTS (
                        SELECT 1
                        FROM notes
                        WHERE user_id = %s AND file_id = %s
                    ) AS note_exists
                """
                select_data = (user_id, file_id)
                cursor.execute(select_query, select_data)
                result = cursor.fetchone()
                if result:
                    note_exists = bool(result[0])
                    return note_exists
            except mysql.connector.Error as err:
                print("Error checking note existence:", err)
            finally:
                cursor.close()

        return False

    def add_note(self, user_id, file_id):
        """
            Add note to the database with a specific user id and file id

            param: user id: specifying user
                   file id: specifies file

        """
        if self.connection:  # if there is a connection call the sql query to add note
            try:
                cursor = self.connection.cursor()
                insert_query = "INSERT INTO notes (user_id, file_id) VALUES (%s, %s)"
                insert_data = [(user_id, file_id)]
                cursor.executemany(insert_query, insert_data)
                self.connection.commit()
                print("Added note successfully!")
            except mysql.connector.Error as err:
                print("Error adding note:", err)
                self.connection.rollback()
            finally:
                cursor.close()

    def modify_note(self, user_id, file_id, new_note):
        """
            Modify a note to the database with a specific user id and file id

            param: user id (int): specifying user
                    file id (int): specifies file
                    new_note (str): text data to load into the note
        """

        try:
            cursor = self.connection.cursor()  # if there is a connection call the sql query to modify the note
            update_query = "UPDATE notes SET note = %s WHERE user_id = %s AND file_id = %s"
            update_data = (new_note, user_id, file_id)
            cursor.execute(update_query, update_data)
            self.connection.commit()
            if cursor.rowcount > 0:
                print("Note modified successfully!")
            else:
                print("No matching note found for modification.")
        except mysql.connector.Error as err:
            print("Error modifying note:", err)
            self.connection.rollback()
        finally:
            if 'cursor' in locals():
                cursor.close()

    def display_note(self, user_id, file_id):
        """
            Display a note to the app with a specific user id and file id

            param: user id (int): specifying user
                   file id (int): specifies file
        """
        try:
            cursor = self.connection.cursor()  # if there is a connection call the sql query to display the note
            select_query = "SELECT note FROM notes WHERE user_id = %s AND file_id = %s"
            select_data = (user_id, file_id)
            cursor.execute(select_query, select_data)
            result = cursor.fetchone()
            note_data = result[
                0]  # have to derefeernce b/c of pulling info from databases work
            return note_data

        except mysql.connector.Error as err:
            print("Error fetching note:", err)
        finally:
            if 'cursor' in locals():
                cursor.close()

    def delete_note(self, user_id, file_id):
        """
           Delete a note from the database with a specific user id and file id

           param: user id (int): specifying user
                  file id (int): specifies file
        """

        if self.connection:  # if there is a connection call the sql query to delete the note
            try:
                cursor = self.connection.cursor()
                delete_query = "DELETE FROM notes WHERE user_id = %s AND file_id = %s"
                delete_data = (user_id, file_id)
                cursor.execute(delete_query, delete_data)
                self.connection.commit()
                if cursor.rowcount > 0:
                    print("Note deleted successfully!")
                else:
                    print("No matching note found for deletion.")
            except mysql.connector.Error as err:
                print("Error deleting note:", err)
                self.connection.rollback()
            finally:
                cursor.close()


