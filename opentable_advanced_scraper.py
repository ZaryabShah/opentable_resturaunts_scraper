"""
Advanced OpenTable Canada Restaurant Scraper
===========================================
Uses curl-cffi for better bot detection avoidance
Scrapes restaurant data from OpenTable.ca for Toronto, Ontario, Canada
Extracts: Name, URL, Phone, and Cuisine
Outputs: CSV file with the restaurant data
"""

try:
    from curl_cffi import requests
    print("Using curl-cffi for enhanced scraping...")
except ImportError:
    import requests
    print("curl-cffi not available, falling back to regular requests...")
    print("Install curl-cffi with: pip install curl-cffi")

from bs4 import BeautifulSoup
import csv
import re
import time
import random
from urllib.parse import urljoin, urlparse
import json

class AdvancedOpenTableScraper:
    def __init__(self):
        self.base_url = "https://www.opentable.ca"
        self.restaurants = []
        
        # Enhanced headers based on your working example
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "accept-encoding": "gzip, deflate, br, zstd",
            "priority": "u=0, i",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        }
    
    def create_session(self):
        """Create a session with appropriate configuration"""
        try:
            # Try to use curl-cffi if available
            from curl_cffi import requests as cf_requests
            session = cf_requests.Session()
            self.use_cffi = True
            print("Using curl-cffi session")
        except ImportError:
            session = requests.Session()
            self.use_cffi = False
            print("Using standard requests session")
        
        session.headers.update(self.headers)
        return session
    
    def fetch_page(self, url, retries=3):
        """Fetch a page with enhanced bot detection avoidance"""
        session = self.create_session()
        
        for attempt in range(retries):
            try:
                print(f"Fetching: {url} (attempt {attempt + 1})")
                
                if self.use_cffi:
                    response = session.get(
                        url,
                        impersonate="chrome",  # Important for curl-cffi
                        timeout=60,
                        allow_redirects=True,
                    )
                else:
                    response = session.get(url, timeout=30, allow_redirects=True)
                
                response.raise_for_status()
                print(f"Success! Status: {response.status_code}")
                return response
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    wait_time = random.uniform(3, 8)
                    print(f"Waiting {wait_time:.1f} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    raise
    
    def extract_phone_from_text(self, text):
        """Extract phone number from text using regex"""
        if not text:
            return ""
        
        # Canadian phone number patterns
        phone_patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'([0-9]{3})[-.]([0-9]{3})[-.]([0-9]{4})',
            r'(\d{3})\s(\d{3})\s(\d{4})'
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
        # Remove extra whitespace and clean up
        cleaned = re.sub(r'\s+', ' ', text.strip())
        # Remove common unwanted characters
        cleaned = re.sub(r'[^\w\s\-\(\)&.,]', '', cleaned)
        return cleaned
    
    def extract_restaurants_from_page(self, soup):
        """Extract restaurant data from page HTML"""
        restaurants = []
        
        # Multiple strategies to find restaurant data
        strategies = [
            self.strategy_restaurant_cards,
            self.strategy_links_and_scripts,
            self.strategy_structured_data,
            self.strategy_generic_links
        ]
        
        for strategy in strategies:
            try:
                found_restaurants = strategy(soup)
                if found_restaurants:
                    print(f"Strategy '{strategy.__name__}' found {len(found_restaurants)} restaurants")
                    restaurants.extend(found_restaurants)
                    break  # Use the first successful strategy
            except Exception as e:
                print(f"Strategy '{strategy.__name__}' failed: {e}")
                continue
        
        return restaurants
    
    def strategy_restaurant_cards(self, soup):
        """Strategy 1: Look for restaurant cards/listings"""
        restaurants = []
        
        # Common selectors for restaurant cards
        card_selectors = [
            '[data-test*="restaurant-card"]',
            '[data-test*="restaurant-listing"]',
            '.restaurant-card',
            '.restaurant-listing',
            '[class*="restaurant-card"]',
            '[class*="listing"]'
        ]
        
        cards = []
        for selector in card_selectors:
            found_cards = soup.select(selector)
            if found_cards:
                cards = found_cards
                print(f"Found {len(cards)} cards with selector: {selector}")
                break
        
        for card in cards:
            restaurant = self.parse_restaurant_card(card)
            if restaurant['name']:
                restaurants.append(restaurant)
        
        return restaurants
    
    def strategy_links_and_scripts(self, soup):
        """Strategy 2: Look for restaurant links and JSON data"""
        restaurants = []
        
        # Find restaurant links
        restaurant_links = soup.find_all('a', href=re.compile(r'/r/[\w-]+'))
        
        for link in restaurant_links[:50]:  # Limit to avoid too many
            name = self.clean_text(link.get_text())
            if name and len(name) > 2:  # Basic validation
                restaurant = {
                    'name': name,
                    'url': urljoin(self.base_url, link.get('href', '')),
                    'phone': '',
                    'cuisine': ''
                }
                
                # Try to find cuisine and other info near the link
                parent = link.find_parent()
                if parent:
                    # Look for cuisine info
                    cuisine_text = parent.get_text()
                    cuisine_match = re.search(r'(Italian|Chinese|Japanese|Mexican|Indian|French|Thai|Greek|American|Canadian|Korean|Vietnamese|Mediterranean|Steakhouse|Seafood|Pizza|Sushi|Burger|BBQ)', cuisine_text, re.I)
                    if cuisine_match:
                        restaurant['cuisine'] = cuisine_match.group(1)
                
                restaurants.append(restaurant)
        
        return restaurants
    
    def strategy_structured_data(self, soup):
        """Strategy 3: Look for JSON-LD structured data"""
        restaurants = []
        
        # Find JSON-LD scripts
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Handle both single objects and arrays
                if isinstance(data, list):
                    items = data
                else:
                    items = [data]
                
                for item in items:
                    if item.get('@type') == 'Restaurant':
                        restaurant = {
                            'name': item.get('name', ''),
                            'url': item.get('url', ''),
                            'phone': item.get('telephone', ''),
                            'cuisine': item.get('servesCuisine', '')
                        }
                        
                        if restaurant['name']:
                            restaurants.append(restaurant)
                            
            except json.JSONDecodeError:
                continue
        
        return restaurants
    
    def strategy_generic_links(self, soup):
        """Strategy 4: Generic approach - find any promising links"""
        restaurants = []
        
        # Find all links that might be restaurants
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            text = self.clean_text(link.get_text())
            
            # Skip if no text or text is too short
            if not text or len(text) < 3:
                continue
            
            # Skip navigation/utility links
            skip_patterns = [
                r'sign.?in', r'sign.?up', r'login', r'register', r'about', r'contact',
                r'privacy', r'terms', r'help', r'support', r'blog', r'careers',
                r'press', r'home', r'search', r'filter', r'sort', r'view', r'more'
            ]
            
            if any(re.search(pattern, text, re.I) for pattern in skip_patterns):
                continue
            
            # Look for restaurant-like links
            if (re.search(r'/r/', href) or 
                any(word in text.lower() for word in ['restaurant', 'cafe', 'bistro', 'grill', 'kitchen', 'house', 'bar'])):
                
                restaurant = {
                    'name': text,
                    'url': urljoin(self.base_url, href) if href else '',
                    'phone': '',
                    'cuisine': ''
                }
                restaurants.append(restaurant)
        
        # Remove duplicates based on name
        seen_names = set()
        unique_restaurants = []
        for restaurant in restaurants:
            if restaurant['name'] not in seen_names:
                seen_names.add(restaurant['name'])
                unique_restaurants.append(restaurant)
        
        return unique_restaurants[:50]  # Limit results
    
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
            name_selectors = [
                '[data-test*="restaurant-card-title"]',
                '[data-test*="title"]',
                'h2', 'h3', 'h4',
                '.title', '.name',
                '[class*="title"]', '[class*="name"]'
            ]
            
            name_elem = None
            for selector in name_selectors:
                name_elem = card.select_one(selector)
                if name_elem:
                    break
            
            if name_elem:
                restaurant['name'] = self.clean_text(name_elem.get_text())
                
                # Try to get URL from the name element or nearby
                link = name_elem.find('a') or name_elem if name_elem.name == 'a' else card.find('a')
                if link and link.get('href'):
                    restaurant['url'] = urljoin(self.base_url, link.get('href'))
            
            # Extract cuisine
            cuisine_selectors = [
                '[data-test*="cuisine"]',
                '[data-test*="category"]',
                '.cuisine', '.category',
                '[class*="cuisine"]', '[class*="category"]'
            ]
            
            for selector in cuisine_selectors:
                cuisine_elem = card.select_one(selector)
                if cuisine_elem:
                    restaurant['cuisine'] = self.clean_text(cuisine_elem.get_text())
                    break
            
            # Extract phone (try text search)
            card_text = card.get_text()
            restaurant['phone'] = self.extract_phone_from_text(card_text)
            
            return restaurant
            
        except Exception as e:
            print(f"Error parsing restaurant card: {e}")
            return restaurant
    
    def get_restaurant_details(self, restaurant_url):
        """Get additional details from restaurant page"""
        try:
            time.sleep(random.uniform(1, 3))  # Be respectful
            response = self.fetch_page(restaurant_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {'phone': '', 'cuisine': ''}
            
            # Look for phone
            phone_selectors = [
                'a[href^="tel:"]',
                '[data-test*="phone"]',
                '.phone', '.contact',
                '[class*="phone"]', '[class*="contact"]'
            ]
            
            for selector in phone_selectors:
                phone_elem = soup.select_one(selector)
                if phone_elem:
                    phone_text = phone_elem.get('href', '') + ' ' + phone_elem.get_text()
                    phone = self.extract_phone_from_text(phone_text)
                    if phone:
                        details['phone'] = phone
                        break
            
            # If no phone found, search page text
            if not details['phone']:
                page_text = soup.get_text()
                details['phone'] = self.extract_phone_from_text(page_text)
            
            # Look for cuisine info
            cuisine_keywords = [
                'Italian', 'Chinese', 'Japanese', 'Mexican', 'Indian', 'French', 'Thai', 'Greek',
                'American', 'Canadian', 'Korean', 'Vietnamese', 'Mediterranean', 'Steakhouse',
                'Seafood', 'Pizza', 'Sushi', 'Burger', 'BBQ', 'Contemporary', 'Modern', 'Traditional'
            ]
            
            page_text = soup.get_text()
            for keyword in cuisine_keywords:
                if re.search(rf'\b{keyword}\b', page_text, re.I):
                    details['cuisine'] = keyword
                    break
            
            return details
            
        except Exception as e:
            print(f"Error getting details for {restaurant_url}: {e}")
            return {'phone': '', 'cuisine': ''}
    
    def scrape_toronto_restaurants(self, max_restaurants=50):
        """Main scraping method for Toronto restaurants"""
        print("Starting Advanced OpenTable Canada restaurant scraper...")
        print(f"Target: {max_restaurants} restaurants from Toronto, Ontario")
        
        # Multiple URLs to try for Toronto
        toronto_urls = [
            f"{self.base_url}/toronto-ontario-restaurants",
            f"{self.base_url}/toronto-restaurants",
            f"{self.base_url}/c/toronto",
            f"{self.base_url}/search?location=toronto"
        ]
        
        restaurants_found = 0
        
        for base_url in toronto_urls:
            if restaurants_found >= max_restaurants:
                break
                
            print(f"\nTrying URL: {base_url}")
            
            page = 1
            consecutive_empty_pages = 0
            
            while restaurants_found < max_restaurants and consecutive_empty_pages < 3:
                try:
                    # Construct page URL
                    if page == 1:
                        current_url = base_url
                    else:
                        separator = '&' if '?' in base_url else '?'
                        current_url = f"{base_url}{separator}page={page}"
                    
                    print(f"\n--- Scraping page {page} ---")
                    response = self.fetch_page(current_url)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract restaurants from this page
                    page_restaurants = self.extract_restaurants_from_page(soup)
                    
                    if not page_restaurants:
                        consecutive_empty_pages += 1
                        print(f"No restaurants found on page {page}")
                    else:
                        consecutive_empty_pages = 0
                        print(f"Found {len(page_restaurants)} restaurants on page {page}")
                        
                        # Process each restaurant
                        for restaurant in page_restaurants:
                            if restaurants_found >= max_restaurants:
                                break
                            
                            if restaurant['name'] and restaurant not in self.restaurants:
                                # Get additional details if we have a URL
                                if restaurant['url'] and (not restaurant['phone'] or not restaurant['cuisine']):
                                    details = self.get_restaurant_details(restaurant['url'])
                                    if not restaurant['phone'] and details['phone']:
                                        restaurant['phone'] = details['phone']
                                    if not restaurant['cuisine'] and details['cuisine']:
                                        restaurant['cuisine'] = details['cuisine']
                                
                                self.restaurants.append(restaurant)
                                restaurants_found += 1
                                
                                print(f"  {restaurants_found}. {restaurant['name']}")
                                if restaurant['cuisine']:
                                    print(f"     Cuisine: {restaurant['cuisine']}")
                                if restaurant['phone']:
                                    print(f"     Phone: {restaurant['phone']}")
                    
                    page += 1
                    
                    # Be respectful - add delay between pages
                    time.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    print(f"Error on page {page}: {e}")
                    consecutive_empty_pages += 1
                    if consecutive_empty_pages >= 3:
                        break
        
        print(f"\nScraping completed! Found {len(self.restaurants)} restaurants.")
        return self.restaurants
    
    def save_to_csv(self, filename="toronto_restaurants_advanced.csv"):
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
        
        # Also save a formatted version for easier reading
        formatted_filename = filename.replace('.csv', '_formatted.csv')
        with open(formatted_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Name', 'URL', 'Phone', 'Cuisine'])
            
            for i, restaurant in enumerate(self.restaurants, 1):
                writer.writerow([
                    f"{i}. {restaurant['name']}",
                    restaurant['url'],
                    restaurant['phone'] or 'N/A',
                    restaurant['cuisine'] or 'N/A'
                ])
        
        print(f"Formatted data also saved to {formatted_filename}")
    
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
        
        # Cuisine breakdown
        cuisines = {}
        for restaurant in self.restaurants:
            cuisine = restaurant['cuisine'] or 'Unknown'
            cuisines[cuisine] = cuisines.get(cuisine, 0) + 1
        
        print(f"\n=== CUISINE BREAKDOWN ===")
        for cuisine, count in sorted(cuisines.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{cuisine}: {count}")
        
        print(f"\n=== SAMPLE DATA ===")
        for i, restaurant in enumerate(self.restaurants[:5]):
            print(f"{i+1}. {restaurant['name']}")
            print(f"   URL: {restaurant['url'] or 'N/A'}")
            print(f"   Phone: {restaurant['phone'] or 'N/A'}")
            print(f"   Cuisine: {restaurant['cuisine'] or 'N/A'}")
            print()


def main():
    """Main function to run the advanced scraper"""
    scraper = AdvancedOpenTableScraper()
    
    try:
        # Scrape restaurants
        restaurants = scraper.scrape_toronto_restaurants(max_restaurants=50)
        
        # Save to CSV
        scraper.save_to_csv("toronto_restaurants_advanced.csv")
        
        # Print summary
        scraper.print_summary()
        
        print("\n=== SCRAPING COMPLETE ===")
        print("Check 'toronto_restaurants_advanced.csv' for the complete data!")
        print("Also check 'toronto_restaurants_advanced_formatted.csv' for a more readable version!")
        
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
