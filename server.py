# -*- coding: iso-8859-15 -*-


from flask import Flask, request, render_template, session, redirect, url_for
import os.path
from os import listdir
import json
from time import time
import sys
app = Flask(__name__)
SITE_ROOT = "/"


def load_user(email, passwd):
    """
    Carga datos usuario (identified by email) del directorio data.
    Busca un archivo de nombre el email del usuario
    :param email: user id
    :param passwd: password 
    :return: pagina home si existe el usuario y es correcto el pass
    """
    file_path = os.path.join(SITE_ROOT, "data/", email)
    if not os.path.isfile(file_path):
        return process_error("User not found / No existe un usuario con ese nombre", url_for("login"))
    with open(file_path, 'r') as f:
        data = json.load(f)
    if data['password'] != passwd:
        return process_error("Incorrect password / la clave no es correcta", url_for("login"))
    session['user_name'] = data['user_name']
    session['messages'] = data['messages']
    session['password'] = passwd
    session['email'] = email
    session['friends'] = data['friends']
    return redirect(url_for("home"))

def save_current_user():
    datos = {
        "user_name": session["user_name"],
        "password": session['password'],
        "messages": session['messages'], # lista de tuplas (time_stamp, mensaje)
        "email": session['email'],
        "friends": session['friends']
    }
    file_path = os.path.join(SITE_ROOT, "data/", session['email'])
    with open(file_path, 'w') as f:
        json.dump(datos, f)
    

def create_user_file(name, email, passwd, passwd_confirmation):
    """
    Crea el fichero (en directorio /data). El nombre será el email.
    Si el fichero ya existe, error.
    Si no coincide el pass con la confirmación, error.
    :param name: Nombre o apodo del usuario
    :param email: correo
    :param passwd: password 
    :param passwd_confirmation: debe coincidir con pass
    :return: Si no hay errores, dirección al usuario a home.
    """

    directory = os.path.join(SITE_ROOT, "data")
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(SITE_ROOT, "data/", email)
    if os.path.isfile(file_path):
        return process_error("The email is already used, you must select a different email / Ya existe un usuario con ese nombre", url_for("signup"))
    if passwd != passwd_confirmation:
        return process_error("Your password and confirmation password do not match / Las claves no coinciden", url_for("signup"))
    datos = {
        "user_name": name,
        "password": passwd,
        "messages": [],
        "friends": []
    }
    with open(file_path, 'w') as f:
        json.dump(datos, f)
    session['user_name'] = name
    session['password'] = passwd
    session['messages'] = []
    session['friends'] = []
    session['email'] = email
    return redirect(url_for("home"))

def process_error(message, next_page):
    """

    :param message:
    :param next_page:
    :return:
    """
    print("ERROOOOOOOOOOOOOOR")
    return render_template("error.html", error_message=message, next=next_page)            

# este codigo controla los errores de campos ausentes
def process_missingFields(campos, next_page):
    """
    :param campos: Lista de Campos que faltan
    :param next_page: ruta al pulsar botón continuar
    :return: plantilla generada
    """
    return render_template("missingFields.html", inputs=campos, next=next_page)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    if 'user_name' in session:
        logged = True
        nickname = session['user_name']
    else:
        logged = False
        nickname = ''
    return render_template('index.html', logged=logged, nickname=nickname)


@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET'])
def login():
    return app.send_static_file('login.html')


@app.route('/signup', methods=['GET'])
def signup():
    return app.send_static_file('signup.html')


@app.route('/processLogin', methods=['GET', 'POST'])
def processLogin():
    missing = []
    fields = ['email', 'passwd', 'login_submit']
    for field in fields:
        value = request.form.get(field, None)
        if value is None:
            missing.append(field)
    if missing:
        return process_missingFields(missing, "/login")

    return load_user(request.form['email'], request.form['passwd'])


@app.route('/processSignup', methods=['GET', 'POST'])
def processSignup():
    missing = []
    fields = ['nickname', 'email', 'passwd','confirm', 'signup_submit']
    for field in fields:
        value = request.form.get(field, None)
        if value is None:
            missing.append(field)
    if missing:
        return process_missingFields(missing, "/login")

    return create_user_file(request.form['nickname'], request.form['email'], request.form['passwd'], request.form['confirm'])


@app.route('/processHome', methods=['GET', 'POST'])
def processHome():
    save_current_user()

    missing = []
    fields = ['message', 'last', 'post_submit']
    
    for field in fields:
        value = request.form.get(field, None)
        
        if value is None:
            missing.append(field)

    if missing: 
        return process_missingFields(missing, "/login")

    return '<!DOCTYPE html> ' \
           '<html lang="es">' \
           '<head>' \
           '<link href="static/css/socialed-style.css" rel="stylesheet" type="text/css"/>' \
           '<title> Inicio - SocialED </title>' \
           '</head>' \
           '<body> <div id="container">' \
		   '<a href="/"> SocialED </a> | <a href="home"> Inicio </a> | <a href="login"> Acceso </a> | <a href="signup"> Registro </a>' \
           '<h1>Hola, Vas bien?</h1>' \
                	'<form action="processHome" method="post" name="home"> ' \
			'<label for="message">Say something:</label><div class="inputs">' \
			'<input id="message" maxlength="128" name="message" size="80" type="text" required="true" value=""/>' \
			'<input id="last" type="hidden" name="last" required="true" value="' + request.form['last'] + '<br>'+ request.form['message'] + '">' \
	                 '</div>' \
                    	'<div class="inputs">' \
                        '<input id="post_submit" name="post_submit" type="submit" value="Post!"/>' \
           		'<br><br>Previous Posts: <br>' + request.form['last'] + '<br>' +request.form['message'] + \
                	'</form>' \
            		'</div></div>' \
           '</body>' \
           '</html>'

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True, port=8080)