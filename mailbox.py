import smtplib
import imaplib
import email
from nltk.corpus import wordnet
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QLabel, QLineEdit,
                               QPushButton, QTextEdit, QMainWindow)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Ustawienia skrzynki pocztowej
        self.email_address = "patrykwno@gmail.com"
        self.email_password = "cyctttrcpjxmiatj"

        # Interfejs użytkownika
        self.init_ui()

    def init_ui(self):
        # Ustawienia głównego okna
        self.setWindowTitle("Mail Client")
        self.setGeometry(100, 100, 800, 600)

        # Przyciski
        self.compose_button = QPushButton("Compose", self)
        self.compose_button.setGeometry(20, 20, 120, 30)
        self.compose_button.clicked.connect(self.compose_message)

        self.receive_button = QPushButton("Receive Mail", self)
        self.receive_button.setGeometry(150, 20, 120, 30)
        self.receive_button.clicked.connect(self.receive_mail)

        # TextEdit
        self.mail_text_edit = QTextEdit(self)
        self.mail_text_edit.setGeometry(20, 70, 760, 500)

    def receive_mail(self):
        mail = imaplib.IMAP4_SSL("smtp.gmail.com")
        mail.login(self.email_address, self.email_password)
        mail.select('inbox')
        status, data = mail.search(None, 'UNSEEN')
        filter_words = ["money", "sell", "buy", "transaction"]
        filtered = False
        mail_ids = []
        for block in data:
            mail_ids += block.split()

        message_content = ''
        for i in mail_ids:
            status, data = mail.fetch(i, '(RFC822)')

            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])
                    mail_from = message['from']
                    mail_subject = message['subject']
                    synonyms = []

                    for word in filter_words:
                        for syn in wordnet.synsets(word):
                            for i in syn.lemmas():
                                synonyms.append(i.name())

                    if message.is_multipart():
                        mail_content = ''
                        for part in message.get_payload():
                            if part.get_content_type() == 'text/plain':
                                mail_content += part.get_payload()
                    else:
                        mail_content = message.get_payload()

                    split_content = mail_content.split()
                    for content in split_content:
                        if content in synonyms:
                            filtered = True

                    if not filtered:
                        message_content += f'From: {mail_from}\nSubject: {mail_subject}\nContent: {mail_content}\n\n'

        self.mail_text_edit.setPlainText(message_content)
        try:
            self.send_message(None, mail_from, "Auto respond", "This is auto respond message")
        except:
            pass

    def compose_message(self):
        compose_window = QDialog(self)
        compose_window.setWindowTitle("Compose Message")
        compose_window.setWindowModality(Qt.ApplicationModal)
        compose_window.resize(500, 400)

        to_label = QLabel("To:")
        to_input = QLineEdit()
        subject_label = QLabel("Subject:")
        subject_input = QLineEdit()
        body_label = QLabel("Body:")
        body_input = QTextEdit()

        send_button = QPushButton("Send")
        send_button.clicked.connect(
            lambda: self.send_message(compose_window, to_input.text(), subject_input.text(), body_input.toPlainText()))

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(compose_window.reject)

        grid = QGridLayout(compose_window)
        grid.setSpacing(10)
        grid.addWidget(to_label, 1, 0)
        grid.addWidget(to_input, 1, 1)
        grid.addWidget(subject_label, 2, 0)
        grid.addWidget(subject_input, 2, 1)
        grid.addWidget(body_label, 3, 0)
        grid.addWidget(body_input, 3, 1)
        grid.addWidget(send_button, 4, 0)
        grid.addWidget(cancel_button, 4, 1)

        compose_window.setLayout(grid)
        compose_window.exec()

    def send_message(self, window, to, subject, body):
        message = MIMEMultipart()
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(body))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.sendmail(self.email_address, to, message.as_string())

        try:
            window.accept()
        except:
            pass


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()