from flask import Flask
from flask import render_template, request, redirect , session
from flask_mysqldb import MySQL
from datetime import datetime
from flask import send_from_directory
import os

app = Flask(__name__)
app.secret_key="develoteca"
mysql = MySQL(app)
# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sitio'

@app.route('/img/<imagen>')
def imagenes(imagen):
    print(imagen)
    return send_from_directory( os.path.join('templates/sitio/img'),imagen)

@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'), archivocss)

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

@app.route('/libros')
def libros():
    conexion = mysql.connection
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM libros")
    libros=cursor.fetchall()
    conexion.commit()
    print(libros)
    return render_template('sitio/libros.html', libros=libros)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/')
def admin_index():
    if not 'login' in session:
        return redirect ("/admin/login")
    return render_template('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')
@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']
    print(_usuario)
    print(_password)

    if _usuario=="admin" and _password=="123":
        session["login"]=True
        session["usuario"]="Administrador"
        return redirect("/admin")

    return render_template("/admin/login.html")

@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()
    return redirect('/admin/login')

@app.route('/admin/libros')
def admin_libros():

    if not 'login' in session:
        return redirect ("/admin/login")
    # Obtén la conexión de forma correcta
    conexion = mysql.connection
    cursor=conexion.cursor()
    cursor.execute("SELECT * FROM libros")
    libros=cursor.fetchall()
    conexion.commit()
    print(libros)

    print(conexion)  # Para verificar que se obtiene la conexión
    return render_template("admin/libros.html", libros=libros)

@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():

    if not 'login' in session:
        return redirect ("/admin/login")
    
    _nombre=request.form['txtNombre']
    _archivo = request.files['txtImagen']
    _url = request.form['txtURL']


    tiempo=datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')
    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)

    
    # Consulta SQL con parámetros
    sql = "INSERT INTO libros (id,nombre, imagen, url) VALUES (NULL, %s,%s ,%s);"
    datos=(_nombre,nuevoNombre,_url)

    # Conexión y cursor
    conexion = mysql.connection
    cursor = conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    print(_nombre)
    print(_archivo.filename)
    print(_url)
    

    return redirect('/admin/libros')

@app.route('/admin/libros/borrar' , methods=['POST'])
def admin_libros_borrar():

    if not 'login' in session:
        return redirect ("/admin/login")

    _id=request.form['txtID']
    print(_id)

    conexion = mysql.connection
    cursor=conexion.cursor()
    cursor.execute("SELECT imagen FROM libros where id=%s",(_id,))
    libro=cursor.fetchall()
    conexion.commit()
    print(libro)

    if os.path.exists("templates/sitio/img/"+str(libro[0][0])):
        os.unlink("templates/sitio/img/"+str(libro[0][0]))

    conexion = mysql.connection
    cursor=conexion.cursor()
    cursor.execute("DELETE FROM libros where id=%s",(_id,))
    conexion.commit()

    return redirect('/admin/libros')


if __name__ == '__main__':
    app.run(debug=True)
