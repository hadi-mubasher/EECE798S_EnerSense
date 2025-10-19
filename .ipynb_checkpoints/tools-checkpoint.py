"""
EnerSense Tools Module
----------------------
This module defines all tool functions used by the EnerSense chatbot.

Each function performs a single well-defined task:
    - Recording customer interest (leads)
    - Logging feedback or unanswered questions
    - Logging site monitoring setup requests
    - Recording report generation requests
    - Scheduling consultations and checking for conflicts
    - Listing available consultation slots

All logs are stored under the 'logs/' directory.
"""

import os
import csv
import re
import datetime as dt

# -------------------------------------------------------------------
# Directory Setup
# -------------------------------------------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def record_customer_interest(name: str, email: str, message: str):
    """
    Records potential customer interest or inquiries.

    Inputs:
    -------
    - name: str. Full name of the customer.
    - email: str. Contact email address.
    - message: str. Inquiry or description of interest.

    Returns:
    --------
    - str: Confirmation message for the user.

    Behavior:
    ---------
    Appends a record to 'logs/leads_log.txt' with UTC timestamp.
    Used to track user inquiries and contact information for follow-up.
    """
    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join(LOG_DIR, "leads_log.txt")
    log_entry = f"[{timestamp}] Lead | Name: {name} | Email: {email} | Message: {message}\n"

    with open(log_path, "a") as f:
        f.write(log_entry)

    print(f"[Lead Recorded] {name} ({email})")
    return f"Thank you {name}, your interest has been recorded. Our energy team will reach out shortly."


def record_feedback(question: str):
    """
    Logs customer feedback or off-topic questions.

    Inputs:
    -------
    - question: str. Feedback or question text from the user.

    Returns:
    --------
    - str: Acknowledgment message confirming receipt.

    Behavior:
    ---------
    Appends the user's question to 'logs/feedback_log.txt' with timestamp.
    Used for internal review to improve assistant responses.
    """
    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join(LOG_DIR, "feedback_log.txt")
    log_entry = f"[{timestamp}] Feedback | Question: {question}\n"

    with open(log_path, "a") as f:
        f.write(log_entry)

    print(f"[Feedback Logged] {question}")
    return "Thank you for your feedback. I've noted your question for our energy experts."


def log_site_monitoring_request(customer_name: str, site_name: str, parameters: str):
    """
    Records a customer request to set up monitoring for a specific site.

    Inputs:
    -------
    - customer_name: str. Name of the customer requesting monitoring.
    - site_name: str. Name of the facility or site (e.g., 'MTC North').
    - parameters: str. Parameters to monitor (e.g., 'temperature, current').

    Returns:
    --------
    - str: Confirmation message for the user.

    Behavior:
    ---------
    Appends the request to 'logs/monitoring_requests.txt' with timestamp.
    Enables engineering follow-up for sensor configuration.
    """
    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join(LOG_DIR, "monitoring_requests.txt")
    log_entry = (
        f"[{timestamp}] Monitoring Request | Customer: {customer_name} | "
        f"Site: {site_name} | Parameters: {parameters}\n"
    )

    with open(log_path, "a") as f:
        f.write(log_entry)

    print(f"[Monitoring Request Logged] {customer_name} - {site_name} ({parameters})")
    return f"Monitoring request for '{site_name}' by {customer_name} has been recorded. Our engineers will contact you soon."


def log_energy_report_request(company_name: str, period: str):
    """
    Logs a customer's request for an energy performance report.

    Inputs:
    -------
    - company_name: str. Name of the company requesting the report.
    - period: str. Reporting frequency (e.g., 'weekly', 'monthly').

    Returns:
    --------
    - str: Confirmation message for the user.

    Behavior:
    ---------
    Appends the request to 'logs/report_requests.txt' with timestamp.
    Allows the analytics team to prepare and deliver reports later.
    """
    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join(LOG_DIR, "report_requests.txt")
    log_entry = f"[{timestamp}] Report Request | Company: {company_name} | Period: {period}\n"

    with open(log_path, "a") as f:
        f.write(log_entry)

    print(f"[Report Request Logged] {company_name} ({period})")
    return f"Energy report request for {company_name} ({period}) recorded successfully."


def schedule_consultation(name: str, date: str, topic: str):
    """
    Books a consultation if the requested time is available.

    Inputs:
    -------
    - name: str. Client's full name.
    - date: str. Requested date and time (e.g., '2025-10-22 11:00' or 'October 22 at 11:00').
    - topic: str. Main topic or purpose of the consultation.

    Returns:
    --------
    - str: Confirmation message or conflict notice.

    Behavior:
    ---------
    Checks 'logs/consultations_calendar.csv' for time conflicts.
    Normalizes various date formats to 'YYYY-MM-DD HH:MM' before comparison.
    Prevents duplicate bookings for the same time slot.
    """

    timestamp = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    filename = os.path.join(LOG_DIR, "consultations_calendar.csv")

    # Create file if not present
    if not os.path.exists(filename):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp (UTC)", "Client Name", "Consultation Date", "Topic"])

    # Helper: Normalize date strings
    def normalize_datetime(date_str: str) -> str:
        try:
            return dt.datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M")
        except Exception:
            month_map = {m: i for i, m in enumerate([
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"], 1)}
            match = re.search(r"([A-Za-z]+)\s+(\d{1,2}).*?(\d{1,2}):(\d{2})", date_str)
            if match:
                month = month_map.get(match.group(1), 1)
                day = int(match.group(2))
                hour, minute = int(match.group(3)), int(match.group(4))
                year = dt.datetime.utcnow().year
                return f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"
            return date_str.strip()

    normalized_date = normalize_datetime(date)

    # Check for existing bookings
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if normalize_datetime(row["Consultation Date"]) == normalized_date:
                print(f"[Conflict] {normalized_date} already booked for {row['Client Name']}")
                day = normalized_date.split()[0]
                return f"That time slot on {day} is already reserved. Please choose another time that day."

    # Log new booking
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, name, normalized_date, topic])

    print(f"[Consultation Scheduled] {name} on {normalized_date} ({topic})")
    return f"Consultation booked for {name} on {normalized_date} about '{topic}'. Our team will confirm shortly."


def list_available_slots(date: str, start: str = "09:00", end: str = "17:00", step_minutes: int = 60):
    """
    Lists available consultation time slots for a given date.

    Inputs:
    -------
    - date: str. Date in 'YYYY-MM-DD' format.
    - start: str. Start of working hours (default = '09:00').
    - end: str. End of working hours (default = '17:00').
    - step_minutes: int. Slot interval in minutes (default = 60).

    Returns:
    --------
    - str: Message listing available slots or noting full booking.

    Behavior:
    ---------
    Reads 'logs/consultations_calendar.csv', checks booked times for the given date,
    and lists remaining available slots in the defined working period.
    """
    filename = os.path.join(LOG_DIR, "consultations_calendar.csv")

    if not os.path.exists(filename):
        return f"No consultations scheduled yet. All slots available between {start} and {end}."

    # Gather booked slots
    booked = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Consultation Date"].startswith(date):
                time_str = row["Consultation Date"].split()[-1]
                booked.append(time_str)

    # Build list of all possible slots
    date_obj = dt.datetime.fromisoformat(date)
    start_dt = dt.datetime.combine(date_obj, dt.time.fromisoformat(start))
    end_dt = dt.datetime.combine(date_obj, dt.time.fromisoformat(end))
    step = dt.timedelta(minutes=step_minutes)

    slots = []
    while start_dt < end_dt:
        time_str = start_dt.strftime("%H:%M")
        if time_str not in booked:
            slots.append(time_str)
        start_dt += step

    if not slots:
        return f"All slots on {date} are booked."
    return f"Available consultation slots on {date}: {', '.join(slots)}"
