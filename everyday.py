#!/usr/bin/env python3

import sqlite3
import vk_api
from random import *
from vk_api.longpoll import *
from pprint import pprint
from lxml import html
import requests
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
            # time.sleep(1)
    except Exception as e:
        print(e)
        pass

def corona():
    data = cursor.execute('SELECT * FROM corona').fetchall()
    new = {}
    response = """
        Сегодня
        __________
        Количество зараженных: {}
        Количество выздоровевших: {}
        Количество летальных случаев: {}
    """
    write_msg(response.format(data[0][1], data[1][1], data[2][1]))

corona()
