
from functools import wraps

from flask import flash, redirect, session, url_for
def roles_required(*roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Verificar si está logueado
            if 'user_id' not in session:
                flash('Por favor, inicia sesión.', 'warning')
                return redirect(url_for('login'))
            
            # 2. Obtener la LISTA de roles de la sesión (usando la clave correcta 'roles')
            user_roles = session.get('roles', [])
            
            # 3. Verificar si el usuario tiene AL MENOS UNO de los roles permitidos
            # Usamos 'any' para comparar las dos listas
            tiene_permiso = any(rol in roles_permitidos for rol in user_roles)
            
            if not tiene_permiso:
                flash('No tienes permiso para acceder a esta sección.', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator