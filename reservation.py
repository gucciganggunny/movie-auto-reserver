from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def reserve_movie(movie_title, showtime, seat_ids, adult_tickets=1, senior_tickets=0, child_tickets=0):
    url = "https://www.fandango.com/amc-metreon-16-aanem/theater-page?format=all"
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print(f"Attempting to reserve {movie_title} at {showtime}")
        driver.get(url)
        
        # Wait for the page to load and scroll down to load dynamic content
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.thtr-mv-list"))
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        
        # Find and click on the movie
        movie_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{movie_title}')]"))
        )
        movie_link.click()
        
        # Find and click on the showtime
        showtime_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{showtime}')]"))
        )
        showtime_button.click()
        
        # Wait for the seat map to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".seat-map"))
        )
        
        # Validate and select the seats
        available_seats = driver.find_elements(By.CSS_SELECTOR, ".seat-map__seat.availableSeat")
        available_seat_ids = [seat.get_attribute("id") for seat in available_seats]
        print(f"Available seat IDs: {available_seat_ids}")

        for seat_id in seat_ids:
            if seat_id in available_seat_ids:
                print(f"Attempting to select seat: {seat_id}")
                seat_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, seat_id))
                )
                seat_element.click()
                print(f"Selected seat: {seat_id}")
            else:
                print(f"Seat ID {seat_id} is not available in this theater")
        
        # Enter ticket quantity by clicking the "+" button the required number of times
        def click_ticket_button(ticket_type, count):
            button_selector = f"button[data-action='add'][data-ticket-type-description='{ticket_type}']"
            for _ in range(count):
                button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
                )
                button.click()

        click_ticket_button("Adult", adult_tickets)
        click_ticket_button("Senior", senior_tickets)
        click_ticket_button("Child", child_tickets)
        
        # Proceed to checkout
        checkout_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn--checkout"))
        )
        checkout_button.click()
        
        # Wait for the payment page to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='cardnumber']"))
        )
        
        driver.find_element(By.CSS_SELECTOR, "input[name='cardnumber']").send_keys("4111111111111111")
        driver.find_element(By.CSS_SELECTOR, "input[name='expdate']").send_keys("12/24")
        driver.find_element(By.CSS_SELECTOR, "input[name='cvv']").send_keys("123")
        
        # Confirm reservation
        confirm_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn--confirm"))
        )
        confirm_button.click()

        print("Reservation process initiated successfully")
        return True
    
    except Exception as e:
        print(f"Reservation failed: {str(e)}")
        print("Debug Information:")
        print(driver.get_log("browser"))  # Capture JavaScript console errors
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    # Test the function
    reserve_movie("Inside Out 2 (2024)", "10:15p", ["A3"], adult_tickets=1, senior_tickets=0, child_tickets=0)
