from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

def scrape_fandango_showtimes(fandango_url):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    service = Service(ChromeDriverManager().install())
    print(f"Using ChromeDriver version: {service.path}")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Accessing the website...")
        driver.get(fandango_url)
        
        # Wait for the movie containers to load
        print("Waiting for movie containers to load...")
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.thtr-mv-list"))
        )
        
        # Scroll to load all content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Wait for any lazy-loaded content
        
        print("Page loaded. Parsing content...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        movies = []
        
        # Find all movie containers
        movie_containers = soup.select("ul.thtr-mv-list > li")
        print(f"Found {len(movie_containers)} movie containers")
        
        for container in movie_containers:
            title_elem = container.select_one('a.thtr-mv-list__detail-link')
            if title_elem:
                title = title_elem.text.strip()
                print(f"Found title: {title}")
            else:
                print("Couldn't find title for a movie")
                continue
            
            showtimes_container = container.find('ol', class_='showtimes-btn-list')
            if showtimes_container:
                showtimes = showtimes_container.select('a.showtime-btn')
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
