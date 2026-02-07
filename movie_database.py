"""
Movie Rating Database
A console application for tracking movies, ratings, and comments.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Tuple


class MovieDatabase:
    """Handles all database operations for the movie rating system."""
    
    def __init__(self, db_name: str = "movies.db"):
        """Initialize database connection and create tables if needed."""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish connection to SQLite database."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """Create necessary tables if they don't exist."""
        # Movies table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                year INTEGER,
                genre TEXT,
                director TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ratings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                rating REAL NOT NULL CHECK(rating >= 0 AND rating <= 10),
                comment TEXT,
                date_rated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (movie_id) REFERENCES movies (id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
    
    def add_movie(self, title: str, year: Optional[int] = None, 
                  genre: Optional[str] = None, director: Optional[str] = None) -> int:
        """Add a new movie to the database."""
        self.cursor.execute('''
            INSERT INTO movies (title, year, genre, director)
            VALUES (?, ?, ?, ?)
        ''', (title, year, genre, director))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def add_rating(self, movie_id: int, rating: float, comment: Optional[str] = None) -> bool:
        """Add a rating and comment for a movie."""
        try:
            self.cursor.execute('''
                INSERT INTO ratings (movie_id, rating, comment)
                VALUES (?, ?, ?)
            ''', (movie_id, rating, comment))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_movies(self) -> List[Tuple]:
        """Retrieve all movies with their average ratings."""
        self.cursor.execute('''
            SELECT 
                m.id,
                m.title,
                m.year,
                m.genre,
                m.director,
                ROUND(AVG(r.rating), 2) as avg_rating,
                COUNT(r.id) as rating_count
            FROM movies m
            LEFT JOIN ratings r ON m.id = r.movie_id
            GROUP BY m.id
            ORDER BY m.title
        ''')
        return self.cursor.fetchall()
    
    def get_movie_by_id(self, movie_id: int) -> Optional[Tuple]:
        """Get a specific movie by ID."""
        self.cursor.execute('''
            SELECT id, title, year, genre, director, date_added
            FROM movies
            WHERE id = ?
        ''', (movie_id,))
        return self.cursor.fetchone()
    
    def get_movie_ratings(self, movie_id: int) -> List[Tuple]:
        """Get all ratings for a specific movie."""
        self.cursor.execute('''
            SELECT rating, comment, date_rated
            FROM ratings
            WHERE movie_id = ?
            ORDER BY date_rated DESC
        ''', (movie_id,))
        return self.cursor.fetchall()
    
    def search_movies(self, search_term: str) -> List[Tuple]:
        """Search movies by title."""
        self.cursor.execute('''
            SELECT 
                m.id,
                m.title,
                m.year,
                m.genre,
                m.director,
                ROUND(AVG(r.rating), 2) as avg_rating
            FROM movies m
            LEFT JOIN ratings r ON m.id = r.movie_id
            WHERE m.title LIKE ?
            GROUP BY m.id
            ORDER BY m.title
        ''', (f'%{search_term}%',))
        return self.cursor.fetchall()
    
    def delete_movie(self, movie_id: int) -> bool:
        """Delete a movie and all its ratings."""
        self.cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


class MovieRatingApp:
    """Main application class for the movie rating console interface."""
    
    def __init__(self):
        """Initialize the application."""
        self.db = MovieDatabase()
        self.running = True
    
    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, text: str):
        """Print a formatted header."""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def print_menu(self):
        """Display the main menu."""
        self.clear_screen()
        self.print_header("MOVIE RATING DATABASE")
        print("\n1. Add a new movie")
        print("2. View all movies")
        print("3. Search for a movie")
        print("4. Add rating to a movie")
        print("5. View movie details")
        print("6. Delete a movie")
        print("7. Exit")
        print("\n" + "-" * 60)
    
    def get_input(self, prompt: str, required: bool = True, 
                  input_type: type = str) -> Optional[any]:
        """Get user input with validation."""
        while True:
            value = input(prompt).strip()
            
            if not value and not required:
                return None
            
            if not value and required:
                print("This field is required. Please try again.")
                continue
            
            if input_type == int:
                try:
                    return int(value)
                except ValueError:
                    print("Please enter a valid number.")
                    continue
            
            if input_type == float:
                try:
                    return float(value)
                except ValueError:
                    print("Please enter a valid number.")
                    continue
            
            return value
    
    def add_movie(self):
        """Handle adding a new movie."""
        self.print_header("ADD NEW MOVIE")
        
        title = self.get_input("\nMovie Title: ")
        year = self.get_input("Year (press Enter to skip): ", required=False, input_type=int)
        genre = self.get_input("Genre (press Enter to skip): ", required=False)
        director = self.get_input("Director (press Enter to skip): ", required=False)
        
        movie_id = self.db.add_movie(title, year, genre, director)
        print(f"\n✓ Movie '{title}' added successfully! (ID: {movie_id})")
        
        # Ask if user wants to add a rating
        add_rating = self.get_input("\nWould you like to add a rating now? (y/n): ").lower()
        if add_rating == 'y':
            self.add_rating_to_movie(movie_id)
        else:
            input("\nPress Enter to continue...")
    
    def view_all_movies(self):
        """Display all movies in the database."""
        self.print_header("ALL MOVIES")
        
        movies = self.db.get_all_movies()
        
        if not movies:
            print("\nNo movies in the database yet.")
        else:
            print(f"\n{'ID':<5} {'Title':<30} {'Year':<6} {'Genre':<15} {'Avg Rating':<12} {'# Ratings'}")
            print("-" * 90)
            
            for movie in movies:
                movie_id, title, year, genre, director, avg_rating, rating_count = movie
                year_str = str(year) if year else "N/A"
                genre_str = genre[:15] if genre else "N/A"
                rating_str = f"{avg_rating}/10" if avg_rating else "Not rated"
                
                # Truncate title if too long
                title_display = title[:28] + ".." if len(title) > 30 else title
                
                print(f"{movie_id:<5} {title_display:<30} {year_str:<6} {genre_str:<15} {rating_str:<12} {rating_count}")
        
        input("\nPress Enter to continue...")
    
    def search_movies(self):
        """Search for movies by title."""
        self.print_header("SEARCH MOVIES")
        
        search_term = self.get_input("\nEnter search term: ")
        movies = self.db.search_movies(search_term)
        
        if not movies:
            print(f"\nNo movies found matching '{search_term}'.")
        else:
            print(f"\n{'ID':<5} {'Title':<35} {'Year':<6} {'Genre':<15} {'Avg Rating'}")
            print("-" * 75)
            
            for movie in movies:
                movie_id, title, year, genre, director, avg_rating = movie
                year_str = str(year) if year else "N/A"
                genre_str = genre[:15] if genre else "N/A"
                rating_str = f"{avg_rating}/10" if avg_rating else "Not rated"
                
                title_display = title[:33] + ".." if len(title) > 35 else title
                print(f"{movie_id:<5} {title_display:<35} {year_str:<6} {genre_str:<15} {rating_str}")
        
        input("\nPress Enter to continue...")
    
    def add_rating_to_movie(self, movie_id: Optional[int] = None):
        """Add a rating to a movie."""
        if movie_id is None:
            self.print_header("ADD RATING")
            movie_id = self.get_input("\nEnter movie ID: ", input_type=int)
        
        # Check if movie exists
        movie = self.db.get_movie_by_id(movie_id)
        if not movie:
            print(f"\n✗ Movie with ID {movie_id} not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nAdding rating for: {movie[1]}")
        
        # Get rating
        while True:
            rating = self.get_input("Rating (0-10): ", input_type=float)
            if 0 <= rating <= 10:
                break
            print("Rating must be between 0 and 10.")
        
        # Get comment
        comment = self.get_input("Comment (press Enter to skip): ", required=False)
        
        if self.db.add_rating(movie_id, rating, comment):
            print(f"\n✓ Rating added successfully!")
        else:
            print(f"\n✗ Failed to add rating.")
        
        input("\nPress Enter to continue...")
    
    def view_movie_details(self):
        """View detailed information about a movie."""
        self.print_header("MOVIE DETAILS")
        
        movie_id = self.get_input("\nEnter movie ID: ", input_type=int)
        movie = self.db.get_movie_by_id(movie_id)
        
        if not movie:
            print(f"\n✗ Movie with ID {movie_id} not found.")
            input("\nPress Enter to continue...")
            return
        
        # Display movie info
        print(f"\nTitle: {movie[1]}")
        print(f"Year: {movie[2] if movie[2] else 'N/A'}")
        print(f"Genre: {movie[3] if movie[3] else 'N/A'}")
        print(f"Director: {movie[4] if movie[4] else 'N/A'}")
        print(f"Date Added: {movie[5]}")
        
        # Get and display ratings
        ratings = self.db.get_movie_ratings(movie_id)
        
        if ratings:
            print(f"\n{'-' * 60}")
            print(f"RATINGS ({len(ratings)} total)")
            print(f"{'-' * 60}")
            
            total_rating = sum(r[0] for r in ratings)
            avg_rating = total_rating / len(ratings)
            print(f"\nAverage Rating: {avg_rating:.2f}/10")
            
            print(f"\n{'Rating':<10} {'Date':<20} {'Comment'}")
            print("-" * 60)
            
            for rating, comment, date_rated in ratings:
                comment_display = comment[:35] + "..." if comment and len(comment) > 38 else (comment or "No comment")
                print(f"{rating}/10{'':<4} {date_rated:<20} {comment_display}")
        else:
            print("\nNo ratings yet for this movie.")
        
        input("\nPress Enter to continue...")
    
    def delete_movie(self):
        """Delete a movie from the database."""
        self.print_header("DELETE MOVIE")
        
        movie_id = self.get_input("\nEnter movie ID to delete: ", input_type=int)
        movie = self.db.get_movie_by_id(movie_id)
        
        if not movie:
            print(f"\n✗ Movie with ID {movie_id} not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nMovie: {movie[1]}")
        confirm = self.get_input("Are you sure you want to delete this movie? (yes/no): ").lower()
        
        if confirm == 'yes':
            if self.db.delete_movie(movie_id):
                print(f"\n✓ Movie deleted successfully!")
            else:
                print(f"\n✗ Failed to delete movie.")
        else:
            print("\nDeletion cancelled.")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main application loop."""
        while self.running:
            self.print_menu()
            
            choice = self.get_input("Enter your choice (1-7): ")
            
            if choice == '1':
                self.add_movie()
            elif choice == '2':
                self.view_all_movies()
            elif choice == '3':
                self.search_movies()
            elif choice == '4':
                self.add_rating_to_movie()
            elif choice == '5':
                self.view_movie_details()
            elif choice == '6':
                self.delete_movie()
            elif choice == '7':
                print("\nThank you for using Movie Rating Database!")
                self.running = False
            else:
                print("\n✗ Invalid choice. Please try again.")
                input("\nPress Enter to continue...")
        
        self.db.close()


def main():
    """Entry point of the application."""
    app = MovieRatingApp()
    app.run()


if __name__ == "__main__":
    main()