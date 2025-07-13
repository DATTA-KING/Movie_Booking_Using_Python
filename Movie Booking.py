import tkinter as tk
from tkinter import messagebox
import sqlite3

# Initialize DB
def init_db():
    conn = sqlite3.connect("booking.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            movie_id INTEGER,
            seat TEXT,
            booked INTEGER DEFAULT 0,
            PRIMARY KEY(movie_id, seat),
            FOREIGN KEY(movie_id) REFERENCES movies(id)
        )
    """)

    # Add sample movies
    movies = ["Avengers: Endgame", "Inception", "Interstellar"]
    for movie in movies:
        cur.execute("INSERT OR IGNORE INTO movies (id, name) VALUES (?, ?)", (movies.index(movie) + 1, movie))

        # Add seats (5 rows x 6 seats each)
        for row in range(1, 6):
            for col in range(1, 7):
                seat = f"{row}-{col}"
                cur.execute("INSERT OR IGNORE INTO tickets (movie_id, seat) VALUES (?, ?)", (movies.index(movie) + 1, seat))

    conn.commit()
    conn.close()

# Fetch movie list
def get_movies():
    conn = sqlite3.connect("booking.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM movies")
    result = cur.fetchall()
    conn.close()
    return result

# Fetch seat status
def get_seat_status(movie_id):
    conn = sqlite3.connect("booking.db")
    cur = conn.cursor()
    cur.execute("SELECT seat, booked FROM tickets WHERE movie_id=?", (movie_id,))
    result = cur.fetchall()
    conn.close()
    return dict(result)

# Book seat
def book_seat(movie_id, seat_id, button):
    conn = sqlite3.connect("booking.db")
    cur = conn.cursor()
    cur.execute("SELECT booked FROM tickets WHERE movie_id=? AND seat=?", (movie_id, seat_id))
    booked = cur.fetchone()[0]

    if booked:
        messagebox.showerror("Error", f"Seat {seat_id} already booked!")
    else:
        cur.execute("UPDATE tickets SET booked=1 WHERE movie_id=? AND seat=?", (movie_id, seat_id))
        conn.commit()
        button.config(bg="red")
        messagebox.showinfo("Success", f"Seat {seat_id} booked successfully!")
    conn.close()

# Seat layout GUI
def open_seat_layout(movie_id, movie_name):
    window = tk.Toplevel()
    window.title(f"Book Tickets - {movie_name}")
    tk.Label(window, text=f"Select seats for: {movie_name}", font=("Arial", 14)).pack(pady=10)

    seats_frame = tk.Frame(window)
    seats_frame.pack()

    seats = get_seat_status(movie_id)

    for row in range(1, 6):
        for col in range(1, 7):
            seat_id = f"{row}-{col}"
            booked = seats.get(seat_id, 0)
            color = "red" if booked else "green"
            btn = tk.Button(seats_frame, text=seat_id, width=6, height=2, bg=color)
            if not booked:
                btn.config(command=lambda b=btn, s=seat_id: book_seat(movie_id, s, b))
            btn.grid(row=row, column=col, padx=3, pady=3)

    tk.Label(window, text="Green = Available | Red = Booked", font=("Arial", 10)).pack(pady=5)

# Main GUI
def main_ui():
    root = tk.Tk()
    root.title("Online Movie Ticket Booking")
    root.geometry("400x400")

    tk.Label(root, text="Select a Movie", font=("Arial", 16)).pack(pady=20)

    movies = get_movies()
    for movie_id, movie_name in movies:
        btn = tk.Button(root, text=movie_name, width=30, height=2,
                        command=lambda mid=movie_id, mname=movie_name: open_seat_layout(mid, mname))
        btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    init_db()
    main_ui()
