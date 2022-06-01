import requests

class StateChecker():

    def state_check(self, url):
            r = requests.head(url)
            return r.status_code

if __name__ == "main":
    #test state
    c = StateChecker()
    print(c.state_check("https://google.com"))