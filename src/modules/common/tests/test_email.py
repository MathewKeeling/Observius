import pytest
from unittest.mock import MagicMock
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.modules.common.email import send_email


def test_send_email_success(mocker):
    # Arrange
    subject = "Test Subject"
    body = "Test Body"
    to_email = "test@example.com"
    from_email = "from@example.com"
    smtp_server = "smtp.example.com"
    smtp_port = 587

    mock_smtp = mocker.patch("smtplib.SMTP", autospec=True)
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    # Act
    send_email(subject, body, to_email, from_email, smtp_server, smtp_port)

    # Assert
    mock_smtp.assert_called_with(smtp_server, smtp_port)
    mock_server.sendmail.assert_called_with(from_email, to_email, mocker.ANY)
    mock_server.quit.assert_called_once()


def test_send_email_failure(mocker):
    # Arrange
    subject = "Test Subject"
    body = "Test Body"
    to_email = "test@example.com"
    from_email = "from@example.com"
    smtp_server = "smtp.example.com"
    smtp_port = 587

    mock_smtp = mocker.patch("smtplib.SMTP", autospec=True)
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server
    mock_server.sendmail.side_effect = Exception("Failed to send email")

    # Act & Assert
    with pytest.raises(Exception, match="Failed to send email"):
        send_email(subject, body, to_email, from_email, smtp_server, smtp_port)


def test_send_email_with_html(mocker):
    # Arrange
    subject = "Test Subject"
    body = "<h1>Test Body</h1>"
    to_email = "test@example.com"
    from_email = "from@example.com"
    smtp_server = "smtp.example.com"
    smtp_port = 587

    mock_smtp = mocker.patch("smtplib.SMTP", autospec=True)
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    # Act
    send_email(subject, body, to_email, from_email, smtp_server, smtp_port)

    # Assert
    mock_smtp.assert_called_with(smtp_server, smtp_port)
    mock_server.sendmail.assert_called_with(from_email, to_email, mocker.ANY)
    mock_server.quit.assert_called_once()


def test_send_email_with_empty_fields(mocker):
    # Arrange
    subject = ""
    body = ""
    to_email = ""
    from_email = ""
    smtp_server = "smtp.example.com"
    smtp_port = 587

    mock_smtp = mocker.patch("smtplib.SMTP", autospec=True)
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid email address"):
        send_email(subject, body, to_email, from_email, smtp_server, smtp_port)


def test_send_email_with_invalid_email(mocker):
    # Arrange
    subject = "Test Subject"
    body = "Test Body"
    to_email = "invalid-email"
    from_email = "from@example.com"
    smtp_server = "smtp.example.com"
    smtp_port = 587

    mock_smtp = mocker.patch("smtplib.SMTP", autospec=True)
    mock_server = MagicMock()
    mock_smtp.return_value = mock_server

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid email address"):
        send_email(subject, body, to_email, from_email, smtp_server, smtp_port)
