# Módulo de escalada a WhatsApp
import json
from datetime import datetime

class EscaladaWhatsApp:
    def __init__(self):
        self.operadores = {
            'admisiones': {
                'nombre': 'Asesor de Admisiones',
                'numero': '+573113610649',
                'disponible': True
            },
            'becas': {
                'nombre': 'Asesor de Becas',
                'numero': '+573113610649',
                'disponible': True
            },
            'soporte': {
                'nombre': 'Soporte General',
                'numero': '+573113610649',
                'disponible': True
            }
        }
    
    def detectar_consulta_compleja(self, mensaje):
        """Detectar si la consulta necesita operador humano"""
        palabras_clave = {
            'admisiones': ['inscribir', 'admisión', 'registro', 'cuándo', 'cómo entro', 'requisito especial'],
            'becas': ['descuento especial', 'situación especial', 'excepción', 'caso particular'],
            'soporte': ['problema', 'error', 'no funciona', 'reportar', 'queja', 'reclamo']
        }
        
        mensaje_lower = mensaje.lower()
        
        for categoria, palabras in palabras_clave.items():
            if any(palabra in mensaje_lower for palabra in palabras):
                return {
                    'necesita_operador': True,
                    'categoria': categoria,
                    'operador': self.operadores[categoria]
                }
        
        return {'necesita_operador': False}
    
    def generar_enlace_whatsapp(self, numero, mensaje_inicial=''):
        """Generar enlace de WhatsApp para contactar operador"""
        if not mensaje_inicial:
            mensaje_inicial = 'Hola, tengo una consulta que Vivi no pudo resolver.'
        
        # Codificar mensaje para URL
        mensaje_codificado = mensaje_inicial.replace(' ', '%20')
        return f'https://wa.me/{numero.replace("+", "")}?text={mensaje_codificado}'
    
    def crear_ticket_escalada(self, usuario_id, mensaje, categoria):
        """Crear ticket para operador"""
        return {
            'id': f'TICKET_{usuario_id}_{datetime.now().timestamp()}',
            'usuario_id': usuario_id,
            'mensaje': mensaje,
            'categoria': categoria,
            'estado': 'pendiente',
            'timestamp': datetime.now().isoformat(),
            'asignado_a': None
        }

escalada = EscaladaWhatsApp()
