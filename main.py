import datetime
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import os
import jsonworker
import res
import random
import statechecker

bot = telebot.TeleBot(res.TOKEN)

city_flag = 0
driverbuff = []
search_flag = 0


def see_weather(message):
    bot.send_message(message.chat.id, 'К вашим услугам')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    location = types.KeyboardButton('Геопозиция🎯', request_location=True)
    city = types.KeyboardButton('Город🌉')
    fact = types.KeyboardButton('Факт дня⁉️')
    news = types.KeyboardButton('Актуальные новости🌏')
    markup.add(location, city, fact, news)
    bot.send_message(message.chat.id, "Выбери: поиск по геопозиции или по городу", reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    weather = types.KeyboardButton('Хочу узнать погоду')
    nevermind = types.KeyboardButton('Просто мимо проходил')
    markup.add(weather, nevermind)
    bot.send_sticker(message.chat.id, random.choice(res.STICKERS3))
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Хочешь узнать погоду в твоём городе?',
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def reply(message):
    if message.text == 'Просто мимо проходил':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Назад'))
        bot.send_message(message.chat.id, 'Рад был повидаться!', reply_markup=markup)
    if message.text == 'Хочу узнать погоду':
        see_weather(message)
    if message.text == 'Город🌉':
        global city_flag
        city_flag = city_flag + 1
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        back = types.KeyboardButton('Назад')
        markup.add(back)
        bot.send_message(message.chat.id, "Напиши название населённого пункта", reply_markup=markup)
    if message.text == 'Назад':
        city_flag = 0
        see_weather(message)
    if city_flag != 0 and message.text != 'Город🌉':
        global search_flag
        search_flag += 1
        city_flag = 0
        bot.send_message(message.chat.id, 'Подождите, обрабатываю запрос')
        bot.send_sticker(message.chat.id, random.choice(res.STICKERS))
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get('https://yandex.ru/pogoda/?via=hl')
        statechecker1 = statechecker.StateChecker()
        statechecker1.state_check(f"{driver.current_url}")
        if statechecker1.state_check(f"{driver.current_url}") // 100 == 4 or statechecker1.state_check(
                f"{driver.current_url}") // 100 == 5:
            driver.close()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
            markup.add(types.KeyboardButton('Назад'))
            bot.send_message(message.chat.id, "Сервис временной недоступен", reply_markup=markup)
        search = driver.find_element_by_tag_name('input')
        search.send_keys(message.text)
        search.send_keys(Keys.ENTER)
        content = driver.page_source
        html = BS(content)
        zero_search = html.select('.content > h1')
        if len(zero_search) != 0:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
            markup.add(types.KeyboardButton('Назад'))
            bot.send_message(message.chat.id, zero_search[0].text, reply_markup=markup)
        if len(zero_search) == 0:
            global driverbuff
            driverbuff = []
            driverbuff = html.select('.place-list__item > .link')
            if message.text != driverbuff[0].text:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
                for el in driverbuff:
                    markup.add(types.KeyboardButton(f'{el.text}'))
                markup.add(types.KeyboardButton('Назад'))
                bot.send_message(message.chat.id, "Вот что удалось найти", reply_markup=markup)
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
                markup.add(types.KeyboardButton('Назад'))
                bot.send_message(message.chat.id, "Обработка...", reply_markup=markup)
            driver.close()
    if message.text != 'Просто мимо проходил' and message.text != 'Хочу узнать погоду' and message.text != 'Город🌉' \
            and city_flag == 0 and message.text != 'Назад' and search_flag == 0 and message.text != 'Да' and message.text != 'Нет' \
            and message.text != 'Факт дня⁉️' and message.text != 'Актуальные новости🌏':
        bot.send_message(message.chat.id, "Не торопи коней, я так тебя не пойму)")

    if len(driverbuff) != 0 and search_flag != 0:
        for city in driverbuff:
            if city.text == message.text:
                global mem
                mem = city
                if os.path.isfile(f"{message.text}.json"):
                    worker = jsonworker.JsonWorker()
                    data = worker.json_read(message)
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
                    yes = types.KeyboardButton("Да")
                    no = types.KeyboardButton("Нет")
                    markup.add(yes, no)
                    bot.send_message(message.chat.id, f"Запрос погоды в {message.text} уже был осуществлён в {data['time']} с результатом {data['weather']} "
                                                      f"Хотите получить актуальный прогноз?",reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, "Ваш прогноз почти готов")
                    bot.send_sticker(message.chat.id, random.choice(res.STICKERS))
                    tmp = str(datetime.datetime.now())
                    driver = webdriver.Chrome(ChromeDriverManager().install())
                    driver.get(f"https://yandex.ru{city['href']}")
                    content = driver.page_source
                    html = BS(content)
                    buff = html.select('.fact__temp-wrap > a')
                    degree = buff[0]['aria-label']
                    bot.send_message(message.chat.id, f'{degree}')
                    worker3 = jsonworker.JsonWorker()
                    json_message = worker3.json_data_organaizer(message.text, tmp, degree)
                    worker3.json_write(json_message, message)
                    search_flag = 0

    if message.text == "Нет" and search_flag != 0:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Назад'))
        bot.send_message(message.chat.id, "Как пожелаете", reply_markup=markup)
        search_flag = 0
    if message.text == 'Да' and search_flag != 0:
        bot.send_message(message.chat.id, "Ваш прогноз почти готов")
        bot.send_sticker(message.chat.id, random.choice(res.STICKERS))
        tmp = str(datetime.datetime.now())
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(f"https://yandex.ru{mem['href']}")
        content = driver.page_source
        html = BS(content)
        buff = html.select('.fact__temp-wrap > a')
        degree = buff[0]['aria-label']
        worker2 = jsonworker.JsonWorker()
        json_message = worker2.json_data_organaizer(mem.text, tmp, degree)
        worker2.json_clean(mem)
        worker2.json_write(json_message, mem)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Назад'))
        bot.send_message(message.chat.id, "Самая свежая информация получена:", reply_markup=markup)
        bot.send_message(message.chat.id, f'{degree}')
        search_flag = 0
    if message.text == 'Факт дня⁉️':
        r = requests.get('https://randstuff.ru/fact/fav/')
        html = BS(r.content, 'html.parser')
        fact = html.select('td')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Назад'))
        bot.send_message(message.chat.id, fact[0].text, reply_markup=markup)
        bot.send_sticker(message.chat.id, random.choice(res.STICKERS4))
    if message.text == 'Актуальные новости🌏':
        r = requests.get('https://www.rbc.ru/')
        html = BS(r.content, 'html.parser')
        news = html.select('.main__feed > a')
        markup = types.InlineKeyboardMarkup()
        for i in range(0, 7):
            elem = types.InlineKeyboardButton(f'{news[i].text.strip()}', url=f"{news[i]['href']}")
            markup.add(elem)
        bot.send_message(message.chat.id, "Актуальные новости:", reply_markup=markup)


@bot.message_handler(content_types=['location'])
def location(message):
    r = requests.get(f"https://yandex.ru/pogoda/?lat={message.location.latitude}&lon={message.location.longitude}")
    html = BS(r.content, 'html.parser')
    buff = html.select('.fact__temp-wrap > a')
    degree = buff[0]['aria-label']
    bot.send_message(message.chat.id, f'{degree}')


@bot.message_handler(content_types=['audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'contact'])
def cancel(message):
    bot.send_message(message.chat.id, "Я тебя не понимаю")
    bot.send_sticker(message.chat.id, random.choice(res.STICKERS2))


if __name__ == "__main__":
    bot.polling(none_stop=True)
