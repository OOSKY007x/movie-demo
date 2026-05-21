from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("movieshop.db") 
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        genre TEXT,
        price REAL,
        image TEXT,
        theater TEXT,
        show_time TEXT
    )
    """)

    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie_id INTEGER,
        customer_name TEXT,
        seats_count INTEGER,
        total_price REAL,
        FOREIGN KEY (movie_id) REFERENCES movies (id)
    )
    """)

    
    cursor = conn.execute("SELECT COUNT(*) FROM movies")
    if cursor.fetchone()[0] == 0:
        sample_movies = [
            ("Avatar: The Way of Water", "Sci-Fi / Action", 240.00, "https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=500&q=80", "Theater 1", "14:30"),
            ("Spirited Away", "Animation / Fantasy", 180.00, "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=500&q=80", "Theater 3", "17:00")
        ]
        conn.executemany("INSERT INTO movies (title, genre, price, image, theater, show_time) VALUES (?, ?, ?, ?, ?, ?)", sample_movies)
        conn.commit()

    conn.close()

init_db()


@app.route("/")
def index():
    conn = get_db()
    movies = conn.execute("SELECT * FROM movies").fetchall()
    conn.close()
    return render_template("movie main.html", movies=movies) 


@app.route("/append", methods=["GET", "POST"])
def append():
    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        price = request.form["price"]
        image = request.form["image"]
        theater = request.form["theater"]
        show_time = request.form["show_time"]

        conn = get_db()
        conn.execute("INSERT INTO movies (title, genre, price, image, theater, show_time) VALUES (?, ?, ?, ?, ?, ?)",
                     (title, genre, price, image, theater, show_time))
        conn.commit()
        conn.close()
        return redirect("/")
    
    return render_template("append.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    if request.method == "POST":
        title = request.form["title"]
        genre = request.form["genre"]
        price = request.form["price"]
        image = request.form["image"]
        theater = request.form["theater"]
        show_time = request.form["show_time"]

        conn.execute("UPDATE movies SET title=?, genre=?, price=?, image=?, theater=?, show_time=? WHERE id=?",
                     (title, genre, price, image, theater, show_time, id))
        conn.commit()
        conn.close()
        return redirect("/")

    movie = conn.execute("SELECT * FROM movies WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", movie=movie)


@app.route("/book/<int:id>", methods=["POST"])
def book_ticket(id):  
    movie_id = id
    customer_name = request.form.get("customer_name", "Guest")
    seats_count = int(request.form.get("seats_count", 1))
    
    conn = get_db()
    movie = conn.execute("SELECT price FROM movies WHERE id=?", (id,)).fetchone()
    
    if movie:
        total_price = movie["price"] * seats_count
        conn.execute("INSERT INTO bookings (movie_id, customer_name, seats_count, total_price) VALUES (?, ?, ?, ?)",
                     (movie_id, customer_name, seats_count, total_price))
        conn.commit()
    
    conn.close()
    return redirect("/")
    


@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM movies WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)