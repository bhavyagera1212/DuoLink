from __future__ import print_function
import os
import base64
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pyttsx3
import speech_recognition as sr

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.send']

'''def authenticate_gmail():
    """Shows basic usage of the Gmail API."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds'''
def authenticate_gmail():
    creds = None
    email_id = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # Fetch the authenticated email ID
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        email_id = profile['emailAddress']
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # Fetch the authenticated email ID
            service = build('gmail', 'v1', credentials=creds)
            profile = service.users().getProfile(userId='me').execute()
            email_id = profile['emailAddress']
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds, email_id

def send_email(creds, to, subject, message_text, file_path=None):
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(message_text, 'plain'))

    if file_path:
        part = MIMEBase('application', 'octet-stream')
        with open(file_path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw}
    try:
        message = (service.users().messages().send(userId="me", body=body).execute())
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print(f'An error occurred while sending the email: {error}')
        return None


def read_users_file(file_path):
    users = {}
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():
                email_id, password, name, created = line.strip().split(';')
                users[email_id] = password
    return users


def read_and_reply_emails(creds, processed_emails):
    service = build('gmail', 'v1', credentials=creds)
    try:
        response = service.users().messages().list(userId='me', q='subject:Anvit is:unread').execute()
        messages = response.get('messages', [])
        if not messages:
            speak("No new emails with the subject 'Anvit'.")
        else:
            for msg in messages:
                msg_id = msg['id']
                if msg_id in processed_emails:
                    continue
                message = service.users().messages().get(userId='me', id=msg_id).execute()
                payload = message.get('payload', {})
                headers = payload.get('headers', [])
                for header in headers:
                    if header.get('name') == 'Subject':
                        subject = header.get('value')
                        if subject == 'Anvit':
                            parts = payload.get('parts', [])
                            for part in parts:
                                if part['mimeType'] == 'text/plain':
                                    body = base64.urlsafe_b64decode(part['body']['data']).decode()
                                    speak("You have an email with the subject 'Anvit'. The message body is as follows:")
                                    speak(body)

                                    # Extract file path or name from the body
                                    file_path = extract_file_path(body)
                                    if file_path:
                                        file_path = search_file(file_path)
                                        if file_path:
                                            reply_to = get_sender_email(headers)
                                            send_email(creds, reply_to, 'Re: ' + subject, 'Here is the file you requested.', file_path)
                                            speak(f"Replied with the file {file_path}.")
                                        else:
                                            speak("File mentioned in the email body does not exist.")
                                    else:
                                        speak("No file path found in the email body.")
                                    mark_as_read(service, msg_id)  # Mark the message as read after processing
                                    processed_emails.add(msg_id)
    except Exception as error:
        print(f'An error occurred while reading emails: {error}')
        speak("Failed to read emails. Please check the logs for more details.")

def extract_file_path(body):
    # This function should be customized based on how the file path is mentioned in the email body
    # For simplicity, let's assume the file path is the entire body content
    return body.strip()

def search_file(file_name):
    for root, dirs, files in os.walk("/"):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

def get_sender_email(headers):
    for header in headers:
        if header.get('name') == 'From':
            return header.get('value')
    return None

def mark_as_read(service, msg_id):
    try:
        service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
    except Exception as error:
        print(f'An error occurred while marking the email as read: {error}')

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_voice_input(prompt):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    speak(prompt)
    with microphone as source:
        print(prompt)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return get_voice_input(prompt)
    except sr.RequestError as e:
        speak("Could not request results; {0}".format(e))
        return None

'''def main():
    creds = authenticate_gmail()
    processed_emails = set()

    action = get_voice_input("Do you want to create a mail or check my inbox?")
    if action.lower() == "create a mail":
        to = get_voice_input("Please say the recipient's email address.")
        subject = get_voice_input("Please say the subject of the email.")
        message_text = get_voice_input("Please say the message body of the email.")
        
        speak("Sending email")
        result = send_email(creds, to, subject, message_text)
        
        if result:
            speak("Email sent successfully. Message Id: " + result['id'])
        else:
            speak("Failed to send email. Please check the logs for more details.")
    elif action.lower() == "check my inbox":
        speak("Reading emails with subject 'Anvit'")
        while True:
            read_and_reply_emails(creds, processed_emails)
            time.sleep(60)  # Check for new emails every 1 minute
    else:
        speak("Invalid action. Please say 'create a mail' or 'check my inbox'.")'''

def main():
    creds, auth_email_id = authenticate_gmail()
    processed_emails = set()

    # Read users.txt and get email_id:password dictionary
    users = read_users_file('users.txt')

    # Check if the authenticated email ID is in users.txt
    if auth_email_id not in users:
        speak("Unauthorized access. Please check your credentials.")
        return

    action = get_voice_input("Do you want to create a mail or check my inbox?")
    if action.lower() == "create a mail":
        # Code for sending email
        to = get_voice_input("Please say the recipient's email address.")
        subject = get_voice_input("Please say the subject of the email.")
        message_text = get_voice_input("Please say the message body of the email.")
        
        speak("Sending email")
        result = send_email(creds, to, subject, message_text)
        
        if result:
            speak("Email sent successfully. Message Id: " + result['id'])
        else:
            speak("Failed to send email. Please check the logs for more details.")
    elif action.lower() == "check my inbox":
        speak("Reading emails with subject 'Anvit'")
        while True:
            read_and_reply_emails(creds, processed_emails)
            time.sleep(60)  # Check for new emails every 1 minute
    else:
        speak("Invalid action. Please say 'create a mail' or 'check my inbox'.")

if __name__ == '__main__':
    main()

