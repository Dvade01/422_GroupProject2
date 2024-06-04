CS 422/522 Software Engineering Project 1: PDF Active-Reading Assistant (ARA)

Brief Descrption of System:
    The ARA app is designed to support SQ3R reading methods on PDFS. The user can view pre-loaded pdfs and take notes on them using these methods.
    Their notes are able to be stored on a database to allow transfer of notes across machines. 
    There are 3 pre-defined users that the user can log in as, however they may add as many users as they wish.
    User storing and loading of notes dependent on a working communication to the database.

Authors: 
    Ryan Helms, William Qiu, Nikhar Ramlakhan, Abie Safdie, Caleb Sutherland

Released: 
    4/29/2024

Creation: 
        This software was created to satisfy the assignment assigned by Prof. Anthony Hornof in CS 422 Spring term 2024 at the U of O.
         The assignment was titled PDF Active-Reading Assistant (ARA)

What needs to be done to run the python program: 

        Correct python version, necessary dependencies, and a working server and database connection need to be established.

        Python Version: 3.12
        Dependencies: os, re, tkinter, and fitz (PyMuPDF) python packages
        Server/Database: mysql-connector

        Please see Installation Instructions and our Server installation instructions 
        in our submission for more information on how to achieve these requirements.

        TO RUN OUR PYTHON PROGRAM:

                macOS / Linux: in the terminal run the command: python3 ara.py
                    - must be in directory containing ara.py, see directory structure below

                Windows: in cmd prompt run the command: python ara.py
                    - must be in directory containing ara.py, see directory structure below

                From IDE: in any IDE of your choice, you may run our program. See your specific IDE's documentation on how to achieve this

What is located in our Directories/Subdirectories:

        Root Directory:
                README.txt                      - this readme file 
                SRS.pdf                         - our software requirements specifcations
                SDS.pdf                         - our software design specifications
                Project_Plan.pdf                - containing the plan to complete this project
                Programmar_Documentation.pdf    - document providing documentation on our source code
                Installation_Instructions.pdf   - document providing documentation on how to install dependencies
                Server_Installation_Instructions- document providing documentation on how to set up the mysql server
                User_Documentation.pdf          - document providing documentation on how the user can use the software
                Ara Source Code/                  - directory contating our source code and necessary pdf/notes files

        Ara Source Code directory:

                ara.py          - this is the main driver of our program.
                database.py     - helper python file that handles communication between app and database

                /Notes          - notes directory containing the example notes on sommerville chapter

                    Somerville Chapter 5 System Modeling.txt

                /PDFs           - PDF directory containing all of the user pdfs

                    A Brief History of M.C. Gregory and Gale Mouthpieces.pdf
                    Acoustic Effects of Variables in Saxophone Accessories.pdf
                    CLRS Chapter 13 Red Black Trees.pdf
                    Henry Lindeman Method for Saxophone.pdf
                    How to Read Technical Material.pdf
                    Project_1_SRS_v1.pdf
                    Somerville Chapter 6 Architectural Design.pdf
                    The Mixing Engineers Handbook Chapter 1.pdf
                    /Examples   - Directory containing the Somerville example PDFS
                        Somerville Chapter 2 Software Processes.pdf
                        Somerville Chapter 22 Team Management.pdf
                        Somerville Chapter 5 System Modeling.pdf

