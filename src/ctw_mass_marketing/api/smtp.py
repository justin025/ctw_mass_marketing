from ..runtimedata import account_pool
import smtplib

def smtp_send_email(fromemail, password, server_url, server_port, toemail, subject, text):
    if not account_pool['smtp']:
        server = smtplib.SMTP(server_url, server_port)
        server.starttls()
        server.login(fromemail, password)
        account_pool['smtp'] = server
    message = f"Subject: {subject}\n\n{text}"
    account_pool['smtp'].sendmail(fromemail, toemail, message)
