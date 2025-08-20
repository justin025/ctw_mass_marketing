import json
import os
from shutil import which


def config_dir():
    if os.name == 'nt' and os.path.exists(os.environ.get('APPDATA', '')):
        base_dir = os.environ['APPDATA']
    elif os.name == 'nt' and os.path.exists(os.environ.get('LOCALAPPDATA', '')):
        base_dir = os.environ['LOCALAPPDATA']
    elif os.path.exists(os.environ.get('XDG_CONFIG_HOME', '')):
        base_dir = os.environ['XDG_CONFIG_HOME']
    else:
        base_dir = os.path.join(os.path.expanduser('~'), '.config')
    return os.path.join(base_dir, 'ctw_marketing')


class Config:
    def __init__(self, cfg_path=None):
        if cfg_path is None or not os.path.isfile(cfg_path):
            cfg_path = os.path.join(config_dir(), "config.json")
        self.__cfg_path = cfg_path
        self.ext_ = ".exe" if os.name == "nt" else ""
        self.__template_data = {
            # System Variables
            "version": "v0.0.2", # Application version
            "template_subject": "Hi {name}!",
            "template_message": "Hi {name}, I was just wondering if you were interested in commercial truck warranty?",
            "smtp_ringcentral_client_id": "",
            "smtp_ringcentral_client_secret": "",
            "smtp_ringcentral_jwt": "",
            "ringcentral_phone_number": "",
            "smtp_email": "",
            "smtp_password": "",
            "smtp_server_url": "smtp.office365.com",
            "smtp_server_port": "587",
        }
        # Load Config
        if os.path.isfile(self.__cfg_path):
            self.__config = json.load(open(cfg_path, "r"))
        else:
            try:
                os.makedirs(os.path.dirname(self.__cfg_path), exist_ok=True)
            except (FileNotFoundError, PermissionError):
                print('Failed to create config dir, attempting fallback path.')
                fallback_path = os.path.abspath(os.path.join(os.path.expanduser('~'), '.config', 'config.json'))
                self.__cfg_path = fallback_path
                os.makedirs(os.path.dirname(self.__cfg_path), exist_ok=True)
            with open(self.__cfg_path, "w") as cf:
                cf.write(json.dumps(self.__template_data, indent=4))
            self.__config = self.__template_data


    def get(self, key, default=None):
        if key in self.__config:
            return self.__config[key]
        elif key in self.__template_data:
            return self.__template_data[key]
        else:
            return default


    def set(self, key, value):
        print(key)
        print(value)
        self.__config[key] = value


    def save(self):
        print(self.__cfg_path)
        with open(self.__cfg_path, "w") as cf:
            cf.write(json.dumps(self.__config, indent=4))


    def reset(self):
        with open(self.__cfg_path, "w") as cf:
            cf.write(json.dumps(self.__template_data, indent=4))
        self.__config = self.__template_data


config = Config()
