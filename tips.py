# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import logging
import redis
import random
import requests
from enum import Enum
import json
from flask_cors import CORS
import uuid

logging.basicConfig(level=logging.INFO)

session = requests.session()
redis_pool = redis.ConnectionPool(host='192.168.31.158')
r = redis.Redis(connection_pool=redis_pool)

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

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


@app.route('/jrebel', methods=['GET'])
def jrebel_code():
    return 'https://jrebel.hexianwei.com/' + str(uuid.uuid4())


@app.route('/img', methods=['GET'])
def random_img():
    type = request.args.get("type")
    result = ImageContext().factory(type).produce()
    if result:
        return jsonify(result.__dict__)
    else:
        return jsonify({"msg": "服务器错误"})


class ImageFactory():

    def produce(self):
        pass


class ImageContext():

    @staticmethod
    def factory(type):
        type = int(type)
        if not type or type == ImageSource.BI_YING.value[0]:
            return BiyingImage()
        if type == ImageSource.KEEP.value[0]:
            return KeepImage()
        if type == ImageSource.ZHI_HU.value[0]:
            return ZhihuImage()
        return ZhihuImage()


class BiyingImage(ImageFactory):

    def produce(self):
        url = biying_url.format(random.randint(0, 300))
        logging.info('url is {}: '.format(url))
        resp = session.get(url).json()
        img = resp['images'][0]
        url = 'https://cn.bing.com{}'.format(img['url'])
        msg = img['copyright']
        data = {
            'img': url,
            'content': msg,
        }
        r.sadd('biying', json.dumps(data))
        return ImageResp(url, msg, ImageSource.BI_YING.name)


class KeepImage(ImageFactory):

    def produce(self):
        content = r.srandmember('keep')
        data = json.loads(content)
        return ImageResp(data['img'], data['content'], ImageSource.KEEP.name)


class ZhihuImage(ImageFactory):

    def produce(self):
        content = r.srandmember('zhihu')
        if not content:
            return
        data = json.loads(content)
        return ImageResp(data['img'], data['content'], ImageSource.ZHI_HU.name)


class ImageSource(Enum):
    BI_YING = 0,
    ZHI_HU = 1,
    KEEP = 2,


class ImageResp():

    def __init__(self, url, msg, source):
        self.url = url if isinstance(url, list) else [url]
        self.msg = msg
        self.source = source


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=8700)
