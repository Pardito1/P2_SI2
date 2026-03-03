# CONTEXTO COMPLETO PARA CONTINUAR LA PRÁCTICA 2 — SI2

## QUIÉN SOY Y MI ENTORNO

Soy Alejandro (e462971), estudiante de Sistemas Informáticos II en la UAM.
Trabajo en el PC del laboratorio de la universidad.
Ruta del proyecto: `/home/alumnos/e462971/Descargas/si2/si2_alumnos-main/`

Arquitectura de VMs (port forwarding):
- VM1 (SSH puerto 12022): PostgreSQL en puerto 15432, RabbitMQ en puerto 5672
- VM2 (SSH puerto 22022): Backend en puerto 28000
- VM3 (SSH puerto 32022): Frontend en puerto 38000

En los PCs del laboratorio el puerto 8000 está ocupado, usar siempre 8001 para pruebas locales.

---

## QUÉ ES ESTA PRÁCTICA

La Práctica 2 transforma la aplicación monolítica `P1-base` (visaApp — sistema de pagos con tarjeta) en una arquitectura distribuida con 3 componentes:

1. **P1-rpc-backend**: Servidor RPC que expone las funciones de acceso a BD como procedimientos remotos usando Modern RPC + XML-RPC. Se despliega en VM2.
2. **P1-rpc-frontend**: Cliente web que mantiene la interfaz HTML pero llama al backend vía XML-RPC (usando `xmlrpc.client.ServerProxy`) en lugar de acceder a la BD directamente. Se despliega en VM3.
3. **Servicio de cancelación de pagos**: Comunicación asíncrona con RabbitMQ + Pika. Un `client_mq.py` deposita mensajes en una cola y un `server_mq.py` los consume y cancela pagos.

---

## ESTRUCTURA DEL PROYECTO COMPLETO

```
si2_alumnos-main/
├── P1-base/                    ← Aplicación monolítica original (NO TOCAR)
│   ├── visaApp/
│   │   ├── management/commands/data.csv, populate.py
│   │   ├── migrations/
│   │   ├── templates/ (6 HTML templates)
│   │   ├── __init__.py, admin.py, apps.py
│   │   ├── forms.py, models.py, pagoDB.py
│   │   ├── urls.py, views.py
│   │   ├── tests_models.py, tests_views.py
│   ├── visaSite/settings.py, urls.py, wsgi.py, asgi.py
│   ├── env, manage.py, requirements.txt, build.sh
│
├── P1-rpc-backend/             ← ✅ CREADO (Fases 1-2 completadas)
│   ├── visaAppRPCBackend/
│   │   ├── management/commands/data.csv, populate.py
│   │   ├── migrations/
│   │   ├── __init__.py, admin.py, apps.py
│   │   ├── models.py              ← Sin cambios respecto a P1-base
│   │   ├── pagoDB.py              ← ✅ MODIFICADO (4 funciones con @rpc_method + model_to_dict)
│   │   ├── urls.py                ← ✅ MODIFICADO (solo ruta RPCEntryPoint)
│   │   ├── tests_rpc_backend.py   ← Copiado del repositorio proporcionado
│   ├── visaSite/settings.py       ← ✅ MODIFICADO (añadido modernrpc + MODERNRPC_METHODS_MODULES)
│   ├── env, manage.py, requirements.txt
│
├── P1-rpc-frontend/            ← ❌ POR CREAR (Fases 5-8)
│
├── rpc-backend/                ← Ficheros proporcionados por el profesor
│   └── visaAppRPCBackend/
│       ├── readme.md
│       └── tests_rpc_server.py
│
├── rpc-frontend/               ← Ficheros proporcionados por el profesor
│   └── visaAppRPCFrontend/
│       ├── readme.md
│       └── tests_views.py
│
├── ws-backend/                 ← De la P1 (ignorar para P2)
├── ws-frontend/                ← De la P1 (ignorar para P2)
```

---

## QUÉ SE HA COMPLETADO YA

### ✅ FASE 1 — Crear estructura P1-rpc-backend (Ejercicio 1)
- Copiado P1-base a P1-rpc-backend
- Renombrado visaApp → visaAppRPCBackend con find sed
- Eliminados: forms.py, views.py, templates/, tests_views.py, tests_models.py
- Copiados tests_rpc_server.py → tests_rpc_backend.py

### ✅ FASE 2 — Exportar funcionalidad como RPC (Ejercicio 2)
- settings.py: añadido "modernrpc" a INSTALLED_APPS + MODERNRPC_METHODS_MODULES
- urls.py: reescrito con solo RPCEntryPoint en /rpc/
- pagoDB.py: las 4 funciones decoradas con @rpc_method, registrar_pago y get_pagos_from_db usan model_to_dict + marcaTiempo manual

---

## QUÉ FALTA POR HACER

### ⬜ FASE 3 — Probar backend RPC en local + tests (Ejercicio 3)
Ejecutar:
1. `python manage.py makemigrations && python manage.py migrate`
2. `python manage.py populate`
3. `python manage.py runserver 8001` → verificar 405 en http://127.0.0.1:8001/visaAppRPCBackend/rpc
4. `python manage.py test visaAppRPCBackend.tests_rpc_backend` → 4 tests OK

### ⬜ FASE 4 — Desplegar backend RPC en VM2 (Ejercicio 4)
- Copiar P1-rpc-backend a VM2
- Configurar env con DATABASE_SERVER_URL apuntando a VM1
- Ejecutar migrate + populate en VM2
- Arrancar con `python manage.py runserver 0.0.0.0:8000`
- Verificar desde PC: http://localhost:28000/visaAppRPCBackend/rpc → 405

### ⬜ FASE 5 — Crear estructura P1-rpc-frontend (Ejercicio 5)
Desde si2_alumnos-main/:
```bash
cp -r P1-base P1-rpc-frontend
cd P1-rpc-frontend
mv visaApp visaAppRPCFrontend
find ./ -type f -exec sed -i "s/visaApp/visaAppRPCFrontend/g" {} \;
rm -rf visaAppRPCFrontend/models.py
rm -rf visaAppRPCFrontend/migrations
rm -rf visaAppRPCFrontend/management
rm -rf visaAppRPCFrontend/tests_models.py
rm -rf visaAppRPCFrontend/tests_views.py
```
- Copiar tests del profesor: `cp ../rpc-frontend/visaAppRPCFrontend/tests_views.py visaAppRPCFrontend/`
- Añadir a env: `RPCAPIBASEURL=http://localhost:28000/visaAppRPCBackend/rpc/`
- Añadir a settings.py: `RPCAPIBASEURL = os.environ.get("RPCAPIBASEURL")`

### ⬜ FASE 6 — Codificar frontend RPC (Ejercicio 6)
Reescribir pagoDB.py del frontend para usar ServerProxy:

```python
from django.conf import settings
from xmlrpc.client import ServerProxy


def verificar_tarjeta(tarjeta_data):
    """Verifica si una tarjeta está registrada en la BD remota.
    :param tarjeta_data: diccionario con datos de la tarjeta
                         (numero, nombre, fechaCaducidad, codigoAutorizacion)
    :return: True si la tarjeta existe, False en caso contrario
    """
    with ServerProxy(settings.RPCAPIBASEURL) as proxy:
        return proxy.verificar_tarjeta(tarjeta_data)


def registrar_pago(pago_dict):
    """Registra un pago invocando el procedimiento remoto del backend.
    :param pago_dict: diccionario con datos del pago
                      (idComercio, idTransaccion, importe, tarjeta_id)
    :return: diccionario con datos del pago registrado
             (id, marcaTiempo, codigoRespuesta, etc.), None si hubo error
    """
    with ServerProxy(settings.RPCAPIBASEURL) as proxy:
        return proxy.registrar_pago(pago_dict)


def eliminar_pago(idPago):
    """Elimina un pago invocando el procedimiento remoto del backend.
    :param idPago: ID (entero) del pago a eliminar
    :return: True si se eliminó correctamente, False si no existe
    """
    with ServerProxy(settings.RPCAPIBASEURL) as proxy:
        return proxy.eliminar_pago(idPago)


def get_pagos_from_db(idComercio):
    """Obtiene los pagos de un comercio invocando el procedimiento remoto.
    :param idComercio: ID del comercio a consultar
    :return: lista de diccionarios con datos de cada pago
    """
    with ServerProxy(settings.RPCAPIBASEURL) as proxy:
        return proxy.get_pagos_from_db(idComercio)
```

### ⬜ FASE 7 — Probar frontend RPC (Ejercicio 7)
- Backend debe estar corriendo en VM2 (o local en otro puerto)
- `python manage.py runserver 8001`
- Probar manualmente en navegador
- `python manage.py test`

### ⬜ FASE 8 — Desplegar frontend RPC en VM3 (Ejercicio 8)
- Copiar a VM3
- Actualizar RPCAPIBASEURL en env con IP real de VM2
- Arrancar en 0.0.0.0:8000
- Probar desde PC en localhost:38000/visaAppRPCFrontend/
- Registrar pago, listar, borrar

### ⬜ FASE 9 — Crear server_mq.py (Ejercicio 9)
Crear en P1-rpc-backend/visaAppRPCBackend/server_mq.py:

```python
import os
import sys
import django
import pika

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'visaSite.settings')
django.setup()

from visaAppRPCBackend.models import Tarjeta, Pago


def main():
    if len(sys.argv) != 3:
        print("Debe indicar el host y el puerto")
        exit()

    hostname = sys.argv[1]
    port = sys.argv[2]

    # Conexión a RabbitMQ
    credentials = pika.PlainCredentials('alumnomq', 'alumnomq')
    parameters = pika.ConnectionParameters(
        host=hostname,
        port=int(port),
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declarar cola
    channel.queue_declare(queue='pago_cancelacion')

    # Callback que procesa mensajes
    def callback(ch, method, properties, body):
        id_pago = body.decode()
        print(f"[x] Recibido mensaje: cancelar pago con ID={id_pago}")
        try:
            pago = Pago.objects.get(id=int(id_pago))
            pago.codigoRespuesta = '111'
            pago.save(update_fields=['codigoRespuesta'])
            print(f"[✓] Pago {id_pago} cancelado correctamente (codigoRespuesta='111')")
        except Pago.DoesNotExist:
            print(f"[✗] Error: Pago con ID={id_pago} no encontrado")
        except Exception as e:
            print(f"[✗] Error al cancelar pago {id_pago}: {e}")

    # Registrar callback y consumir
    channel.basic_consume(
        queue='pago_cancelacion',
        on_message_callback=callback,
        auto_ack=True
    )

    print('[*] Esperando mensajes de cancelación. Pulsa CTRL+C para salir.')
    channel.start_consuming()


if __name__ == '__main__':
    main()
```

### ⬜ FASE 10 — Crear client_mq.py (Ejercicio 10)
Crear en P1-rpc-frontend/cliente_mom/client_mq.py:

```python
import pika
import sys


def cancelar_pago(hostname, port, id_pago):
    try:
        credentials = pika.PlainCredentials('alumnomq', 'alumnomq')
        parameters = pika.ConnectionParameters(
            host=hostname,
            port=int(port),
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
    except Exception as e:
        print(f"Error al conectar al host remoto: {e}")
        exit()

    channel = connection.channel()
    channel.queue_declare(queue='pago_cancelacion')

    channel.basic_publish(
        exchange='',
        routing_key='pago_cancelacion',
        body=str(id_pago)
    )

    print(f"[x] Enviado mensaje: cancelar pago con ID={id_pago}")
    connection.close()


def main():
    if len(sys.argv) != 4:
        print("Debe indicar el host, el numero de puerto, "
              "y el ID del pago a cancelar como un argumento.")
        exit()

    cancelar_pago(sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
```

### ⬜ FASE 11 — Ejecución y demostración completa (Ejercicio 11)
1. Registrar pago desde frontend
2. Ejecutar client_mq.py (sin servidor arrancado)
3. Verificar cola con `sudo rabbitmqctl list_queues` en VM1
4. Arrancar server_mq.py en VM2
5. Verificar cancelación (codigoRespuesta = '111')
6. Verificar cola vacía

### ⬜ FASE 12 — Documentación y entrega

---

## CONTENIDO DE LOS FICHEROS CLAVE YA MODIFICADOS

### P1-rpc-backend/visaAppRPCBackend/pagoDB.py (ACTUAL)

```python
"Interface with the database - RPC Backend"
from visaAppRPCBackend.models import Tarjeta, Pago
from modernrpc.core import rpc_method
from django.forms.models import model_to_dict


@rpc_method
def verificar_tarjeta(tarjeta_data):
    if bool(tarjeta_data) is False or not \
       Tarjeta.objects.filter(**tarjeta_data).exists():
        return False
    return True


@rpc_method
def registrar_pago(pago_dict):
    try:
        pago = Pago.objects.create(**pago_dict)
        pago = Pago.objects.get(pk=pago.pk)
    except Exception as e:
        print("Error: Registrando pago: ", e)
        return None
    pago_a_devolver = model_to_dict(pago)
    pago_a_devolver['marcaTiempo'] = str(pago.marcaTiempo)
    return pago_a_devolver


@rpc_method
def eliminar_pago(idPago):
    try:
        pago = Pago.objects.get(id=idPago)
    except Pago.DoesNotExist:
        return False
    pago.delete()
    return True


@rpc_method
def get_pagos_from_db(idComercio):
    pagos = Pago.objects.filter(idComercio=idComercio)
    lista_pagos = []
    for pago in pagos:
        pago_dict = model_to_dict(pago)
        pago_dict['marcaTiempo'] = str(pago.marcaTiempo)
        lista_pagos.append(pago_dict)
    return lista_pagos
```

### P1-rpc-backend/visaAppRPCBackend/urls.py (ACTUAL)

```python
from django.urls import path
from modernrpc.views import RPCEntryPoint

urlpatterns = [
    path("rpc/", RPCEntryPoint.as_view(), name="rpc")
]
```

### P1-rpc-backend/visaSite/settings.py — CAMBIOS REALIZADOS
- Añadido `"modernrpc"` a INSTALLED_APPS
- Añadido `MODERNRPC_METHODS_MODULES = ["visaAppRPCBackend.pagoDB"]`

---

## LECCIONES DE LA PRÁCTICA 1A (POST-MORTEM) — NO REPETIR ESTOS ERRORES

1. **Tests antiguos no eliminados**: Al crear un proyecto derivado con cp + find sed, SIEMPRE borrar los ficheros de test del proyecto original que ya no aplican. En P2: borrar tests_views.py y tests_models.py del backend, borrar tests_models.py y tests_views.py del frontend.

2. **env incompleto**: CADA proyecto tiene su propio env con variables ESPECÍFICAS. El backend necesita DATABASE_SERVER_URL. El frontend necesita RPCAPIBASEURL (y posiblemente DATABASE_SERVER_URL si los tests lo requieren). SIEMPRE verificar que settings.py lee TODAS las variables del env.

3. **pagoDB.py sin modificar**: Este fue el error más grave de la P1. Se entregó pagoDB.py de P1-base (con ORM directo) en lugar del modificado. En P2: el pagoDB.py del FRONTEND debe usar ServerProxy, NO el ORM. El pagoDB.py del BACKEND usa @rpc_method + model_to_dict.

4. **Verificar el ZIP antes de entregar**: Descomprimir en carpeta temporal y comprobar que los ficheros clave tienen el contenido correcto.

## CHECKLIST PRE-ENTREGA PARA P2

```bash
# Backend RPC
cd P1-rpc-backend
grep "@rpc_method" visaAppRPCBackend/pagoDB.py | wc -l          # Debe ser 4
grep "model_to_dict" visaAppRPCBackend/pagoDB.py | wc -l        # Debe ser 3
grep "modernrpc" visaSite/settings.py | wc -l                   # Debe ser 2
cat visaAppRPCBackend/urls.py                                    # Solo RPCEntryPoint
ls visaAppRPCBackend/forms.py 2>/dev/null && echo "ERROR: forms.py no debería existir"
ls visaAppRPCBackend/views.py 2>/dev/null && echo "ERROR: views.py no debería existir"
ls visaAppRPCBackend/templates 2>/dev/null && echo "ERROR: templates/ no debería existir"
ls visaAppRPCBackend/server_mq.py                                # Debe existir
python manage.py test visaAppRPCBackend.tests_rpc_backend        # 4 tests OK

# Frontend RPC
cd ../P1-rpc-frontend
grep "ServerProxy" visaAppRPCFrontend/pagoDB.py                  # DEBE encontrar
grep "objects" visaAppRPCFrontend/pagoDB.py                      # NO debe encontrar nada
grep "RPCAPIBASEURL" visaSite/settings.py                        # Debe encontrar
grep "RPCAPIBASEURL" env                                         # Debe encontrar
ls visaAppRPCFrontend/models.py 2>/dev/null && echo "ERROR: models.py no debería existir"
ls visaAppRPCFrontend/migrations 2>/dev/null && echo "ERROR: migrations/ no debería existir"
ls visaAppRPCFrontend/management 2>/dev/null && echo "ERROR: management/ no debería existir"
python manage.py test                                            # Tests OK (con backend corriendo)

# Servicio cancelación
ls P1-rpc-frontend/cliente_mom/client_mq.py                      # Debe existir
```

---

## PUNTUACIÓN

| Ejercicio | Puntos | Descripción | Estado |
|-----------|--------|-------------|--------|
| 1 | 0.5 | Crear proyecto backend RPC | ✅ Hecho |
| 2 | 0.5 | Exportar como procedimientos remotos | ✅ Hecho |
| 3 | 0.75 | Probar backend RPC + tests | ⬜ Pendiente |
| 4 | 1.0 | Desplegar backend en VM2 | ⬜ Pendiente |
| 5 | 0.5 | Crear proyecto frontend RPC | ⬜ Pendiente |
| 6 | 0.5 | Codificar frontend con ServerProxy | ⬜ Pendiente |
| 7 | 0.75 | Probar frontend RPC + tests | ⬜ Pendiente |
| 8 | 1.5 | Desplegar frontend en VM3 | ⬜ Pendiente |
| 9 | 1.0 | Servidor cancelación (server_mq.py) | ⬜ Pendiente |
| 10 | 1.0 | Cliente cancelación (client_mq.py) | ⬜ Pendiente |
| 11 | 1.0 | Ejecución completa | ⬜ Pendiente |
| Memoria | 1.0 | Informe técnico | ⬜ Pendiente |

**REQUISITO MÍNIMO PARA APROBAR**: El backend RPC debe funcionar para registrar pagos. Si no funciona, nota máxima = 4.9.

---

## SIGUIENTE PASO INMEDIATO

Continuar con la **FASE 3**: probar el backend RPC en local y pasar los 4 tests. Los comandos son:

```bash
cd /home/alumnos/e462971/Descargas/si2/si2_alumnos-main/P1-rpc-backend
python manage.py makemigrations
python manage.py migrate
python manage.py populate
python manage.py runserver 8001
# Verificar http://127.0.0.1:8001/visaAppRPCBackend/rpc → 405
# Ctrl+C y luego:
python manage.py test visaAppRPCBackend.tests_rpc_backend
# Deben pasar 4 tests
```
