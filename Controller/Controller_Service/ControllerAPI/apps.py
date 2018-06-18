from django.apps import AppConfig
import json, os

class ControllerapiConfig(AppConfig):
    name = 'ControllerAPI'
    
    def ready(self):
        module_dir = os.path.dirname(__file__)
        f = open(f'{module_dir}/conf.json')
        text = ''
        for line in f:
            text += line
        conf_dict = json.loads(text)
        self.inv_addr = conf_dict['inventory']
        self.notif_addr = conf_dict['notification']
        self.broker = conf_dict['broker']
        self.retries = conf_dict['retries']
        self.wait = conf_dict['wait']
        f.close()