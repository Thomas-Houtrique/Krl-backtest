import os
import yaml


class UserConfig:
    def __init__(self):
        self.advanced_user_choice = self.yes_no_question(question="Do you want to configure the script ?")
        self.config = self.__advanced_configuration(advanced=self.advanced_user_choice)
        self.config_file = self.__config_file()
        self.login = self.__auto_login()

    def write_config(self, key, value):
        with open(r"config.yaml", "r") as conf_file:
            new_conf_file = yaml.load(conf_file)
            new_conf_file[key] = value
        with open(r"config.yaml", "w") as conf_file:
            yaml.dump(new_conf_file, conf_file)

    def __auto_login(self):
        if "email" and "password" in self.config_file:
            login = {"email": self.config_file["email"], "password": self.config_file["password"]}
            return login

    def yes_no_question(self, question):
        """
        Takes a question, return the answer y or n
        """
        response = input(question + " (y/n)").lower()
        while response not in ("y", "n"):
            print("invalid choice")
            response = self.yes_no_question(question)
        return response

    def __advanced_configuration(self, advanced):
        """
        Takes if client want advanced config, return user config
        """
        user_advanced_configuration = {}
        if advanced == "y":
            user_advanced_configuration["global"] = self.yes_no_question("Do you want to test the global period ?")
            user_advanced_configuration["last_three_months"] = self.yes_no_question("Do you want to test the last three months ?")
            user_advanced_configuration["every_pairs"] = self.yes_no_question("do you want to test every pairs ?")
            user_advanced_configuration["exchanges"] = self.yes_no_question("do you want to test every exchanges ?")
            user_advanced_configuration["verbose"] = self.yes_no_question("do you want to show verbose logs ?")
        else:
            user_advanced_configuration["global"] = "y"
            user_advanced_configuration["last_three_months"] = "y"
            user_advanced_configuration["every_pairs"] = "n"
            user_advanced_configuration["exchanges"] = "n"
            user_advanced_configuration["verbose"] = "n"
        return user_advanced_configuration

    def __config_file(self):
        """
        Return user config if config file exist, if not return -1
        """
        if os.path.exists("config.yaml"):
            with open(r"config.yaml") as conf_file:
                config_file = yaml.load(conf_file, Loader=yaml.FullLoader)
                return config_file
        else:
            token = input("Enter your token :")
            config_file = self.write_config(key="token", value=token)
            return config_file
