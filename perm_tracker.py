
# perm_tracker.py
from playwright.sync_api import sync_playwright
import smtplib 
from email.mime.text import MIMEText   
from email.mime.multipart import MIMEMultipart
import os
        
# ---------------- CONFIG ----------------
CASE_NUMBER = "YOUR CASE NUMBER"
SENDER_EMAIL = "youremail@gmail.com"    # Your FROM email
RECEIVER_EMAIL = "youremail@gmail.com"  # Your TO email
APP_PASSWORD = "GMAIL APP PASSWORD"     # Gmail App Password
STATUS_FILE = "/<PATH>/perm-tracker/last_status.txt"   # Update Path
# ----------------------------------------
    
def get_status():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://flag.dol.gov/case-status-search")

        # Type case number and click search
        page.get_by_role("textbox", name="Enter up to 30 case numbers,").fill(CASE_NUMBER)
        page.get_by_role("button", name="Search").click()
    
        page.wait_for_timeout(5000)  # wait for results
        
        # Grab the status from the 6th column of the first row
        try:
            status = page.locator("table").locator("tr").nth(1).locator("td").nth(5).inner_text()
        except:
            status = "Status not found"
    
        context.close()
        browser.close()
        return status
        
def send_email(current_status, last_status):
    subject = f"Status for PERM CASE {CASE_NUMBER} has changed to {current_status}"
    body = f"Current Status for PERM CASE {CASE_NUMBER} has changed to {current_status} from {last_status}"
        
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

def main():
    current_status = get_status()
        
    # Read last status (can be any text)
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            last_status = f.read().strip()
    else:
        last_status = ""  # empty if file does not exist
        
    # Only send email if status changed
    if current_status != last_status:
        send_email(current_status, last_status)  # pass both
        print(f"Status changed. Email sent: {current_status}")
        
        # Update last status
        with open(STATUS_FILE, "w") as f:
            f.write(current_status)
    else:
        print(f"No change. Current status: {current_status}")
    
if __name__ == "__main__":
    main()
