# Gmail URL Scanner Bot

A Python security tool that automatically monitors your Gmail inbox, extracts URLs from emails, and scans them for potential threats using urlscan.io.

## Overview

This bot provides automated email security by:
- 🔍 Logging into Gmail and extracting URLs from recent emails
- 🛡️ Scanning each URL with urlscan.io for malware, phishing, and other threats
- 📊 Generating comprehensive security reports with risk scores
- ⚡ Handling Gmail's dynamic interface with robust automation

## Requirements

- Python 3.7+
- Chrome browser
- Gmail account (2FA disabled or app password configured)
- urlscan.io API key (optional, recommended for better limits)

## Quick Start

### 1. Install Dependencies
```bash
pip install selenium requests webdriver-manager
```

### 2. Configure Credentials
Edit `config.py`:
```python
class Config:
    GMAIL_USERNAME = "your-email@gmail.com"
    GMAIL_PASSWORD = "your-password-or-app-password"
    URLSCAN_API_KEY = "your-api-key-here" 
```

### 3. Run the Bot
```bash
python main.py
```

## Example Output

```
============================================================
GMAIL URL SCANNER BOT
============================================================

📧 Logging into Gmail...
✅ Found 20 emails to process.

============================================================
URL EXTRACTION RESULTS
============================================================

📧 Email 1: Newsletter from TechCrunch
   🔗 https://techcrunch.com/2024/01/15/ai-startup-funding
   🔗 https://techcrunch.com/newsletter-signup

📧 Email 2: Security Alert from Bank
   🔗 https://secure.bank.com/verify-account
   🔗 https://support.bank.com/security

📊 SUMMARY:
   • Total emails processed: 20
   • Total unique URLs found: 6

============================================================
URL SCANNING RESULTS
============================================================

🔍 Scanning URL 1/6: https://techcrunch.com/2024/01/15/ai-startup-funding
✅ SAFE (Score: 0)
   Categories: []

🔍 Scanning URL 2/6: https://example-store.com/sale
🚨 MALICIOUS DETECTED (Score: 85)
   Categories: phishing, malware

============================================================
FINAL SUMMARY
============================================================
📊 SCAN RESULTS:
   ✅ Successfully scanned: 2
   🚨 Malicious URLs found: 1

✅ Bot finished successfully!
```

## Troubleshooting

### Common Issues

**Login Failures**
- Verify credentials in `config.py`
- Use app password if 2FA is enabled
- Ensure account is not locked

**Click Interception Errors**
- Bot handles this automatically
- Try headless mode if persistent: `headless=True`

**Scan Timeouts**
- Increase timeout in `url_scanner.py`
- Check urlscan.io service status
- Some URLs may be slow to respond

**No Emails Found**
- Verify inbox has recent emails
- Run diagnostic: `python debug_email_count.py`

## Configuration

### Modify Email Count
```python
# In main.py
emails = gmail_monitor.get_new_emails(max_emails=50)  # Default: 20
```

### Adjust Scan Timeout
```python
# In url_scanner.py
TIMEOUT_SECONDS = 120  # Default: 90 seconds
```

### Test Login
```bash
python test_login.py
```

## How It Works

1. **Gmail Integration**: Uses Selenium to automate Chrome, log into Gmail, and extract email content
2. **URL Extraction**: Parses email bodies using regex to find all HTTP/HTTPS URLs
3. **Threat Scanning**: Submits URLs to urlscan.io for security analysis
4. **Reporting**: Provides formatted results with security scores and threat categories

## Security Considerations

- Store credentials securely (never in version control)
- Use environment variables for production
- Respect urlscan.io rate limits
- Only scan URLs you own or trust
- Review logs for sensitive information

## API Details

### urlscan.io Integration
- Free tier: 100 scans/day, 3-minute timeout
- API key: Higher limits, faster response
- Rate limiting: Automatic handling
- Error handling: Comprehensive categorization


## License

This project is for educational and security research purposes. Use responsibly and in accordance with applicable laws and terms of service.

---

**Disclaimer**: This tool is for educational purposes. Always respect privacy, terms of service, and applicable laws when scanning URLs or accessing email accounts. 