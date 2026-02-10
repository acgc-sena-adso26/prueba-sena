from flask import Blueprint, redirect, url_for, request, jsonify
import stripe
import os
from db import query
from dotenv import load_dotenv
from auth import roles_required
load_dotenv()

pagos_bp = Blueprint('pagos', __name__)

stripe.api_key = os.getenv("STRIPE_KEY")

@pagos_bp.route('/checkout/<int:id_producto>', methods=['POST'])
@roles_required('cliente','admin','vendedor')  # Solo clientes pueden hacer checkout
def checkout(id_producto): # Cambiado de crear_sesion_pago a checkout
    # 1. Obtener datos (id_producto, nombre, precio, stock, img_url)
    producto = query("SELECT nombre, precio, img_url FROM productos WHERE id_producto=%s", (id_producto,), fetchone=True)

    if not producto:
        return "Producto no encontrado", 404

    try:
        # producto[0] es nombre, producto[1] es precio, producto[2] es img_url
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': producto[0],
                        'images': [producto[2]] if producto[2] else [],
                    },
                    'unit_amount': int(producto[1] * 100), # Stripe usa centavos
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('pagos.pago_exitoso', _external=True),
            cancel_url=url_for('tienda', _external=True),
        )
        return redirect(checkout_session.url, code=303)

    except Exception as e:
        print(f"Error en Stripe: {e}")
        return "Error al procesar el pago", 500

@pagos_bp.route('/pago-exitoso')
@roles_required('cliente','admin','vendedor')  # Solo clientes pueden ver esta página
def pago_exitoso():
    return "¡Gracias por tu compra! El pago fue procesado correctamente."