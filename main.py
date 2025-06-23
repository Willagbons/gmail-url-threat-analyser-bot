#!/usr/bin/env python3
"""
Gmail URL Scanner Bot - Main Script

Monitors Gmail for new emails, extracts URLs, and scans them for threats using urlscan.io.
Runs continuously until interrupted with Ctrl+C.

Usage: python main.py
"""

import os
import sys
import time
import logging
import re
from datetime import datetime
from typing import List, Dict, Optional

# Add current directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom modules
from config import Config
from gmail_monitor import GmailMonitor
from url_scanner import URLScanner
from alert_system import AlertSystem

def setup_logging():
    """Set up logging to both file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('url_scanner_bot.log'),
            logging.StreamHandler()
        ]
    )

def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract URLs from text using regex.
    
    Finds HTTP and HTTPS URLs with optional query parameters and fragments.
    Returns a list of unique, cleaned URLs.
    """
    if not text:
        return []
    
    # Find all URLs in the text
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    urls = re.findall(url_pattern, text)
    
    # Clean and validate URLs
    cleaned_urls = []
    for url in urls:
        url = url.strip()
        if url and len(url) > 10:  # Basic validation
            cleaned_urls.append(url)
    
    return list(set(cleaned_urls))  # Remove duplicates

def analyze_email_urls(email_data: Dict, url_scanner: URLScanner, alert_system: AlertSystem) -> Dict:
    """
    Analyze URLs found in an email for threats.
    
    Extracts URLs from subject and body, scans each one, and generates alerts
    for URLs with threat scores above 50%.
    """
    results = {
        'email_id': email_data.get('id', 'unknown'),
        'sender': email_data.get('sender', 'unknown'),
        'subject': email_data.get('subject', 'unknown'),
        'urls_found': [],
        'urls_scanned': [],
        'threats_detected': []
    }
    
    # Extract URLs from both subject and body
    subject_urls = extract_urls_from_text(email_data.get('subject', ''))
    body_urls = extract_urls_from_text(email_data.get('body', ''))
    
    all_urls = list(set(subject_urls + body_urls))  # Remove duplicates
    results['urls_found'] = all_urls
    
    if not all_urls:
        logging.info(f"No URLs found in email from {email_data.get('sender', 'unknown')}")
        return results
    
    logging.info(f"Found {len(all_urls)} URLs in email from {email_data.get('sender', 'unknown')}")
    
    # Scan each URL for threats
    for url in all_urls:
        try:
            logging.info(f"Scanning URL: {url}")
            
            scan_result = url_scanner.scan_url(url)
            results['urls_scanned'].append({
                'url': url,
                'scan_result': scan_result
            })
            
            # Check if URL is a threat (score > 50%)
            if scan_result and scan_result.get('threat_score', 0) > 50:
                threat_info = {
                    'url': url,
                    'threat_score': scan_result.get('threat_score', 0),
                    'malicious': scan_result.get('malicious', False),
                    'categories': scan_result.get('categories', []),
                    'scan_id': scan_result.get('scan_id', 'unknown')
                }
                results['threats_detected'].append(threat_info)
                
                # Generate alert for the threat
                alert_message = f"THREAT DETECTED!\n"
                alert_message += f"Email: {email_data.get('sender', 'unknown')}\n"
                alert_message += f"Subject: {email_data.get('subject', 'unknown')}\n"
                alert_message += f"URL: {url}\n"
                alert_message += f"Threat Score: {scan_result.get('threat_score', 0)}%\n"
                alert_message += f"Categories: {', '.join(scan_result.get('categories', []))}\n"
                alert_message += f"Scan ID: {scan_result.get('scan_id', 'unknown')}"
                
                alert_system.send_alert(alert_message, "HIGH")
                logging.warning(f"Threat detected in URL: {url}")
            
            # Rate limiting: be respectful to urlscan.io API
            time.sleep(1)
            
        except Exception as e:
            logging.error(f"Error scanning URL {url}: {e}")
            results['urls_scanned'].append({
                'url': url,
                'scan_result': {'error': str(e)}
            })
    
    return results

def main():
    """
    Main function that runs the URL scanning bot.
    
    Sets up components, logs into Gmail, and continuously monitors for new emails.
    Processes URLs found in emails and generates alerts for threats.
    """
    # Display bot header
    print("\n" + "="*60)
    print("URL SCANNER BOT")
    print("Extracts URLs from emails and scans them with urlscan.io")
    print("="*60)
    
    setup_logging()
    
    # Load configuration
    config = Config()
    
    # Check required settings
    if not config.GMAIL_USERNAME or not config.GMAIL_PASSWORD:
        print("Error: GMAIL_USERNAME and GMAIL_PASSWORD must be set in config.py")
        return
    
    if not config.URLSCAN_API_KEY:
        print("Warning: URLSCAN_API_KEY not set. Some scans may be limited.")
    
    # Initialize bot components
    try:
        gmail_monitor = GmailMonitor(config.GMAIL_USERNAME, config.GMAIL_PASSWORD, headless=False)
        url_scanner = URLScanner(config.URLSCAN_API_KEY)
        alert_system = AlertSystem()
        print("Components initialized successfully")
        
    except Exception as e:
        print(f"Error initializing components: {e}")
        return
    
    # Setup Chrome WebDriver
    print("\nSetting up Chrome WebDriver...")
    if not gmail_monitor.setup_driver():
        print("Failed to setup Chrome WebDriver")
        print("Make sure ChromeDriver is installed and in your PATH")
        return
    
    print("Chrome WebDriver setup successful")
    
    # Login to Gmail
    print("\nLogging into Gmail...")
    print("Browser window will open - you can watch the login process")
    print("Please wait while the browser loads...")
    
    if not gmail_monitor.login_gmail():
        print("Failed to login to Gmail")
        print("You may need to manually complete the login process in the browser window")
        return
    
    print("Successfully logged into Gmail")
    print("Browser window will remain open so you can see the email processing")
    
    # Initialize statistics
    start_time = datetime.now()
    emails_processed = 0
    urls_found = 0
    urls_scanned = 0
    threats_detected = 0
    
    # Main monitoring loop
    try:
        print("\nStarting URL scanning loop...")
        print("Press Ctrl+C to stop the bot\n")
        
        while True:
            try:
                # Get new emails (max 5 per cycle)
                emails = gmail_monitor.get_new_emails(max_emails=5)
                
                if emails:
                    print(f"\nFound {len(emails)} new emails")
                    
                    # Process each email
                    for email in emails:
                        try:
                            print(f"\nProcessing email from: {email.get('sender', 'unknown')}")
                            print(f"   Subject: {email.get('subject', 'unknown')}")
                            
                            # Analyze URLs in the email
                            results = analyze_email_urls(email, url_scanner, alert_system)
                            
                            # Update statistics
                            emails_processed += 1
                            urls_found += len(results['urls_found'])
                            urls_scanned += len(results['urls_scanned'])
                            threats_detected += len(results['threats_detected'])
                            
                            # Display results
                            if results['urls_found']:
                                print(f"   URLs found: {len(results['urls_found'])}")
                                for url in results['urls_found']:
                                    print(f"      - {url}")
                            
                            if results['threats_detected']:
                                print(f"   Threats detected: {len(results['threats_detected'])}")
                                for threat in results['threats_detected']:
                                    print(f"      - {threat['url']} (Score: {threat['threat_score']}%)")
                            
                        except Exception as e:
                            logging.error(f"Error processing email: {e}")
                            continue
                else:
                    print("No new emails found")
                
                # Display current statistics
                runtime = datetime.now() - start_time
                print(f"\nSTATISTICS:")
                print(f"   Runtime: {runtime}")
                print(f"   Emails Processed: {emails_processed}")
                print(f"   URLs Found: {urls_found}")
                print(f"   URLs Scanned: {urls_scanned}")
                print(f"   Threats Detected: {threats_detected}")
                print("-" * 40)
                
                # Wait before next check (30 seconds)
                print("Waiting 30 seconds before next check...")
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n\nBot stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                print(f"Error: {e}")
                time.sleep(10)
                continue
    
    finally:
        # Cleanup
        print("\nCleaning up...")
        gmail_monitor.close()
        
        # Display final statistics
        runtime = datetime.now() - start_time
        print(f"\nFINAL STATISTICS:")
        print(f"   Total Runtime: {runtime}")
        print(f"   Emails Processed: {emails_processed}")
        print(f"   URLs Found: {urls_found}")
        print(f"   URLs Scanned: {urls_scanned}")
        print(f"   Threats Detected: {threats_detected}")
        print("\nBot finished")

if __name__ == "__main__":
    main() 