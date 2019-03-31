import requests

class APIBase:

    def __init__(self):
        self.operations = 0

    def get(self, url, params={}, skip_operation=False):
        d = requests.get(url, params)
        if not skip_operation:
            self.operations += 1
        return d
