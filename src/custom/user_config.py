import os
import yaml
import datetime
from pprint import pprint
from common import ROOT_DIR

class UserConfig:

    def __init__(self, args):
        if args.config is None:
            self.config_filename = "config.yaml"
        else:
            self.config_filename = args.config
        self.advanced_user_choice = None
        self.config_file = self.__config_file(args)
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

    def __config_file(self,args):
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
        
        config_file['command'] = False
        if "headless" not in config_file:
            config_file["headless"] = "n"
        
        #pprint(args)
        if "open_browser" in config_file and config_file["open_browser"].lower() == "y":
            config_file['headless'] = False
        if "disable_marketplace" in config_file and config_file["disable_marketplace"].lower() == "y":
            config_file['marketplace'] = False
        if "disable_2fa" in config_file and config_file["disable_2fa"].lower() == "y":
            config_file['ask_2fa'] = False

        if args.browser is not None:
            config_file['browser'] = args.browser
        if args.email is not None:
            config_file['email'] = args.email
        if args.password is not None:
            config_file['password'] = args.password
        if args.token is not None:
            config_file['token'] = args.token
        if args.history is not None:
            config_file['history'] = args.history

        if args.save_logs is not None:
            config_file['save_logs'] = args.save_logs
        if ('save_logs' in config_file) and config_file['save_logs'] == '':
            if "my_strats" in self.user_config_file:
                config_file['save_logs'] = 'my_results'
            else:
                config_file['save_logs'] = 'results'
        if ('save_logs' in config_file) and (not config_file['save_logs'].endswith(os.sep)):
            config_file['save_logs'] = config_file['save_logs'] + os.sep
        if ('save_logs' in config_file) and (not config_file['save_logs'].startswith(os.sep)):
            config_file['save_logs'] = ROOT_DIR + os.sep + config_file['save_logs']
        try:
            if not os.path.isdir(config_file['save_logs']):
                os.makedirs(config_file['save_logs'])
        except Exception as error:
            raise Exception("[❌] Can't create save_logs directory: " + config_file['save_logs'] + "\n" + str(error), True)

        if args.save_results is not None:
            config_file['save_results'] = args.save_results
        if ('save_results' in config_file) and config_file['save_results'] == '':
            if "my_strats" in self.user_config_file:
                config_file['save_results'] = 'my_results'
            else:
                config_file['save_results'] = 'results'
        if ('save_results' in config_file) and (not config_file['save_results'].endswith(os.sep)):
            config_file['save_results'] = config_file['save_results'] + os.sep
        if ('save_results' in config_file) and (not config_file['save_results'].startswith(os.sep)):
            config_file['save_results'] = ROOT_DIR + os.sep + config_file['save_results']
        try:
            if not os.path.isdir(config_file['save_results']):
                os.makedirs(config_file['save_results'])
        except Exception as error:
            raise Exception("[❌] Can't create save_results directory: " + config_file['save_results'] + "\n" + str(error), True)


        if args.every_pairs:
            config_file['every_pairs'] = 'y'
        if args.upgrade_strat:
            config_file['update_strat'] = 'y'
        if args.verbose:
            config_file['verbose'] = 'y'
        if args.force:
            config_file['force'] = 'y'
        if args.open_browser:
            config_file['headless'] = 'n'
        if args.disable_marketplace:
            config_file['marketplace'] = 'n'
        if args.disable_2fa:
            config_file['ask_2fa'] = 'n'
        if args.delete_strats:
            config_file['command'] = 'delete_strats'
            config_file['delete_strats'] = args.delete_strats
        
        if args.exchanges is not None:
            config_file['exchanges'] = args.exchanges.split(',')
        if args.accu is not None:
            config_file['accu'] = args.accu.upper().split(',')
        if args.pairs is not None:
            config_file['pair'] = args.pairs.upper().split(',')
        if args.strat_ids is not None:
            config_file['strat_ids'] = args.strat_ids.split(',')
        if args.my_strats is not None:
            config_file['my_strats'] = args.my_strats.split(',')
        
        periods = {}
        if args.periods is not None:
            arg_periods = args.periods.split(',')
            for arg_period in arg_periods:
                [name,dates] = arg_period.split(':')
                periods[name]= [
                    datetime.datetime.strptime(dates.split('..')[0], '%Y-%m-%d').date(),
                    datetime.datetime.strptime(dates.split('..')[1], '%Y-%m-%d').date()
                ]
        if len(periods) > 0:
            config_file['periods'] = periods

        #pprint(config_file)
        #sys.exit()
        return config_file
