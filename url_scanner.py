"""
URL Scanner Module for Threat Analysis

Scans URLs for threats using urlscan.io API with comprehensive threat scoring.
Provides detailed analysis including malicious indicators, categories, and risk assessment.
"""

import requests
import time
import logging
from typing import Dict, Optional
from urllib.parse import urlparse

class URLScanner:
    """
    URL threat scanner using urlscan.io API.
    
    Submits URLs for scanning and retrieves detailed threat analysis results.
    Handles API rate limiting and provides comprehensive threat scoring.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize URL scanner with optional API key.
        
        Args:
            api_key: urlscan.io API key for higher rate limits (optional)
        """
        self.api_key = api_key
        self.base_url = "https://urlscan.io/api/v1"
        self.scan_url = "https://urlscan.io/entry"
        
        # Set up headers for API requests
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Gmail-URL-Scanner-Bot/1.0'
        }
        
        if self.api_key:
            self.headers['API-Key'] = self.api_key
            logging.info("URLScanner initialized with API key")
        else:
            logging.info("URLScanner initialized without API key (limited rate)")
    
    def scan_url(self, url: str) -> Optional[Dict]:
        """
        Scan a URL for threats using urlscan.io.
        
        Submits URL for scanning, waits for completion, and returns detailed results.
        Includes threat scoring, malicious indicators, and categorization.
        
        Args:
            url: URL to scan for threats
            
        Returns:
            Dictionary with scan results or None if scan failed
        """
        try:
            # Validate URL format
            if not self._is_valid_url(url):
                logging.warning(f"Invalid URL format: {url}")
                return None
            
            logging.info(f"Submitting URL for scanning: {url}")
            
            # Submit URL for scanning
            scan_id = self._submit_url_for_scanning(url)
            if not scan_id:
                logging.error(f"Failed to submit URL for scanning: {url}")
                return None
            
            logging.info(f"URL submitted successfully, scan ID: {scan_id}")
            
            # Wait for scan to complete and get results
            scan_result = self._wait_for_scan_completion(scan_id)
            if not scan_result:
                logging.error(f"Failed to get scan results for: {url}")
                return None
            
            # Process and analyze the scan results
            analysis = self._analyze_scan_results(scan_result, url)
            
            logging.info(f"Scan completed for {url}: Threat score = {analysis.get('threat_score', 0)}%")
            return analysis
            
        except Exception as e:
            logging.error(f"Error scanning URL {url}: {e}")
            return None
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL has valid format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _submit_url_for_scanning(self, url: str) -> Optional[str]:
        """
        Submit URL to urlscan.io for scanning.
        
        Returns scan ID if successful, None otherwise.
        """
        try:
            payload = {
                "url": url,
                "visibility": "public"
            }
            
            response = requests.post(
                f"{self.scan_url}/",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('uuid')
            else:
                logging.error(f"Failed to submit URL: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error submitting URL: {e}")
            return None
        except Exception as e:
            logging.error(f"Error submitting URL: {e}")
            return None
    
    def _wait_for_scan_completion(self, scan_id: str, max_wait: int = 60) -> Optional[Dict]:
        """
        Wait for scan to complete and retrieve results.
        
        Polls the API until scan is complete or timeout reached.
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Get scan results
                response = requests.get(
                    f"{self.base_url}/result/{scan_id}/",
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if scan is complete
                    if result.get('status') == 200:
                        logging.info(f"Scan completed: {scan_id}")
                        return result
                    elif result.get('status') == 404:
                        logging.info(f"Scan still in progress: {scan_id}")
                    else:
                        logging.warning(f"Unexpected scan status: {result.get('status')}")
                
                # Wait before next check
                time.sleep(5)
                
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request error checking scan status: {e}")
                time.sleep(5)
            except Exception as e:
                logging.warning(f"Error checking scan status: {e}")
                time.sleep(5)
        
        logging.error(f"Scan timeout after {max_wait} seconds: {scan_id}")
        return None
    
    def _analyze_scan_results(self, scan_result: Dict, original_url: str) -> Dict:
        """
        Analyze scan results and extract threat information.
        
        Processes raw scan data to calculate threat scores and identify risks.
        """
        analysis = {
            'url': original_url,
            'scan_id': scan_result.get('uuid'),
            'scan_time': scan_result.get('time'),
            'threat_score': 0,
            'malicious': False,
            'categories': [],
            'indicators': [],
            'summary': 'No threats detected'
        }
        
        try:
            # Extract page data
            page_data = scan_result.get('page', {})
            stats_data = scan_result.get('stats', {})
            lists_data = scan_result.get('lists', {})
            
            # Calculate threat score based on various indicators
            threat_indicators = []
            
            # Check for malicious indicators
            if lists_data.get('ips'):
                analysis['indicators'].append(f"IPs in blacklists: {len(lists_data['ips'])}")
                threat_indicators.append(len(lists_data['ips']) * 10)
            
            if lists_data.get('countries'):
                analysis['indicators'].append(f"Countries in blacklists: {len(lists_data['countries'])}")
                threat_indicators.append(len(lists_data['countries']) * 5)
            
            if lists_data.get('domains'):
                analysis['indicators'].append(f"Domains in blacklists: {len(lists_data['domains'])}")
                threat_indicators.append(len(lists_data['domains']) * 15)
            
            if lists_data.get('urls'):
                analysis['indicators'].append(f"URLs in blacklists: {len(lists_data['urls'])}")
                threat_indicators.append(len(lists_data['urls']) * 20)
            
            # Check for suspicious categories
            categories = lists_data.get('categories', [])
            if categories:
                analysis['categories'] = categories
                for category in categories:
                    if any(keyword in category.lower() for keyword in ['malware', 'phishing', 'scam', 'malicious']):
                        threat_indicators.append(30)
                    elif any(keyword in category.lower() for keyword in ['suspicious', 'suspected']):
                        threat_indicators.append(20)
                    else:
                        threat_indicators.append(10)
            
            # Check for suspicious behavior
            if stats_data.get('malicious'):
                analysis['malicious'] = True
                threat_indicators.append(50)
                analysis['indicators'].append("Malicious behavior detected")
            
            # Check for suspicious requests
            if stats_data.get('requests', 0) > 100:
                analysis['indicators'].append(f"High number of requests: {stats_data['requests']}")
                threat_indicators.append(10)
            
            # Check for suspicious domains
            if stats_data.get('domains', 0) > 20:
                analysis['indicators'].append(f"High number of domains: {stats_data['domains']}")
                threat_indicators.append(10)
            
            # Calculate final threat score
            if threat_indicators:
                total_score = sum(threat_indicators)
                analysis['threat_score'] = min(total_score, 100)  # Cap at 100%
                
                if analysis['threat_score'] > 50:
                    analysis['summary'] = f"High threat detected (Score: {analysis['threat_score']}%)"
                elif analysis['threat_score'] > 25:
                    analysis['summary'] = f"Medium threat detected (Score: {analysis['threat_score']}%)"
                else:
                    analysis['summary'] = f"Low threat detected (Score: {analysis['threat_score']}%)"
            else:
                analysis['summary'] = "No threats detected"
            
            # Add additional metadata
            analysis['page_title'] = page_data.get('title', 'Unknown')
            analysis['server'] = page_data.get('server', 'Unknown')
            analysis['ip'] = page_data.get('ip', 'Unknown')
            analysis['country'] = page_data.get('country', 'Unknown')
            
        except Exception as e:
            logging.error(f"Error analyzing scan results: {e}")
            analysis['summary'] = "Error analyzing results"
        
        return analysis
    
    def get_scan_status(self, scan_id: str) -> Optional[Dict]:
        """
        Get current status of a scan without waiting.
        
        Useful for checking scan progress or retrieving results later.
        """
        try:
            response = requests.get(
                f"{self.base_url}/result/{scan_id}/",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to get scan status: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting scan status: {e}")
            return None
    
    def search_existing_scans(self, url: str) -> Optional[Dict]:
        """
        Search for existing scan results for a URL.
        
        Checks if URL has been scanned recently to avoid duplicate scans.
        """
        try:
            # Search for existing scans
            search_url = f"{self.base_url}/search/?q=url:{url}"
            response = requests.get(search_url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                results = response.json()
                if results.get('results'):
                    # Return the most recent scan
                    return results['results'][0]
            
            return None
            
        except Exception as e:
            logging.error(f"Error searching existing scans: {e}")
            return None 