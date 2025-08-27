import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedXboxROGAllyScraper:
    def __init__(self, use_selenium=True):
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
        self.use_selenium = use_selenium
        self.driver = None
        self.scraped_data = {}
        
        if self.use_selenium:
            self.setup_selenium()
    
    def setup_selenium(self):
        """Setup Selenium WebDriver for JavaScript rendering"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            logger.info("Falling back to requests-only mode")
            self.use_selenium = False
    
    def get_page_with_selenium(self, url):
        """Get page content using Selenium for JavaScript rendering"""
        if not self.driver:
            return None
        
        try:
            logger.info(f"Loading page with Selenium: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(5)
            
            # Get the rendered page source
            page_source = self.driver.page_source
            logger.info("Page loaded successfully with Selenium")
            return page_source
            
        except TimeoutException:
            logger.warning("Page load timeout, proceeding with available content")
            return self.driver.page_source
        except Exception as e:
            logger.error(f"Selenium error: {e}")
            return None
    
    def get_page_content(self, url):
        """Get page content with fallback options"""
        if self.use_selenium:
            selenium_content = self.get_page_with_selenium(url)
            if selenium_content:
                return selenium_content
        
        # Fallback to requests
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
                time.sleep(2 ** attempt)
        return None
    
    def extract_all_tabs_and_sections(self, soup):
        """Extract content from all tabs, sections, and interactive elements"""
        logger.info("Extracting all tabs and sections...")
        all_content = {}
        
        # Find all tab-like elements
        tab_selectors = [
            '[role="tab"]',
            '[class*="tab"]',
            '[class*="pivot"]',
            '[class*="section"]',
            '[class*="accordion"]',
            '[class*="collapse"]'
        ]
        
        for selector in tab_selectors:
            tabs = soup.select(selector)
            for i, tab in enumerate(tabs):
                tab_data = {}
                tab_data['type'] = selector
                tab_data['index'] = i
                tab_data['id'] = tab.get('id', f'tab_{i}')
                tab_data['class'] = tab.get('class', [])
                tab_data['text'] = tab.get_text(strip=True)
                
                # Extract tab content
                tab_content = tab.find_parent() or tab
                if tab_content:
                    tab_data['content'] = tab_content.get_text(strip=True)[:1000]
                
                all_content[f'tab_{selector}_{i}'] = tab_data
        
        # Find all expandable/collapsible content
        expandable_selectors = [
            '[class*="expand"]',
            '[class*="collapse"]',
            '[class*="accordion"]',
            '[aria-expanded]',
            '[data-toggle]'
        ]
        
        for selector in expandable_selectors:
            elements = soup.select(selector)
            for i, element in enumerate(elements):
                element_data = {}
                element_data['type'] = 'expandable'
                element_data['selector'] = selector
                element_data['index'] = i
                element_data['id'] = element.get('id', f'expandable_{i}')
                element_data['aria_expanded'] = element.get('aria-expanded', '')
                element_data['text'] = element.get_text(strip=True)
                
                # Get parent content
                parent = element.find_parent()
                if parent:
                    element_data['parent_content'] = parent.get_text(strip=True)[:1000]
                
                all_content[f'expandable_{selector}_{i}'] = element_data
        
        return all_content
    
    def extract_interactive_elements(self, soup):
        """Extract interactive elements like buttons, links, and forms"""
        logger.info("Extracting interactive elements...")
        interactive = {}
        
        # Extract all buttons
        buttons = soup.find_all('button')
        for i, button in enumerate(buttons):
            button_data = {}
            button_data['type'] = 'button'
            button_data['index'] = i
            button_data['text'] = button.get_text(strip=True)
            button_data['id'] = button.get('id', f'button_{i}')
            button_data['class'] = button.get('class', [])
            button_data['onclick'] = button.get('onclick', '')
            
            # Get button context
            parent = button.find_parent()
            if parent:
                button_data['context'] = parent.get_text(strip=True)[:500]
            
            interactive[f'button_{i}'] = button_data
        
        # Extract all links
        links = soup.find_all('a')
        for i, link in enumerate(links):
            link_data = {}
            link_data['type'] = 'link'
            link_data['index'] = i
            link_data['text'] = link.get_text(strip=True)
            link_data['href'] = link.get('href', '')
            link_data['id'] = link.get('id', f'link_{i}')
            link_data['class'] = link.get('class', [])
            
            # Get link context
            parent = link.find_parent()
            if parent:
                link_data['context'] = parent.get_text(strip=True)[:500]
            
            interactive[f'link_{i}'] = link_data
        
        # Extract all forms and inputs
        forms = soup.find_all('form')
        for i, form in enumerate(forms):
            form_data = {}
            form_data['type'] = 'form'
            form_data['index'] = i
            form_data['id'] = form.get('id', f'form_{i}')
            form_data['action'] = form.get('action', '')
            form_data['method'] = form.get('method', '')
            
            # Extract form inputs
            inputs = form.find_all('input')
            form_data['inputs'] = []
            for inp in inputs:
                input_data = {
                    'type': inp.get('type', ''),
                    'name': inp.get('name', ''),
                    'id': inp.get('id', ''),
                    'placeholder': inp.get('placeholder', '')
                }
                form_data['inputs'].append(input_data)
            
            interactive[f'form_{i}'] = form_data
        
        return interactive
    
    def extract_comprehensive_specifications(self, soup):
        """Extract comprehensive specifications from all sources"""
        logger.info("Extracting comprehensive specifications...")
        specs = {}
        
        # Extract from tables
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            table_data = {}
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value and len(key) > 2:
                        table_data[key] = value
            
            if table_data:
                specs[f'table_specs_{i}'] = table_data
        
        # Extract from definition lists
        dl_elements = soup.find_all('dl')
        for i, dl in enumerate(dl_elements):
            dl_data = {}
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            
            for j, (dt, dd) in enumerate(zip(dts, dds)):
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                if key and value:
                    dl_data[key] = value
            
            if dl_data:
                specs[f'definition_list_{i}'] = dl_data
        
        # Extract from structured lists
        structured_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'spec|specification|tech|technical|feature'))
        for i, list_elem in enumerate(structured_lists):
            list_data = []
            items = list_elem.find_all('li')
            
            for item in items:
                text = item.get_text(strip=True)
                if text and len(text) > 5:
                    # Try to parse key-value pairs
                    if ':' in text:
                        parts = text.split(':', 1)
                        if len(parts) == 2:
                            list_data.append({
                                'key': parts[0].strip(),
                                'value': parts[1].strip()
                            })
                        else:
                            list_data.append({'text': text})
                    else:
                        list_data.append({'text': text})
            
            if list_data:
                specs[f'structured_list_{i}'] = list_data
        
        # Extract from text content with regex patterns
        spec_patterns = [
            r'AMD Ryzen[^.]*',
            r'\d+GB\s+(?:LPDDR5X?|RAM)[^.]*',
            r'\d+TB\s+(?:M\.2|SSD)[^.]*',
            r'\d+\.?\d*["\']?\s*(?:inch|")[^.]*',
            r'\d+p\s+(?:FHD|resolution)[^.]*',
            r'\d+Hz\s+(?:refresh|frequency)[^.]*',
            r'\d+Wh\s+(?:battery|power)[^.]*',
            r'WiFi\s+\d+[^.]*',
            r'Bluetooth\s+\d+\.?\d*[^.]*',
            r'USB\s+\d+[^.]*',
            r'Thunderbolt\s+\d+[^.]*',
            r'DisplayPort\s+\d+\.?\d*[^.]*',
            r'Gorilla Glass[^.]*',
            r'Corning[^.]*',
            r'FreeSync[^.]*',
            r'IPS[^.]*',
            r'FHD[^.]*',
            r'1080p[^.]*'
        ]
        
        for pattern in spec_patterns:
            matches = soup.find_all(text=re.compile(pattern, re.IGNORECASE))
            for match in matches:
                if match.parent:
                    parent_text = match.parent.get_text(strip=True)
                    if len(parent_text) > 20:
                        specs[f'regex_match_{pattern[:20]}'] = parent_text
        
        return specs
    
    def extract_all_data(self):
        """Extract ALL data from the Xbox ROG Ally website"""
        logger.info(f"Starting COMPREHENSIVE data extraction from {self.base_url}")
        
        # Get page content
        page_content = self.get_page_content(self.base_url)
        if not page_content:
            logger.error("Failed to fetch page content")
            return None
        
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Extract ALL categories of data
        self.scraped_data = {
            'url': self.base_url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'scraping_method': 'Selenium + Requests' if self.use_selenium else 'Requests only',
            
            # Comprehensive content extraction
            'all_tabs_and_sections': self.extract_all_tabs_and_sections(soup),
            'interactive_elements': self.extract_interactive_elements(soup),
            'comprehensive_specifications': self.extract_comprehensive_specifications(soup),
            
            # Main content structure
            'main_content': {
                'headings': [{'level': h.name, 'text': h.get_text(strip=True)} for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) if h.get_text(strip=True)],
                'paragraphs': [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 20],
                'images': [{'src': img.get('src', ''), 'alt': img.get('alt', ''), 'title': img.get('title', '')} for img in soup.find_all('img') if img.get('src')],
                'sections': [
                    {'id': s.get('id', ''), 'class': s.get('class', []), 'content': s.get_text(strip=True)[:1000]} 
                    for s in soup.find_all(['section', 'div']) 
                    if s.get('id') or (s.get('class') and any('section' in c.lower() for c in s.get('class', [])))
                ],
            },
            
            # Detailed feature extraction
            'gaming_features': self.extract_gaming_features(soup),
            'model_comparisons': self.extract_model_comparisons(soup),
            'controls_and_interface': self.extract_controls_and_interface(soup),
            'connectivity_and_ports': self.extract_connectivity_and_ports(soup),
            'technical_details': self.extract_technical_details(soup),
            'accessories_and_packaging': self.extract_accessories_and_packaging(soup),
            'use_cases_and_scenarios': self.extract_use_cases_and_scenarios(soup),
            'pricing_and_availability': self.extract_pricing_and_availability(soup),
            
            # Page metadata
            'page_metadata': {
                'title': soup.find('title').get_text(strip=True) if soup.find('title') else '',
                'meta_description': soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) else '',
                'meta_keywords': soup.find('meta', attrs={'name': 'keywords'})['content'] if soup.find('meta', attrs={'name': 'keywords'}) else '',
                'canonical_url': soup.find('link', attrs={'rel': 'canonical'})['href'] if soup.find('link', attrs={'rel': 'canonical'}) else '',
                'language': soup.find('html').get('lang', '') if soup.find('html') else '',
            },
            
            # Script and style information
            'scripts': [script.get('src', '') for script in soup.find_all('script') if script.get('src')],
            'stylesheets': [link.get('href', '') for link in soup.find_all('link', rel='stylesheet') if link.get('href')],
            'inline_styles': [style.get_text(strip=True) for style in soup.find_all('style') if style.get_text(strip=True)],
        }
        
        logger.info("COMPREHENSIVE data extraction completed successfully")
        return self.scraped_data
    
    def extract_gaming_features(self, soup):
        """Extract gaming-related features"""
        logger.info("Extracting gaming features...")
        gaming = {}
        
        gaming_keywords = ['Game Pass', 'Cloud Gaming', 'Play Anywhere', 'Remote Play', 'Xbox', 'Gaming', 'Stream', 'Library']
        
        for keyword in gaming_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.parent:
                    parent = element.parent
                    context = parent.get_text(strip=True)
                    if len(context) > 20:
                        gaming[keyword.lower().replace(' ', '_')] = context
        
        return gaming
    
    def extract_model_comparisons(self, soup):
        """Extract model comparison data"""
        logger.info("Extracting model comparisons...")
        comparisons = {}
        
        comparison_elements = soup.find_all(text=re.compile(r'Ally X|Ally X vs|vs Ally|difference|compare', re.IGNORECASE))
        
        for element in comparison_elements:
            if element.parent:
                parent = element.parent
                context = parent.get_text(strip=True)
                if len(context) > 30:
                    comparisons[f"comparison_{len(comparisons)}"] = context
        
        return comparisons
    
    def extract_controls_and_interface(self, soup):
        """Extract controls and interface information"""
        logger.info("Extracting controls and interface...")
        controls = {}
        
        control_keywords = ['controls', 'buttons', 'triggers', 'grips', 'Xbox button', 'Game Bar']
        
        for keyword in control_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.parent:
                    parent = element.parent
                    context = parent.get_text(strip=True)
                    if len(context) > 20:
                        controls[keyword.lower().replace(' ', '_')] = context
        
        return controls
    
    def extract_connectivity_and_ports(self, soup):
        """Extract connectivity and port information"""
        logger.info("Extracting connectivity and ports...")
        connectivity = {}
        
        connectivity_keywords = ['USB', 'WiFi', 'Bluetooth', 'microSD', 'audio', 'port', 'connectivity']
        
        for keyword in connectivity_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                if element.parent:
                    parent = element.parent
                    context = parent.get_text(strip=True)
                    if len(context) > 20:
                        connectivity[keyword.lower().replace(' ', '_')] = context
        
        return connectivity
    
    def extract_technical_details(self, soup):
        """Extract technical details"""
        logger.info("Extracting technical details...")
        technical = {}
        
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
    
    def generate_comprehensive_summary(self):
        """Generate a comprehensive summary of scraped data"""
        if not self.scraped_data:
            return "No data available"
        
        total_data_points = 0
        for key, value in self.scraped_data.items():
            if isinstance(value, dict):
                total_data_points += len(value)
            elif isinstance(value, list):
                total_data_points += len(value)
        
        summary = f"""
=== XBOX ROG ALLY COMPREHENSIVE DATA EXTRACTION SUMMARY ===
URL: {self.scraped_data['url']}
Timestamp: {self.scraped_data['timestamp']}
Scraping Method: {self.scraped_data['scraping_method']}

COMPREHENSIVE DATA CATEGORIES EXTRACTED:
1. All Tabs & Sections: {len(self.scraped_data['all_tabs_and_sections'])} items
2. Interactive Elements: {len(self.scraped_data['interactive_elements'])} items
3. Comprehensive Specifications: {len(self.scraped_data['comprehensive_specifications'])} items
4. Main Content: {len(self.scraped_data['main_content']['headings'])} headings, {len(self.scraped_data['main_content']['paragraphs'])} paragraphs, {len(self.scraped_data['main_content']['images'])} images, {len(self.scraped_data['main_content']['sections'])} sections
5. Gaming Features: {len(self.scraped_data['gaming_features'])} items
6. Model Comparisons: {len(self.scraped_data['model_comparisons'])} items
7. Controls & Interface: {len(self.scraped_data['controls_and_interface'])} items
8. Connectivity & Ports: {len(self.scraped_data['connectivity_and_ports'])} items
9. Technical Details: {len(self.scraped_data['technical_details'])} items
10. Accessories & Packaging: {len(self.scraped_data['accessories_and_packaging'])} items
11. Use Cases & Scenarios: {len(self.scraped_data['use_cases_and_scenarios'])} items
12. Pricing & Availability: {len(self.scraped_data['pricing_and_availability'])} items
13. Page Metadata: {len(self.scraped_data['page_metadata'])} items
14. Scripts: {len(self.scraped_data['scripts'])} items
15. Stylesheets: {len(self.scraped_data['stylesheets'])} items
16. Inline Styles: {len(self.scraped_data['inline_styles'])} items

TOTAL COMPREHENSIVE DATA POINTS: {total_data_points}
        """
        return summary
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")

def main():
    """Main function to run the advanced scraper"""
    logger.info("Starting Xbox ROG Ally COMPREHENSIVE data scraper...")
    
    scraper = AdvancedXboxROGAllyScraper(use_selenium=True)
    
    try:
        # Extract ALL data
        data = scraper.extract_all_data()
        
        if data:
            # Generate and display comprehensive summary
            summary = scraper.generate_comprehensive_summary()
            print(summary)
            
            # Save data to file
            scraper.save_data()
            
            # Display sample data
            print("\n=== SAMPLE EXTRACTED DATA ===")
            print(f"Tabs & Sections found: {list(scraper.scraped_data['all_tabs_and_sections'].keys())[:5]}")
            print(f"Interactive elements found: {list(scraper.scraped_data['interactive_elements'].keys())[:5]}")
            print(f"Comprehensive specs found: {list(scraper.scraped_data['comprehensive_specifications'].keys())[:5]}")
            
            logger.info("COMPREHENSIVE scraping completed successfully!")
        else:
            logger.error("Comprehensive scraping failed!")
    
    finally:
        # Clean up
        scraper.cleanup()

if __name__ == "__main__":
    main() 