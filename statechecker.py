import requests

class StateChecker():

    def state_check(self, url):
            r = requests.head(url)
            return r.status_code