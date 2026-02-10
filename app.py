from flask import Flask, render_template, json, request, session, flash,redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from db import conectar
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'
app.config['SESSION_PERMANENT'] = False

@app.route('/')
def index():
    return render_template('sistema/home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 1. Verificar si ya está logueado antes de procesar nada
    if 'user_id' in session:
        flash('Ya has iniciado sesión', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = conectar()
        cursor = conn.cursor()
        
        # 2. Solo buscamos por email. No metas la contraseña en el SELECT.
        cursor.execute("SELECT id_usuario, username, password_hash FROM usuarios WHERE email=%s", (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()

        # 3. Validar usuario y verificar el hash de la contraseña
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Inicio de sesión exitoso', 'success')
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
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)