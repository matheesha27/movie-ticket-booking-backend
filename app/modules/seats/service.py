from datetime import datetime


def generate_unique_seat_id(cinema_id: int, movie_id: int, date: datetime, show_time: str, seat_name: str):

    output = ""

    output += str(cinema_id) + "/"
    output += str(movie_id) + "/"
    output += date.strftime("%Y%m%d") + "/"
    output += show_time + "/"
    output += seat_name

    return output
