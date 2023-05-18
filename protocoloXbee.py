import time
import serial
import threading
from funciones import *
from base_datos import *
import variables

casos = {0xC0: 'config_inicial', 0xC1: 'peticion_estado', 0xC2: 'configurar_productos', 0xC3: 'cambiar_precios',
         0xC5: 'reset_mfc', 0xC6: 'reportar_venta', 0xD2: 'consignar', 0xCC: 'imprimir', 0xC8: 'pet_autorizar_venta',
         0xC9: 'autorizar_venta', 0xCA: 'datos_turno', 0xC7: 'pet_producto_canasta', 0xCB: 'datos_producto_canasta',
         0xCD: 'venta_canasta', 0xCE: 'autorizar_venta_canasta', 0xCF: 'confirmacion_turno', 0xD0: 'cerrar_turno'}


class ProtocoloXbee(threading.Thread):
    def __init__(self, out_lcd1_queque, out_lcd2_queque, out_mfc_queque, in_xbee_queque):
        threading.Thread.__init__(self)
        self.out_lcd1_queque = out_lcd1_queque
        self.out_lcd2_queque = out_lcd2_queque
        self.out_mfc_queque = out_mfc_queque
        self.in_xbee_queque = in_xbee_queque
        self.id_venta_activa = 0
        self.id_turno = 0
        self.puerto = serial.Serial('/dev/ttyS2', 115200, timeout=1)
        self.rxBufferXbee = list()
        self.txBufferXbee = list(range(300))
        self.rxBufferSize = 0
        self.txBufferSize = 0
        self.comandoIntegrador = 0
        self.fecha = [0, 0, 0]
        self.hora = [0, 0]
        self.funciones = Funciones()
        self.checksum = 0
        self.posicion = 0
        self.mangueras = 0
        self.ppux10 = 0
        self.placa_ob = 0
        self.decimales_din = 0
        self.decimales_vol = 0
        self.decimales_ppu = 0
        self.nombre_estacion = ' '
        self.direccion_estacion = ' '
        self.lema_1 = ' '
        self.lema_2 = ' '
        self.p1 = 0
        self.p2 = 0
        self.p3 = 0
        self.mfc_name = ' '
        self.nit_estacion = ' '
        self.size_trama_print = 0
        self.trama_print = list(range(4000))
        self.tiempo_ini = 0
        self.tiempo_fin = 0
        self.comunicacion = 1

    def enviar_respuesta(self, size):
        print(self.txBufferXbee[0: size])
        self.puerto.write(self.txBufferXbee[0: size])

    def config_inicial(self):
        self.fecha[2] = self.rxBufferXbee[17]
        self.fecha[1] = self.rxBufferXbee[18]
        self.fecha[0] = self.rxBufferXbee[19]
        self.hora[2] = self.rxBufferXbee[20]
        self.hora[1] = self.rxBufferXbee[21]
        self.hora[0] = self.rxBufferXbee[22]
        msg = {'funcion': variables.func_config_fecha, 'fecha': self.fecha, 'hora': self.hora}
        self.out_lcd1_queque.put(msg)
        self.out_lcd2_queque.put(msg)
        self.mangueras = (self.rxBufferXbee[24] & 0x0F) / 2
        self.ppux10 = self.rxBufferXbee[25] & 0x0F
        self.placa_ob = self.rxBufferXbee[26] & 0x0F
        self.decimales_din = self.rxBufferXbee[27] & 0x0F
        self.decimales_vol = self.rxBufferXbee[28] & 0x0F
        self.decimales_ppu = self.rxBufferXbee[29] & 0x0F
        self.nombre_estacion = self.funciones.convertir_string(self.rxBufferXbee, 30, 30)
        self.direccion_estacion = self.funciones.convertir_string(self.rxBufferXbee, 60, 30)
        self.lema_1 = self.funciones.convertir_string(self.rxBufferXbee, 90, 30)
        self.lema_2 = self.funciones.convertir_string(self.rxBufferXbee, 110, 30)
        self.p1 = self.funciones.convertir_entero(self.rxBufferXbee, 140, 7)
        self.p2 = self.funciones.convertir_entero(self.rxBufferXbee, 147, 7)
        self.p3 = self.funciones.convertir_entero(self.rxBufferXbee, 154, 7)
        self.mfc_name = self.funciones.convertir_string(self.rxBufferXbee, 162, 16)
        self.nit_estacion = self.funciones.convertir_string(self.rxBufferXbee, 178, 30)
        db.connect()
        surtidor = Surtidor(mangueras=self.mangueras, ppux10=self.ppux10, placa_ob=self.placa_ob,
                            decimales_din=self.decimales_din, decimales_vol=self.decimales_vol,
                            decimales_ppu=self.decimales_ppu, nombre_estacion=self.nombre_estacion,
                            direccion_estacion=self.direccion_estacion, lema_1=self.lema_1, lema_2=self.lema_2,
                            p1=self.p1, p2=self.p2, p3=self.p3, mfc_name=self.mfc_name, nit_estacion=self.nit_estacion)
        surtidor.save()
        db.close()
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wconfiguraciones_iniciales
        self.txBufferXbee[19] = variables.ack
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)

    def peticion_estado(self):
        db.connect()
        estado = Estado.get(Estado.id == self.posicion).estado_dragon
        db.close()
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wpeticion_estado
        self.txBufferXbee[19] = estado
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)

    def configurar_productos(self):
        index1 = self.rxBufferXbee.index(59)
        nombre_producto1 = self.funciones.convertir_string(self.rxBufferXbee, 17, (index1 - 17))
        self.rxBufferXbee.remove(59)
        index2 = self.rxBufferXbee.index(59)
        nombre_producto2 = self.funciones.convertir_string(self.rxBufferXbee, index1, (index2 - index1))
        self.rxBufferXbee.remove(59)
        index3 = self.rxBufferXbee.index(59)
        nombre_producto3 = self.funciones.convertir_string(self.rxBufferXbee, index1, (index3 - index2))
        msg = {'funcion': variables.func_config_productos, 'producto1': nombre_producto1, 'producto2': nombre_producto2,
               'producto3': nombre_producto3}
        self.out_lcd1_queque.put(msg)
        self.out_lcd2_queque.put(msg)
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wconfigurar_productos
        self.txBufferXbee[19] = variables.ack
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def cambiar_precios(self):
        ppu1 = self.funciones.convertir_entero(self.rxBufferXbee, 17, 5)
        ppu2 = self.funciones.convertir_entero(self.rxBufferXbee, 22, 5)
        ppu3 = self.funciones.convertir_entero(self.rxBufferXbee, 27, 5)
        db.connect()
        precios = Precios.select().where(Precios.id == self.posicion).get()
        precios.precio_1 = ppu1
        precios.precio_2 = ppu2
        precios.precio_3 = ppu3
        precios.save()
        db.close()
        msg = {'funcion': variables.cambiar_precios, 'pos': self.posicion}
        self.out_mfc_queque.put(msg)
        ok_cambio = 0
        while ok_cambio != variables.func_ok:
            ok_cambio = self.in_xbee_queque.get()
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wcambiar_precios
        self.txBufferXbee[19] = variables.ack
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)

    def reset_mfc(self):
        casos_reset = {1: 'reset_venta', 2: 'reset_venta_canasta', 3: 'reset_cancelada', 4: 'reset_reimpresion',
                       6: 'reset_consig', 7: 'obligar_consignar', 8: 'reset_consignar', 9: 'reset_fpagos'}
        tipo_reset = casos_reset[self.rxBufferXbee[17]]
        db.connect()
        estado_dragon = Estado.get(Estado.id == self.posicion).estado_dragon
        db.close()
        if tipo_reset == 'reset_venta':
            if estado_dragon == variables.estado_venta:
                db.connect()
                self.id_venta_activa = VentasActivas.get(VentasActivas.id == self.posicion).id_venta
                venta = Ventas.select().where(Ventas.id == self.id_venta_activa).get()
                venta.sync = 4
                venta.save()
                estado = Estado.select().where(Estado.id == self.posicion).get()
                estado.estado_dragon = variables.estado_libre
                estado.save()
                db.close()
                self.id_venta_activa[self.posicion - 1] = 0
        elif tipo_reset == 'reset_venta_canasta':
            if estado_dragon[self.posicion - 1] == variables.estado_venta_canasta:
                db.connect()
                estado = Estado.select().where(Estado.id == self.posicion).get()
                estado.estado_dragon = variables.estado_libre
                estado.save()
                db.close()
        elif tipo_reset == 'reset_cancelada':
            if estado_dragon == variables.estado_venta_cancelada:
                db.connect()
                estado = Estado.select().where(Estado.id == self.posicion).get()
                estado.estado_dragon = variables.estado_libre
                estado.save()
                db.close()
        elif tipo_reset == 'reset_reimpresion':
            if estado_dragon == variables.estado_imp_turno or \
                    estado_dragon == variables.estado_imp_venta or \
                    estado_dragon == variables.estado_imp_venta_opues or \
                    estado_dragon == variables.estado_arqueo:
                db.connect()
                estado = Estado.select().where(Estado.id == self.posicion).get()
                estado.estado_dragon = variables.estado_libre
                estado.save()
                db.close()
        elif tipo_reset == 'reset_consig':
            if estado_dragon == variables.estado_consignacion:
                db.connect()
                estado = Estado.select().where(Estado.id == self.posicion).get()
                estado.estado_dragon = variables.estado_libre
                estado.save()
                db.close()
        elif tipo_reset == 'obligar_consignar':
            msg = {'funcion': variables.func_obligar_consig}
            if (self.posicion % 2) == 1:
                self.out_lcd1_queque.put(msg)
            else:
                self.out_lcd2_queque.put(msg)
        elif tipo_reset == 'reset_consignar':
            msg = {'funcion': variables.func_reset_consig}
            if (self.posicion % 2) == 1:
                self.out_lcd1_queque.put(msg)
            else:
                self.out_lcd2_queque.put(msg)
        elif tipo_reset == 'reset_fpagos':
            print('falta')
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wreset
        self.txBufferXbee[19] = variables.ack
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def reportar_venta(self):
        db.connect()
        self.id_venta_activa = VentasActivas.get(VentasActivas.id == self.posicion).id_venta
        venta = Ventas.select().where(Ventas.id == self.id_venta_activa).get()
        db.close()
        manguera = venta.manguera
        dinero = format(str(venta.dinero), ">07s")
        dinero = dinero[::-1]
        volumen = format(str(venta.volumen), ">07s")
        volumen = volumen[::-1]
        ppu = format(str(venta.ppu), ">07s")
        ppu = ppu[::-1]
        placa = venta.placa
        tipo_id = venta.tipo_id
        if tipo_id == 'I':
            id_cliente = self.funciones.convertir_string_to_ibutton(venta.id_cliente)
        else:
            id_cliente = venta.id_cliente
        km = venta.km
        fecha_ini = self.funciones.convertir_fecha_to_lista(venta.fecha_ini)
        fecha_fin = self.funciones.convertir_fecha_to_lista(venta.fecha_fin)
        tipo_venta = venta.tipo_venta
        tipo_preset = venta.tipo_preset
        preset = format(str(venta.preset), ">07s")
        preset = preset[::-1]
        tipo_id_vendedor = venta.tipo_id_vendedor
        id_vendedor = venta.id_vendedor
        totales_ini_vol = format(str(venta.totales_ini_vol), ">012s")
        totales_ini_vol = totales_ini_vol[::-1]
        totales_ini_din = format(str(venta.totales_ini_din), ">012s")
        totales_ini_din = totales_ini_din[::-1]
        totales_ini = totales_ini_vol + totales_ini_din
        totales_fin_vol = format(str(venta.totales_fin_vol), ">012s")
        totales_fin_vol = totales_fin_vol[::-1]
        totales_fin_din = format(str(venta.totales_fin_din), ">012s")
        totales_fin_din = totales_fin_din[::-1]
        totales_fin = totales_fin_vol + totales_fin_din
        nit = venta.nit
        cedula = venta.cedula
        no_print = venta.no_print
        volumen_redimido = format(str(venta.volumen_redimido), ">07s")
        volumen_redimido = volumen_redimido[::-1]
        tipo_vehiculo = venta.tipo_vehiculo
        self.txBufferSize = 176
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0xAC
        self.txBufferXbee[18] = variables.wreset
        self.txBufferXbee[19] = manguera
        for i in range(7):
            self.txBufferXbee[20 + i] = ord(dinero[i]) & 0x0F
            self.txBufferXbee[27 + i] = ord(volumen[i]) & 0x0F
        for i in range(5):
            self.txBufferXbee[34 + i] = ord(ppu[i]) & 0x0F
        for i in range(5):
            self.txBufferXbee[39 + i] = placa[i]
        self.txBufferXbee[45] = tipo_id
        for i in range(10):
            self.txBufferXbee[46 + i] = id_cliente[i]
            self.txBufferXbee[56 + i] = km[i]
        for i in range(6):
            self.txBufferXbee[66 + i] = fecha_ini[i]
            self.txBufferXbee[72 + i] = fecha_fin[i]
        self.txBufferXbee[78] = tipo_venta
        self.txBufferXbee[79] = tipo_preset
        for i in range(7):
            self.txBufferXbee[80 + i] = ord(preset[i]) & 0x0F
        self.txBufferXbee[87] = tipo_id_vendedor
        for i in range(10):
            self.txBufferXbee[88 + i] = id_vendedor[i]
        for i in range(24):
            self.txBufferXbee[98 + i] = ord(totales_ini[i]) & 0x0F
            self.txBufferXbee[122 + i] = ord(totales_fin[i]) & 0x0F
        for i in range(10):
            self.txBufferXbee[156 + i] = nit[i]
            self.txBufferXbee[146 + i] = cedula[i]
        self.txBufferXbee[166] = no_print
        for i in range(7):
            self.txBufferXbee[167 + i] = ord(volumen_redimido[i]) & 0x0F
        self.txBufferXbee[174] = tipo_vehiculo
        self.checksum = 0
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[175] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def consignar(self):
        db.connect()
        consignacion = Consignaciones.select().where(Consignaciones.id == self.posicion).get()
        db.close()
        valor = format(str(consignacion.valor), ">07s")
        valor = valor[::-1]
        fecha = self.funciones.convertir_fecha_to_lista(consignacion.fecha)
        id_vendedor = consignacion.id_vendedor
        self.txBufferSize = 44
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x28
        self.txBufferXbee[18] = variables.wconsignacion
        for i in range(7):
            self.txBufferXbee[19 + i] = ord(valor[i]) & 0x0F
        for i in range(6):
            self.txBufferXbee[26 + i] = fecha[i]
        self.txBufferXbee[32] = 'C'
        for i in range(10):
            self.txBufferXbee[33 + i] = id_vendedor[i]
        self.checksum = 0
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[43] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def imprimir(self):
        size = ((self.rxBufferXbee[1] << 8) | self.rxBufferXbee[2]) + 3
        self.size_trama_print = size + self.size_trama_print
        if self.rxBufferXbee[17] != 0:
            for i in range(18, size):
                self.trama_print[self.size_trama_print + i - 18] = self.rxBufferXbee[i]
            pos_print = self.posicion
            no_copias = self.rxBufferXbee[17]
            msg = {'funcion': variables.reset_id, 'pos': pos_print, 'copias': no_copias,
                   'size': self.size_trama_print, 'trama': self.trama_print}
            self.out_mfc_queque.put(msg)
            ok_cambio = 0
            while ok_cambio != variables.func_ok:
                ok_cambio = self.in_xbee_queque.get()
        else:
            for i in range(18, size):
                self.trama_print[self.size_trama_print + i - 18] = self.rxBufferXbee[i]
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wimprimir
        self.txBufferXbee[19] = variables.ack
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def pet_autorizar_venta(self):
        db.connect()
        autorizacion = Autorizaciones.select().where(Autorizaciones.id == self.posicion).get()
        db.close()
        tipo_id = autorizacion.tipo_id
        if tipo_id == 'I':
            identificador = self.funciones.convertir_string_to_ibutton(autorizacion.identificador)
        else:
            identificador = autorizacion.identificador
        km = autorizacion.km
        tipo_venta = autorizacion.tipo_venta
        combustible = autorizacion.combustible
        manguera = autorizacion.manguera
        self.txBufferSize = 55
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x33
        self.txBufferXbee[18] = variables.wpautorizarventa
        self.txBufferXbee[19] = tipo_id
        for i in range(10):
            self.txBufferXbee[20 + i] = identificador[i]
        for i in range(10):
            self.txBufferXbee[30 + i] = km[i]
        self.txBufferXbee[40] = tipo_venta
        self.txBufferXbee[41] = combustible
        self.txBufferXbee[42] = 'I'
        for i in range(10):
            self.txBufferXbee[43 + i] = 0
        self.txBufferXbee[53] = manguera
        self.checksum = 0
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[54] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def autorizar_venta(self):
        tipo_preset = self.txBufferXbee[18]
        msj_lcd = "".join(self.txBufferXbee[19:117])
        autorizacion = self.txBufferXbee[17]
        cantidad_auto = self.funciones.convertir_entero(self.txBufferXbee, 119, 7)
        is_auto_man_1 = self.txBufferXbee[119]
        is_auto_man_2 = (self.txBufferXbee[130] >> 1) & 1
        is_auto_man_3 = self.txBufferXbee[141]
        ppu_1 = self.funciones.convertir_entero(self.txBufferXbee, 120, 5)
        ppu_2 = self.funciones.convertir_entero(self.txBufferXbee, 131, 7)
        ppu_3 = self.funciones.convertir_entero(self.txBufferXbee, 142, 7)
        db.connect()
        sentencia = Autorizaciones.select().where(Autorizaciones.id == self.posicion).get()
        sentencia.tipo_preset = tipo_preset
        sentencia.msg_lcd = msj_lcd
        sentencia.autorizacion = autorizacion
        sentencia.cantidad_auto = cantidad_auto
        sentencia.is_auto_man_1 = is_auto_man_1
        sentencia.is_auto_man_2 = is_auto_man_2
        sentencia.is_auto_man_3 = is_auto_man_3
        sentencia.ppu_1 = ppu_1
        sentencia.ppu_2 = ppu_2
        sentencia.ppu_3 = ppu_3
        sentencia.save()
        estado = Estado.select().where(Estado.id == self.posicion).get()
        estado.estado_dragon = variables.estado_libre
        estado.save()
        db.close()
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wautorizarventa
        self.txBufferXbee[19] = variables.ack
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def datos_turno(self):
        db.connect()
        if self.posicion < 3:
            turno_activo = TurnosActivos.get(TurnosActivos.id == 1).id_turno
        else:
            turno_activo = TurnosActivos.get(TurnosActivos.id == 1).id_turno2
        self.id_turno = turno_activo
        turno = Turnos.select().where(Turnos.id == self.id_turno).get()
        db.close()
        tipo_peticion = turno.tipo_peticion
        tipo_id = turno.tipo_id
        cedula_vendedor = turno.cedula_vendedor
        fecha = self.funciones.convertir_fecha_to_lista(turno.fecha)
        ppu_1_1 = turno.ppu_1_1
        totales_vol_1_1 = format(str(turno.totales_vol_1_1), ">012s")
        totales_din_1_1 = format(str(turno.totales_din_1_1), ">012s")
        ppu_1_2 = format(str(turno.ppu_1_2), ">05s")
        totales_vol_1_2 = format(str(turno.totales_vol_1_2), ">012s")
        totales_din_1_2 = format(str(turno.totales_din_1_2), ">012s")
        ppu_1_3 = format(str(turno.ppu_1_3), ">05s")
        totales_vol_1_3 = format(str(turno.totales_vol_1_3), ">012s")
        totales_din_1_3 = format(str(turno.totales_din_1_3), ">012s")
        ppu_2_1 = format(str(turno.ppu_2_1), ">05s")
        totales_vol_2_1 = format(str(turno.totales_vol_2_1), ">012s")
        totales_din_2_1 = format(str(turno.totales_din_2_1), ">012s")
        ppu_2_2 = format(str(turno.ppu_2_2), ">05s")
        totales_vol_2_2 = format(str(turno.totales_vol_2_2), ">012s")
        totales_din_2_2 = format(str(turno.totales_din_2_2), ">012s")
        ppu_2_3 = format(str(turno.ppu_2_3), ">05s")
        totales_vol_2_3 = format(str(turno.totales_vol_2_3), ">012s")
        totales_din_2_3 = format(str(turno.totales_din_2_3), ">012s")
        totales = ppu_1_1 + totales_vol_1_1 + totales_din_1_1 + ppu_1_2 + totales_vol_1_2 + totales_din_1_2 + ppu_1_3 \
                  + totales_vol_1_3 + totales_din_1_3 + ppu_2_1 + totales_vol_2_1 + totales_din_2_1 + ppu_2_2 + \
                  totales_vol_2_2 + totales_din_2_2 + ppu_2_3 + totales_vol_2_3 + totales_din_2_3
        password = turno.password
        self.txBufferSize = 216
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0xD4
        self.txBufferXbee[18] = variables.wdatosturno
        self.txBufferXbee[19] = tipo_peticion
        self.txBufferXbee[20] = tipo_id
        for i in range(10):
            self.txBufferXbee[21 + i] = cedula_vendedor[i]
        for i in range(6):
            self.txBufferXbee[21 + i] = fecha[i]
        for i in range(174):
            self.txBufferXbee[37 + i] = ord(totales[i]) & 0x0F
        for i in range(4):
            self.txBufferXbee[211 + i] = password[i]
        self.checksum = 0
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[215] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def pet_producto_canasta(self):
        db.connect()
        autorizacion = Autorizaciones.select().where(Autorizaciones == self.posicion).get()
        db.close()
        self.txBufferSize = 34
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x1E
        self.txBufferXbee[18] = variables.wpet_producto_canasta
        self.txBufferXbee[19:31] = autorizacion.idenificador
        self.txBufferXbee[32] = 'B'
        self.checksum = 0
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[33] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def datos_producto_canasta(self):
        produco_encontrado = self.txBufferXbee[17] + 1
        nombre_producto_canasta = self.txBufferXbee[18:38]
        valor_producto_canasta = self.funciones.convertir_entero(self.txBufferXbee, 38, 7)
        db.connect()
        indice = Autorizaciones.get(Autorizaciones.id == self.posicion).indice_canasta
        if indice == 1:
            sentencia = VentaCanasta.select(VentaCanasta.id == self.posicion).get()
            sentencia.nom_prod_1 = nombre_producto_canasta
            sentencia.val_prod_1 = valor_producto_canasta
            sentencia.ok_pro_1 = produco_encontrado
            sentencia.save()
        elif indice == 2:
            sentencia = VentaCanasta.select(VentaCanasta.id == self.posicion).get()
            sentencia.nom_prod_2 = nombre_producto_canasta
            sentencia.val_prod_2 = valor_producto_canasta
            sentencia.ok_pro_2 = produco_encontrado
            sentencia.save()
        elif indice == 3:
            sentencia = VentaCanasta.select(VentaCanasta.id == self.posicion).get()
            sentencia.nom_prod_3 = nombre_producto_canasta
            sentencia.val_prod_3 = valor_producto_canasta
            sentencia.ok_pro_3 = produco_encontrado
            sentencia.save()
        elif indice == 4:
            sentencia = VentaCanasta.select(VentaCanasta.id == self.posicion).get()
            sentencia.nom_prod_3 = nombre_producto_canasta
            sentencia.val_prod_3 = valor_producto_canasta
            sentencia.ok_pro_3 = produco_encontrado
            sentencia.save()
        estado = Estado.select().where(Estado.id == self.posicion).get()
        estado.estado_dragon = variables.estado_libre
        estado.save()
        db.close()
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wdatosproductocanasta
        self.txBufferXbee[19] = variables.ack
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def venta_canasta(self):
        db.connect()
        venta_canasta = VentaCanasta.select().where(VentaCanasta.id == self.posicion).get()
        db.close()
        fecha = self.funciones.convertir_fecha_to_lista(venta_canasta.fecha)
        id_producto_canasta_1 = venta_canasta.id_producto_canasta_1
        cantidad_producto_canasta_1 = venta_canasta.cantidad_producto_canasta_1
        valor_producto_canasta_1 = format(str(venta_canasta.valor_producto_canasta_1), ">07s")
        id_producto_canasta_2 = venta_canasta.id_producto_canasta_2
        cantidad_producto_canasta_2 = venta_canasta.cantidad_producto_canasta_2
        valor_producto_canasta_2 = format(str(venta_canasta.cantidad_producto_canasta_2), ">07s")
        id_producto_canasta_3 = venta_canasta.id_producto_canasta_3
        cantidad_producto_canasta_3 = venta_canasta.cantidad_producto_canasta_3
        valor_producto_canasta_3 = format(str(venta_canasta.valor_producto_canasta_3), ">07s")
        id_producto_canasta_4 = venta_canasta.id_producto_canasta_4
        cantidad_producto_canasta_4 = venta_canasta.cantidad_producto_canasta_4
        valor_producto_canasta_4 = format(str(venta_canasta.valor_producto_canasta_4), ">07s")
        tipo_venta = venta_canasta.tipo_venta
        tipo_id_canasta = venta_canasta.tipo_id_canasta
        id_cliente_canasta = venta_canasta.id_cliente_canasta
        id_vendedor_canasta = venta_canasta.id_vendedor_canasta
        no_impresiones_canasta = venta_canasta.no_impresiones_canasta
        self.txBufferSize = 134
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x82
        self.txBufferXbee[18] = variables.wventacanasta
        for i in range(6):
            self.txBufferXbee[19 + i] = fecha[i]
        self.txBufferXbee[25:38] = id_producto_canasta_1
        self.txBufferXbee[38] = cantidad_producto_canasta_1
        self.txBufferXbee[39:46] = valor_producto_canasta_1
        self.txBufferXbee[46:59] = id_producto_canasta_2
        self.txBufferXbee[59] = cantidad_producto_canasta_2
        self.txBufferXbee[60:67] = valor_producto_canasta_2
        self.txBufferXbee[67:80] = id_producto_canasta_3
        self.txBufferXbee[80] = cantidad_producto_canasta_3
        self.txBufferXbee[81:88] = valor_producto_canasta_3
        self.txBufferXbee[88:101] = id_producto_canasta_4
        self.txBufferXbee[101] = cantidad_producto_canasta_4
        self.txBufferXbee[102:109] = valor_producto_canasta_4
        self.txBufferXbee[109] = tipo_venta
        self.txBufferXbee[110] = tipo_id_canasta
        self.txBufferXbee[111:121] = id_cliente_canasta
        self.txBufferXbee[121] = 'C'
        self.txBufferXbee[122:132] = id_vendedor_canasta
        self.txBufferXbee[132] = no_impresiones_canasta
        self.checksum = 0
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[133] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def autorizar_venta_canasta(self):
        msj_lcd = "".join(self.txBufferXbee[18:87])
        autorizacion = self.txBufferXbee[17]
        cantidad_auto = self.funciones.convertir_entero(self.txBufferXbee, 119, 7)
        db.connect()
        sentencia = Autorizaciones.select().where(Autorizaciones.id == self.posicion).get()
        sentencia.msg_lcd = msj_lcd
        sentencia.autorizacion = autorizacion
        sentencia.cantidad_auto = cantidad_auto
        sentencia.save()
        estado = Estado.select().where(Estado.id == self.posicion).get()
        estado.estado_dragon = variables.estado_libre
        estado.save()
        db.close()
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wautorizaventacanasta
        self.txBufferXbee[19] = variables.ack
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def confirmacion_turno(self):
        ok = self.rxBufferXbee[17]
        db.connect()
        if self.posicion < 3:
            turno_activo = TurnosActivos.get(TurnosActivos.id == 1).id_turno
        else:
            turno_activo = TurnosActivos.get(TurnosActivos.id == 1).id_turno2
        self.id_turno = turno_activo
        if ok == 1:
            estado_turno = self.rxBufferXbee[52]
            turno = Turnos.select().where(Turnos.id == self.id_turno).get()
            turno.estado_actual = estado_turno
            turno.sync = 4
            turno.save()
        else:
            turno = Turnos.select().where(Turnos.id == self.id_turno).get()
            turno.sync = 3
            turno.save()
        msg = {'funcion': variables.reset_id}
        if (self.posicion % 2) == 1:
            self.out_lcd1_queque.put(msg)
        else:
            self.out_lcd2_queque.put(msg)
        estado = Estado.select().where(Estado.id == self.posicion).get()
        estado.estado_dragon = variables.estado_libre
        estado.save()
        db.close()
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wconfirmacionturno
        self.txBufferXbee[19] = variables.ack
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def cerrar_turno(self):
        tipo_peticion = 0
        fecha = time.strftime("%Y%m%d%H%M%S")
        msg = {'funcion': variables.pedir_totales, 'fuente': 'xbee'}
        self.out_mfc_queque.put(msg)
        ok_cambio = 0
        while ok_cambio != variables.func_ok:
            ok_cambio = self.in_xbee_queque.get()
        db.connect()
        totales_1 = Totales.select().where(Totales.id == 1).get()
        totales_2 = Totales.select().where(Totales.id == 2).get()
        totales_3 = Totales.select().where(Totales.id == 3).get()
        totales_4 = Totales.select().where(Totales.id == 4).get()
        if self.posicion < 3:
            id_turno = TurnosActivos.get_by_id(1).id_turno
        else:
            id_turno = TurnosActivos.get_by_id(1).id_turno2
        turno = Turnos.select().where(Turnos.id == id_turno).get()
        if self.posicion == 1 or self.posicion == 2:
            ppu_1_1 = totales_1.ppu_1
            totales_vol_1_1 = totales_1.totales_vol_1
            totales_din_1_1 = totales_1.totales_din_1
            ppu_1_2 = totales_1.ppu_2
            totales_vol_1_2 = totales_1.totales_vol_2
            totales_din_1_2 = totales_1.totales_din_2
            ppu_1_3 = totales_1.ppu_3
            totales_vol_1_3 = totales_1.totales_vol_3
            totales_din_1_3 = totales_1.totales_din_3
            ppu_2_1 = totales_2.ppu_1
            totales_vol_2_1 = totales_2.totales_vol_1
            totales_din_2_1 = totales_2.totales_din_1
            ppu_2_2 = totales_2.ppu_2
            totales_vol_2_2 = totales_2.totales_vol_2
            totales_din_2_2 = totales_2.totales_din_2
            ppu_2_3 = totales_2.ppu_3
            totales_vol_2_3 = totales_2.totales_vol_3
            totales_din_2_3 = totales_2.totales_din_3
        else:
            ppu_1_1 = totales_3.ppu_1
            totales_vol_1_1 = totales_3.totales_vol_1
            totales_din_1_1 = totales_3.totales_din_1
            ppu_1_2 = totales_3.ppu_2
            totales_vol_1_2 = totales_3.totales_vol_2
            totales_din_1_2 = totales_3.totales_din_2
            ppu_1_3 = totales_3.ppu_3
            totales_vol_1_3 = totales_3.totales_vol_3
            totales_din_1_3 = totales_3.totales_din_3
            ppu_2_1 = totales_4.ppu_1
            totales_vol_2_1 = totales_4.totales_vol_1
            totales_din_2_1 = totales_4.totales_din_1
            ppu_2_2 = totales_4.ppu_2
            totales_vol_2_2 = totales_4.totales_vol_2
            totales_din_2_2 = totales_4.totales_din_2
            ppu_2_3 = totales_4.ppu_3
            totales_vol_2_3 = totales_4.totales_vol_3
            totales_din_2_3 = totales_4.totales_din_3
        estado_actual = turno.estado_actual
        tipo_id = 'C'
        cedula_vendedor = turno.cedula_vendedor
        password = turno.password
        pos = self.posicion
        sync = 1
        Turnos.create(tipo_peticion=tipo_peticion, estado_actual=estado_actual, tipo_id=tipo_id,
                      cedula_vendedor=cedula_vendedor, fecha=fecha, ppu_1_1=ppu_1_1,
                      totales_vol_1_1=totales_vol_1_1,
                      totales_din_1_1=totales_din_1_1, ppu_1_2=ppu_1_2, totales_vol_1_2=totales_vol_1_2,
                      totales_din_1_2=totales_din_1_2, ppu_1_3=ppu_1_3, totales_vol_1_3=totales_vol_1_3,
                      totales_din_1_3=totales_din_1_3, ppu_2_1=ppu_2_1, totales_vol_2_1=totales_vol_2_1,
                      totales_din_2_1=totales_din_2_1, ppu_2_2=ppu_2_2, totales_vol_2_2=totales_vol_2_2,
                      totales_din_2_2=totales_din_2_2, ppu_2_3=ppu_2_3, totales_vol_2_3=totales_vol_2_3,
                      totales_din_2_3=totales_din_2_3, password=password, pos=pos, sync=sync)
        id_actual = Turnos.select().order_by(Turnos.id.desc()).get()
        if self.posicion < 3:
            turno_activo = TurnosActivos.select().where(TurnosActivos.id == 1)
            turno_activo.id_turno = id_actual
            turno_activo.save()
        else:
            turno_activo = TurnosActivos.select().where(TurnosActivos.id == 1)
            turno_activo.id_turno2 = id_actual
            turno_activo.save()
        db.close()
        self.txBufferXbee[1] = 0
        self.txBufferXbee[2] = 0x11
        self.txBufferXbee[18] = variables.wpet_cerrar_turno
        self.txBufferXbee[19] = variables.ack
        self.checksum = 0
        self.txBufferSize = 21
        for i in range(3, (self.txBufferSize - 1)):
            self.checksum += self.txBufferXbee[i]
        self.checksum = 0xFF - (self.checksum & 0xFF)
        self.txBufferXbee[20] = self.checksum
        self.enviar_respuesta(self.txBufferSize)
        self.rxBufferXbee.clear()

    def leer_puerto(self):
        size = self.puerto.in_waiting
        time.sleep(0.005)
        size_aux = self.puerto.in_waiting
        if (size == size_aux) and size > 10:
            self.rxBufferSize = self.puerto.in_waiting
            self.rxBufferXbee = self.puerto.read(self.rxBufferSize)
            if (self.rxBufferXbee[0] == 0x7E) and (self.rxBufferXbee[3] == 0x90):
                self.txBufferXbee[0] = 0x7E
                self.txBufferXbee[3] = 0x10
                self.txBufferXbee[4] = 0x01
                self.txBufferXbee[5] = self.rxBufferXbee[4]
                self.txBufferXbee[6] = self.rxBufferXbee[5]
                self.txBufferXbee[7] = self.rxBufferXbee[6]
                self.txBufferXbee[8] = self.rxBufferXbee[7]
                self.txBufferXbee[9] = self.rxBufferXbee[8]
                self.txBufferXbee[10] = self.rxBufferXbee[9]
                self.txBufferXbee[11] = self.rxBufferXbee[10]
                self.txBufferXbee[12] = self.rxBufferXbee[11]
                self.txBufferXbee[13] = 0xFF
                self.txBufferXbee[14] = 0xFE
                self.txBufferXbee[15] = 0x00
                self.txBufferXbee[16] = 0x00
                self.txBufferXbee[17] = self.rxBufferXbee[15]
                self.comandoIntegrador = self.rxBufferXbee[16]
                self.posicion = self.rxBufferXbee[15]
                return 1
            else:
                return 0
        else:
            return 0

    def run(self):
        while True:
            if self.leer_puerto():
                method_name = casos[self.comandoIntegrador]
                method = getattr(self, method_name, lambda: "error")
                method()
