from itertools import repeat
from os import path
from flask import Flask, json, jsonify
from flask_restx import Api, Resource, reqparse
from flask import session 
import pymysql
from werkzeug.wrappers import response
from db import create_db
from utils import upload_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True) # 다른 포트번호에 대한 보안 제거
api = Api(app)


user_ns = api.namespace('user',description = '사용자 계정 API')
image_ns = api.namespace('satellite',description = '위성 영상 데이터 API')


#imageNum, userid, keyword, shootingtime, shootingperiod, title, color, font, url
join_parser = reqparse.RequestParser()
login_parser = reqparse.RequestParser()
image_parser = reqparse.RequestParser()
save_parser = reqparse.RequestParser()
delete_parser = reqparse.RequestParser()

# 회원가입 
@user_ns.route("/api/join")
class user_join(Resource):
    join_parser.add_argument('id', type=str, help='사용자 아이디')
    join_parser.add_argument('password', type=str, help='사용자 비밀번호')
    join_parser.add_argument('name', type=str, help='사용자 이름')

    @user_ns.expect(join_parser)
    def post(self):
        args = join_parser.parse_args()
        input_id = args['id']
        input_pw = args['password']
        input_name = args['name']
        
        db = conn_db()
        cursor= db.cursor(pymysql.cursors.DictCursor)
        sql= "SELECT userId FROM user WHERE userId = %s;"
        cursor.execute(sql,input_id)
        check = cursor.fetchall()

        for row in check:
            check = row['userId']
        
        if check:
            db.close()
            data = {
                "status": 409,
                "success":False,
                "message": "아이디 중복"
            }
            return jsonify(data)
        else:
            sql="INSERT INTO user (userId,userPw,name) values (%s,%s,%s)"
            cursor.execute(sql,(input_id,input_pw,input_name))
            db.commit()
            db.close()
            data = {
                "status": 201,
                "success":True,
                "message": "회원가입 성공"
            }
            return jsonify(data)
            


# 로그인 
@user_ns.route("/api/login")
class user_login(Resource):
    login_parser.add_argument('id', type=str, help='사용자 아이디')
    login_parser.add_argument('password', type=str, help='사용자 비밀번호')

    @user_ns.expect(login_parser)
    def post(self):
        args = join_parser.parse_args()
        input_id = args['id']
        input_pw = args['password']

        db = conn_db()
        cursor= db.cursor(pymysql.cursors.DictCursor)
        sql= "SELECT name FROM user WHERE userId = %s and userPw = %s;"
        cursor.execute(sql,(input_id,input_pw))
        check = cursor.fetchall()

        for row in check:
            name = row['name']

        db.close()
        if check: # 로그인 성공 
            session['userId'] = input_id 
            data = {
                "status": 201,
                "success":True,
                "name": name,
                "message": "로그인 성공"
            }
            return jsonify(data)
        else: # 로그인 실패
            data = {
                "status": 401,
                "success":True,
                "message": "로그인 실패"
            }
            return jsonify(data)

# 로그아웃 
@user_ns.route("/api/logout")
class logout(Resource):
    def get(self):
        session.pop('userId',None)
        data = {
            "status": 200,
            "success":True,
            "message": "로그아웃 성공"
        }
        return jsonify(data)
        
# 위성 영상 생성 및 조회 
# keyword, shooting period, shooting time, title, font, latitude font, longitude font 
@image_ns.route("/api/createImage")
class create_image(Resource):
    image_parser.add_argument("keyword")
    image_parser.add_argument("shooting_period")
    image_parser.add_argument("shooting_time")
    image_parser.add_argument("title")
    image_parser.add_argument("font")
    image_parser.add_argument("latitude_font")
    image_parser.add_argument("longitude_font")
    
    @image_ns.expect(image_parser)
    def post(self):
        args = image_parser.parse_args()
        keyword = args["keyword"]
        shooting_period = args["shooting_period"]
        shooting_time = args["shooting_time"]
        title = args["title"]
        font = args["font"]
        latitude_font = args["latitude_font"]
        longitude_font = args["longitude_font"]
        
        # console print 
        print(keyword, shooting_period, shooting_time, title)

        # TODO
        # main.py 실행하는 코드 넣기
        # os.system("python ./map_generator/main.py **argvs") 형식으로 작성

        url = upload_file("apple.jpeg") ## 예성이가 파일경로 줘야함
        data = {
            "status": 200,
            "success": True,
            "url": url,
            "message": "url_list"
        }
        return jsonify(data)

# 전시 영상 페이지에서 저장버튼 클릭한 경우
@image_ns.route("/api/saveImage")
class save_image(Resource):

    save_parser.add_argument("url")
    save_parser.add_argument("title")
    save_parser.add_argument("shootingperiod")
    save_parser.add_argument("shootingtime")
    save_parser.add_argument("keyword")

    @image_ns.expect(save_parser)
    #(userid(fk), url), title, shootingperiod, shootingtime,keyword
    def post(self):
        args = save_parser.parse_args()
        id = session['userId']
        url = args["url"]
        title = args["title"]
        shootingperiod = args["shootingperiod"]
        shootingtime = args["shootingtime"]
        keyword = args["keyword"]

        print(id,url,keyword)
        db = conn_db()
        cursor= db.cursor(pymysql.cursors.DictCursor)
        sql= "INSERT INTO image(userId,url,title,shootingPeriod,shootingTime,keyword) VALUES(%s,%s,%s,%s,%s,%s);"
        cursor.execute(sql,(id,url,title,shootingperiod,shootingtime,keyword))
        db.commit()
        db.close()

        #url = ???
        data = {
            "status": 200,
            "success":True,
            "message": "success"
        }
        return jsonify(data)

# 갤러리 삭제
@image_ns.route("/api/deleteImage")
class delete_image(Resource):
    delete_parser.add_argument('url')

    @image_ns.expect(delete_parser)
    def delete(self):
        args = delete_parser.parse_args()
        id = session['userId']
        url = args["url"]

        db = conn_db()
        cursor= db.cursor(pymysql.cursors.DictCursor)
        sql= "DELETE FROM image WHERE userId=%s AND url=%s;"
        cursor.execute(sql,(id,url))
        db.commit()
        db.close()

        data = {
            "status": 200,
            "success":True,
            "message": "success delete image"
        }
        return jsonify(data)


# 갤러리 조회
@image_ns.route("/api/showGallery")
class save_image(Resource):

    #(userid(fk), url), title, shootingperiod, shootingtime,keyword
    def get(self):
        db = conn_db()
        cursor= db.cursor(pymysql.cursors.DictCursor)
        sql= "SELECT url,title,shootingperiod,shootingtime,keyword FROM image WHERE userId = %s"
        cursor.execute(sql,(session['userId']))
        check = json.dumps(cursor.fetchall())
        db.close()

        data = {
            "status": 200,
                "success":True,
                "result": check,
                "message": "success"
        }
        return jsonify(data)


def conn_db():
    db = pymysql.connect(host='localhost',
                        port=3306,
                        user='root',
                        passwd='3412',
                        db='satellite',
                        charset='utf8')
    return db


if __name__ == '__main__':
    create_db()
    # secret_key 생성해야 세션 생성 가능 
    app.config['SESSION_TYPE'] = 'memcached'
    app.secret_key = 'my super secret key'.encode('utf8')
    app.run()