"""Advanced Web Crawler with source type filtering.

This module provides web crawling capabilities with support for different source types.
It can be integrated into the Research Agent for real web scraping.

Usage:
    from utils.web_crawler import WebCrawler
    
    crawler = WebCrawler()
    results = crawler.crawl_candidates(
        candidates=["Python", "JavaScript"],
        source_types=["news", "forums"],
        context={"entity_type": "programming languages"}
    )
"""

from typing import List, Dict, Optional
import time
import re
from datetime import datetime
from urllib.parse import urlparse, quote_plus

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available. Install with: pip install selenium webdriver-manager")

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

from bs4 import BeautifulSoup

# Import source configurations
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import SOURCE_CONFIGS, RATE_LIMIT_DELAY, MAX_SOURCES_PER_CANDIDATE


class WebCrawler:
    """Advanced web crawler with source type filtering."""
    
    def __init__(self):
        """Initialize the web crawler."""
        if not SELENIUM_AVAILABLE:
            raise RuntimeError("Selenium is required. Install with: pip install selenium webdriver-manager")
        
        self.driver = None
        
    def __enter__(self):
        """Context manager entry."""
        self._init_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def _init_driver(self):
        """Initialize Chrome WebDriver."""
        if self.driver:
            return
        
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--window-size=1920,1080')
        opts.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=opts)
            else:
                self.driver = webdriver.Chrome(options=opts)
            
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            print("✅ WebDriver initialized successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to create WebDriver: {e}")
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def crawl_candidates(
        self,
        candidates: List[str],
        source_types: List[str],
        context: Dict[str, str] = None,
        max_results_per_candidate: int = MAX_SOURCES_PER_CANDIDATE
    ) -> Dict[str, Dict[str, any]]:
        """
        Crawl multiple candidates with source type filtering.
        
        Args:
            candidates: List of candidate names
            source_types: List of source types to search (e.g., ['news', 'forums'])
            context: Optional context (entity_type, region, etc.)
            max_results_per_candidate: Max sources per candidate
        
        Returns:
            Dict mapping candidate to {text, sources}
        """
        if not self.driver:
            self._init_driver()
        
        context = context or {}
        results = {}
        
        for candidate in candidates:
            print(f"\n🔍 Crawling: {candidate}")
            
            candidate_data = self._crawl_single_candidate(
                candidate,
                source_types,
                context,
                max_results_per_candidate
            )
            
            results[candidate] = candidate_data
            
            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)
        
        return results
    
    def _crawl_single_candidate(
        self,
        candidate: str,
        source_types: List[str],
        context: Dict[str, str],
        max_results: int
    ) -> Dict[str, any]:
        """Crawl a single candidate across multiple source types."""
        
        all_texts = []
        all_sources = []
        
        for source_type in source_types:
            if source_type not in SOURCE_CONFIGS:
                continue
            
            print(f"  📚 Source type: {source_type}")
            
            # Build search query
            query = self._build_query(candidate, source_type, context)
            
            # Perform search
            urls = self._google_search(query, max_results=max_results)
            
            # Filter URLs by source type
            filtered_urls = self._filter_urls_by_source(urls, source_type)
            
            print(f"    Found {len(filtered_urls)} relevant URLs")
            
            # Extract content from URLs
            for url in filtered_urls[:max_results]:
                text = self._extract_text(url)
                
                if text:
                    all_texts.append(text)
                    all_sources.append({
                        "url": url,
                        "title": self._extract_title(url),
                        "source_type": source_type,
                        "domain": self._extract_domain(url),
                        "icon": SOURCE_CONFIGS[source_type].get("icon", "📄"),
                        "collected_at": datetime.now().isoformat()
                    })
                
                time.sleep(1)  # Rate limit between pages
        
        return {
            "text": "\n\n".join(all_texts),
            "sources": all_sources
        }
    
    def _build_query(
        self,
        candidate: str,
        source_type: str,
        context: Dict[str, str]
    ) -> str:
        """Build search query with source type filtering."""
        
        query_parts = [candidate]
        
        # Add context
        if context.get('entity_type'):
            query_parts.append(context['entity_type'])
        
        if context.get('region'):
            query_parts.append(context['region'])
        
        # Add source-specific suffix
        config = SOURCE_CONFIGS.get(source_type, {})
        if config.get('search_suffix'):
            query_parts.append(config['search_suffix'])
        
        return ' '.join(query_parts)
    
    def _google_search(
        self,
        query: str,
        max_results: int = 10
    ) -> List[str]:
        """Perform Google search and extract URLs."""
        
        urls = []
        
        try:
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            self.driver.get(search_url)
            
            time.sleep(2)
            
            # Extract links
            link_selectors = [
                'div.g a[href]',
                'div.yuRUbf a[href]',
                'a[jsname="UWckNb"]',
            ]
            
            for selector in link_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for link in links:
                        href = link.get_attribute('href')
                        if href and href.startswith('http') and 'google.com' not in href:
                            if href not in urls:
                                urls.append(href)
                                if len(urls) >= max_results:
                                    return urls
                except Exception:
                    continue
            
            return urls
            
        except Exception as e:
            print(f"    ⚠️  Search error: {e}")
            return []
    
    def _filter_urls_by_source(
        self,
        urls: List[str],
        source_type: str
    ) -> List[str]:
        """Filter URLs to match source type domains."""
        
        if source_type not in SOURCE_CONFIGS:
            return urls
        
        config = SOURCE_CONFIGS[source_type]
        allowed_domains = config.get('domains', [])
        
        if not allowed_domains:
            return urls
        
        filtered = []
        for url in urls:
            domain = self._extract_domain(url)
            
            # Check if domain matches any allowed domain
            for allowed in allowed_domains:
                if allowed in domain or domain.endswith(allowed):
                    filtered.append(url)
                    break
        
        return filtered
    
    def _extract_text(self, url: str, timeout: int = 10) -> str:
        """Extract visible text from URL."""
        
        try:
            self.driver.set_page_load_timeout(timeout)
            self.driver.get(url)
            
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Remove non-content tags
            for tag in soup(['script', 'style', 'noscript', 'iframe', 'nav', 'footer', 'header', 'aside']):
                tag.extract()
            
            text = ' '.join(soup.stripped_strings)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Limit text length
            return text[:5000]
            
        except Exception as e:
            print(f"    ⚠️  Extract error for {url}: {e}")
            return ""
    
    def _extract_title(self, url: str) -> str:
        """Extract page title."""
        try:
            return self.driver.title or self._extract_domain(url)
        except:
            return self._extract_domain(url)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "unknown.com"


# Example usage
if __name__ == "__main__":
    print("🕷️  Advanced Web Crawler - Test\n")
    
    # Test with context manager
    with WebCrawler() as crawler:
        results = crawler.crawl_candidates(
            candidates=["Python programming language"],
            source_types=["news", "forums"],
            context={"entity_type": "programming language"},
            max_results_per_candidate=2
        )
        
        for candidate, data in results.items():
            print(f"\n{'='*80}")
            print(f"Candidate: {candidate}")
            print(f"Text length: {len(data['text'])} characters")
            print(f"Sources found: {len(data['sources'])}")
            
            print("\nSources:")
            for source in data['sources']:
                print(f"  {source['icon']} {source['title']}")
                print(f"     {source['url']}")
                print(f"     Type: {source['source_type']}, Domain: {source['domain']}")
            
            print(f"\nText preview:")
            print(f"{data['text'][:300]}...")