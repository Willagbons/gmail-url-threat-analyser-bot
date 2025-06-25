import os
import sys
import time
from config import Config
from gmail_monitor import GmailMonitor

def main():
    print("=" * 60)
    print("EMAIL COUNT DIAGNOSTIC")
    print("=" * 60)
    
    config = Config()
    if not config.GMAIL_USERNAME or not config.GMAIL_PASSWORD:
        print("❌ Error: GMAIL_USERNAME and GMAIL_PASSWORD must be set in config.py")
        return
    
    print("\n🔧 Setting up Gmail monitor...")
    gmail_monitor = GmailMonitor(config.GMAIL_USERNAME, config.GMAIL_PASSWORD, headless=False)
    
    print("🌐 Setting up Chrome WebDriver...")
    if not gmail_monitor.setup_driver():
        print("❌ Failed to setup Chrome WebDriver")
        return
    
    print("📧 Logging into Gmail...")
    if not gmail_monitor.login_gmail():
        print("❌ Failed to login to Gmail")
        return
    
    print("\n📊 ANALYZING EMAIL EXTRACTION...")
    
    # Check how many email rows are actually visible
    try:
        if "mail.google.com/mail/u/0/#inbox" not in gmail_monitor.driver.current_url:
            gmail_monitor.driver.get("https://mail.google.com/mail/u/0/#inbox")
            time.sleep(3)

        email_row_selectors = [
            "tr[role='row']",
            "div[role='row']",
            "div[data-testid='message-row']",
            "div[class*='message-row']",
            "tr[class*='message']"
        ]

        total_rows = 0
        working_selector = None
        
        for selector in email_row_selectors:
            try:
                WebDriverWait(gmail_monitor.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                rows = gmail_monitor.driver.find_elements(By.CSS_SELECTOR, selector)
                if rows:
                    total_rows = len(rows)
                    working_selector = selector
                    print(f"✅ Found {total_rows} email rows using selector: {selector}")
                    break
            except:
                continue

        if not total_rows:
            print("❌ No email rows found with any selector")
            return

        print(f"\n📈 DETAILED ANALYSIS:")
        print(f"   • Total email rows visible: {total_rows}")
        print(f"   • Working selector: {working_selector}")
        
        # Test processing first 20 emails
        print(f"\n🔍 Testing processing of first 20 emails...")
        
        processed_count = 0
        failed_count = 0
        no_body_count = 0
        
        for i, row in enumerate(rows[:20], 1):
            try:
                print(f"\n   Email {i}:")
                
                # Get email ID
                email_id = gmail_monitor._get_email_id(row)
                print(f"      ID: {email_id}")
                
                if not email_id:
                    print(f"      ❌ No email ID found")
                    failed_count += 1
                    continue
                
                if email_id in gmail_monitor.processed_emails:
                    print(f"      ⏭️  Already processed")
                    continue
                
                # Try to extract email data
                email_data = gmail_monitor._extract_email_data(row)
                
                if not email_data:
                    print(f"      ❌ Failed to extract email data")
                    failed_count += 1
                    continue
                
                if not email_data.get('body'):
                    print(f"      ⚠️  No body content")
                    no_body_count += 1
                    continue
                
                print(f"      ✅ Successfully processed")
                print(f"      Sender: {email_data.get('sender', 'Unknown')}")
                print(f"      Subject: {email_data.get('subject', 'No Subject')}")
                print(f"      Body length: {len(email_data.get('body', ''))} chars")
                
                processed_count += 1
                gmail_monitor.processed_emails.add(email_id)
                
            except Exception as e:
                print(f"      ❌ Error: {str(e)[:100]}...")
                failed_count += 1
        
        print(f"\n📊 RESULTS:")
        print(f"   ✅ Successfully processed: {processed_count}")
        print(f"   ❌ Failed to process: {failed_count}")
        print(f"   ⚠️  No body content: {no_body_count}")
        print(f"   📧 Total attempted: {min(20, total_rows)}")
        
        if processed_count < 20:
            print(f"\n💡 REASONS FOR LIMITED PROCESSING:")
            if failed_count > 0:
                print(f"   • {failed_count} emails failed due to click interception or extraction errors")
            if no_body_count > 0:
                print(f"   • {no_body_count} emails had no extractable body content")
            if total_rows < 20:
                print(f"   • Only {total_rows} email rows are visible in the inbox")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    
    gmail_monitor.close()
    print("\n✅ Diagnostic completed!")

if __name__ == "__main__":
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    main() 