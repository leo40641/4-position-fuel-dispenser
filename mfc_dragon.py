#!/usr/bin/python

import queue
from base_datos import *
from protocoloXbee import *
from protocolo_mfc import *
from protocoloLcd import *


def init_dragon():
    lcd1_queue = queue.Queue()
    lcd2_queue = queue.Queue()
    mfc_queue = queue.Queue()
    xbee_queue = queue.Queue()

    initDb()

    db.connect()
    estado = Estado.update(estado_dragon=1).where(Estado.id < 5)
    estado.execute()
    db.close()

    db.connect()
    estado = Precios.update(precio_1=8700, precio_2=9400, precio_3=7800).where(Precios.id < 5)
    estado.execute()
    db.close()

    xbee = ProtocoloXbee(lcd1_queue, lcd2_queue, mfc_queue, xbee_queue)
    xbee.start()

    mfc = ProtocoloMfc(lcd1_queue, lcd2_queue, mfc_queue, xbee_queue)
    mfc.start()

    lcd1 = ProtocoloLcd(lcd1_queue, mfc_queue)
    lcd1.configurar_puerto('/dev/ttyUSB0', 1)
    lcd1.start()


if __name__ == '__main__':
    init_dragon()
