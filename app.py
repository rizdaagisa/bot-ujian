from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
import pandas as pd
import csv
import hashlib
import secrets
from datetime import datetime
import re,os,sys
import shutil

from odb import pypyodbc

# file_path = "odbc"
# sys.path.append(os.path.dirname(file_path))

# https://stackoverflow.com/questions/51122790/install-odbc-driver-heroku
# https://elements.heroku.com/buildpacks/matt-bertoncello/python-pyodbc-buildpack
# https://github.com/matt-bertoncello/python-pyodbc-buildpack

app = Flask(__name__)
path = os.path.dirname(__file__)
# print(path)
# path = path.replace("\\","/")
# os.path.join(path + "/" + "odbc/")
path1= path+"/.apt/usr/lib/odbc/"
path2= path+"/.apt/usr/lib/x86_64-linux-gnu/"
a= os.listdir(path)
print("before",a)
shutil.move(path2+"libodbc.so", path)
b= os.listdir(path)
c = os.listdir(path1)
d = os.listdir(path2)
# h = path + "/odbc/"
print("after",b)
# sys.path.append(path + "/odbc/")

# os.environ['LD_LIBRARY_PATH'] = os.getcwd()



def create_user(nama,kelas,npm):
    try:
        with open(r'DB_admin.csv', 'a', newline='') as csvfile:
            generated_key = secrets.token_urlsafe(16)
            token = generated_key.replace("-","").replace("_","")
            password = hashlib.md5((str(npm)+token).encode()).hexdigest()
            fieldnames = ['nama','npm', 'kelas', 'password','token']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'nama': nama,
                            'npm': npm,
                            'kelas': kelas,
                            'password': password,
                            'token': token
                        })
            return {"npm":npm,"user_token" : token, "status": "sukses"}
    except:
        return {'status' : 'failed create user'}

def cek_user(npm,token):
    df = pd.read_csv("DB_admin.csv")
    # try:
    password = df.loc[df["npm"]  == npm]['password'][0]
    # password = (df['password'].where(df['npm'] == npm))[0]
    # token = (df['token'].where(df['npm'] == npm))[0]
    # credit = df.loc[df["npm"]  == npm]['credit'][0]
    # print("credit",credit)
    cek = str(npm)+token
    valid = hashlib.md5(cek.encode()).hexdigest()
    if valid == password:
        return True
    else:
        return False

def kuncijawaban(soal,kode):
    # dbq = "Dbq=D:/rizda/note/api-botum/" + kode + ".mdb;"
    dbq = "Dbq="+path+"/" + kode + ".mdb;"
    dbq = "Dbq=" + kode + ".mdb;"
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
        else:
            jawaban = rows[0][kunci]
        return (jawaban)
    except:
        return ("Pass / Tidak menjawab")

@app.route('/',methods=['GET'])
def index():
    return 'Upss mau iseng ya? Silakan hubungi admin untuk membeli program bot UM'

@app.route('/create_user',methods=['POST'])
def user():
    result = request.get_json()
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
        return {'status' : 'User sudah ada didalam database'}


@app.route('/kunci',methods=['POST'])
def kunci():
    result = request.get_json()
    npm = result['npm']
    kode = result['kode']
    soal = result['soal']
    token = result['token']
    password = cek_user(int(npm),token)
    if password == True:
        jawaban = kuncijawaban(soal,kode)
        return {'jawaban' : jawaban}
    else:
        return {'status' : 'User tidak valid, silakan lakukan pembelian token di instagram @jokiambis'}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    # app.run(debug=True)