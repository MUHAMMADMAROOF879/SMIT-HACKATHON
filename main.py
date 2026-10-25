"""Smart Bus Reservation System
One file | pure Python | no imports | data stays in memory only (lost when program closes)."""
 
CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")     # tuple
MENU = ["View Available Routes", "Search for a Route", "Book a Ticket", "View My Bookings",
        "Cancel a Booking", "View Seat Availability", "Generate Booking Report", "Exit"]
 
# Starting data: route ID, from, to, departure time, fare per seat, total seats
ROUTE_DATA = [["R101", "Karachi", "Hyderabad", "08:00 AM", 1200, 40],
              ["R102", "Karachi", "Sukkur", "09:30 AM", 2000, 36],
              ["R103", "Hyderabad", "Mirpur Khas", "11:00 AM", 800, 32],
              ["R104", "Karachi", "Lahore", "07:00 PM", 5000, 45],
              ["R105", "Sukkur", "Hyderabad", "02:00 PM", 1500, 30]]
 
routes = []          # list of route dictionaries
bookings = []        # list of booking dictionaries (never deleted, so history is kept)
issued_ids = set()   # booking IDs already used, so no ID is ever repeated
 
for route_id, start, end, time, price, seats in ROUTE_DATA:
    routes.append({"route_id": route_id, "departure_city": start, "destination_city": end,
                   "departure_time": time, "ticket_price": price,
                   "total_seats": seats, "available_seats": seats})
 
 
# ------------------------------------------------------------ helper functions
def journey(route):
    return f"{route['departure_city']} -> {route['destination_city']}"
 
 
def seat_status(route):
    if route["available_seats"] == 0:
        return "Fully Booked"
    if route["available_seats"] == route["total_seats"]:
        return "Available"
    return "Partially Booked"
 
 
def route_line(route):
    """One text line with everything about a route (used by options 1, 2 and 6)."""
    return (f"{route['route_id']} | {journey(route)} | {route['departure_time']} | "
            f"Rs. {route['ticket_price']} | {route['available_seats']}/{route['total_seats']} seats | "
            f"{seat_status(route)}")
 
 
def find_route(route_id):
    for route in routes:
        if route["route_id"] == route_id.strip().upper():
            return route
    return None
 
 
def read_positive_number(prompt):
    """Ask for a whole number above zero. Return None if the answer is not valid."""
    text = input(prompt).strip()
    if text.isdecimal() and len(text) <= 9 and int(text) > 0:
        return int(text)
    return None
 
 
def ask_yes(question):
    return input(question).strip().lower() in ("y", "yes")
 
 
def new_booking_id():
    number = 1001
    while f"B{number}" in issued_ids:       # keep going until we find an unused ID
        number += 1
    issued_ids.add(f"B{number}")
    return f"B{number}"
 
 
# ------------------------------------------------------------------- features
def show_routes(title):
    """Options 1 and 6: list routes, optionally hiding fully booked ones."""
    only_free = ask_yes("Show only routes with seats left? (y/n): ")
    visible = []
    for route in routes:
        if only_free and route["available_seats"] == 0:
            continue                         # skip fully booked routes
        visible.append(route)
    print(f"\n{title}")
    if not visible:
        print("No routes with seats available.")
    for number, route in enumerate(visible, 1):
        print(f"{number}. {route_line(route)}")
 
 
def show_schedule():
    print("\nROUTE SCHEDULE BY DEPARTURE CITY")
    for city in CITIES:                      # outer loop: every city
        print(f"\n{city}")
        has_departure = False
        for route in routes:                 # inner loop: every route
            if route["departure_city"] == city:
                print(f"  {route['route_id']} -> {route['destination_city']} | {route['departure_time']}")
                has_departure = True
        if not has_departure:
            print("  No scheduled departures.")
 
 
def view_routes():
    show_routes("AVAILABLE BUS ROUTES")
    if ask_yes("View schedule by departure city? (y/n): "):
        show_schedule()
 
 
def search_route():
    term = input("Search by route ID or city: ").strip().lower()
    if term == "":
        print("Error: please type a route ID or city name.")
        return
    for route in routes:
        if route["route_id"].lower() == term:      # a route ID is unique, so stop at the first hit
            print(route_line(route))
            break
    else:                                          # no ID matched, so search the city names
        matches = [r for r in routes
                   if term in r["departure_city"].lower() or term in r["destination_city"].lower()]
        for route in matches:
            print(route_line(route))
        if not matches:
            print("No matching route found.")
 
 
def book_ticket():
    # Step 1: collect and check every input. Nothing is changed until all checks pass.
    name = " ".join(input("Passenger name: ").split())
    if not any(ch.isalpha() for ch in name):
        print("Error: name cannot be empty and must contain letters.")
        return
    age = read_positive_number("Passenger age: ")
    if age is None or age > 120:
        print("Error: age must be a whole number from 1 to 120.")
        return
    route = find_route(input("Route ID: "))
    if route is None:
        print("Error: route not found.")
        return
    seats = read_positive_number("Number of seats: ")
    if seats is None:
        print("Error: seats must be a positive whole number.")
        return
    if seats > route["available_seats"]:
        print(f"Error: only {route['available_seats']} seat(s) available on {route['route_id']}.")
        return
 
    # Step 2: everything is valid, so save the booking and reduce the seats.
    booking = {"booking_id": new_booking_id(), "passenger_name": name, "passenger_age": age,
               "route_id": route["route_id"], "seats": seats,
               "total_fare": route["ticket_price"] * seats, "status": "Confirmed"}
    bookings.append(booking)
    route["available_seats"] -= seats
    print(f"\nBooking confirmed!\nBooking ID: {booking['booking_id']}\nPassenger: {name}\n"
          f"Route: {route['route_id']} ({journey(route)})\nSeats booked: {seats}\n"
          f"Fare per seat: Rs. {route['ticket_price']}\nTotal fare: Rs. {booking['total_fare']}\n"
          f"Status: Confirmed")
 
 
def view_bookings():
    if not bookings:
        print("No bookings found.")
    for number, b in enumerate(bookings, 1):
        print(f"{number}. {b['booking_id']} | {b['passenger_name']} (age {b['passenger_age']}) | "
              f"{b['route_id']} | {b['seats']} seat(s) | Rs. {b['total_fare']} | {b['status']}")
 
 
def cancel_booking():
    booking_id = input("Enter booking ID to cancel: ").strip().upper()
    for b in bookings:
        if b["booking_id"] == booking_id:
            if b["status"] != "Confirmed":
                print(f"Booking {booking_id} is already cancelled. No seats restored.")
                break
            route = find_route(b["route_id"])
            route["available_seats"] += b["seats"]   # give the seats back (only this one time)
            b["status"] = "Cancelled"                # keep the record for history
            print(f"Booking {booking_id} has been cancelled.\nSeats restored: {b['seats']}\n"
                  f"Route {route['route_id']} available seats: {route['available_seats']}")
            break
    else:                                            # loop ended without break: ID never found
        print("Booking ID not found.")
 
 
def generate_report():
    confirmed = [b for b in bookings if b["status"] == "Confirmed"]
    reserved_seats = 0
    revenue = 0
    for route in routes:                             # outer loop: every route
        for b in confirmed:                          # inner loop: confirmed bookings of that route
            if b["route_id"] == route["route_id"]:
                reserved_seats += b["seats"]
                revenue += b["total_fare"]
    full_routes = len([r for r in routes if r["available_seats"] == 0])
    print(f"\nBOOKING REPORT\nTotal bookings created: {len(bookings)}\n"
          f"Confirmed bookings: {len(confirmed)}\nCancelled bookings: {len(bookings) - len(confirmed)}\n"
          f"Seats currently reserved: {reserved_seats}\nConfirmed revenue: Rs. {revenue:,}\n"
          f"Fully booked routes: {full_routes}")
 
 
# ----------------------------------------------------------------------- menu
def main():
    actions = {"1": view_routes, "2": search_route, "3": book_ticket, "4": view_bookings,
               "5": cancel_booking, "6": lambda: show_routes("SEAT AVAILABILITY"),
               "7": generate_report}
    while True:
        print("\nSMART BUS RESERVATION SYSTEM\n" + "=" * 32)
        for number, item in enumerate(MENU, 1):
            print(f"{number}. {item}")
        choice = input("=" * 32 + "\nEnter your choice: ").strip()
        if choice == "8":
            print("Thank you for using Smart Bus Reservation System. Goodbye!")
            break
        if choice not in actions:
            print("Invalid choice. Please enter a number from 1 to 8.")
            continue
        actions[choice]()
 
 
try:
    main()
except (KeyboardInterrupt, EOFError):               # Ctrl+C or Ctrl+D closes politely
    print("\nProgram closed.")
