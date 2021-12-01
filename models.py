from config import db
from flask import session
from flask.helpers import url_for
from werkzeug.utils import redirect

class Departamento(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    nombre = db.Column(db.String(100), nullable = False)

    def __init__(self, nombre):
        self.nombre = nombre

    @classmethod
    def traerCiudades(cls, id):
        return Ciudad.query.filter_by(dep_id = id).all()


class Ciudad(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    nombre = db.Column(db.String(100), nullable = False)

    # Llaves foraneas
    dep_id = db.Column(db.Integer, db.ForeignKey(Departamento.id), nullable = False)

    # Relaciones
    departamento = db.relationship('Departamento')

    def __init__(self, id, nombre, dep_id):
        self.id = id
        self.nombre = nombre
        self.dep_id = dep_id

    @classmethod
    def traerSucursales(cls, id):
        return Sucursal.query.filter_by(ciu_id = id).all()


class Administrador(db.Model):
    numDocumento = db.Column(db.String(20), primary_key = True)
    correo = db.Column(db.String(100), nullable = False, unique = True)
    contrasena = db.Column(db.String(30), nullable = False)
    nombre = db.Column(db.String(100), nullable = False)
    apellido = db.Column(db.String(100), nullable = False)
    foto = db.Column(db.BLOB())

    # Llaves foraneas
    dep_id = db.Column(db.Integer, db.ForeignKey(Departamento.id), nullable = False)

    # Relaciones
    departamento = db.relationship('Departamento')

    # Constructor
    def __init__(self, correo, nombre, apellido, numDocumento, contrasena):
        self.numDocumento = numDocumento
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.contrasena = contrasena

    def iniciarSesion(self):
        session['numDocumento'] = self.numDocumento
        session['nombre'] = self.nombre
        session['apellido'] = self.apellido
        session['correo'] = self.correo
        session['contrasena'] = self.contrasena
        session['idDepartamento'] = self.dep_id
        session['tipo'] = "Administrador"

        return redirect(url_for('admPerfil'))



class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    nombre = db.Column(db.String(100), nullable = False)
    direccion = db.Column(db.String(200), nullable = False)

    # Llaves foraneas
    ciu_id = db.Column(db.Integer, db.ForeignKey(Ciudad.id), nullable = False)

    # Relaciones
    ciudad = db.relationship('Ciudad')

    # Constructor
    def __init__(self, nombre, direccion, ciu_id):
        self.nombre = nombre
        self.direccion = direccion
        self.ciu_id = ciu_id

    @classmethod
    def traerOperarios(cls, id):
        return Operario.query.filter_by(suc_id = id).all()


class Operario(db.Model):
    numDocumento = db.Column(db.String(20), primary_key = True)
    correo = db.Column(db.String(100), nullable = False, unique = True)
    contrasena = db.Column(db.String(30), nullable = False)
    nombre = db.Column(db.String(100), nullable = False)
    apellido = db.Column(db.String(100), nullable = False)
    foto = db.Column(db.BLOB())

    # Llaves foraneas
    suc_id = db.Column(db.Integer, db.ForeignKey(Sucursal.id), nullable = False)

    # Relaciones
    sucursal = db.relationship('Sucursal')

    # Constructor
    def __init__(self, numDocumento, correo, contrasena, nombre, apellido, suc_id):
        self.nombre = nombre
        self.numDocumento = numDocumento
        self.correo = correo
        self.contrasena = contrasena
        self.apellido = apellido
        self.suc_id = suc_id

    def iniciarSesion(self):
        session['numDocumento'] = self.numDocumento
        session['nombre'] = self.nombre
        session['apellido'] = self.apellido
        session['correo'] = self.correo
        session['contrasena'] = self.contrasena
        session['idSucursal'] = self.suc_id
        session['tipo'] = "Operario"

        return redirect(url_for('opePerfil'))


class Proveedor(db.Model):

    id = db.Column(db.String(100), primary_key = True)
    nombre = db.Column(db.String(100), nullable = False)
    telefono = db.Column(db.String(20), nullable = False)

    #Constructor
    def __init__(self, id, nombre, telefono):
        self.id = id
        self.nombre = nombre
        self.telefono = telefono


class Tipo(db.Model):

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    nombre = db.Column(db.String(30), nullable = False)

    #Constructor
    def __init__(self, nombre):
        self.nombre = nombre


class Encuesta(db.Model):

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    nombre = db.Column(db.String(100), nullable = False)

    #Llaves foraneas
    tip_id = db.Column(db.Integer, db.ForeignKey(Tipo.id), nullable = False)

    #Relaciones
    tipo = db.relationship('Tipo')

    def __init__(self, nombre, tip_id):
        self.nombre = nombre
        self.tip_id = tip_id
    

class Oferta(db.Model):

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    nombre = db.Column(db.String(100), nullable = False)
    garantia = db.Column(db.String(100), nullable = True)
    precio = db.Column(db.Integer, nullable = False)

    #Llaves foraneas
    pro_id = db.Column(db.Integer, db.ForeignKey(Proveedor.id), nullable = False)
    enc_id = db.Column(db.Integer, db.ForeignKey(Encuesta.id), nullable = False)

    #Relaciones 
    proveedor = db.relationship('Proveedor')
    encuesta = db.relationship('Encuesta')

    #Constructor
    def __init__(self, nombre, garantia, precio, pro_id, enc_id):
        self.nombre = nombre
        self.garantia = garantia
        self.precio = precio
        self.pro_id = pro_id
        self.enc_id = enc_id


class Vitrina(db.Model):

    ofe_id = db.Column(db.Integer, db.ForeignKey(Oferta.id), primary_key = True)
    suc_id = db.Column(db.Integer, db.ForeignKey(Sucursal.id), primary_key = True)
    
    #Relaciones
    sucursal = db.relationship('Sucursal')
    oferta = db.relationship('Oferta')


class Reporte(db.Model):

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    fecha = db.Column(db.DateTime(), nullable = False)
    descripcion = db.Column(db.String(500), nullable = False)

    #Llaves foraneas
    suc_id = db.Column(db.Integer, db.ForeignKey(Sucursal.id), nullable = False)
    ofe_id = db.Column(db.Integer, db.ForeignKey(Oferta.id), nullable = False)

    #Relaciones
    sucursal = db.relationship('Sucursal')
    oferta = db.relationship('Oferta')

    #Constructor
    def __init__(self, descripcion):
        self.descripcion = descripcion


class Cliente(db.Model):
    numDocumento = db.Column(db.String(20), primary_key = True)
    tipoDocumento = db.Column(db.String(20), nullable = False)
    nombre = db.Column(db.String(100), nullable = False)
    apellido = db.Column(db.String(100), nullable = False)
    correo = db.Column(db.String(100), nullable = False)
    telefono = db.Column(db.String(20), nullable = False)

    #Constructor
    def __init__(self, numDocumento, tipoDocumento, correo, nombre, apellido, telefono):
        self.numDocumento = numDocumento
        self.tipoDocumento = tipoDocumento
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.telefono = telefono


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement= True)
    fecha = db.Column(db.DateTime(), nullable = False)
    cantidad = db.Column(db.Integer, nullable = False)

    #Llaves Foraneas
    cli_id = db.Column(db.String, db.ForeignKey(Cliente.numDocumento), nullable = False)
    suc_id = db.Column(db.Integer, db.ForeignKey(Sucursal.id), nullable = False)
    ofe_id = db.Column(db.Integer, db.ForeignKey(Oferta.id), nullable = False)

    #Relaciones
    cliente = db.relationship('Cliente')
    sucursal = db.relationship('Sucursal')
    oferta = db.relationship('Oferta')

    #Constructor
    def __init__(self, fecha, cantidad, cli_id, suc_id, ofe_id):
        self.fecha = fecha
        self.cantidad = cantidad
        self.cli_id = cli_id
        self.suc_id = suc_id
        self.ofe_id = ofe_id


class Preguntas(db.Model):

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    descripcion = db.Column(db.String(400), nullable = False)
    porcentaje = db.Column(db.Integer, nullable = False)

    #Llaves foraneas
    enc_id = db.Column(db.Integer, db.ForeignKey(Encuesta.id), nullable = False)

    #Relaciones
    encuesta = db.relationship('Encuesta')

    #Constructor
    def __init__(self, descripcion, porcentaje):
        self.descripcion = descripcion
        self.porcentaje = porcentaje


class Respuestas(db.Model):

    id = db.Column(db.Integer, primary_key = True, unique = True, autoincrement = True)
    descripcion = db.Column(db.String(100), nullable = False)
    fecha = db.Column(db.DateTime(), nullable = False)

    #Llaves foraneas
    pre_id = db.Column(db.Integer, db.ForeignKey(Preguntas.id), nullable = False)
    cli_numDocumento = db.Column(db.Integer, db.ForeignKey(Cliente.numDocumento), nullable = False)
    ofe_id = db.Column(db.Integer, db.ForeignKey(Oferta.id), nullable = False)

    #Relaciones
    preguntas = db.relationship('Preguntas')
    cliente = db.relationship('Cliente')
    oferta = db.relationship('Oferta')

    #Constructor
    def init(self, descripcion, ofe_id, fecha):
        self.descripcion = descripcion
        self.fecha = fecha
        self.ofe_id = ofe_id