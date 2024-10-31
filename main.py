from scrape_movies import scrape_fandango_showtimes
from reservation import reserve_movie
from email_sender import send_email

def main():
    fandango_url = "https://www.fandango.com/amc-metreon-16-aanem/theater-page?format=all"
    
    while True:
        print("\nAMC Metreon Auto-Reserver")
        print("1. View available movies")
        print("2. Make a reservation")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            try:
                movies = scrape_fandango_showtimes(fandango_url)
                for movie in movies:
                    print(f"\n{movie['title']}")
                    print("Showtimes:", ", ".join(movie['showtimes']))
            except Exception as e:
                print(f"Error fetching movie information: {str(e)}")
        
        elif choice == '2':
            try:
                movies = scrape_fandango_showtimes(fandango_url)
                if not movies:
                    print("No movies available at the moment. Please try again later.")
                    continue

                print("\nAvailable movies:")
                for i, movie in enumerate(movies):
                    print(f"{i+1}. {movie['title']}")
                
                while True:
                    try:
                        movie_choice = int(input("Enter the number of the movie you want to reserve: ")) - 1
                        if 0 <= movie_choice < len(movies):
                            break
                        else:
                            print("Invalid movie number. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                selected_movie = movies[movie_choice]
                
                print(f"\nShowtimes for {selected_movie['title']}:")
                for i, showtime in enumerate(selected_movie['showtimes']):
                    print(f"{i+1}. {showtime}")
                
                while True:
                    try:
                        showtime_choice = int(input("Enter the number of the showtime you want to reserve: ")) - 1
                        if 0 <= showtime_choice < len(selected_movie['showtimes']):
                            break
                        else:
                            print("Invalid showtime number. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                selected_showtime = selected_movie['showtimes'][showtime_choice]
                
                seat_ids = input("Enter the seat IDs you want to select, separated by commas (e.g., A14,A13): ").split(',')
                
                adult_tickets = int(input("Enter the number of adult tickets: "))
                senior_tickets = int(input("Enter the number of senior tickets: "))
                child_tickets = int(input("Enter the number of child tickets: "))
                
                success = reserve_movie(selected_movie['title'], selected_showtime, seat_ids, adult_tickets, senior_tickets, child_tickets)
                if success:
                    user_email = input("Enter your email for confirmation: ")
                    send_email("Movie Reservation Successful", 
                               f"Your reservation for {selected_movie['title']} at {selected_showtime} was successful!",
                               user_email)
                    print("Reservation successful! Check your email for confirmation.")
                else:
                    print("Reservation failed. Please try again.")
            except Exception as e:
                print(f"An error occurred during the reservation process: {str(e)}")
        
        elif choice == '3':
            print("Thank you for using AMC Metreon Auto-Reserver. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()