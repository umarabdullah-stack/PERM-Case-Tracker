
# perm_tracker.py
from playwright.sync_api import sync_playwright
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
        
# ---------------- CONFIG ----------------
CASE_NUMBER = "YOUR CASE NUMBER"
SENDER_EMAIL = "youremail@gmail.com"    # Your FROM email
RECEIVER_EMAIL = "youremail@gmail.com"  # Your TO email
APP_PASSWORD = "GMAIL APP PASSWORD"     # Gmail App Password (remove spaces... e.g. abcdefghijklmnop)
STATUS_FILE = "/<PATH>/perm-tracker/last_status.txt"   # Update Path
LOG_FILE = "/<PATH>/perm-tracker/status_log.txt"   # Update Path
# ----------------------------------------
    
def get_case_details():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
    
        page.goto("https://flag.dol.gov/case-status-search")

        page.get_by_role("textbox", name="Enter up to 30 case numbers,").fill(CASE_NUMBER)
        page.get_by_role("button", name="Search").click()
        
        page.wait_for_selector("table tbody tr")
        
        try:
            row = page.locator("table tbody tr").first
            cells = row.locator("td").all_inner_texts()
    
            print("DEBUG cells:", cells)
    
            data = {
                "Visa Program": cells[0],
                "Case Number": cells[1],
                "Employer Name": cells[2],
                "Job Title": cells[3],
                "Submit Date": cells[4],
                "Status": cells[5]
            }

        except:
            data = {"Status": "Status not found"}

        context.close()
        browser.close()

        return data
   

def log_status(status):  
    now = datetime.now().strftime("%m/%d/%Y %H:%M")
    line = f"{now} {status}\n"
    
    with open(LOG_FILE, "a") as f:
        f.write(line)
    
    print(f"Logged: {line.strip()}")  # debug print


def send_email(data, last_status):
    current_status = data["Status"] 

    subject = f"Status for PERM CASE {CASE_NUMBER} has changed to {current_status}"

    body = f"""PERM Case Update

Status changed from {last_status} to {current_status}

--------------------------------------------------------------------------------
Visa Program: {data.get("Visa Program", "")}
Case Number: {data.get("Case Number", "")}
Employer: {data.get("Employer Name", "")}
Job Title: {data.get("Job Title", "")}
Submit Date: {data.get("Submit Date", "")}
Status: {data.get("Status", "")}
Previous Status: {data.get("Previous Status", "")} 
--------------------------------------------------------------------------------
"""
        
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL   
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
        
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

        
def main():
    data = get_case_details()
    current_status = data["Status"]
            
    log_status(current_status)
            
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            last_status = f.read().strip()
    else:
        last_status = ""
                
    data["Previous Status"] = last_status

    if current_status != last_status:
        send_email(data)
        print(f"Status changed. Email sent: {current_status}")
        
        with open(STATUS_FILE, "w") as f:
            f.write(current_status)
    else:
        print(f"No change. Current status: {current_status}")


if __name__ == "__main__":
    main()
