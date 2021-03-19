from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
import pandas as pd
import csv
import hashlib 
import pypyodbc
import secrets
from datetime import datetime
import re,os

app = Flask(__name__)
api = Api(app)

def create_database():
    df = pd.DataFrame({'nama': ['M Rizdalah'],
                    'npm': ['14117220'],
                    'kelas': ['4ka13'],
                    'password': ['f896031dff851757eae67b65c87eadb1'],
                    'token': ['Ai-fleFLxiclFFRgr-vklA']
                    })
    df.to_csv('database_um.csv',index=False)

def create_user(nama,kelas,npm):
    with open(r'DB_admin.csv', 'a', newline='') as csvfile:
        generated_key = secrets.token_urlsafe(16)
        token = generated_key.replace("-","").replace("_","")
        password = hashlib.md5((str(npm)+token).encode()).hexdigest()
        fieldnames = ['nama','npm', 'kelas', 'password','user_token','credit']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'nama': nama,
                        'npm': npm,
                        'kelas': kelas,
                        'password': password,
                        'user_token': token,
                        'credit': 1,
                    })
        return {"npm":npm,"user_token" : token, "status": "sukses"}

def read_data(npm,admin_token):
    df = pd.read_csv("DB_admin.csv")
    # try:
    password = df.loc[df["npm"]  == npm]['password'][0]
    # password = (df['password'].where(df['npm'] == npm))[0]
    # token = (df['token'].where(df['npm'] == npm))[0]
    credit = df.loc[df["npm"]  == npm]['credit'][0]
    print("credit",credit)
    cek = str(npm)+admin_token
    valid = hashlib.md5(cek.encode()).hexdigest()
    print(valid,password)
    if valid == password:
        print(valid,password,credit)
        return True,credit
    else:
        return False,credit
    # except:
    #     return False,0

def cek_user(npm_user,login_token):
    df = pd.read_csv("DB_user.csv")
    login_token_user = df.loc[df["npm_user"]  == npm_user]['login_token'][0]
    if login_token == login_token_user:
        print(login_token,login_token_user)
        return True
    else:
        return False

def kuncijawaban(soal,kode):
    dbq = "Dbq=D:/rizda/note/api-botum/" + kode + ".mdb;"
    conn = pypyodbc.connect(
    r"Driver={MICROSOFT ACCESS DRIVER (*.mdb)};" + dbq)
    cur = conn.cursor()
    print(soal)
    # soal.replace('"','')
    if ('"' in soal):
        starind = soal.find('\"')
        endind= soal.find('\"',starind+1)
        # print(starind,endind)
        soal1= soal[starind+1:endind]

        try:
            soal2= re.findall('"(.*?)"', soal)[0]
        except:
            soal2= ""
        soal3=  soal[endind+2:]
        # print(soal1)
        # print(soal2)
        # print(soal3)
        query = "SELECT soal,A,B,C,D,kunci FROM " + kode + " WHERE soal like '%" + soal1 + "%'" + "and soal like '%" + soal2 +"%'" + "and soal like '%" + soal3 +"%'"
    else:
        query = "SELECT soal,A,B,C,D,kunci FROM " + kode + " WHERE soal like '%" + soal + "%'"
    
    try:
        cur.tables()
        cur.execute(query)
        rows = cur.fetchall()
        print(rows)
        kunci = rows[0]['kunci']
        if rows[0][kunci] == None:
            jawaban = rows[0][kunci.lower()]
            # print(jawaban)
        else:
            jawaban = rows[0][kunci]
        return (jawaban)
    except:
        return ("Pass / Tidak menjawab")

def history(npm):
    df = pd.read_csv("DB_user.csv")

def update_data():
    filename = 'DB_user.csv'
    tempfile = NamedTemporaryFile(mode='w', delete=False)

    fields = ['npm_admin','npm_user','nama_user','kelas_user','user_token', 'login_token','kode_matkul','matkul','status','nilai','tanggal']

    with open(filename, 'r') as csvfile, tempfile:
        reader = csv.DictReader(csvfile, fieldnames=fields)
        writer = csv.DictWriter(tempfile, fieldnames=fields)
        for row in reader:
            if row['ID'] == str(stud_ID):
                print('updating row', row['ID'])
                row['Name'], row['Course'], row['Year'] = stud_name, stud_course, stud_year
            row = {'ID': row['ID'], 'Name': row['Name'], 'Course': row['Course'], 'Year': row['Year']}
            writer.writerow(row)

args_kunci = reqparse.RequestParser()
class KUNCI(Resource):
    def post(self):
        args_kunci.add_argument("kode", type=str, help="kode required",required=True)
        args_kunci.add_argument("soal", type=str, help="soal required",required=True)
        args_kunci.add_argument("npm_user", type=int, help="npm required" ,required=True)
        args_kunci.add_argument("login_token", type=str, help="login_token required", required=True)
        args_kunci.add_argument("admin_token", type=str, help="admin_token required", required=True)
        result = args_kunci.parse_args()
        login_token = result['login_token']
        npm = result['npm_user']
        validate_token = cek_user(npm,login_token)
        if(validate_token):
            result['login'],credit = read_data(int(npm),result['admin_token'])
            if result['login'] == True:
                if credit > 0:
                    jawaban = kuncijawaban(result['soal'],result['kode'])
                    print("jawaban",jawaban)
                    result['jawaban'] = jawaban
                    return result
                else:
                    return {'Note' : 'Silakan melakukan topup credit untuk bisa menggunakan layanan ini, hubungi instagram @jokiambis'}
            else:
                return {'Note' : 'User tidak valid, silakan lakukan pembelian token di instagram @jokiambis'}
        else:
            return {'Note' : 'Token login tidak valid'}    

args = reqparse.RequestParser()
class USER(Resource):
    def post(self):
        args.add_argument("npm", type=int, help="npm",required=True)
        args.add_argument("nama", type=str, help="nama",required=True)
        args.add_argument("kelas", type=str, help="kelas",required=True)
        result = args.parse_args()
        npm = result['npm']
        nama = result['nama']
        kelas = result['kelas']
        df = pd.read_csv("DB_admin.csv")
        np = df.loc[df['npm'] == npm]['npm']
        print(npm)
        if(np.empty):
            data = create_user(nama,kelas,npm)
            return data
        else:
            return {'Note' : 'User sudah ada didalam database'}

args_login= reqparse.RequestParser()
class LOGIN(Resource):
    def post(self):
        args_login.add_argument("npm_admin", type=int, help="parameter npm admin required",required=True)
        args_login.add_argument("admin_token", type=str, help="parameter admin_token required",required=True)

        args_login.add_argument("npm_user", type=int, help="parameter npm_user required",required=True)
        args_login.add_argument("nama_user", type=str, help="parameter matkul required",required=True)
        args_login.add_argument("kelas_user", type=str, help="parameter matkul required",required=True)
        args_login.add_argument("kode_matkul", type=str, help="parameter matkul required",required=True)
        args_login.add_argument("matkul", type=str, help="parameter matkul required",required=True)
        result = args_login.parse_args()

        npm_admin = result['npm_admin']
        admin_token = result['admin_token']
        npm = result['npm_user']
        nama = result['nama_user']
        kelas = result['kelas_user']
        kode_matkul = result['kode_matkul']
        matkul = result['matkul']
        tanggal= datetime.now().strftime("%d %B %Y : %H.%M")

        generated_key = secrets.token_urlsafe(16)
        login_token = generated_key.replace("-","").replace("_","")

        result['login'],credit = read_data(int(npm_admin),admin_token)
        if result['login'] == True:
            if credit > 0:
                credit -= 1
                fieldnames = ['npm_admin','npm_user','nama_user','kelas_user','kode_matkul','matkul','login_token','tanggal']
                with open(r'DB_user.csv', 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'npm_admin':npm_admin,'npm_user':npm,'nama_user':nama,'kelas_user':kelas, 'kode_matkul':kode_matkul,'matkul':matkul,'login_token':login_token,'tanggal':tanggal})

                df = pd.read_csv("DB_admin.csv")
                # credit = df.loc[df["npm"]  == npm_admin]['credit'][0]
                df.loc[(df["npm"]  == npm_admin),'credit'] = credit
                df.to_csv('DB_admin.csv', index = False)
                return {"npm_user":npm,"login_token" : login_token, "status": "sukses", "credit" : str(credit)}
            else:
                return {'Note' : 'Credit anda sudah habis, Silakan melakukan topup untuk bisa menggunakan layanan ini, hubungi instagram @jokiambis'}
        else:
            return {'Note' : 'User tidak valid, silakan daftar untuk menggunakan layanan ini, hubungi instagram @jokiambis'}
    
    def get(self):
        return {'note': 'get method not allowed'}

args_index = reqparse.RequestParser()
class INDEX(Resource):
    def get(self):
        return {'note': 'get method not allowed'}

api.add_resource(INDEX,"/")    
api.add_resource(USER,"/create_user/")
api.add_resource(LOGIN,"/login/")
api.add_resource(KUNCI,"/kunci/")


if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host="0.0.0.0", port=port)
    app.run(debug=True)
