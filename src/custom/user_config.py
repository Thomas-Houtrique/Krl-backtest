import os
import yaml


class UserConfig:
    def __init__(self, config_filename="config.yaml"):
        self.config_filename = config_filename
        self.advanced_user_choice = None
        self.config_file = self.__config_file()
        self.login = self.__auto_login()

    @staticmethod
    def write_config(key, value):
        with open(r"{self.config_filename}", "r") as conf_file:
            new_conf_file = yaml.safe_load(conf_file)
            new_conf_file[key] = value
        with open(r"{self.config_filename}", "w") as conf_file:
            yaml.dump(new_conf_file, conf_file)

    def __auto_login(self):
        if "email" and "password" in self.config_file:
            login = {"email": self.config_file["email"], "password": self.config_file["password"]}
            return login
        return None

    def __config_file(self):
        """
        Return user config if config file exist, if not return -1
        """
        if os.path.exists(self.config_filename):
            with open(self.config_filename, "r") as conf_file:
                config_file = yaml.safe_load(conf_file)
        else:
            token = input("Enter your token :")
            with open(r"{self.config_filename}", "w+") as conf_file:
                yaml.dump({"token": token}, conf_file)
            with open(r"{self.config_filename}") as conf_file:
                config_file = yaml.safe_load(conf_file)
        if "headless" not in config_file:
            config_file["headless"] = "n"
        return config_file
