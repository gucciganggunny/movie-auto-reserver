from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import json
import time

def scrape_fandango_showtimes(fandango_url):
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--window-size=1920,1080")
    
    service = FirefoxService(GeckoDriverManager().install())
    print(f"Using GeckoDriver version: {service.path}")
    driver = webdriver.Firefox(service=service, options=firefox_options)
    
    try:
        print("Accessing the website...")
        driver.get(fandango_url)
        
        # Wait for the movie containers to load
        print("Waiting for movie containers to load...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li[class^='movie-']"))
        )
        
        # Scroll to load all content
        print("Scrolling to load all content...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for any lazy-loaded content
        
        print("Page loaded. Parsing content...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        movies = []
        
        # Find all movie containers
        movie_containers = soup.select("li[class^='movie-']")
        print(f"Found {len(movie_containers)} movie containers")
        
        for i, container in enumerate(movie_containers):
            title_elem = container.select_one('a.thtr-mv-list__detail-link')
            if title_elem:
                title = title_elem.text.strip()
                print(f"Found title for movie {i+1}: {title}")
            else:
                print(f"Couldn't find title for movie {i+1}")
                continue
            
            showtimes_container = container.find_next('div', class_='showtime-card__showtime-container')
            if showtimes_container:
                showtimes = showtimes_container.select('a.showtime-btn--available')
                movie_showtimes = [showtime.text.strip() for showtime in showtimes]
                print(f"Found showtimes for {title}: {movie_showtimes}")
            else:
                movie_showtimes = []
                print(f"No showtimes found for {title}")
            
            movies.append({
                'title': title,
                'showtimes': movie_showtimes
            })
        
        return movies
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []
    
    finally:
        driver.quit()

def save_to_file(data, filename='movies.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    fandango_url = "https://www.fandango.com/amc-metreon-16-aanem/theater-page?format=all"
    movie_data = scrape_fandango_showtimes(fandango_url)
    print(json.dumps(movie_data, indent=2))
    save_to_file(movie_data)
