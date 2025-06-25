import os
import sys
import time
import re
from config import Config
from gmail_monitor import GmailMonitor
from url_scanner import SimpleURLScanner

def extract_urls_from_text(text: str):
    if not text:
        return []
    url_pattern = r'https?://[\w\-\.]+(?:[:\d]+)?(?:/[\w/_.-]*)?(?:\?[\w&=%.]*)?(?:#[\w\.-]*)?'
    return list(set(re.findall(url_pattern, text)))

def main():
    print("=" * 60)
    print("GMAIL URL SCANNER BOT")
    print("=" * 60)
    
    config = Config()
    if not config.GMAIL_USERNAME or not config.GMAIL_PASSWORD:
        print("❌ Error: GMAIL_USERNAME and GMAIL_PASSWORD must be set in config.py")
        return
    if not config.URLSCAN_API_KEY:
        print("⚠️  Warning: URLSCAN_API_KEY not set. Some scans may be limited.")
    
    print("\n🔧 Setting up components...")
    gmail_monitor = GmailMonitor(config.GMAIL_USERNAME, config.GMAIL_PASSWORD, headless=False)
    url_scanner = SimpleURLScanner(config.URLSCAN_API_KEY)
    
    print("🌐 Setting up Chrome WebDriver...")
    if not gmail_monitor.setup_driver():
        print("❌ Failed to setup Chrome WebDriver")
        return
    
    print("📧 Logging into Gmail...")
    if not gmail_monitor.login_gmail():
        print("❌ Failed to login to Gmail")
        return
    
    print("\n📥 Extracting emails...")
    emails = gmail_monitor.get_new_emails(max_emails=20)
    print(f"✅ Found {len(emails)} emails to process.")
    
    if not emails:
        print("ℹ️  No emails found to process.")
        gmail_monitor.close()
        return
    
    print("\n" + "=" * 60)
    print("URL EXTRACTION RESULTS")
    print("=" * 60)
    
    all_urls = set()
    email_urls = {}
    
    for i, email in enumerate(emails, 1):
        body = email.get('body', '')
        subject = email.get('subject', '[No Subject]')
        urls = extract_urls_from_text(body)
        
        if urls:
            print(f"\n📧 Email {i}: {subject}")
            for url in urls:
                print(f"   🔗 {url}")
                all_urls.add(url)
                if subject not in email_urls:
                    email_urls[subject] = []
                email_urls[subject].append(url)
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Total emails processed: {len(emails)}")
    print(f"   • Total unique URLs found: {len(all_urls)}")
    
    if not all_urls:
        print("\nℹ️  No URLs found in any emails.")
        gmail_monitor.close()
        return
    
    print("\n" + "=" * 60)
    print("URL SCANNING RESULTS")
    print("=" * 60)
    
    scan_results = {
        'completed': [],
        'failed': [],
        'blocked': [],
        'timeout': []
    }
    
    for i, url in enumerate(all_urls, 1):
        print(f"\n🔍 Scanning URL {i}/{len(all_urls)}: {url}")
        print("-" * 50)
        
        result = url_scanner.scan_url(url)
        
        if 'error' in result:
            error_msg = result['error']
            if 'DNS Error' in str(error_msg):
                print("❌ CANNOT SCAN: Domain does not exist")
                scan_results['failed'].append(url)
            elif 'Scan prevented' in str(error_msg):
                print("🚫 CANNOT SCAN: URL blocked by urlscan.io")
                scan_results['blocked'].append(url)
            elif 'timeout' in str(error_msg):
                print("⏰ TIMEOUT: Scan took too long to complete")
                scan_results['timeout'].append(url)
            else:
                print(f"❌ ERROR: {error_msg}")
                scan_results['failed'].append(url)
        elif 'verdicts' in result:
            verdicts = result.get('verdicts', {})
            overall = verdicts.get('overall', {})
            score = overall.get('score', 0)
            malicious = overall.get('malicious', False)
            categories = overall.get('categories', [])
            
            if malicious:
                print(f"🚨 MALICIOUS DETECTED (Score: {score})")
                print(f"   Categories: {', '.join(categories) if categories else 'None'}")
            else:
                print(f"✅ SAFE (Score: {score})")
                if categories:
                    print(f"   Categories: {', '.join(categories)}")
            
            scan_results['completed'].append({
                'url': url,
                'malicious': malicious,
                'score': score,
                'categories': categories
            })
        else:
            print("❓ UNKNOWN RESULT FORMAT")
            scan_results['failed'].append(url)
    
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    print(f"📊 SCAN RESULTS:")
    print(f"   ✅ Successfully scanned: {len(scan_results['completed'])}")
    print(f"   ❌ Failed to scan: {len(scan_results['failed'])}")
    print(f"   🚫 Blocked by urlscan.io: {len(scan_results['blocked'])}")
    print(f"   ⏰ Timed out: {len(scan_results['timeout'])}")
    
    if scan_results['completed']:
        malicious_count = sum(1 for r in scan_results['completed'] if r['malicious'])
        print(f"\n🚨 SECURITY ALERTS:")
        print(f"   • Malicious URLs found: {malicious_count}")
        
        if malicious_count > 0:
            print("\n   Malicious URLs:")
            for result in scan_results['completed']:
                if result['malicious']:
                    print(f"      • {result['url']} (Score: {result['score']})")
    
    gmail_monitor.close()
    print("\n✅ Bot finished successfully!")

if __name__ == "__main__":
    main() 