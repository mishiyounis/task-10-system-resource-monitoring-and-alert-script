                                    System Resource Monitor & Alert Script

A Python application that monitors system resources (CPU, RAM, Disk) in real-time and sends alerts when usage exceeds user-defined thresholds.

Features:

- Real-time monitoring of CPU, RAM, and Disk usage
- Visual progress bars with color-coded indicators (Green for normal, Orange for high, Red for critical)
- User-defined alert thresholds for each resource
- Popup alerts with sound when thresholds are exceeded
- Email alerts (Bonus feature) - sends email notifications on threshold breach
- CSV logging with timestamps for all monitoring data
- View logs in table format
- Save logs to CSV file manually
- Clear logs option
- Scrollable interface for smaller screens
- Start/Stop monitoring controls

Requirements:

- Python 3.7 or higher
- psutil
- customtkinter

Installation:

Install the required libraries:

pip install psutil customtkinter

How to Run:

python system_monitor.py

How to Use:

1. Start Monitoring: Click "Start Monitoring" button to begin real-time monitoring
2. Stop Monitoring: Click "Stop Monitoring" to pause
3. Set Thresholds: Enter values for CPU, RAM, Disk and click "Update Thresholds"
4. Email Alerts: Enable email alerts, enter your Gmail and App Password, then click "Test Email" to verify
5. View Logs: Click "View Logs" to see monitoring history in a table
6. Save Logs: Click "Save Logs as CSV" to export logs
7. Clear Logs: Click "Clear Logs" to delete all logs

Thresholds:

- CPU Threshold (default: 80%) - Alert when CPU usage exceeds this value
- RAM Threshold (default: 80%) - Alert when RAM usage exceeds this value
- Disk Threshold (default: 90%) - Alert when Disk usage exceeds this value

Email Alert Setup (For Gmail)

1. Enable 2-Step Verification on your Google Account
2. Go to Security → App Passwords
3. Select "Mail" and "Other" device
4. Generate 16-digit App Password
5. Use this password in the application (not your regular password)
