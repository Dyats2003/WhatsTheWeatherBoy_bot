import json


class JsonWorker():

    def json_read(self, message):
        with open(f"{message.text}.json", 'r') as j:
            json_data = json.load(j)
        return json_data

    def json_write(self, json_message, message):
        with open(f'{message.text}.json', 'w') as file:
            json.dump(json_message, file)

    def json_clean(self, message):
        with open(f'{message.text}.json', 'w') as file:
            pass

    def json_data_organaizer(self, city, time, weather):
        data = {}
        data["city"] = city
        data["time"] = time
        data["weather"] = weather
        return data

    def __str__(self):
        return "I am class to work with JSON and format data to correct json object"