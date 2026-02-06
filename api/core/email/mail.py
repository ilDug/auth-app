import smtplib
from email.mime.text import MIMEText
from pydantic import BaseModel
from pydantic.networks import EmailStr


class DagMailConfig(BaseModel):
    """
    Configurazione per l'invio di mail
    PORTS: 25 , 465, 587,
    """

    host: str
    port: int = 465
    user: EmailStr
    password: str


class DagMail:
    """
    ESEMPIO:

        try:
            with DagMail(config) as ms:
                ms.add_receiver('marco@gmail.com')
                ms.add_receiver('mario@gmail.com')
                ms.messageHTML(body, "invio della classe python")
                ms.send()
        except Exception as e:
            print(str(e))
    OPPURE:

        ms = DagMail(config)
        ms.create_server()
        ms.login()
        ms.add_receiver("address")
        ms.set_sender("sender@address")
        ms.messageHTML(body, "subject")
        ms.send()
    """

    mail_server = None
    sender: str
    receivers = []

    def __init__(self, config: DagMailConfig) -> None:
        self.config = config
        self.sender = self.config.user

    def __enter__(self):
        self.create_server()
        print("mail server creato")
        self.login()
        return self

    def __exit__(self, exception_type, exception_value, tb):
        self.mail_server.quit()
        if exception_type is not None:
            raise exception_value
        return True

    def create_server(self):
        print("creazione del email server ...")
        self.mail_server = smtplib.SMTP_SSL(
            host=self.config.host, port=self.config.port
        )
        return self

    def login(self):
        print("login to mail server....")
        self.mail_server.login(self.config.user, self.config.password)
        return self

    # opzionale
    def set_sender(self, address: str = None):
        self.sender = self.config.user if not address else address
        print("aggiunto mittente...")
        return self

    def add_receiver(self, address):
        self.receivers.append(address)
        print("aggiunto destinatatio...")
        return self

    def messageHTML(self, body, subject):
        self.msg = MIMEText(body, "html")
        self.msg["Subject"] = subject
        self.msg["From"] = self.sender
        self.msg["To"] = ", ".join(self.receivers)
        return self

    def send(self):
        err = self.mail_server.sendmail(
            self.sender, self.receivers, self.msg.as_string()
        )
        print("messaggio inviato")
        return err
