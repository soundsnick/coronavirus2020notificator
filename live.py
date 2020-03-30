#!/usr/bin/env python3

import sqlite3
import vk_api
from random import *
from vk_api.longpoll import *
from pprint import pprint
from lxml import html
import requests
import re
import time

token = "e5db0fa484d58ede03d97771c9b1ea8aeecb6475aa739390fb1b005a0684e27b981fad7fd7b4267da3e3d"
vk = vk_api.VkApi(token=token)
conn = sqlite3.connect("corona.db")
cursor = conn.cursor()

def write_msg(message):
    try:
        for i in range(1, 25):
            try:
                vk.method('messages.send', {'chat_id': i, 'message': message, 'random_id': random()})
            except Exception as e:
                print(e)
            time.sleep(1)
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
        'deaths': int(tree.xpath('//div[@class="deaths_bl"]//span')[-1].text),
        'all_cities': list(map(lambda x: [s for s in x.text.split() if s.isdigit()][0], tree.xpath('//div[@class="city_cov"]')[0].xpath('div'))),
        'healed_cities': list(map(lambda x: [s for s in x.text.split() if s.isdigit()][0], tree.xpath('//div[@class="city_cov"]')[1].xpath('div'))),
    }

    data = cursor.execute('SELECT * FROM corona').fetchall()

    new = {}

    if len(data) == 0:
        cursor.execute('INSERT INTO `corona` VALUES ("all", "{}")'.format(corona['all']))
        cursor.execute('INSERT INTO `corona` VALUES ("healed", "{}")'.format(corona['healed']))
        cursor.execute('INSERT INTO `corona` VALUES ("deaths", "{}")'.format(corona['deaths']))
        cursor.execute('INSERT INTO `corona` VALUES ("all_cities", "{}")'.format(','.join(corona['all_cities'])))
        cursor.execute('INSERT INTO `corona` VALUES ("healed_cities", "{}")'.format(','.join(corona['healed_cities'])))
        conn.commit()
    else:
        for el in data:
            if len(str(el[1]).split(',')) == 1:
                if int(el[1]) != corona[el[0]]:
                    new[el[0]] = corona[el[0]] - int(el[1])
                    query = 'UPDATE `corona` SET amount="{}" WHERE title="{}"'.format(corona[el[0]], el[0])
                    cursor.execute(query)
            else:
                cities = el[1].split(',')
                new_cities = []
                for ci in range(len(cities)):
                    if cities[ci] != corona[el[0]][ci]:
                        new_cities.append(int(corona[el[0]][ci]) - int(cities[ci]))
                    else:
                        new_cities.append(0)
                query = 'UPDATE `corona` SET amount="{}" WHERE title="{}"'.format(','.join(corona[el[0]]), el[0])
                if len(new_cities) != 0 and sum(new_cities) != 0:
                    new[el[0]] = new_cities
                cursor.execute(query)

    conn.commit()

    def keyToText(key, amount, all=None):
        res = {
            'all': 'Число зараженных {} человек. ({}{})'.format(all, '+' if (amount>0) else '-', abs(amount)),
            'healed': 'Ура! Еще {} человек вылечилось! Количество вылеченных: {}'.format(abs(amount), all),
            'deaths': 'К сожалению, вирус забрал жизнь еще {} человек. Количество умерших: {}'.format(abs(amount), all)
        }
        return res[key]

    def cityToText(key, i):
        res = ""
        if key == 'all_cities':
            city = re.findall(r'^.*?(?=\s*–)', tree.xpath('//div[@class="city_cov"]')[0].xpath('div')[i].text)[0]
            res = "{}: {} ({}{})".format(city, corona[key][i], '+' if (new[key][i]>0) else '-', str(abs(new[key][i])))
        elif key == 'healed_cities':
            city = re.findall(r'^.*?(?=\s*–)', tree.xpath('//div[@class="city_cov"]')[1].xpath('div')[i].text)[0]
            res = "{}: {} ({}{})".format(city, corona[key][i], '+' if (new[key][i]>0) else '-', str(abs(new[key][i])))
        return res

    response = ""
    for el in new:
        if el in ['all', 'healed', 'deaths']:
            response += keyToText(el, new[el], corona[el])+"\n"
            if el == 'all' and new['all_cities'] != None:
                for ci in range(len(new['all_cities'])):
                    if new['all_cities'][ci] != 0:
                        response += cityToText('all_cities', ci)+"\n"

            elif el == 'healed' and new['healed_cities'] != None:
                for ci in range(len(new['healed_cities'])):
                    if new['healed_cities'][ci] != 0:
                        response += cityToText('healed_cities', ci)+"\n"
    if len(response) > 5:
        response = "Новая информация по коронавирусу в Казахстане:\n" + response
        write_msg(response)
corona()
