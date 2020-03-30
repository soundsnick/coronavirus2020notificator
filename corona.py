#!/usr/bin/env python3

import sqlite3
import vk_api
from vk_api.longpoll import *
from pprint import pprint
from lxml import html
import requests

token = "e5db0fa484d58ede03d97771c9b1ea8aeecb6475aa739390fb1b005a0684e27b981fad7fd7b4267da3e3d"
vk = vk_api.VkApi(token=token)
conn = sqlite3.connect("corona.db")
cursor = conn.cursor()

def write_msg(message):
    try:
        for i in range(1, 15):
            try:
                vk.method('messages.send', {'chat_id': i, 'message': message, 'random_id': random()})
            except:
                pass
    except Exception as e:
        print(e)
        pass

def corona():
    url = 'http://coronavirus2020.kz'
    r = requests.get(url)
    tree = html.fromstring(r.text.encode('utf-8'))
    corona = {
        'all': int(tree.xpath('//span[@class="number_cov marg_med"]')[0].text),
        'healed': int(tree.xpath('//div[@class="recov_bl"]//span')[-1].text),
        'deaths': int(tree.xpath('//div[@class="deaths_bl"]//span')[-1].text)
    }
    data = cursor.execute('SELECT * FROM corona').fetchall()

    new = {}

    if len(data) == 0:
        cursor.execute('INSERT INTO `corona` VALUES ("all", {})'.format(corona['all']))
        cursor.execute('INSERT INTO `corona` VALUES ("healed", {})'.format(corona['healed']))
        cursor.execute('INSERT INTO `corona` VALUES ("deaths", {})'.format(corona['deaths']))
        conn.commit()
    else:
        for el in data:
            if el[1] != corona[el[0]]:
                new[el[0]] = abs(el[1] - corona[el[0]])
                query = 'UPDATE `corona` SET amount={} WHERE title="{}"'.format(corona[el[0]], el[0])
                cursor.execute(query)

    conn.commit()

    def keyToText(key, amount):
        res = {
            'all': 'Заразились еще {} человек.'.format(amount),
            'healed': 'Ура! Еще {} человек вылечилось!'.format(amount),
            'deaths': 'К сожалению, вирус забрал жизнь еще {} человек.'.format(amount)
        }
        return res[key]

    response = ""
    for el in new:
        response += keyToText(el, corona[el])+"\n"
    if len(response) > 5:
        response = "Новая информация по коронавирусу в Казахстане:\n" + response
        write_msg(response)
corona()
