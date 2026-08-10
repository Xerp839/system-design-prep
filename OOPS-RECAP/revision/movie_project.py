class Movie:

    #method 

    def __init__(self, movie_name: str, total_seat: int, ticket_price: int, booked_seat=0) -> None:

        #Abstraciton
        self.movie_name = movie_name
        self.total_seat = total_seat
        self.ticket_price = ticket_price
        self.booked_seat = booked_seat

    def book_ticket(self, num_tickets) -> None:
        avail_tickets = self.total_seat - self.booked_seat
        bill = 0

        if num_tickets <= avail_tickets:
            self.booked_seat += num_tickets
            self.total_seat -= num_tickets
            bill = self.ticket_price * num_tickets
            print(f"Your Tickets Are confirmed, Bill:{bill}")
        else:
            print("Sorrry Not enoguh Available Seat")
        
    def show_status(self) -> None:
        avail_tickets = self.total_seat - self.booked_seat
        print(f"Movie Name: {self.movie_name}")
        print(f"Available Seats: {avail_tickets}")
        print(f"Seats Booked: {self.booked_seat}")


m1 = Movie("Odessey", 80, 800)
m1.book_ticket(4)
# m1.show_status()

m1.book_ticket(10)
# m1.show_status()

m1.book_ticket(64)

# m1.show_status()

m1.book_ticket(4)
m1.show_status()