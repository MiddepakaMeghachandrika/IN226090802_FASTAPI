from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# -----------------------------
# PRELOADED DATABASE
# -----------------------------

movies = [

    {"id": 1, "title": "RRR", "genre": "Action", "rating": 8.8, "price": 210},
    {"id": 2, "title": "Bahubali", "genre": "Action", "rating": 9.0, "price": 180},
    {"id": 3, "title": "KGF", "genre": "Action", "rating": 8.7, "price": 200},
    {"id": 4, "title": "Pushpa", "genre": "Drama", "rating": 8.3, "price": 150},
    {"id": 5, "title": "Salaar", "genre": "Action", "rating": 8.6, "price": 230}

]

users = [

    {"id": 1, "name": "Megha", "email": "megha@gmail.com"},
    {"id": 2, "name": "Rahul", "email": "rahul@gmail.com"},
    {"id": 3, "name": "Anjali", "email": "anjali@gmail.com"}

]

bookings = [

    {
        "booking_id": 1,
        "movie_id": 1,
        "user_id": 1,
        "seats": 2,
        "total": 420,
        "status": "paid"
    },

    {
        "booking_id": 2,
        "movie_id": 2,
        "user_id": 2,
        "seats": 3,
        "total": 540,
        "status": "paid"
    },

    {
        "booking_id": 3,
        "movie_id": 3,
        "user_id": 3,
        "seats": 1,
        "total": 200,
        "status": "cancelled"
    }

]

# -----------------------------
# MODELS
# -----------------------------

class Movie(BaseModel):

    id: int
    title: str = Field(min_length=2)
    genre: str
    rating: float = Field(ge=0, le=10)
    price: float = Field(gt=0)


class User(BaseModel):

    id: int
    name: str
    email: str


class Booking(BaseModel):

    booking_id: int
    movie_id: int
    user_id: int
    seats: int = Field(gt=0)


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def find_movie(movie_id):

    for m in movies:

        if m["id"] == movie_id:

            return m

    return None


def find_user(user_id):

    for u in users:

        if u["id"] == user_id:

            return u

    return None


def calculate_total(price, seats):

    return price * seats


# -----------------------------
# GET APIs
# -----------------------------

@app.get("/")
def home():

    return {"message": "Movie Ticket Booking API Running"}


@app.get("/movies")
def get_movies():

    return movies


@app.get("/movies/count")
def movie_count():

    return {"total_movies": len(movies)}


@app.get("/movies/search")
def search_movies(

        keyword: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        limit: int = 5):

    result = movies

    if keyword:

        result = [

            m for m in result

            if keyword.lower() in m["title"].lower()

        ]

    if sort_by == "price":

        result = sorted(result, key=lambda x: x["price"])

    if sort_by == "rating":

        result = sorted(result, key=lambda x: x["rating"], reverse=True)

    start = (page - 1) * limit
    end = start + limit

    return result[start:end]


@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):

    movie = find_movie(movie_id)

    if not movie:

        raise HTTPException(status_code=404)

    return movie


@app.get("/bookings")
def get_bookings():

    return bookings


@app.get("/users/search")
def search_users(name: Optional[str] = None):

    if name is None:

        return users

    return [

        u for u in users

        if name.lower() in u["name"].lower()

    ]


@app.get("/combined")
def combined_view(

        keyword: Optional[str] = None,
        page: int = 1,
        limit: int = 5):

    result = movies

    if keyword:

        result = [

            m for m in result

            if keyword.lower() in m["title"].lower()

        ]

    start = (page - 1) * limit
    end = start + limit

    return {

        "movies": result[start:end],

        "total": len(result)

    }


# -----------------------------
# POST APIs
# -----------------------------

@app.post("/movies", status_code=201)
def add_movie(movie: Movie):

    movies.append(movie.dict())

    return movie


@app.post("/users", status_code=201)
def add_user(user: User):

    users.append(user.dict())

    return user


@app.post("/book-ticket")
def book_ticket(data: Booking):

    movie = find_movie(data.movie_id)

    user = find_user(data.user_id)

    if not movie:

        raise HTTPException(status_code=404)

    if not user:

        raise HTTPException(status_code=404)

    total_amount = calculate_total(movie["price"], data.seats)

    record = data.dict()

    record["total"] = total_amount

    record["status"] = "booked"

    bookings.append(record)

    return {

        "message": "Ticket booked",

        "total_amount": total_amount

    }


@app.post("/payment/{booking_id}")
def payment(booking_id: int):

    for b in bookings:

        if b["booking_id"] == booking_id:

            b["status"] = "paid"

            return {"message": "Payment successful"}

    raise HTTPException(status_code=404)


@app.post("/cancel/{booking_id}")
def cancel_ticket(booking_id: int):

    for b in bookings:

        if b["booking_id"] == booking_id:

            b["status"] = "cancelled"

            return {"message": "Ticket cancelled"}

    raise HTTPException(status_code=404)


# -----------------------------
# PUT APIs
# -----------------------------

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, updated: Movie):

    movie = find_movie(movie_id)

    if not movie:

        raise HTTPException(status_code=404)

    movie.update(updated.dict())

    return movie


@app.put("/users/{user_id}")
def update_user(user_id: int, updated: User):

    user = find_user(user_id)

    if not user:

        raise HTTPException(status_code=404)

    user.update(updated.dict())

    return user


# -----------------------------
# DELETE APIs
# -----------------------------

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):

    movie = find_movie(movie_id)

    if not movie:

        raise HTTPException(status_code=404)

    movies.remove(movie)

    return {"message": "Movie deleted"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int):

    user = find_user(user_id)

    if not user:

        raise HTTPException(status_code=404)

    users.remove(user)

    return {"message": "User deleted"}