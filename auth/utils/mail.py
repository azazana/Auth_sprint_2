from threading import Thread
from flask import Flask
from flask_mail import Message
from api import mail, app


def async_send_mail(app: Flask, msg: Message) -> None:
    with app.app_context():
        mail.send(msg)


def send_mail(subject: str, recipient: str, password_to_send: str) -> Thread:
    msg = Message(subject, recipients=[recipient])
    msg.body = password_to_send
    thr = Thread(target=async_send_mail, args=[app, msg])
    thr.start()
    return thr
