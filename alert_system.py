"""
Alert System for URL Scanner Bot

Handles security alerts and notifications for detected threats.
Provides logging, file output, and optional email notifications.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class AlertSystem:
    """
    Security alert system for threat notifications.
    
    Logs alerts to files and console, with optional email notifications.
    Provides different alert levels and formatting for security events.
    """
    
    def __init__(self, alert_file: str = "security_alerts.log", enable_email_alerts: bool = False):
        """Initialize alert system with log file path."""
        self.alert_file = alert_file
        self.enable_email_alerts = enable_email_alerts
        self.alert_history = []
        self.setup_alert_logging()
        
    def setup_alert_logging(self):
        """Configure logging specifically for security alerts."""
        # Create alert logger
        self.alert_logger = logging.getLogger('security_alerts')
        self.alert_logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.alert_logger.handlers:
            # File handler for alerts
            file_handler = logging.FileHandler(self.alert_file)
            file_handler.setLevel(logging.INFO)
            
            # Console handler for immediate visibility
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Format for alerts
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.alert_logger.addHandler(file_handler)
            self.alert_logger.addHandler(console_handler)
    
    def create_alert(self, email_data: Dict, email_analysis: Dict, url_scans: List[Dict]) -> Dict:
        """Create a comprehensive security alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'alert_id': f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'email_data': {
                'sender': email_data.get('sender', 'Unknown'),
                'subject': email_data.get('subject', 'No Subject'),
                'timestamp': email_data.get('timestamp', ''),
                'body_preview': email_data.get('body', '')[:200] + '...' if len(email_data.get('body', '')) > 200 else email_data.get('body', '')
            },
            'email_analysis': email_analysis,
            'url_scans': url_scans,
            'overall_risk': self._calculate_overall_risk(email_analysis, url_scans),
            'alert_level': self._determine_alert_level(email_analysis, url_scans)
        }
        
        return alert
    
    def _calculate_overall_risk(self, email_analysis: Dict, url_scans: List[Dict]) -> str:
        """Calculate overall risk level"""
        email_score = email_analysis.get('overall_score', 0)
        url_score = sum(scan.get('risk_score', 0) for scan in url_scans)
        total_score = email_score + url_score
        
        if total_score >= 25:
            return 'CRITICAL'
        elif total_score >= 15:
            return 'HIGH'
        elif total_score >= 8:
            return 'MEDIUM'
        elif total_score >= 3:
            return 'LOW'
        else:
            return 'SAFE'
    
    def _determine_alert_level(self, email_analysis: Dict, url_scans: List[Dict]) -> str:
        """Determine alert level based on threats"""
        threats = []
        
        # Check email analysis threats
        if email_analysis.get('sender_analysis', {}).get('risks'):
            threats.extend(email_analysis['sender_analysis']['risks'])
        
        if email_analysis.get('content_analysis', {}).get('threats'):
            for threat in email_analysis['content_analysis']['threats']:
                threats.append(threat['description'])
        
        # Check URL scan threats
        for scan in url_scans:
            if scan.get('threats'):
                threats.extend(scan['threats'])
        
        # Determine alert level
        if any('CRITICAL' in threat.upper() or 'MALWARE' in threat.upper() or 'PHISHING' in threat.upper() for threat in threats):
            return 'CRITICAL'
        elif any('HIGH' in threat.upper() or 'SUSPICIOUS' in threat.upper() for threat in threats):
            return 'HIGH'
        elif threats:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def display_alert(self, alert: Dict):
        """Display alert in console with formatting"""
        alert_level = alert['alert_level']
        overall_risk = alert['overall_risk']
        
        # Color codes for different alert levels
        colors = {
            'CRITICAL': '\033[91m',  # Red
            'HIGH': '\033[93m',      # Yellow
            'MEDIUM': '\033[94m',    # Blue
            'LOW': '\033[92m',       # Green
            'RESET': '\033[0m'       # Reset
        }
        
        color = colors.get(alert_level, colors['RESET'])
        
        alert_message = f"""
{color}🚨 SECURITY ALERT - {alert_level} LEVEL 🚨{colors['RESET']}
{'='*60}

📧 Email Details:
   From: {alert['email_data']['sender']}
   Subject: {alert['email_data']['subject']}
   Time: {alert['email_data']['timestamp']}

🎯 Risk Assessment:
   Overall Risk: {overall_risk}
   Alert Level: {alert_level}

🔍 Email Analysis:
   Sender Risk Score: {alert['email_analysis']['sender_analysis']['risk_score']}
   Content Risk Score: {alert['email_analysis']['content_analysis']['total_score']}
   Overall Score: {alert['email_analysis']['overall_score']}

"""
        
        # Add sender risks
        if alert['email_analysis']['sender_analysis']['risks']:
            alert_message += "   Sender Risks:\n"
            for risk in alert['email_analysis']['sender_analysis']['risks']:
                alert_message += f"     ⚠️  {risk}\n"
        
        # Add content threats
        if alert['email_analysis']['content_analysis']['threats']:
            alert_message += "   Content Threats:\n"
            for threat in alert['email_analysis']['content_analysis']['threats']:
                alert_message += f"     🚨 {threat['description']} (Score: {threat['score']})\n"
        
        # Add URL scan results
        if alert['url_scans']:
            alert_message += "\n🔗 URL Scan Results:\n"
            for scan in alert['url_scans']:
                alert_message += f"   URL: {scan['url']}\n"
                alert_message += f"   Risk Level: {scan['risk_level']} (Score: {scan['risk_score']})\n"
                if scan['threats']:
                    for threat in scan['threats']:
                        alert_message += f"     ⚠️  {threat}\n"
                alert_message += "\n"
        
        alert_message += f"""
📝 Email Preview:
{alert['email_data']['body_preview']}

⏰ Alert Time: {alert['timestamp']}
🆔 Alert ID: {alert['alert_id']}
{'='*60}
"""
        
        print(alert_message)
        logging.warning(f"Security alert triggered: {alert_level} level - {alert['email_data']['sender']}")
        
        # Save to alert history
        self.alert_history.append(alert)
        
        # Save to file
        self._save_alert_to_file(alert)
        
        # Send email alert if enabled
        if self.enable_email_alerts:
            self._send_email_alert(alert)
    
    def _save_alert_to_file(self, alert: Dict):
        """Save alert to log file"""
        try:
            with open(self.alert_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"ALERT ID: {alert['alert_id']}\n")
                f.write(f"TIMESTAMP: {alert['timestamp']}\n")
                f.write(f"ALERT LEVEL: {alert['alert_level']}\n")
                f.write(f"OVERALL RISK: {alert['overall_risk']}\n")
                f.write(f"SENDER: {alert['email_data']['sender']}\n")
                f.write(f"SUBJECT: {alert['email_data']['subject']}\n")
                f.write(f"EMAIL ANALYSIS: {json.dumps(alert['email_analysis'], indent=2)}\n")
                f.write(f"URL SCANS: {json.dumps(alert['url_scans'], indent=2)}\n")
                f.write(f"{'='*80}\n")
                
        except Exception as e:
            logging.error(f"Error saving alert to file: {e}")
    
    def _send_email_alert(self, alert: Dict):
        """Send email alert (if configured)"""
        try:
            # This would need to be configured with SMTP settings
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            alert_recipient = os.getenv('ALERT_RECIPIENT')
            
            if not all([smtp_server, smtp_username, smtp_password, alert_recipient]):
                logging.warning("Email alert configuration incomplete - skipping email alert")
                return
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = alert_recipient
            msg['Subject'] = f"SECURITY ALERT: {alert['alert_level']} - Suspicious Email Detected"
            
            # Create email body
            body = f"""
SECURITY ALERT - {alert['alert_level']} LEVEL

Email Details:
- From: {alert['email_data']['sender']}
- Subject: {alert['email_data']['subject']}
- Time: {alert['email_data']['timestamp']}

Risk Assessment:
- Overall Risk: {alert['overall_risk']}
- Alert Level: {alert['alert_level']}

Email Analysis:
- Sender Risk Score: {alert['email_analysis']['sender_analysis']['risk_score']}
- Content Risk Score: {alert['email_analysis']['content_analysis']['total_score']}
- Overall Score: {alert['email_analysis']['overall_score']}

Threats Detected:
"""
            
            # Add threats
            for risk in alert['email_analysis']['sender_analysis']['risks']:
                body += f"- Sender Risk: {risk}\n"
            
            for threat in alert['email_analysis']['content_analysis']['threats']:
                body += f"- Content Threat: {threat['description']}\n"
            
            for scan in alert['url_scans']:
                if scan['threats']:
                    body += f"- URL Threat ({scan['url']}): {', '.join(scan['threats'])}\n"
            
            body += f"\nAlert ID: {alert['alert_id']}\nTimestamp: {alert['timestamp']}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            logging.info(f"Email alert sent to {alert_recipient}")
            
        except Exception as e:
            logging.error(f"Error sending email alert: {e}")
    
    def get_alert_summary(self) -> Dict:
        """Get summary of all alerts"""
        if not self.alert_history:
            return {"message": "No alerts recorded"}
        
        total_alerts = len(self.alert_history)
        alert_levels = {}
        risk_levels = {}
        
        for alert in self.alert_history:
            # Count alert levels
            level = alert['alert_level']
            alert_levels[level] = alert_levels.get(level, 0) + 1
            
            # Count risk levels
            risk = alert['overall_risk']
            risk_levels[risk] = risk_levels.get(risk, 0) + 1
        
        return {
            'total_alerts': total_alerts,
            'alert_levels': alert_levels,
            'risk_levels': risk_levels,
            'latest_alert': self.alert_history[-1]['timestamp'] if self.alert_history else None
        }
    
    def clear_alert_history(self):
        """Clear alert history"""
        self.alert_history = []
        logging.info("Alert history cleared")
    
    def export_alerts(self, filename: str = None) -> str:
        """Export alerts to JSON file"""
        if not filename:
            filename = f"alerts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.alert_history, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Alerts exported to {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"Error exporting alerts: {e}")
            return None 