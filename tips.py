# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import json
import redis
import random
import requests

session = requests.session()
redis_pool = redis.ConnectionPool()
r = redis.Redis(connection_pool=redis_pool)

app = Flask(__name__)

path = 'daily_tips.csv'


def get_length():
    count = 0
    with open(path, 'r') as f:
        for line in f.readlines():
            count = count + 1
    return count


key = 'daily_tips'
key_len = 'daily_tips_len'

biying_url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx={}&n=1'

@app.route('/tips', methods=['GET'])
def daily_tips():
    length = r.get(key_len)
    if not length:
        length = get_length()
        r.set(key_len, length, 1 * 3600)
    length = int(length)
    index = random.randint(0, length - 1)
    return r.hget(key, index)


@app.route('/cron', methods=['GET'])
def daily_cron():
    index = 0
    with open(path, 'r') as f:
        for line in f.readlines():
            r.hset(key, index, line.strip())
            index = index + 1
    r.set(key_len, index - 1)
    return jsonify({'status': 'success'})


@app.route('/img', methods=['GET'])
def random_img():
    base_url = session.get(biying_url.format(random.randint(0, 10000))).json()['images'][0]['url']
    return 'https://cn.bing.com{}'.format(base_url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=8700)
