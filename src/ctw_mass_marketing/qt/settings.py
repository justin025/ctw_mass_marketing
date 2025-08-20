import os
from PyQt6.QtWidgets import QMessageBox
from ..otsconfig import config


def load_config(self):
    self.input_template_subject.setText(config.get("template_subject"))
    self.input_template_message.setPlainText(config.get("template_message"))
    self.input_ringcentral_client_id.setText(config.get("ringcentral_client_id"))
    self.input_ringcentral_client_secret.setText(config.get("ringcentral_client_secret"))
    self.input_ringcentral_jwt.setText(config.get("ringcentral_jwt"))
    self.input_ringcentral_phone_number.setText(config.get("ringcentral_phone_number"))
    self.input_smtp_email.setText(config.get("smtp_email"))
    self.input_smtp_password.setText(config.get("smtp_password"))
    self.input_smtp_server_url.setText(config.get("smtp_server_url"))
    self.input_smtp_server_port.setText(config.get("smtp_server_port"))


def save_config(self):
    config.set('template_subject', self.input_template_subject.text())
    config.set('template_message', self.input_template_message.toPlainText())
    config.set('ringcentral_client_id', self.input_ringcentral_client_id.text())
    config.set('ringcentral_client_secret', self.input_ringcentral_client_secret.text())
    config.set('ringcentral_jwt', self.input_ringcentral_jwt.text())
    config.set('ringcentral_phone_number', self.input_ringcentral_phone_number.text())
    config.set('smtp_email', self.input_smtp_email.text())
    config.set('smtp_password', self.input_smtp_password.text())
    config.set('smtp_server_url', self.input_smtp_server_url.text())
    config.set('smtp_server_port', self.input_smtp_server_port.text())
    config.save()
    msg = QMessageBox(self)
    msg.setWindowTitle("Config Saved")
    msg.setText(f"Config sved, settings will persist after restarting the app.")
    msg.show()


def reset_config(self):
    config.reset()
    msg = QMessageBox(self)
    msg.setWindowTitle("Config Reset")
    msg.setText(f"Config reset, please restart the app.")
    msg.show()


