from enum import Enum, auto
import smtplib
import ssl
from typing import Annotated
from email.mime.text import MIMEText
from pydantic import BaseModel, SecretStr, Field
from pydantic.networks import EmailStr
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("dagmail")


class TLS_MODE(Enum):
    """How to handle TLS for SMTP connections"""

    AUTO = auto()
    SSL = auto()
    STARTTLS = auto()
    NONE = auto()


class DagMailConfig(BaseModel):
    """
    Configurazione per l'invio di mail
    PORTS:
    - 25: SMTP non cifrato
    - 465: SMTP cifrato (SSL/TLS)
    - 587: SMTP con STARTTLS (cifratura opzionale)

    TLS_MODE:
    - AUTO: decide in base alla porta
    - SSL: forza SMTP_SSL
    - STARTTLS: forza STARTTLS
    - NONE: disabilita TLS
    """

    host: Annotated[str, Field(description="Indirizzo del server SMTP")]
    port: Annotated[int, Field(description="Porta del server SMTP: 25, 465, 587")] = 465
    user: Annotated[EmailStr, Field(description="Indirizzo email dell'utente")]
    password: Annotated[SecretStr, Field(description="Password dell'utente")]
    tls_mode: Annotated[
        TLS_MODE,
        Field(description="Modalità TLS da utilizzare: AUTO, SSL, STARTTLS, NONE"),
    ] = TLS_MODE.AUTO


class DagMail:
    """
    ESEMPIO:

        try:
            with DagMail(config) as ms:
                ms.set_sender("sender@address")
                ms.add_receiver('marco@gmail.com')
                ms.add_receiver('mario@gmail.com')
                ms.messageHTML(body, "invio della classe python")
                ms.send()
        except Exception as e:
            logger.error(str(e))
    OPPURE:

        ms = DagMail(config)
        ms.create_server()
        ms.login()
        ms.add_receiver("address")
        ms.set_sender("sender@address")
        ms.messageHTML(body, "subject")
        ms.send()
    """

    def __init__(self, config: DagMailConfig) -> None:
        self.config = config
        self.sender = self.config.user
        self.receivers = []
        self.mail_server = None
        self.msg = None

    def __enter__(self):
        self.create_server()
        logger.info("mail server creato")
        self.login()
        return self

    def __exit__(self, exception_type, exception_value, tb):
        if self.mail_server is not None:
            try:
                self.mail_server.quit()
            except Exception as exc:
                logger.error("errore chiusura mail server: %s", exc)
        if exception_type is not None:
            logger.error(str(exception_value))
        return False

    def create_server(self) -> "DagMail":
        logger.info("creazione del email server ...")
        tls_mode = self.config.tls_mode

        if tls_mode == TLS_MODE.AUTO:
            match self.config.port:
                case 465:
                    tls_mode = TLS_MODE.SSL
                case 587:
                    tls_mode = TLS_MODE.STARTTLS
                case _:
                    tls_mode = TLS_MODE.NONE

        match tls_mode:
            case TLS_MODE.SSL:
                self.mail_server = smtplib.SMTP_SSL(
                    host=self.config.host,
                    port=self.config.port,
                )
            case TLS_MODE.STARTTLS:
                self.mail_server = smtplib.SMTP(
                    host=self.config.host,
                    port=self.config.port,
                )
                self.mail_server.ehlo()
                self.mail_server.starttls(context=ssl.create_default_context())
                self.mail_server.ehlo()
            case TLS_MODE.NONE:
                self.mail_server = smtplib.SMTP(
                    host=self.config.host,
                    port=self.config.port,
                )
        return self

    def login(self) -> "DagMail":
        logger.info("login to mail server....")
        self.mail_server.login(
            self.config.user, self.config.password.get_secret_value()
        )
        return self

    def set_sender(self, address: str = None) -> "DagMail":
        """imposta il mittente, se non specificato usa l'utente di login"""
        self.sender = self.config.user if not address else address
        logger.info("aggiunto mittente...")
        return self

    def add_receiver(self, address) -> "DagMail":
        """aggiunge un destinatario alla lista dei destinatari, è possibile aggiungere più destinatari chiamando più volte questo metodo"""
        self.receivers.append(address)
        logger.info("aggiunto destinatario...")
        return self

    def messageHTML(self, body, subject) -> "DagMail":
        """imposta il corpo del messaggio, è possibile chiamare questo metodo più volte per sovrascrivere il messaggio precedente"""
        self.msg = MIMEText(body, "html")
        self.msg["Subject"] = subject
        self.msg["From"] = self.sender
        self.msg["To"] = ", ".join(self.receivers)
        return self

    def send(self) -> dict:
        """
        Invia il messaggio, restituisce un dizionario con eventuali errori di invio per destinatario.

        Se l'invio è andato a buon fine il dizionario sarà vuoto, altrimenti conterrà le chiavi dei destinatari per cui l'invio è fallito e come valore il codice di errore restituito dal server SMTP.
        """
        if self.mail_server is None:
            raise RuntimeError("mail server non inizializzato")
        if not self.receivers:
            raise RuntimeError("nessun destinatario impostato")
        if self.msg is None:
            raise RuntimeError("messaggio non impostato")
        if not self.sender:
            self.set_sender()
        err = self.mail_server.sendmail(
            self.sender, self.receivers, self.msg.as_string()
        )
        logger.info("messaggio inviato")
        return err
