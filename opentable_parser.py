"""
OpenTable Document Parser
========================
Parses the existing OpenTable response documents to extract restaurant data
Extracts: Name, URL, Phone, and Cuisine
Outputs: CSV file with the restaurant data
"""

import json
import csv
import re
from bs4 import BeautifulSoup
import html


class OpenTableDocumentParser:
    def __init__(self):
        self.restaurants = []
        self.base_url = "https://www.opentable.ca"
    
    def parse_html_file(self, filepath):
        """Parse the OpenTable HTML response file"""
        print(f"Parsing HTML file: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Extract JSON data from the script tag
            json_data = self.extract_json_from_html(content)
            if json_data:
                restaurants = self.extract_restaurants_from_json(json_data)
                self.restaurants.extend(restaurants)
                print(f"Extracted {len(restaurants)} restaurants from HTML file")
            else:
                print("No JSON data found in HTML file")
                
        except Exception as e:
            print(f"Error parsing HTML file: {e}")
    
    def extract_json_from_html(self, html_content):
        """Extract JSON data from HTML script tag"""
        try:
            # Look for the script tag containing window variables
            script_pattern = r'<script id="primary-window-vars" type="application/json">(.*?)</script>'
            match = re.search(script_pattern, html_content, re.DOTALL)
            
            if match:
                json_str = match.group(1)
                # Decode HTML entities
                json_str = html.unescape(json_str)
                data = json.loads(json_str)
                return data
            
            return None
            
        except Exception as e:
            print(f"Error extracting JSON from HTML: {e}")
            return None
    
    def extract_restaurants_from_json(self, data):
        """Extract restaurant data from the JSON structure"""
        restaurants = []
        
        try:
            # Navigate through the JSON structure to find restaurants
            lolz_data = data.get('windowVariables', {}).get('__INITIAL_STATE__', {}).get('lolzViewAll', {})
            search_results = lolz_data.get('searchResults', {})
            restaurant_list = search_results.get('restaurants', [])
            
            for rest_data in restaurant_list:
                restaurant = self.parse_restaurant_data(rest_data)
                if restaurant['name']:  # Only add if we have a name
                    restaurants.append(restaurant)
            
        except Exception as e:
            print(f"Error extracting restaurants from JSON: {e}")
        
        return restaurants
    
    def parse_restaurant_data(self, rest_data):
        """Parse individual restaurant data from JSON"""
        restaurant = {
            'name': '',
            'url': '',
            'phone': '',
            'cuisine': ''
        }
        
        try:
            # Extract name
            restaurant['name'] = rest_data.get('name', '').strip()
            
            # Extract URL
            urls = rest_data.get('urls', {})
            profile_link = urls.get('profileLink', {})
            if profile_link:
                link = profile_link.get('link', '')
                if link:
                    if link.startswith('http'):
                        restaurant['url'] = link
                    else:
                        restaurant['url'] = self.base_url + link
            
            # Extract phone
            contact_info = rest_data.get('contactInformation', {})
            if contact_info:
                phone = contact_info.get('formattedPhoneNumber', '') or contact_info.get('phoneNumber', '')
                restaurant['phone'] = self.clean_phone(phone)
            
            # Extract cuisine
            primary_cuisine = rest_data.get('primaryCuisine', {})
            if primary_cuisine:
                restaurant['cuisine'] = primary_cuisine.get('name', '').strip()
            
        except Exception as e:
            print(f"Error parsing restaurant data: {e}")
        
        return restaurant
    
    def clean_phone(self, phone):
        """Clean and format phone number"""
        if not phone:
            return ""
        
        # Remove any non-digit characters except + and spaces for formatting
        phone = phone.strip()
        
        # If it's already formatted nicely, return it
        if re.match(r'\(\d{3}\) \d{3}-\d{4}', phone):
            return phone
        
        # Extract digits only
        digits = re.sub(r'[^\d]', '', phone)
        
        # Format North American phone numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return phone  # Return original if we can't format it
    
    def save_to_csv(self, filename="toronto_restaurants_parsed.csv"):
        """Save parsed data to CSV file"""
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
        """Print summary of parsed data"""
        if not self.restaurants:
            print("No restaurants parsed!")
            return
        
        print(f"\n=== PARSING SUMMARY ===")
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
    """Main function to run the parser"""
    parser = OpenTableDocumentParser()
    
    try:
        # Parse the HTML file
        html_file = "opentable_response.html"
        parser.parse_html_file(html_file)
        
        # Save to CSV
        parser.save_to_csv("toronto_restaurants_parsed.csv")
        
        # Print summary
        parser.print_summary()
        
        print("\n=== PARSING COMPLETE ===")
        print("Check 'toronto_restaurants_parsed.csv' for the complete data!")
        
    except Exception as e:
        print(f"Error during parsing: {e}")


if __name__ == "__main__":
    main()
