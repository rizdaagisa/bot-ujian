import requests
import pickle
import hashlib 
import secrets
import pandas as pd
from datetime import datetime
import re
# from data import npm,nama,kelas,key,admin_token,matkul,kode_matkul


# generated_key = secrets.token_urlsafe(16)
# generated_key.replace("-","")
# token = "14117220" + generated_key
# print(generated_key)
# print("token",token)

# password = npm+token
# result = hashlib.md5(password.encode())

# print("password",result.hexdigest())


base = "http://127.0.0.1:5000/"
base = "https://botumfinal.herokuapp.com/"

data = {
    "npm_user" : "14117220",
    "admin_token" : "PHBzPlMI2JdWVyrRzdbZg",
    "login_token" : "",
    "soal" : '"Do you know what she is going ?" He asked me if .......',
    "kode" : "KD021216"
}

data = {
    "npm" : "14117220",
    "token" : "PHBzPlMI2JdWVyrRzdbZg",
    "soal" : '"Do you know what she is going ?" He asked me if .......',
    "kode" : "KD021216"
}

result = requests.post(base+"kunci",json=data)
# data['login_token'] = "6MfR5pkGvHLp09YhTnA3lg"
# print(data)
# result = requests.post(base+"/kunci/",data=data)
# print(data2)
# result = requests.post(base+"/create_user/",data=data2)

print(result.json())