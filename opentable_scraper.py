"""
OpenTable Canada Restaurant Scraper
====================================
Scrapes restaurant data from OpenTable.ca for Toronto, Ontario, Canada
Extracts: Name, URL, Phone, and Cuisine
Outputs: CSV file with the restaurant data
"""

import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import random
from urllib.parse import urljoin, urlparse
import json

class OpenTableScraper:
    def __init__(self):
        self.base_url = "https://www.opentable.ca"
        self.session = requests.Session()
        self.restaurants = []
        
        # Headers to mimic a real browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.session.headers.update(self.headers)
    
    def get_toronto_restaurants_url(self):
        """Construct URL for Toronto restaurants"""
        # OpenTable URL for Toronto restaurants
        return f"{self.base_url}/toronto-ontario-restaurants"
    
    def fetch_page(self, url, retries=3):
        """Fetch a page with retry logic"""
        for attempt in range(retries):
            try:
                print(f"Fetching: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(2, 5))
                else:
                    raise
    
    def extract_phone_from_text(self, text):
        """Extract phone number from text using regex"""
        if not text:
            return ""
        
        # Common phone number patterns
        phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'([0-9]{3})[-.]([0-9]{3})[-.]([0-9]{4})'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 3:
                    return f"({match.group(1)}) {match.group(2)}-{match.group(3)}"
                else:
                    return match.group(0)
        
        return ""
    
    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def parse_restaurant_card(self, card):
        """Parse individual restaurant card/listing"""
        restaurant = {
            'name': '',
            'url': '',
            'phone': '',
            'cuisine': ''
        }
        
        try:
            # Extract restaurant name
            name_elem = card.find(['h2', 'h3', 'a'], {'data-test': 'restaurant-card-title'}) or \
                       card.find('a', class_=re.compile(r'.*title.*|.*name.*', re.I)) or \
                       card.find(['h2', 'h3']) or \
                       card.select_one('[data-test*="title"], [data-test*="name"]')
            
            if name_elem:
                restaurant['name'] = self.clean_text(name_elem.get_text())
                # Extract URL from name link
                href = name_elem.get('href')
                if href:
                    restaurant['url'] = urljoin(self.base_url, href)
            
            # Extract cuisine
            cuisine_elem = card.find(text=re.compile(r'cuisine|food', re.I)) or \
                          card.find(['span', 'div'], class_=re.compile(r'cuisine|category', re.I)) or \
                          card.select_one('[data-test*="cuisine"], [data-test*="category"]')
            
            if cuisine_elem:
                if hasattr(cuisine_elem, 'get_text'):
                    restaurant['cuisine'] = self.clean_text(cuisine_elem.get_text())
                else:
                    restaurant['cuisine'] = self.clean_text(str(cuisine_elem))
            
            # Try to find phone in the card
            phone_elem = card.find(text=re.compile(r'\(\d{3}\)|\d{3}[-.\s]\d{3}', re.I))
            if phone_elem:
                restaurant['phone'] = self.extract_phone_from_text(phone_elem)
            
            # If no phone found in card, try to get it from restaurant page
            if not restaurant['phone'] and restaurant['url']:
                restaurant['phone'] = self.get_restaurant_phone(restaurant['url'])
            
            return restaurant
            
        except Exception as e:
            print(f"Error parsing restaurant card: {e}")
            return restaurant
    
    def get_restaurant_phone(self, restaurant_url):
        """Get phone number from individual restaurant page"""
        try:
            time.sleep(random.uniform(1, 3))  # Be respectful
            response = self.fetch_page(restaurant_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for phone numbers in various locations
            phone_selectors = [
                '[data-test*="phone"]',
                '[class*="phone"]',
                'a[href^="tel:"]',
                '.restaurant-info',
                '.contact-info'
            ]
            
            for selector in phone_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text() if hasattr(elem, 'get_text') else str(elem)
                    phone = self.extract_phone_from_text(text)
                    if phone:
                        return phone
            
            # Search for phone in page text
            page_text = soup.get_text()
            phone = self.extract_phone_from_text(page_text)
            if phone:
                return phone
                
        except Exception as e:
            print(f"Error getting phone for {restaurant_url}: {e}")
        
        return ""
    
    def scrape_restaurants(self, max_restaurants=50):
        """Main scraping method"""
        print("Starting OpenTable Canada restaurant scraper...")
        print(f"Target: {max_restaurants} restaurants from Toronto, Ontario")
        
        # Start with the main Toronto restaurants page
        toronto_url = self.get_toronto_restaurants_url()
        
        page = 1
        restaurants_found = 0
        
        while restaurants_found < max_restaurants:
            print(f"\n--- Scraping page {page} ---")
            
            # Construct URL for current page
            if page == 1:
                current_url = toronto_url
            else:
                current_url = f"{toronto_url}?page={page}"
            
            try:
                response = self.fetch_page(current_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find restaurant cards/listings
                # OpenTable uses various selectors, try multiple approaches
                restaurant_cards = (
                    soup.select('[data-test*="restaurant-card"]') or
                    soup.select('.restaurant-card') or
                    soup.select('[class*="restaurant"]') or
                    soup.select('article') or
                    soup.select('.listing')
                )
                
                if not restaurant_cards:
                    print("No restaurant cards found, trying alternative selectors...")
                    # Try to find any links that look like restaurant links
                    restaurant_links = soup.find_all('a', href=re.compile(r'/r/[\w-]+'))
                    restaurant_cards = [link.find_parent() for link in restaurant_links if link.find_parent()]
                
                if not restaurant_cards:
                    print("No restaurants found on this page, ending scrape.")
                    break
                
                print(f"Found {len(restaurant_cards)} restaurant listings on page {page}")
                
                # Parse each restaurant
                page_restaurants = 0
                for card in restaurant_cards:
                    if restaurants_found >= max_restaurants:
                        break
                    
                    restaurant = self.parse_restaurant_card(card)
                    
                    if restaurant['name']:  # Only add if we got a name
                        self.restaurants.append(restaurant)
                        restaurants_found += 1
                        page_restaurants += 1
                        
                        print(f"  {restaurants_found}. {restaurant['name']}")
                        if restaurant['cuisine']:
                            print(f"     Cuisine: {restaurant['cuisine']}")
                        if restaurant['phone']:
                            print(f"     Phone: {restaurant['phone']}")
                
                print(f"Extracted {page_restaurants} restaurants from page {page}")
                
                if page_restaurants == 0:
                    print("No valid restaurants found on this page, ending scrape.")
                    break
                
                page += 1
                
                # Be respectful - add delay between pages
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
        
        print(f"\nScraping completed! Found {len(self.restaurants)} restaurants.")
        return self.restaurants
    
    def save_to_csv(self, filename="toronto_restaurants.csv"):
        """Save scraped data to CSV file"""
        if not self.restaurants:
            print("No restaurants to save!")
            return
        
        print(f"Saving {len(self.restaurants)} restaurants to {filename}")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'url', 'phone', 'cuisine']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for restaurant in self.restaurants:
                writer.writerow(restaurant)
        
        print(f"Data saved successfully to {filename}")
    
    def print_summary(self):
        """Print summary of scraped data"""
        if not self.restaurants:
            print("No restaurants scraped!")
            return
        
        print(f"\n=== SCRAPING SUMMARY ===")
        print(f"Total restaurants: {len(self.restaurants)}")
        
        with_phone = sum(1 for r in self.restaurants if r['phone'])
        with_cuisine = sum(1 for r in self.restaurants if r['cuisine'])
        with_url = sum(1 for r in self.restaurants if r['url'])
        
        print(f"With phone numbers: {with_phone} ({with_phone/len(self.restaurants)*100:.1f}%)")
        print(f"With cuisine info: {with_cuisine} ({with_cuisine/len(self.restaurants)*100:.1f}%)")
        print(f"With URLs: {with_url} ({with_url/len(self.restaurants)*100:.1f}%)")
        
        print(f"\n=== SAMPLE DATA ===")
        for i, restaurant in enumerate(self.restaurants[:5]):
            print(f"{i+1}. {restaurant['name']}")
            print(f"   URL: {restaurant['url']}")
            print(f"   Phone: {restaurant['phone'] or 'N/A'}")
            print(f"   Cuisine: {restaurant['cuisine'] or 'N/A'}")
            print()


def main():
    """Main function to run the scraper"""
    scraper = OpenTableScraper()
    
    try:
        # Scrape restaurants (you can adjust the number)
        restaurants = scraper.scrape_restaurants(max_restaurants=50)
        
        # Save to CSV
        scraper.save_to_csv("toronto_restaurants.csv")
        
        # Print summary
        scraper.print_summary()
        
        print("\n=== SCRAPING COMPLETE ===")
        print("Check 'toronto_restaurants.csv' for the complete data!")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
        if scraper.restaurants:
            scraper.save_to_csv("toronto_restaurants_partial.csv")
            print("Partial data saved.")
    except Exception as e:
        print(f"Error during scraping: {e}")
        if scraper.restaurants:
            scraper.save_to_csv("toronto_restaurants_error.csv")
            print("Partial data saved due to error.")


if __name__ == "__main__":
    main()
