from flask import Flask, render_template, request, session, json
from flask.helpers import url_for
from werkzeug.utils import redirect
from datetime import datetime
import sqlite3

con = sqlite3.connect('database/genesisSystem.db', check_same_thread=False)
cur = con.cursor()


app = Flask(__name__)

from models import *
from utilities import Contador

 
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        numDoc = request.form['numDocumento']
        cliente = db.session.query(Cliente).filter(Cliente.numDocumento == numDoc and Cliente.tipoDocumento == request.form['tipDocumento']).count()

        if cliente == 1:
            return redirect(url_for('productoServ', numDoc = numDoc, enc_id = 0))


    return render_template('index.html')


@app.route('/cli-pro-serv/<numDoc>/<enc_id>', methods=['GET', 'POST'])
def productoServ(numDoc, enc_id):
   
    compras = cur.execute("SELECT oferta.* FROM venta JOIN oferta ON venta.ofe_id = oferta.id WHERE venta.cli_id = '%s' EXCEPT SELECT oferta.* FROM venta JOIN oferta ON venta.ofe_id = oferta.id JOIN respuestas ON oferta.id = respuestas.ofe_id WHERE venta.cli_id = '%s'" % (numDoc, numDoc))
    
    preguntas = None
    if enc_id != 0:
        preguntas = db.session.query(Preguntas).filter(Preguntas.enc_id == enc_id)

    cont1 = Contador(0) 
    return render_template('cli-productos.html', compras = compras,  preguntas =  preguntas, numDoc = numDoc, enc_id = enc_id, cont1 = cont1)

#AGREGAR LAS EVALUACIONES






# INICIO SESIÓN

@app.route('/login/<comprobacion>', methods=['GET', 'POST'])
def login(comprobacion):
    if 'nombre' in session:
        if session['tipo'] == 'Administrador':
            return redirect(url_for('admPerfil'))

        return redirect(url_for('opePerfil'))

    if request.method == 'POST':
        correoUsuario = request.form['correoUsuario']
        contrasenaUsuario = request.form['contrasenaUsuario']

        user = Administrador.query.filter_by(correo = correoUsuario, contrasena = contrasenaUsuario).first()
        if not user:
            user = Operario.query.filter_by(correo = correoUsuario, contrasena = contrasenaUsuario).first()

        if user:
            return user.iniciarSesion()

        return redirect(url_for('login', comprobacion = 'noLoggedIn'))
        
    return render_template('login.html', comprobacion = comprobacion)

@app.route('/login')
def redirectLogin():
    return redirect(url_for('login', comprobacion = 'Logged'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('redirectLogin'))


# ADMINISTRADOR

@app.route('/adm-perfil', methods=['GET', 'POST'])
def admPerfil():
    if 'nombre' in session:
        return render_template('adm-perfil.html')
    
    return redirect(url_for('login', comprobacion = 'Logged'))


@app.route('/adm-ventas', methods=["GET", "POST"])
def admVentas():
    if 'nombre' in session:
        sucursales = db.session.query(Sucursal).\
        join(Ciudad).join(Departamento).join(Administrador).filter(Administrador.numDocumento == session['numDocumento'])
        
        if request.method == 'POST':
            sucursal = request.form['sucuOpc']
            ofertas = db.session.query(Oferta).\
            join(Vitrina).join(Sucursal).filter(Sucursal.id == sucursal).all()

            cantidad = db.session.query(Venta.cantidad, Oferta.nombre).\
            join(Oferta).filter(Venta.suc_id == sucursal).all()

            ofer = None
            jsonOfer = []
            for oferta in ofertas:
                ofer = oferta.__dict__
                del ofer['_sa_instance_state']
                ofer['cantidad'] = 0
                for cant in cantidad:
                    if cant[1] == ofer['nombre']:
                        ofer['cantidad'] += cant[0]

                jsonOfer.append(ofer)
            
            return render_template('adm-ventas.html', sucursales = sucursales, ofertas = map(json.dumps, jsonOfer))

        return render_template('adm-ventas.html', sucursales = sucursales)

    return redirect(url_for('login', comprobacion = 'Logged'))


@app.route('/registrarProveedor', methods=['GET', 'POST'])
def registrarProveedor():
    if 'nombre' in session:
        if request.method == 'POST':
            db.session.add(Proveedor(id = request.form['identificacion'], nombre = request.form['nombre'], telefono = request.form['telefono']))
            db.session.commit()

        return render_template('adm-proveedores.html', proveedores = Proveedor.query.all())

    return redirect(url_for('login', comprobacion = 'Logged'))

    
@app.route('/eliminarProveedor/<id>')
def eliminarProveedor(id):
    if 'nombre' in session:
        Proveedor.query.filter_by(id = id).delete()
        db.session.commit()

        return redirect(url_for('registrarProveedor'))

    return redirect(url_for('login', comprobacion = 'Logged'))


@app.route('/registrarOferta', methods=['GET', 'POST'])
def registrarOferta():
    if 'nombre' in session:
        if request.method == 'POST':
            garantia = None
            if request.form['garantia'] != '':
                garantia = request.form['garantia']
            db.session.add(Oferta(nombre = request.form['nombre'], garantia = garantia, precio = request.form['precio'], pro_id = request.form['idProveedor'], enc_id = request.form['idEncuesta']))
            db.session.commit()

        return render_template('adm-proveedor__ofertas.html', proveedores = Proveedor.query.all(), encuestas = db.session.query(Encuesta, Tipo.nombre).join(Tipo).all(), ofertas = db.session.query(Oferta, Proveedor.nombre, Encuesta.nombre).join(Proveedor, Oferta.proveedor).join(Encuesta, Oferta.encuesta).all())

    return redirect(url_for('login', comprobacion = 'Logged'))

@app.route('/eliminarOferta/<id>')
def eliminarOferta(id):
    if 'nombre' in session:
        Oferta.query.filter_by(id = id).delete()
        db.session.commit()

        return redirect(url_for('registrarOferta'))

    return redirect(url_for('login', comprobacion = 'Logged'))


@app.route('/registrarSucursal', methods=["GET", "POST"])
def registrarSucursal():
    if 'nombre' in session:
        if request.method == 'POST':
            db.session.add(Sucursal(nombre = request.form['nombre'], direccion = request.form['direccion'], ciu_id = request.form['idCiudad']))
            db.session.commit()

        sucursalesPorCiudad = []
        for ciudad in Departamento.traerCiudades(session['idDepartamento']):
            sucursalesPorCiudad.append({"ciudad" : ciudad, "sucursales" : Ciudad.traerSucursales(ciudad.id)})

        return render_template('adm-sucursales.html', sucursalesPorCiudad = sucursalesPorCiudad)

    return redirect(url_for('login', comprobacion = 'Logged'))


@app.route('/eliminarSucursal/<id>', methods=['POST', 'GET'])
def eliminarSucursal(id):
    if 'nombre' in session:
        Operario.query.filter_by(suc_id = id).delete()
        db.session.commit()
        Sucursal.query.filter_by(id = int(id)).delete()
        db.session.commit()

        return redirect(url_for('registrarSucursal'))
    
    return redirect(url_for('login', comprobacion = 'Logged'))


@app.route('/registrarOperario', methods=["GET", "POST"])
def registrarOperario():
    if 'nombre' in session:
        if request.method == 'POST':
            db.session.add(Operario(numDocumento = request.form['numDocumento'], correo = request.form['correo'], contrasena = request.form['contrasena'], nombre = request.form['nombres'], apellido = request.form['apellidos'], suc_id = request.form['idSucursal']))
            db.session.commit()

        return render_template('adm-sucursales__operarios.html', sucursales = db.session.query(Sucursal).join(Ciudad).filter(Ciudad.dep_id == session['idDepartamento']).all(), operarios = db.session.query(Operario, Sucursal.nombre).join(Sucursal).join(Ciudad).filter(Ciudad.dep_id == session['idDepartamento']))

    return redirect(url_for('login', comprobacion = 'Logged'))


@app.route('/eliminarOperario/<numDocumento>')
def eliminarOperario(numDocumento):
    if 'nombre' in session:
        Operario.query.filter_by(numDocumento = numDocumento).delete()
        db.session.commit()

        return redirect(url_for('registrarOperario'))

    return redirect(url_for('login', comprobacion = 'Logged'))
    

@app.route('/agregarOferta')
def agregarOferta():
    if 'nombre' in session:
        sucursales = sucursales = db.session.query(Sucursal).join(Ciudad).filter(Ciudad.dep_id == session['idDepartamento']).all()

        return render_template('adm-sucursales__ofertas.html', sucursales = sucursales)

    return redirect(url_for('login', comprobacion = 'Logged'))

@app.route('/registrarEvaluaciones', methods=["GET", "POST"])
def registrarEvaluaciones():
    if 'nombre' in session:
        if request.method == 'POST':
            db.session.add(Encuesta(nombre = request.form['nombre'], tip_id = request.form['idTipo']))
            db.session.commit()

        return render_template('adm-evaluaciones.html', tipos = Tipo.query.all(), encuestas = db.session.query(Encuesta, Tipo.nombre).join(Tipo).all())

    return redirect(url_for('login', comprobacion = 'Logged'))



@app.route('/eliminarEncuesta/<id>')
def eliminarEncuesta(id):
    if 'nombre' in session:
        Encuesta.query.filter_by(id = id).delete()
        db.session.commit()

        return redirect(url_for('registrarEvaluaciones'))

    return redirect(url_for('login', comprobacion = 'Logged'))
@app.route('/registrarPreguntas', methods=['GET', 'POST'])
def registrarPreguntas():
    if 'nombre' in session:
        alerta = 0
        if request.method == 'POST':

            cantPreguntas = Preguntas.query.filter_by(enc_id = request.form['idEncuesta']).count()

            if cantPreguntas == 0:

                db.session.add(Preguntas(descripcion = request.form['Pregunta1'], porcentaje = request.form['porcentaje1'], enc_id = request.form['idEncuesta']))
                db.session.add(Preguntas(descripcion = request.form['Pregunta2'], porcentaje = request.form['porcentaje2'], enc_id = request.form['idEncuesta']))
                db.session.add(Preguntas(descripcion = request.form['Pregunta3'], porcentaje = request.form['porcentaje3'], enc_id = request.form['idEncuesta']))
                db.session.add(Preguntas(descripcion = request.form['Pregunta4'], porcentaje = request.form['porcentaje4'], enc_id = request.form['idEncuesta']))
                db.session.add(Preguntas(descripcion = request.form['Pregunta5'], porcentaje = request.form['porcentaje5'], enc_id = request.form['idEncuesta']))
                db.session.commit()
            else:
                alerta = 1

        return render_template('adm-preguntas.html', encuestas = Encuesta.query.all(), alerta = alerta)

    return redirect(url_for('login', comprobacion = 'Logged'))


# OPERARIO

@app.route('/ope-perfil')
def opePerfil():
    if 'nombre' in session:

        return render_template('ope-perfil.html')

    return redirect(url_for('login', comprobacion = 'Logged'))


@app.route('/registrarClientes', methods=['GET', 'POST'])
def registrarClientes():
    if 'nombre' in session:
        if request.method == 'POST':
            db.session.add(Cliente(numDocumento = request.form['numDocumento'], tipoDocumento = request.form['tipoDocumento'], correo = request.form['correo'], nombre = request.form['nombres'], apellido = request.form['apellidos'], telefono = request.form['telefono']))
            db.session.commit()
        
        return render_template('ope-clientes.html')

    return redirect(url_for('login', comprobacion = 'Logged'))


@app.route('/registrarVentas', methods=['GET', 'POST'])
def registrarVentas():
    if 'nombre' in session:
        if request.method == 'POST':
            db.session.add(Venta(fecha = datetime.today(), cantidad = request.form['cant'], cli_id = request.form['nDocumento'], suc_id = session['idSucursal'], ofe_id = request.form['oferta']))
            db.session.commit()

        return render_template('ope-ventas.html', ofertas = db.session.query(Oferta.nombre, Oferta.id).join(Vitrina).filter(Vitrina.suc_id == session['idSucursal']))

    return redirect(url_for('login', comprobacion = 'Logged'))