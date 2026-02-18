import unittest
from unittest.mock import ANY, MagicMock, patch

from core.email.mail import DagMail, DagMailConfig


class TestDagMailTLSMatrix(unittest.TestCase):
    def _config(self, port, tls_mode="auto"):
        return DagMailConfig(
            host="smtp.example.com",
            port=port,
            user="user@example.com",
            password="secret",
            tls_mode=tls_mode,
        )

    @patch("core.email.mail.smtplib.SMTP_SSL")
    @patch("core.email.mail.smtplib.SMTP")
    def test_auto_port_465_uses_ssl(self, smtp_mock, smtp_ssl_mock):
        smtp_ssl_instance = MagicMock()
        smtp_ssl_mock.return_value = smtp_ssl_instance

        mail = DagMail(self._config(465, "auto"))
        mail.create_server()

        smtp_ssl_mock.assert_called_once_with(host="smtp.example.com", port=465)
        smtp_mock.assert_not_called()
        smtp_ssl_instance.starttls.assert_not_called()
        smtp_ssl_instance.ehlo.assert_not_called()

    @patch("core.email.mail.smtplib.SMTP_SSL")
    @patch("core.email.mail.smtplib.SMTP")
    def test_auto_port_587_uses_starttls(self, smtp_mock, smtp_ssl_mock):
        smtp_instance = MagicMock()
        smtp_mock.return_value = smtp_instance

        mail = DagMail(self._config(587, "auto"))
        mail.create_server()

        smtp_ssl_mock.assert_not_called()
        smtp_mock.assert_called_once_with(host="smtp.example.com", port=587)
        self.assertEqual(smtp_instance.ehlo.call_count, 2)
        smtp_instance.starttls.assert_called_once_with(context=ANY)

    @patch("core.email.mail.smtplib.SMTP_SSL")
    @patch("core.email.mail.smtplib.SMTP")
    def test_auto_port_25_no_tls(self, smtp_mock, smtp_ssl_mock):
        smtp_instance = MagicMock()
        smtp_mock.return_value = smtp_instance

        mail = DagMail(self._config(25, "auto"))
        mail.create_server()

        smtp_ssl_mock.assert_not_called()
        smtp_mock.assert_called_once_with(host="smtp.example.com", port=25)
        smtp_instance.starttls.assert_not_called()
        smtp_instance.ehlo.assert_not_called()

    @patch("core.email.mail.smtplib.SMTP_SSL")
    @patch("core.email.mail.smtplib.SMTP")
    def test_forced_starttls_overrides_port(self, smtp_mock, smtp_ssl_mock):
        smtp_instance = MagicMock()
        smtp_mock.return_value = smtp_instance

        mail = DagMail(self._config(25, "starttls"))
        mail.create_server()

        smtp_ssl_mock.assert_not_called()
        smtp_mock.assert_called_once_with(host="smtp.example.com", port=25)
        self.assertEqual(smtp_instance.ehlo.call_count, 2)
        smtp_instance.starttls.assert_called_once_with(context=ANY)

    @patch("core.email.mail.smtplib.SMTP_SSL")
    @patch("core.email.mail.smtplib.SMTP")
    def test_forced_none_disables_starttls(self, smtp_mock, smtp_ssl_mock):
        smtp_instance = MagicMock()
        smtp_mock.return_value = smtp_instance

        mail = DagMail(self._config(587, "none"))
        mail.create_server()

        smtp_ssl_mock.assert_not_called()
        smtp_mock.assert_called_once_with(host="smtp.example.com", port=587)
        smtp_instance.starttls.assert_not_called()
        smtp_instance.ehlo.assert_not_called()

    @patch("core.email.mail.smtplib.SMTP_SSL")
    @patch("core.email.mail.smtplib.SMTP")
    def test_forced_ssl_overrides_port(self, smtp_mock, smtp_ssl_mock):
        smtp_ssl_instance = MagicMock()
        smtp_ssl_mock.return_value = smtp_ssl_instance

        mail = DagMail(self._config(587, "ssl"))
        mail.create_server()

        smtp_ssl_mock.assert_called_once_with(host="smtp.example.com", port=587)
        smtp_mock.assert_not_called()
        smtp_ssl_instance.starttls.assert_not_called()
        smtp_ssl_instance.ehlo.assert_not_called()


if __name__ == "__main__":
    unittest.main()
