import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XboxROGAllyScraper:
    def __init__(self):
        self.base_url = "https://www.xbox.com/en-AU/handhelds/rog-xbox-ally"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.scraped_data = {}
        
    def get_page_content(self, url):
        """Get page content with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
    
    def extract_main_content(self, soup):
        """Extract main content from the page"""
        logger.info("Extracting main content...")
        
        # Extract main heading and taglines
        main_content = {}
        
        # Main headings
        headings = soup.find_all(['h1', 'h2', 'h3'])
        main_content['headings'] = []
        for heading in headings:
            if heading.get_text(strip=True):
                main_content['headings'].append({
                    'level': heading.name,
                    'text': heading.get_text(strip=True)
                })
        
        # Extract main sections
        sections = soup.find_all('section') or soup.find_all('div', class_=re.compile(r'section|pivot|tab'))
        main_content['sections'] = []
        
        for section in sections:
            section_data = {}
            section_data['id'] = section.get('id', '')
            section_data['class'] = section.get('class', [])
            
            # Extract section content
            section_text = section.get_text(strip=True)
            if len(section_text) > 50:  # Only include substantial sections
                section_data['content'] = section_text[:500] + "..." if len(section_text) > 500 else section_text
            
            # Extract images
            images = section.find_all('img')
            section_data['images'] = []
            for img in images:
                img_data = {
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                }
                if img_data['src']:
                    section_data['images'].append(img_data)
            
            main_content['sections'].append(section_data)
        
        return main_content
    
    def extract_specifications(self, soup):
        """Extract detailed specifications"""
        logger.info("Extracting specifications...")
        specs = {}
        
        # Look for specification tables or lists
        spec_sections = soup.find_all(['table', 'ul', 'ol'], class_=re.compile(r'spec|specification|tech|technical'))
        
        for spec_section in spec_sections:
            # Extract table data
            if spec_section.name == 'table':
                rows = spec_section.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            specs[key] = value
            
            # Extract list data
            elif spec_section.name in ['ul', 'ol']:
                items = spec_section.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if text and len(text) > 10:
                        # Try to parse key-value pairs
                        if ':' in text:
                            key, value = text.split(':', 1)
                            specs[key.strip()] = value.strip()
                        else:
                            specs[f"feature_{len(specs)}"] = text
        
        # Look for specification text in the page
        spec_text = soup.find_all(text=re.compile(r'AMD Ryzen|RAM|GB|TB|SSD|Display|Battery|WiFi|Bluetooth|USB|Processor|Memory|Storage'))
        for text in spec_text:
            if text.parent and text.parent.name in ['p', 'div', 'span']:
                parent_text = text.parent.get_text(strip=True)
                if len(parent_text) > 20:
                    specs[f"spec_{len(specs)}"] = parent_text
        
        return specs
    
    def extract_gaming_features(self, soup):
        """Extract gaming-related features"""
        logger.info("Extracting gaming features...")
        gaming = {}
        
        # Look for gaming-related content
        gaming_keywords = ['Game Pass', 'Cloud Gaming', 'Play Anywhere', 'Remote Play', 'Xbox', 'Gaming']
        
        for keyword in gaming_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.parent:
                    parent = element.parent
                    # Get surrounding context
                    context = parent.get_text(strip=True)
                    if len(context) > 20:
                        gaming[keyword.lower().replace(' ', '_')] = context
        
        # Look for specific gaming sections
        gaming_sections = soup.find_all(['div', 'section'], class_=re.compile(r'gaming|game|xbox'))
        for section in gaming_sections:
            section_text = section.get_text(strip=True)
            if len(section_text) > 50:
                gaming[f"gaming_section_{len(gaming)}"] = section_text
        
        return gaming
    
    def extract_model_comparisons(self, soup):
        """Extract model comparison data"""
        logger.info("Extracting model comparisons...")
        comparisons = {}
        
        # Look for comparison tables or sections
        comparison_elements = soup.find_all(text=re.compile(r'Ally X|Ally X vs|vs Ally|difference|compare', re.IGNORECASE))
        
        for element in comparison_elements:
            if element.parent:
                parent = element.parent
                # Get the full comparison context
                context = parent.get_text(strip=True)
                if len(context) > 30:
                    comparisons[f"comparison_{len(comparisons)}"] = context
        
        # Look for specification comparisons
        spec_comparisons = soup.find_all(text=re.compile(r'24GB|16GB|1TB|512GB|80Wh|60Wh|Z2 Extreme|Z2 A'))
        for spec in spec_comparisons:
            if spec.parent:
                parent_text = spec.parent.get_text(strip=True)
                if len(parent_text) > 20:
                    comparisons[f"spec_comparison_{len(comparisons)}"] = parent_text
        
        return comparisons
    
    def extract_controls_and_interface(self, soup):
        """Extract controls and interface information"""
        logger.info("Extracting controls and interface...")
        controls = {}
        
        # Look for control-related content
        control_keywords = ['controls', 'buttons', 'triggers', 'grips', 'Xbox button', 'Game Bar']
        
        for keyword in control_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.parent:
                    parent = element.parent
                    context = parent.get_text(strip=True)
                    if len(context) > 20:
                        controls[keyword.lower().replace(' ', '_')] = context
        
        # Look for interface descriptions
        interface_elements = soup.find_all(text=re.compile(r'interface|UI|experience|boot|startup'))
        for element in interface_elements:
            if element.parent:
                parent_text = element.parent.get_text(strip=True)
                if len(parent_text) > 30:
                    controls[f"interface_{len(controls)}"] = parent_text
        
        return controls
    
    def extract_connectivity_and_ports(self, soup):
        """Extract connectivity and port information"""
        logger.info("Extracting connectivity and ports...")
        connectivity = {}
        
        # Look for connectivity-related content
        connectivity_keywords = ['USB', 'WiFi', 'Bluetooth', 'microSD', 'audio', 'port', 'connectivity']
        
        for keyword in connectivity_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.parent:
                    parent = element.parent
                    context = parent.get_text(strip=True)
                    if len(context) > 20:
                        connectivity[keyword.lower().replace(' ', '_')] = context
        
        # Look for port specifications
        port_specs = soup.find_all(text=re.compile(r'USB 4|USB 3.2|Thunderbolt|DisplayPort|Power Delivery'))
        for spec in port_specs:
            if spec.parent:
                parent_text = spec.parent.get_text(strip=True)
                if len(parent_text) > 20:
                    connectivity[f"port_spec_{len(connectivity)}"] = parent_text
        
        return connectivity
    
    def extract_technical_details(self, soup):
        """Extract technical details"""
        logger.info("Extracting technical details...")
        technical = {}
        
        # Look for technical specifications
        tech_keywords = ['120Hz', 'refresh rate', 'FreeSync', 'brightness', 'Gorilla Glass', 'anti-reflection', 'IPS', 'FHD', '1080p']
        
        for keyword in tech_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.parent:
                    parent = element.parent
                    context = parent.get_text(strip=True)
                    if len(context) > 20:
                        technical[keyword.lower().replace(' ', '_')] = context
        
        return technical
    
    def extract_accessories_and_packaging(self, soup):
        """Extract accessories and packaging information"""
        logger.info("Extracting accessories and packaging...")
        accessories = {}
        
        # Look for accessory-related content
        accessory_keywords = ['included', 'accessories', 'stand', 'charger', '65W', 'packaging']
        
        for keyword in accessory_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.parent:
                    parent = element.parent
                    context = parent.get_text(strip=True)
                    if len(context) > 20:
                        accessories[keyword.lower().replace(' ', '_')] = context
        
        return accessories
    
    def extract_use_cases_and_scenarios(self, soup):
        """Extract use cases and scenarios"""
        logger.info("Extracting use cases and scenarios...")
        use_cases = {}
        
        # Look for use case descriptions
        use_case_keywords = ['portable', 'travel', 'home', 'gaming', 'use', 'scenario', 'when']
        
        for keyword in use_case_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.parent:
                    parent = element.parent
                    context = parent.get_text(strip=True)
                    if len(context) > 30:
                        use_cases[keyword.lower().replace(' ', '_')] = context
        
        return use_cases
    
    def extract_pricing_and_availability(self, soup):
        """Extract pricing and availability information"""
        logger.info("Extracting pricing and availability...")
        pricing = {}
        
        # Look for pricing information
        pricing_keywords = ['price', 'cost', 'buy', 'purchase', 'available', 'retailer']
        
        for keyword in pricing_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.parent:
                    parent = element.parent
                    context = parent.get_text(strip=True)
                    if len(context) > 20:
                        pricing[keyword.lower().replace(' ', '_')] = context
        
        return pricing
    
    def extract_all_data(self):
        """Extract all data from the Xbox ROG Ally website"""
        logger.info(f"Starting comprehensive data extraction from {self.base_url}")
        
        # Get main page content
        main_content = self.get_page_content(self.base_url)
        if not main_content:
            logger.error("Failed to fetch main page")
            return None
        
        soup = BeautifulSoup(main_content, 'html.parser')
        
        # Extract all categories of data
        self.scraped_data = {
            'url': self.base_url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'main_content': self.extract_main_content(soup),
            'specifications': self.extract_specifications(soup),
            'gaming_features': self.extract_gaming_features(soup),
            'model_comparisons': self.extract_model_comparisons(soup),
            'controls_and_interface': self.extract_controls_and_interface(soup),
            'connectivity_and_ports': self.extract_connectivity_and_ports(soup),
            'technical_details': self.extract_technical_details(soup),
            'accessories_and_packaging': self.extract_accessories_and_packaging(soup),
            'use_cases_and_scenarios': self.extract_use_cases_and_scenarios(soup),
            'pricing_and_availability': self.extract_pricing_and_availability(soup)
        }
        
        logger.info("Data extraction completed successfully")
        return self.scraped_data
    
    def save_data(self, filename='xbox_rog_ally_complete_data.json'):
        """Save scraped data to JSON file"""
        if not self.scraped_data:
            logger.error("No data to save")
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False
    
    def generate_summary(self):
        """Generate a summary of scraped data"""
        if not self.scraped_data:
            return "No data available"
        
        summary = f"""
=== XBOX ROG ALLY COMPLETE DATA EXTRACTION SUMMARY ===
URL: {self.scraped_data['url']}
Timestamp: {self.scraped_data['timestamp']}

DATA CATEGORIES EXTRACTED:
1. Main Content: {len(self.scraped_data['main_content'].get('headings', []))} headings, {len(self.scraped_data['main_content'].get('sections', []))} sections
2. Specifications: {len(self.scraped_data['specifications'])} items
3. Gaming Features: {len(self.scraped_data['gaming_features'])} items
4. Model Comparisons: {len(self.scraped_data['model_comparisons'])} items
5. Controls & Interface: {len(self.scraped_data['controls_and_interface'])} items
6. Connectivity & Ports: {len(self.scraped_data['connectivity_and_ports'])} items
7. Technical Details: {len(self.scraped_data['technical_details'])} items
8. Accessories & Packaging: {len(self.scraped_data['accessories_and_packaging'])} items
9. Use Cases & Scenarios: {len(self.scraped_data['use_cases_and_scenarios'])} items
10. Pricing & Availability: {len(self.scraped_data['pricing_and_availability'])} items

TOTAL DATA POINTS: {sum(len(v) if isinstance(v, dict) else 0 for v in self.scraped_data.values() if isinstance(v, dict))}
        """
        return summary

def main():
    """Main function to run the scraper"""
    logger.info("Starting Xbox ROG Ally comprehensive data scraper...")
    
    scraper = XboxROGAllyScraper()
    
    # Extract all data
    data = scraper.extract_all_data()
    
    if data:
        # Generate and display summary
        summary = scraper.generate_summary()
        print(summary)
        
        # Save data to file
        scraper.save_data()
        
        # Display some sample data
        print("\n=== SAMPLE EXTRACTED DATA ===")
        print(f"Specifications found: {list(scraper.scraped_data['specifications'].keys())[:5]}")
        print(f"Gaming features found: {list(scraper.scraped_data['gaming_features'].keys())[:5]}")
        print(f"Model comparisons found: {list(scraper.scraped_data['model_comparisons'].keys())[:5]}")
        
        logger.info("Scraping completed successfully!")
    else:
        logger.error("Scraping failed!")

if __name__ == "__main__":
    main() 