from flask import Flask, render_template, json, request, session, flash,redirect, url_for,Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from db import conectar, query
from dotenv import load_dotenv
import os
from functools import wraps
from pago import pagos_bp
from auth import roles_required

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") 
app.config['SESSION_PERMANENT'] = False
app.register_blueprint(pagos_bp, url_prefix='/pagos')
@app.route('/')
def index():
    print(session)
    return render_template('sistema/home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 1. Verificar si ya está logueado
    if 'user_id' in session:
        flash('Ya has iniciado sesión', 'info')
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # 2. Buscamos el usuario usando tu método abreviado
        # Obtenemos: id_usuario, username, password_hash
        user = query("SELECT id_usuario, username, password_hash FROM usuarios WHERE email=%s", (email,), fetchone=True)

        # 3. Validar usuario y verificar hash
        if user and check_password_hash(user[2], password):
            # Guardamos datos básicos en sesión
            session['user_id'] = user[0]
            session['username'] = user[1]
            
            # 4. BUSCAR ROLES (Adaptado a tu tabla usuario_rol y roles)
            # Traemos los nombres de los roles asociados al ID del usuario
            sql_roles = """
                SELECT r.nombre 
                FROM roles r
                JOIN usuario_rol ur ON r.id_rol = ur.id_rol
                WHERE ur.id_usuario = %s
            """
            roles_db = query(sql_roles, (user[0],), fetchone=False)
            
            # Guardamos los roles como una lista simple: ['admin', 'vendedor']
            # roles_db devuelve una lista de tuplas [( 'admin',), ('vendedor',)]
            session['roles'] = [r[0] for r in roles_db] if roles_db else []

            flash(f'Bienvenido {user[1]}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))

    return render_template('sistema/login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # 1. Encriptar la contraseña (crear el hash)
        # 'pbkdf2:sha256' es el método por defecto, muy seguro.
        hashed_password = generate_password_hash(password)
        
        try:
            conn = conectar()
            cursor = conn.cursor()
            
            # 2. Insertar el hash, NO la password real
            cursor.execute(
                "INSERT INTO usuarios (username, email, password_hash) VALUES (%s, %s, %s)", 
                (username, email, hashed_password)
            )
            
            conn.commit()
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('login')) # Mejor usar redirect que render_template
            
        except Exception as e:
            # En caso de que el email ya exista o haya un error de base de datos
            print(f"Error: {e}")
            flash('El correo o usuario ya están registrados.', 'danger')
            return redirect(url_for('registro'))
            
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    return render_template('sistema/registro.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('index'))


# tienda
@app.route('/tienda')
def tienda():
    productos = query("SELECT id_producto, nombre, precio, stock, img_url FROM productos", fetchone=False)
    if not productos:
        flash('No hay productos disponibles en este momento.', 'info')
    productos = [dict(id=prod[0], nombre=prod[1], precio=prod[2],stock=prod[3], img_url=prod[4]) for prod in productos]
    return render_template('sistema/tienda.html' , productos=productos)

@app.route('/agregar_producto', methods=['POST', 'GET'])
@roles_required('admin')  # Solo admins pueden agregar productos
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']
        provedor = request.form['provedor']
        url_imagen = request.form['imagen']

        sql = "INSERT INTO productos (nombre, precio, stock, proveedor, img_url) VALUES (%s, %s, %s, %s, %s)"
        try:
            query(sql, (nombre, precio, stock, provedor, url_imagen))
            flash('Producto agregado exitosamente', 'success')
        except Exception as e:
            print(f"Error al agregar producto: {e}")
            flash('Error al agregar el producto. Intenta nuevamente.', 'danger')
        
        return redirect(url_for('tienda'))
    return render_template('sistema/productos/agregar_producto.html') 


@app.errorhandler(404)
def page_not_found(e):
    return render_template('sistema/404.html'), 404

@app.route('/usuarios')
@roles_required('admin')  # Solo admins pueden ver la lista de usuarios
def usuarios():
    sql = "SELECT id_usuario, username, email, id_usuario FROM usuarios"
    try:
        usuarios_db = query(sql, fetchone=False)
        usuarios_list = [dict(id=u[0], username=u[1], email=u[2], rol=u[3]) for u in usuarios_db]
        return render_template('sistema/usuarios.html', usuarios=usuarios_list)
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        flash('Error al cargar la lista de usuarios.', 'danger')
        return render_template('sistema/usuarios.html', usuarios=usuarios_list)
        

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)