#coding: utf-8

import time
import os
import re

import requests
from lxml import etree

from aip import AipFace

#百度云 人脸检测 申请信息
#唯一必须填的信息就这三行
APP_ID = "15528557"
API_KEY = "0lWqcU5h1MrGzvbnUYXp1vSF"
SECRET_KEY = "UYknUWhFGqk8YvCzbhD1Wv9e8gza2zuX"

# 文件存放目录名，相对于当前目录
DIR = "image3"
# 过滤颜值阈值，存储空间大的请随意
BEAUTY_THRESHOLD = 70

#浏览器中打开知乎，在开发者工具复制一个，无需登录
#如何替换该值下文有讲述
AUTHORIZATION = "oauth c3cef7c66a1843f8b3a9e6a1e3160e20"

#以下皆无需改动

#每次请求知乎的讨论列表长度，不建议设定太长，注意节操
LIMIT = 5

#这是话题『美女』的 ID，其是『颜值』（20013528）的父话题
SOURCE = "19552207"

#爬虫假装下正常浏览器请求
USER_AGENT = "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.5 Safari/534.55.3"
#爬虫假装下正常浏览器请求
REFERER = "https://www.zhihu.com/topic/%s/newest" % SOURCE
#某话题下讨论列表请求 url
BASE_URL = "https://www.zhihu.com/api/v4/topics/%s/feeds/timeline_activity"
#初始请求 url 附带的请求参数
URL_QUERY = "?include=data%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Danswer%29%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Danswer%29%5D.target.is_normal%2Ccomment_count%2Cvoteup_count%2Ccontent%2Crelevant_info%2Cexcerpt.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Darticle%29%5D.target.content%2Cvoteup_count%2Ccomment_count%2Cvoting%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Dpeople%29%5D.target.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Danswer%29%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Danswer%29%5D.target.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Darticle%29%5D.target.content%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dquestion%29%5D.target.comment_count&limit=" + str(LIMIT)

#指定 url，获取对应原始内容 / 图片
def fetch_image(url):
    try:
        headers = {
                "User-Agent": USER_AGENT,
                "Referer": REFERER,
                "authorization": AUTHORIZATION
                }
        s = requests.get(url, headers=headers)
    except Exception as e:
        print("fetch last activities fail. " + url)
        raise e

    return s.content

#指定 url，获取对应 JSON 返回 / 话题列表
def fetch_activities(url):
    try:
        headers = {
                "User-Agent": USER_AGENT,
                "Referer": REFERER,
                "authorization": AUTHORIZATION
                }
        s = requests.get(url, headers=headers)
    except Exception as e:
        print("fetch last activities fail. " + url)
        raise e

    return s.json()

#处理返回的话题列表
def process_activities(datums, face_detective):
    for data in datums["data"]:

        target = data["target"]
        if "content" not in target or "question" not in target or "author" not in target:
            continue

        #解析列表中每一个元素的内容
        html = etree.HTML(target["content"])

        seq = 0

        #question_url = target["question"]["url"]
        question_title = target["question"]["title"]

        author_name = target["author"]["name"]
        #author_id = target["author"]["url_token"]

        print("current answer: " + question_title + " author: " + author_name)

        #获取所有图片地址
        images = html.xpath("//img/@src")
        for image in images:
            if not image.startswith("http"):
                continue
            s = fetch_image(image)
            
            #请求人脸检测服务
            scores = face_detective(s)

            for score in scores:
                filename = ("%d--" % score) + author_name + "--" + question_title + ("--%d" % seq) + ".jpg"
                filename = re.sub(r'(?u)[^-\w.]', '_', filename)
                #注意文件名的处理，不同平台的非法字符不一样，这里只做了简单处理，特别是 author_name / question_title 中的内容
                seq = seq + 1
                with open(os.path.join(DIR, filename), "wb") as fd:
                    fd.write(s)

            #人脸检测 免费，但有 QPS 限制
            time.sleep(2)

    if not datums["paging"]["is_end"]:
        #获取后续讨论列表的请求 url
        return datums["paging"]["next"]
    else:
        return None

def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '_', s)

import base64
def detect_face(image, token):
    try:
        URL = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        params = {
                "access_token": token
                }
        data = {
                "face_field": "age,gender,beauty,qualities",
                "image_type": "BASE64",
                "image": base64.b64encode(image)
                }
        s = requests.post(URL, params=params, data=data)
        return s.json()["result"]
    except Exception as e:
        print("detect face fail. " + url)
        raise e

def fetch_auth_token(api_key, secret_key):
    try:
        URL = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
                "grant_type": "client_credentials",
                "client_id": api_key,
                "client_secret": secret_key
                }
        s = requests.post(URL, params=params)
        return s.json()["access_token"]
    except Exception as e:
        print("fetch baidu auth token fail. " + url)
        raise e

def init_face_detective(app_id, api_key, secret_key):
    # client = AipFace(app_id, api_key, secret_key)
    # 百度云 V3 版本接口，需要先获取 access token   
    token = fetch_auth_token(api_key, secret_key)
    def detective(image):
        #r = client.detect(image, options)
        # 直接使用 HTTP 请求
        r = detect_face(image, token)
        #如果没有检测到人脸
        if r is None or r["face_num"] == 0:
            return []
        scores = []
        for face in r["face_list"]:
            #人脸置信度太低
            if face["face_probability"] < 0.6:
                continue
            #颜值低于阈值
            if face["beauty"] < BEAUTY_THRESHOLD:
                continue
            #性别非女性
            if face["gender"]["type"] != "female":
                continue
            scores.append(face["beauty"])

        return scores

    return detective

def init_env():
    if not os.path.exists(DIR):
        os.makedirs(DIR)

init_env()
face_detective = init_face_detective(APP_ID, API_KEY, SECRET_KEY)

url = BASE_URL % SOURCE + URL_QUERY
while url is not None:
    #print("current url: " + url)
    datums = fetch_activities(url)
    url = process_activities(datums, face_detective)
    #注意节操，爬虫休息间隔不要调小
    time.sleep(5)