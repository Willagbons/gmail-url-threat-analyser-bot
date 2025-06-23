# Gmail URL Scanner Bot

A Python-based bot that monitors Gmail for new emails, extracts URLs, and scans them for threats using urlscan.io. The bot provides real-time threat detection and alerting for suspicious URLs found in emails.

## Features

The bot integrates with Gmail through Selenium WebDriver for reliable email monitoring. It uses regex patterns to extract URLs from email content and submits them to urlscan.io's scanning service. The threat analysis includes blacklist checking, malicious behavior detection, and suspicious category identification. All activities are logged for monitoring and debugging purposes.

## Requirements

You'll need Python 3.7 or higher, Chrome browser installed, and a Gmail account with app password enabled. An urlscan.io API key is optional but recommended for higher rate limits.


## Prerequisites

- Python 3.7 or higher
- Chrome browser installed
- ChromeDriver (will be downloaded automatically)
- Gmail account with app password enabled
- urlscan.io API key

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/gmail-url-scanner-bot.git
   cd gmail-url-scanner-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Gmail App Password**
   - Go to your Google Account settings
   - Enable 2-factor authentication
   - Generate an app password for this bot
   - Use the app password (not your regular password)

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   GMAIL_USERNAME=your-email@gmail.com
   GMAIL_PASSWORD=your-app-password
   URLSCAN_API_KEY=your-urlscan-api-key
   ```

## Usage

### Basic Usage

Run the bot to start monitoring Gmail:

```bash
python main.py
```

The bot will:
1. Open Chrome browser (visible mode)
2. Log into Gmail automatically
3. Monitor for new emails every 30 seconds
4. Extract and scan URLs found in emails
5. Generate alerts for threats detected

### Configuration Options

You can customize the bot behavior by modifying the `.env` file:

```env
# Bot behavior
CHECK_INTERVAL=60                    # Seconds between email checks
MAX_EMAILS_PER_CHECK=10             # Max emails to process per cycle

# Chrome settings
CHROME_HEADLESS=false               # Set to true for headless mode
CHROME_WINDOW_SIZE=1920,1080        # Browser window size

# Logging
LOG_LEVEL=INFO                      # Logging verbosity
LOG_FILE=threat_analyzer.log        # Log file path

# Alerts
ALERT_FILE=security_alerts.log      # Alert log file
ENABLE_EMAIL_ALERTS=false           # Email notifications
```

## Project Structure

```
threat-analyzer-bot/
├── main.py              # Main bot script
├── config.py            # Configuration management
├── gmail_monitor.py     # Gmail automation and email extraction
├── url_scanner.py       # URL scanning with urlscan.io
├── alert_system.py      # Alert generation and logging
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## How It Works

1. **Gmail Monitoring**: Uses Selenium WebDriver to automate Chrome browser interactions with Gmail
2. **Email Processing**: Extracts email content including sender, subject, and body
3. **URL Extraction**: Uses regex patterns to find URLs in email content
4. **Threat Scanning**: Submits URLs to urlscan.io for comprehensive security analysis
5. **Alert Generation**: Creates alerts for URLs with threat scores above 50%
6. **Logging**: Records all activities and scan results for monitoring

## Threat Scoring

The bot calculates threat scores based on multiple factors:
- **Blacklisted IPs/Domains**: URLs associated with known malicious entities
- **Suspicious Categories**: Phishing, malware, scam indicators
- **Malicious Behavior**: Detected malicious activities during scanning
- **High Request Counts**: Unusual number of external requests
- **Suspicious Domains**: Domains with suspicious characteristics

## Security Considerations

- **App Passwords**: Always use Gmail app passwords, never regular passwords
- **API Keys**: Store API keys securely in environment variables
- **Log Files**: Review log files regularly for security insights
- **Browser Security**: The bot runs in a controlled browser environment

## Troubleshooting

### Common Issues

1. **Login Failures**
   - Ensure you're using an app password, not your regular password
   - Check that 2-factor authentication is enabled
   - Verify Gmail credentials in the `.env` file

2. **ChromeDriver Issues**
   - The bot will attempt to download ChromeDriver automatically
   - Ensure Chrome browser is installed and up to date
   - Check internet connection for driver download

3. **URL Scanning Failures**
   - Verify urlscan.io API key if using private API
   - Check internet connection for API access
   - Review rate limiting if scanning many URLs

4. **No Emails Found**
   - Ensure Gmail inbox has emails to process
   - Check that the bot is properly logged into Gmail
   - Verify email selectors are working with current Gmail interface

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file:

```env
LOG_LEVEL=DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## Disclaimer

This tool is for educational and security research purposes. Always ensure you have permission to scan URLs and comply with relevant laws and terms of service. The authors are not responsible for any misuse of this software.

## Support

If you encounter issues or have questions:
1. Check the troubleshooting section above
2. Review the log files for error details
3. Open an issue on GitHub with detailed information
4. Include relevant log excerpts and error messages

## Acknowledgments

- [urlscan.io](https://urlscan.io) for providing the URL scanning API
- [Selenium](https://selenium.dev/) for browser automation capabilities
- The open-source community for various Python libraries used in this project 