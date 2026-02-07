# Overview

This is a console app written in python that connects to an SQLite Database. The database is created inside the root folder and as it is a console app, the user is prompted to select from a menu to add movies, see movies details, search for a movie, add rating, or delete existing movies.

This software was developed to get an understanding of SQLite and SQL relational database in general using a simple console app.


[Software Demo Video](https://youtu.be/YtZ-BEXV_Us)

# Relational Database

I am using SQLite to create the table and seed the table.

So here, I am creating two different tables, on for the movies and one for the ratings.
The movies table is structured as such: id(primary key), title, year, genre, director, date_added
The ratings table is structured as such: id(primary key), movie_id (foreign key to connect to movies table), rating, comment, date_added

# Development Environment

VSCode for writing the code and github to host the source code and installing python 3.

I am using python3 and SQLite.

# Useful Websites

- Python (https://www.python.org/)
- SQLite (https://sqlite.org/)
- SQLite Tutorial (https://www.sqlitetutorial.net/)

# Future Work

- Converting the app to have a GUI
- Deploying it live by using a web app approach
- Hosting the database to an online database provider