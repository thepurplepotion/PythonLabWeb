from flask import Flask
from flask import render_template

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, TextAreaField

from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired

from werkzeug.utils import secure_filename
import os

from flask import request
import numpy as np

import plotly.graph_objs as go

from flask import Response
import base64
from PIL import Image
from io import BytesIO
import json

import lxml.etree as ET

app = Flask(__name__)

@app.route("/")
def hello():
    return " <html><head></head> <body> <i><h1>Hello World!</h1></i> </body></html>"


@app.route("/data_to")
def data_to():
    some_pars = {'user':'Ivan','color':'red'}
    some_str = 'Hello my dear friends!'
    some_value = 10
    return render_template('simple.html', some_str=some_str, some_value=some_value, some_pars=some_pars)


# метод для обработки запроса от пользователя
@app.route("/apinet", methods=['GET', 'POST'])
def apinet():
    # проверяем что в запросе json данные
    #test
    neurodic = {}
    if request.mimetype == 'application/json':
        # получаем json данные
        data = request.get_json()
        # берем содержимое по ключу, где хранится файл
        # закодированный строкой base64
        # декодируем строку в массив байт используя кодировку utf-8
        # первые 128 байт ascii и utf-8 совпадают, потому можно
        filebytes = data['imagebin'].encode('utf-8')
        # декодируем массив байт base64 в исходный файл изображение
        cfile = base64.b64decode(filebytes)
        # чтобы считать изображение как файл из памяти используем BytesIO
        img = Image.open(BytesIO(cfile))
        decode = neuronet.getresult([img])
        for elem in decode:
            neurodic[elem[0][1]] = str(elem[0][2])
            print(elem)
        # пример сохранения переданного файла
        # handle = open('./static/f.png','wb')
        # handle.write(cfile)
        # handle.close()
    # преобразуем словарь в json строку
    ret = json.dumps(neurodic)
    # готовим ответ пользователю
    resp = Response(response=ret, status=200, mimetype="application/json")
    # возвращаем ответ
    return resp

@app.route("/apixml",methods=['GET', 'POST'])
def apixml():
    #парсим xml файл в dom
    dom = ET.parse("./static/xml/file.xml")
    #парсим шаблон в dom
    xslt = ET.parse("./static/xml/file.xslt")
    #получаем трансформер
    transform = ET.XSLT(xslt)
    #преобразуем xml с помощью трансформера xslt
    newhtml = transform(dom)
    #преобразуем из памяти dom в строку, возможно, понадобится указать кодировку
    strfile = ET.tostring(newhtml)

    return strfile

@app.route("/graph",methods=['GET', 'POST'])
def graph():
    # загрузить из json
    with open('./static/data.json', 'r') as file:  # открываем файл на чтение
        data = json.load(file)  # загружаем из файла данные в словарь data
    print(data)
    x = np.arange(len(data) / 2)
    y = np.arange(len(data) / 2)
    i = 0
    for index in data:
        if index == 'x' + str(i):
            x[i] = data.get(index)
        elif index == 'y' + str(i):
            y[i] = data.get(index)
        i = i + 1
        if i == len(data) / 2:
            i = 0
    print(x)
    print(y)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y))
    fig.show()
    return "<html><head></head> <body> <i><h1>Graph</h1></i> </body></html>"


# используем капчу и полученные секретные ключи с сайта google
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcrEfoUAAAAAEUT-G_eQNnVjvfzRLHRKyOKTS5I'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcrEfoUAAAAAHrgRuynjStzi9hWbL1s2LgpMxGY'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

# создаем форму для загрузки файла
class NetForm(FlaskForm):
    openid = StringField('openid', validators = [DataRequired()])
    upload = FileField('Load image', validators=[
    FileRequired(),
    FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    recaptcha = RecaptchaField()
    submit = SubmitField('send')
# функция обработки запросов на адрес 127.0.0.1:5000/net
# модуль проверки и преобразование имени файла
# для устранения в имени символов типа / и т.д.

# подключаем наш модуль и переименовываем
# для исключения конфликта имен


import net as neuronet


# метод обработки запроса GET и POST от клиента
@app.route("/net",methods=['GET', 'POST'])
def net():
    form = NetForm()
    # обнуляем переменные передаваемые в форму
    filename=None
    neurodic = {}
    # проверяем нажатие сабмит и валидацию введенных данных
    if form.validate_on_submit():
    # файлы с изображениями читаются из каталога static
        filename = os.path.join('./static', secure_filename(form.upload.data.filename))
        fcount, fimage = neuronet.read_image_files(10,'./static')
        # передаем все изображения в каталоге на классификацию
        # можете изменить немного код и передать только загруженный файл
        decode = neuronet.getresult(fimage)
        # записываем в словарь данные классификации
        for elem in decode:
            neurodic[elem[0][1]] = elem[0][2]
            # сохраняем загруженный файл
            form.upload.data.save(filename)
            # передаем форму в шаблон, так же передаем имя файла и результат работы нейронной
            # сети если был нажат сабмит, либо передадим falsy значения
    return render_template('net.html',form=form,image_name=filename,neurodic=neurodic)

#wtf.quick_form(form, method='post', enctype="multipart/form-data", action="net")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)