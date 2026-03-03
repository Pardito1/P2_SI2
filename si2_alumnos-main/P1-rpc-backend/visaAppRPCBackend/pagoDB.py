# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# author: rmarabini
"Interface with the database - RPC Backend"
from visaAppRPCBackend.models import Tarjeta, Pago
from modernrpc.core import rpc_method
from django.forms.models import model_to_dict


@rpc_method
def verificar_tarjeta(tarjeta_data):
    """Check if the tarjeta is registered.
    :param tarjeta_data: dictionary with the tarjeta data
                         (numero, nombre, fechaCaducidad, codigoAutorizacion)
    :return: True if exists, False otherwise
    """
    if bool(tarjeta_data) is False or not \
       Tarjeta.objects.filter(**tarjeta_data).exists():
        return False
    return True


@rpc_method
def registrar_pago(pago_dict):
    """Register a payment in the database.
    :param pago_dict: dictionary with pago data
                      (idComercio, idTransaccion, importe, tarjeta_id)
    :return: dictionary with pago data if successful, None otherwise
    """
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
    """Delete a pago from the database.
    :param idPago: id (integer) of the pago to delete
    :return: True if successful, False otherwise
    """
    try:
        pago = Pago.objects.get(id=idPago)
    except Pago.DoesNotExist:
        return False
    pago.delete()
    return True


@rpc_method
def get_pagos_from_db(idComercio):
    """Get all pagos for a given comercio.
    :param idComercio: id of the comercio
    :return: list of dictionaries with pago data
    """
    pagos = Pago.objects.filter(idComercio=idComercio)
    lista_pagos = []
    for pago in pagos:
        pago_dict = model_to_dict(pago)
        pago_dict['marcaTiempo'] = str(pago.marcaTiempo)
        lista_pagos.append(pago_dict)
    return lista_pagos