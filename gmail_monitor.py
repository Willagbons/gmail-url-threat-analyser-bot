"""
Gmail Monitor Module for URL Scanner Bot

Handles Gmail authentication, email retrieval, and content extraction using Selenium.
Provides browser automation for Gmail with robust error handling and fallback mechanisms.
"""

import time
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class GmailMonitor:
    """
    Gmail monitoring and email extraction class.
    
    Uses Selenium WebDriver to automate Chrome browser interactions with Gmail.
    Handles login, email retrieval, and content extraction with robust error handling.
    """
    
    def __init__(self, username: str, password: str, headless: bool = True):
        """Initialize the Gmail monitor with credentials."""
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None
        self.processed_emails = set()
        self.wait_timeout = 20  # Increased timeout for reliability
        
    def setup_driver(self) -> bool:
        """
        Setup Chrome WebDriver with appropriate options.
        
        Configures Chrome for Gmail automation with stealth settings and proper window sizing.
        """
        try:
            chrome_options = Options()
            
            # Configure headless mode if requested
            if self.headless:
                chrome_options.add_argument("--headless")
            else:
                # For visible mode, ensure window is properly sized and positioned
                chrome_options.add_argument("--window-size=1200,800")
                chrome_options.add_argument("--window-position=100,100")
                chrome_options.add_argument("--start-maximized")
            
            # Standard Chrome options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Add user agent to look more like a real browser
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Create WebDriver instance
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # For visible mode, ensure window is front and center
            if not self.headless:
                self.driver.maximize_window()
                time.sleep(2)  # Give time for window to maximize
            
            logging.info("Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    def login_gmail(self) -> bool:
        """
        Login to Gmail using Selenium.
        
        Handles the complete login process with multiple selector fallbacks
        and detailed feedback during the process.
        """
        try:
            logging.info("Attempting to login to Gmail...")
            print("Opening Gmail login page...")
            self.driver.get("https://mail.google.com")
            
            # Wait for page to load
            print("Loading login page...")
            time.sleep(5)
            
            # Try multiple selectors for email input
            email_selectors = [
                "input[name='identifier']",
                "input[type='email']",
                "input[data-testid='identifier']",
                "#identifierId",
                "input[aria-label*='Email']",
                "input[placeholder*='email']"
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if email_input:
                        logging.info(f"Found email input with selector: {selector}")
                        print("Found email input field")
                        break
                except:
                    continue
            
            if not email_input:
                logging.error("Could not find email input field")
                print("Could not find email input field")
                return False
            
            # Enter email address
            print(f"Entering email: {self.username}")
            email_input.clear()
            email_input.send_keys(self.username)
            time.sleep(2)
            
            # Submit email
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], #identifierNext, button[jsname='LgbsSe']")
                print("Clicking Next button...")
                next_button.click()
            except:
                print("Submitting email...")
                email_input.submit()
            
            time.sleep(5)
            
            # Look for password input field
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[data-testid='password']",
                "input[aria-label*='Password']",
                "input[placeholder*='password']"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if password_input:
                        logging.info(f"Found password input with selector: {selector}")
                        print("Found password input field")
                        break
                except:
                    continue
            
            if not password_input:
                logging.error("Could not find password input field")
                print("Could not find password input field")
                print("You may need to manually complete the login process")
                return False
            
            # Enter password
            print("Entering password...")
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(2)
            
            # Submit password
            try:
                password_next = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], #passwordNext, button[jsname='LgbsSe']")
                print("Clicking Next button...")
                password_next.click()
            except:
                print("Submitting password...")
                password_input.submit()
            
            # Wait for Gmail to load
            print("Loading Gmail...")
            time.sleep(8)
            
            # Check if login was successful
            gmail_indicators = [
                "div[role='main']",
                "div[data-testid='inbox']",
                "div[aria-label*='Inbox']",
                "div[data-tooltip*='Inbox']"
            ]
            
            for indicator in gmail_indicators:
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                    )
                    logging.info("Successfully logged into Gmail")
                    print("Successfully logged into Gmail!")
                    return True
                except:
                    continue
            
            # Check for security challenges
            if "accounts.google.com" in self.driver.current_url:
                logging.warning("Still on Google accounts page - may need manual intervention")
                print("Still on Google accounts page - you may need to manually complete the login")
                print("Check for security challenges, 2FA prompts, or other verification steps")
                return False
            
            logging.info("Successfully logged into Gmail")
            print("Successfully logged into Gmail!")
            return True
            
        except TimeoutException as e:
            logging.error(f"Timeout during Gmail login: {e}")
            print(f"Timeout during login: {e}")
            return False
        except Exception as e:
            logging.error(f"Error during Gmail login: {e}")
            print(f"Error during login: {e}")
            return False
    
    def get_new_emails(self, max_emails: int = 10) -> list:
        """
        Get new emails from Gmail inbox.
        Retrieves emails and extracts their content using multiple selector strategies
        to handle Gmail's dynamic interface.
        """
        try:
            if "mail.google.com/mail/u/0/#inbox" not in self.driver.current_url:
                self.driver.get("https://mail.google.com/mail/u/0/#inbox")
                time.sleep(3)

            email_row_selectors = [
                "tr[role='row']",
                "div[role='row']",
                "div[data-testid='message-row']",
                "div[class*='message-row']",
                "tr[class*='message']"
            ]

            email_rows = []
            for selector in email_row_selectors:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    email_rows = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if email_rows:
                        break
                except:
                    continue

            if not email_rows:
                return []

            new_emails = []
            for row in email_rows[:max_emails]:
                try:
                    email_id = self._get_email_id(row)
                    if email_id and email_id not in self.processed_emails:
                        email_data = self._extract_email_data(row)
                        if email_data and email_data.get('body'):
                            email_data['id'] = email_id
                            new_emails.append(email_data)
                            self.processed_emails.add(email_id)
                except Exception as e:
                    continue
            return new_emails
        except Exception as e:
            return []
    
    def _get_email_id(self, row) -> Optional[str]:
        """Extract email ID from row element to prevent duplicate processing."""
        try:
            # Try multiple methods to get email ID
            email_id = (
                row.get_attribute("id") or
                row.get_attribute("data-legacy-thread-id") or
                row.get_attribute("data-thread-id")
            )
            
            # Clean up the ID if it has a prefix
            if email_id and email_id.startswith('thread-'):
                email_id = email_id.replace('thread-', '')
            
            return email_id
            
        except Exception:
            return None
    
    def _extract_email_data(self, row) -> Optional[Dict]:
        """
        Extract email data from row element.
        
        Gets sender, subject, timestamp, and body content using multiple selector strategies.
        """
        try:
            # Get sender - try multiple selectors
            sender = ""
            sender_selectors = [
                "td[data-tooltip]",
                "td[title]",
                "td[aria-label*='@']",
                "td span[email]",
                "td[class*='sender']",
                "td[class*='from']",
                "td[role='gridcell'] span[email]",
                "td[role='gridcell'] span[title*='@']",
                "td[role='gridcell'] span[aria-label*='@']",
                "td span[title*='@']",
                "td span[aria-label*='@']"
            ]
            
            for selector in sender_selectors:
                try:
                    sender_element = row.find_element(By.CSS_SELECTOR, selector)
                    sender = sender_element.get_attribute("data-tooltip") or sender_element.get_attribute("title") or sender_element.get_attribute("aria-label") or sender_element.text
                    if sender and '@' in sender and sender != "Select":
                        break
                except:
                    continue
            
            # Get subject - try multiple selectors
            subject = ""
            subject_selectors = [
                "td[data-thread-id] span",
                "td[class*='subject'] span",
                "td span[class*='subject']",
                "td[aria-label*='Subject']",
                "td span[dir='ltr']",
                "td[class*='message'] span"
            ]
            
            for selector in subject_selectors:
                try:
                    subject_element = row.find_element(By.CSS_SELECTOR, selector)
                    subject = subject_element.text
                    if subject and len(subject) > 0:
                        break
                except:
                    continue
            
            # Get timestamp if available
            timestamp = ""
            timestamp_selectors = [
                "td[data-tooltip] span",
                "td[class*='date']",
                "td[aria-label*='Date']",
                "td span[class*='date']"
            ]
            
            for selector in timestamp_selectors:
                try:
                    time_element = row.find_element(By.CSS_SELECTOR, selector)
                    timestamp = time_element.text
                    if timestamp and len(timestamp) > 0:
                        break
                except:
                    pass
            
            # Try to click email row with multiple strategies to handle interception
            click_success = False
            click_strategies = [
                # Strategy 1: Try to dismiss overlays first, then click
                lambda: self._click_with_overlay_dismissal(row),
                # Strategy 2: Use JavaScript click
                lambda: self._click_with_javascript(row),
                # Strategy 3: Try to scroll to element and click
                lambda: self._click_with_scroll(row),
                # Strategy 4: Try to click on a specific part of the row
                lambda: self._click_on_row_part(row),
                # Strategy 5: Last resort - try direct click
                lambda: row.click()
            ]
            
            for i, strategy in enumerate(click_strategies):
                try:
                    strategy()
                    time.sleep(2)
                    # Check if we successfully opened an email (look for email body)
                    body_selectors = [
                        "div[role='main'] div[dir='ltr']",
                        "div[role='main'] div[data-message-id]",
                        "div[role='main'] div[class*='message']",
                        "div[data-testid='message-content']"
                    ]
                    
                    for body_selector in body_selectors:
                        try:
                            body_elements = self.driver.find_elements(By.CSS_SELECTOR, body_selector)
                            if any(len(el.text) > 20 for el in body_elements):
                                click_success = True
                                break
                        except:
                            continue
                    
                    if click_success:
                        break
                        
                except Exception as e:
                    logging.warning(f"Click strategy {i+1} failed: {e}")
                    continue
            
            if not click_success:
                logging.warning("All click strategies failed for email row")
                return None
            
            # Get email body content
            body = self._get_email_body()
            
            # Go back to inbox
            self._return_to_inbox()
            
            return {
                'sender': sender.strip(),
                'subject': subject.strip(),
                'timestamp': timestamp.strip(),
                'body': body
            }
            
        except Exception as e:
            logging.warning(f"Error extracting email data: {e}")
            return None
    
    def _click_with_overlay_dismissal(self, row):
        """Try to dismiss overlays before clicking."""
        try:
            # Try to dismiss notification prompts
            overlay_selectors = [
                "span[id='link_enable_notifications_hide']",
                "div[class='vh']",
                "div[tabindex='0'][role='button'][class='bBe']",
                "div[aria-label*='Close']",
                "button[aria-label*='Close']",
                "span[class='a8k']"
            ]
            
            for selector in overlay_selectors:
                try:
                    overlay = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if overlay.is_displayed():
                        overlay.click()
                        time.sleep(1)
                except:
                    continue
            
            # Now try to click the row
            row.click()
            
        except Exception as e:
            raise e
    
    def _click_with_javascript(self, row):
        """Use JavaScript to click the element."""
        try:
            self.driver.execute_script("arguments[0].click();", row)
        except Exception as e:
            raise e
    
    def _click_with_scroll(self, row):
        """Scroll to element and then click."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", row)
            time.sleep(1)
            row.click()
        except Exception as e:
            raise e
    
    def _click_on_row_part(self, row):
        """Try to click on a specific part of the row that might be clickable."""
        try:
            # Try to find clickable elements within the row
            clickable_selectors = [
                "td[role='gridcell']",
                "td[class*='subject']",
                "td[class*='sender']",
                "span[dir='ltr']"
            ]
            
            for selector in clickable_selectors:
                try:
                    element = row.find_element(By.CSS_SELECTOR, selector)
                    element.click()
                    return
                except:
                    continue
            
            # If no specific element found, try the row itself
            row.click()
            
        except Exception as e:
            raise e
    
    def _get_email_body(self) -> str:
        """Extract email body content using multiple selector strategies."""
        try:
            # Try multiple selectors for email body
            body_selectors = [
                "div[role='main'] div[dir='ltr']",
                "div[role='main'] div[data-message-id]",
                "div[role='main'] div[class*='message']",
                "div[role='main'] div[class*='body']",
                "div[role='main'] div[class*='content']",
                "div[data-testid='message-content']",
                "div[class*='message-body']",
                "div[class*='email-content']",
                "div[aria-label*='Message body']",
                "div[class*='text']"
            ]
            
            for selector in body_selectors:
                try:
                    body_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in body_elements:
                        body_text = element.text
                        if body_text and len(body_text) > 20:  # Minimum meaningful content
                            return body_text
                except:
                    continue
            
            # Fallback: get all text from main area
            try:
                main_area = self.driver.find_element(By.CSS_SELECTOR, "div[role='main']")
                return main_area.text
            except:
                return ""
                
        except Exception as e:
            logging.warning(f"Error getting email body: {e}")
            return ""
    
    def _return_to_inbox(self):
        """Navigate back to inbox after viewing an email."""
        try:
            self.driver.get("https://mail.google.com/mail/u/0/#inbox")
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Error returning to inbox: {e}")
    
    def mark_email_as_read(self, email_id: str) -> bool:
        """Mark an email as read (placeholder for future functionality)."""
        # TODO: Implement email marking functionality
        return True
    
    def refresh_inbox(self):
        """Refresh the Gmail inbox to get latest emails."""
        try:
            self.driver.refresh()
            time.sleep(3)
        except Exception as e:
            logging.warning(f"Error refreshing inbox: {e}")
    
    def is_logged_in(self) -> bool:
        """Check if currently logged into Gmail."""
        try:
            return "mail.google.com" in self.driver.current_url
        except:
            return False
    
    def logout(self):
        """Logout from Gmail (placeholder for future functionality)."""
        # TODO: Implement logout functionality
        pass
    
    def close(self):
        """Close the browser and cleanup resources."""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("WebDriver closed successfully")
        except Exception as e:
            logging.error(f"Error closing WebDriver: {e}")
    
    def __enter__(self):
        """Context manager entry point."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point - ensures cleanup."""
        self.close() 