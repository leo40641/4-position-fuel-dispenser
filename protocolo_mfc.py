import time
import threading
import serial
from funciones import *
from base_datos import *
import variables

casos_surt = {0: 'error', 6: 'espera', 7: 'listo', 8: 'autorizado', 9: 'surtiendo', 10: 'venta', 11: 'venta'}
casos_id = {1: 'libre', 2: 'leyendo', 3: 'leido'}


class ProtocoloMfc(threading.Thread):
    def __init__(self, out_lcd1_queque, out_lcd2_queque, in_mfc_queque, out_xbee_queque):
        threading.Thread.__init__(self)
        self.new_estado = 0
        self.old_estado = [0, 0, 0, 0, 0]
        self.ver_id = [0, 0, 0, 0, 0]
        self.puerto = serial.Serial('/dev/ttyS3', 115200, timeout=5)
        self.version = 6
        self.decimales_dinero = 0
        self.decimales_volumen = 3
        self.decimales_ppu = 0
        self.decimales_total_dinero = 0
        self.decimales_total_volumen = 2
        self.manguera_venta = 0
        self.dinero = 0
        self.volumen = 0
        self.ppu_venta = 0
        self.mangueras = 6
        self.funciones = Funciones()
        self.out_mfc = 0
        self.in_mfc_queque = in_mfc_queque
        self.out_xbee_queque = out_xbee_queque
        self.out_lcd1_queque = out_lcd1_queque
        self.out_lcd2_queque = out_lcd2_queque
        self.ok_surtiendo = [0, 0, 0, 0, 0]

    def enviar_recibir(self, trama, size):
        self.puerto.write(trama)
        total_data = self.puerto.read(size)
        return total_data

    def estado(self, pos):
        trama = [0x7E, pos, 0x01, 0x00, 0xEF, 0xFE]
        total_data = self.enviar_recibir(trama, 7)
        # print(total_data)
        if len(total_data) == 7:
            if (total_data[6] == 0xFE) and (total_data[5] == 0xEF):
                estado = total_data[4]
                return estado
            else:
                return 0
        else:
            return 0

    def pedir_totales(self, pos, mangueras):
        trama = [0x7E, pos, 0x02, 0x01, mangueras, 0xEF, 0xFE]
        total_data = self.enviar_recibir(trama, 78)
        print(total_data)
        if len(total_data) == 78:
            if (total_data[77] == 0xFE) and (total_data[76] == 0xEF):
                t_volumen1 = self.funciones.convertir_entero(total_data, 4, 12)
                t_dinero1 = self.funciones.convertir_entero(total_data, 16, 12)
                t_volumen2 = self.funciones.convertir_entero(total_data, 28, 12)
                t_dinero2 = self.funciones.convertir_entero(total_data, 40, 12)
                t_volumen3 = self.funciones.convertir_entero(total_data, 52, 12)
                t_dinero3 = self.funciones.convertir_entero(total_data, 64, 12)
                return t_dinero1, t_dinero2, t_dinero3, t_volumen1, t_volumen2, t_volumen3
            else:
                return 0, 0, 0, 0, 0, 0
        else:
            return 0, 0, 0, 0, 0, 0

    def cambiar_precio(self, pos, manguera, ppu):
        trama = [0x7E, pos, 0x03, 0x06, manguera, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEF, 0xFE]
        ppu_lista = list(map(int, str(ppu)))
        for i in range(5-len(ppu_lista)):
            ppu_lista.insert(0, 0)
        ppu_lista.reverse()
        for i in range(5):
            trama[i+5] = ppu_lista[i]
        total_data = self.enviar_recibir(trama, 7)
        print(total_data)
        if len(total_data) == 7:
            if (total_data[6] == 0xFE) and (total_data[5] == 0xEF):
                ok = total_data[4]
                return ok
            else:
                return 0
        else:
            return 0

    def pedir_manguera(self, pos):
        trama = [0x7E, pos, 0x04, 0x00, 0xEF, 0xFE]
        total_data = self.enviar_recibir(trama, 7)
        print(total_data)
        if len(total_data) == 7:
            if (total_data[6] == 0xFE) and (total_data[5] == 0xEF):
                manguera = total_data[4]
                return manguera
            else:
                return 0
        else:
            return 0

    def programar_venta(self, pos, manguera, preset, tipo_preset):
        trama = [0x7E, pos, 0x05, 0x09, manguera, tipo_preset, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xEF, 0xFE]
        preset_lista = list(map(int, str(preset)))
        for i in range(7-len(preset_lista)):
            preset_lista.insert(0, 0)
        preset_lista.reverse()
        for i in range(7):
            trama[i+6] = preset_lista[i]
        total_data = self.enviar_recibir(trama, 7)
        print(total_data)
        if len(total_data) == 7:
            if (total_data[6] == 0xFE) and (total_data[5] == 0xEF):
                ok = total_data[4]
                return ok
            else:
                return 0
        else:
            return 0

    def autorizar_venta(self, pos):
        trama = [0x7E, pos, 0x06, 0x00, 0xEF, 0xFE]
        total_data = self.enviar_recibir(trama, 7)
        print(total_data)
        if len(total_data) == 7:
            if (total_data[6] == 0xFE) and (total_data[5] == 0xEF):
                ok = total_data[4]
                return ok
            else:
                return 0
        else:
            return 0

    def reporte_venta(self, pos):
        trama = [0x7E, pos, 0x07, 0x00, 0xEF, 0xFE]
        total_data = self.enviar_recibir(trama, 26)
        print(total_data)
        if len(total_data) == 26:
            if (total_data[25] == 0xFE) and (total_data[24] == 0xEF):
                dinero = self.funciones.convertir_entero(total_data, 4, 7)
                volumen = self.funciones.convertir_entero(total_data, 11, 7)
                ppu = self.funciones.convertir_entero(total_data, 18, 5)
                manguera = total_data[23]
                return dinero, volumen, ppu, manguera
            else:
                return 0, 0, 0, 0
        else:
            return 0, 0, 0, 0

    def estado_id(self, pos):
        trama = [0x7E, pos, 0x08, 0x00, 0xEF, 0xFE]
        total_data = self.enviar_recibir(trama, 7)
        print(total_data)
        if len(total_data) == 7:
            if (total_data[6] == 0xFE) and (total_data[5] == 0xEF):
                estado = total_data[4]
                return estado
            else:
                return 0
        else:
            return 0

    def leer_id(self, pos, tipo_id):
        trama = [0x7E, pos, 0x09, 0x01, tipo_id, 0xEF, 0xFE]
        total_data = self.enviar_recibir(trama, 7)
        print(total_data)
        if len(total_data) == 7:
            if (total_data[6] == 0xFE) and (total_data[5] == 0xEF):
                ok = total_data[4]
                return ok
            else:
                return 0
        else:
            return 0

    def peticion_id(self, pos):
        trama = [0x7E, pos, 0x0A, 0x00, 0xEF, 0xFE]
        id = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        total_data = self.enviar_recibir(trama, 23)
        print(total_data)
        if len(total_data) == 23:
            if (total_data[22] == 0xFE) and (total_data[21] == 0xEF):
                for i in range(16):
                    id[i] = total_data[i+5]
                id = self.funciones.convertir_ibutton_to_string(id[0:8])
                return id
            else:
                return id
        else:
            return id

    def reset_id(self, pos):
        trama = [0x7E, pos, 0x0B, 0x00, 0xEF, 0xFE]
        total_data = self.enviar_recibir(trama, 7)
        print(total_data)
        if len(total_data) == 7:
            if (total_data[6] == 0xFE) and (total_data[5] == 0xEF):
                ok = total_data[4]
                return ok
            else:
                return 0
        else:
            return 0

    def imprimir(self, pos, size, no_copias, trama_print):
        trama = [0x7E, pos, 0x0C, no_copias, size, 0xEF, 0xFE]
        for i in range(size):
            trama[5+i] = trama_print[i]
        trama[size + 5] = 0xEF
        trama[size + 6] = 0xFE
        total_data = self.enviar_recibir(trama, 7)
        print(total_data)
        if len(total_data) == 7:
            if (total_data[6] == 0xFE) and (total_data[5] == 0xEF):
                ok = total_data[4]
                return ok
            else:
                return 0
        else:
            return 0

    def listo(self, pos):
        print('Listo: ' + str(pos))
        db.connect()
        venta_activa = VentasActivas.get(VentasActivas.id == pos).id_venta
        if venta_activa != 0:
            ok_autorizado = Ventas.get(Ventas.id == venta_activa).sync
            if ok_autorizado == 1:
                manguera = self.pedir_manguera(pos)
                manguera_auto = Ventas.get(Ventas.id == venta_activa).manguera
                if manguera == manguera_auto:
                    ppu = Ventas.get(Ventas.id == venta_activa).ppu
                    if self.cambiar_precio(pos, manguera, ppu) != 0:
                        preset = Ventas.get(Ventas.id == venta_activa).preset
                        tipo_preset = Ventas.get(Ventas.id == venta_activa).tipo_preset
                        if self.programar_venta(pos, manguera, preset, tipo_preset) != 0:
                            self.autorizar_venta(pos)
        db.close()

    @staticmethod
    def error(pos):
        print('Error: ' + str(pos))

    def espera(self, pos):
        if self.ok_surtiendo[pos] == 1:
            self.ok_surtiendo[pos] = 0
            db.connect()
            estado = Estado.update(estado_dragon=variables.estado_venta_cancelada).where(Estado.id == pos)
            estado.execute()
            venta_activa = VentasActivas.get(VentasActivas.id == pos).id_venta
            sync = Ventas.update(sync=6).where(Ventas.id == venta_activa)
            sync.execute()
            db.close()

    @staticmethod
    def autorizado(pos):
        print('Autorizado: ' + str(pos))

    def surtiendo(self, pos):
        if self.ok_surtiendo[pos] == 0:
            db.connect()
            venta_activa = VentasActivas.get(VentasActivas.id == pos).id_venta
            surtiendo = Ventas.select().where(Ventas.id == venta_activa).get()
            if surtiendo.sync == 1:
                surtiendo.sync = 2
                surtiendo.save()
                self.ok_surtiendo[pos] = 1
            db.close()

    def venta(self, pos):
        self.ok_surtiendo[pos] = 0
        dinero, volumen, ppu, manguera = self.reporte_venta(pos)
        t_dinero1, t_dinero2, t_dinero3, t_volumen1, t_volumen2, t_volumen3 = self.pedir_totales(pos, 3)
        db.connect()
        fecha_f = FechaActual.get_by_id(1).fecha
        venta_activa = VentasActivas.get(VentasActivas.id == pos).id_venta
        datos_venta = Ventas.select().where(Ventas.id == venta_activa).get()
        datos_venta.dinero = dinero
        datos_venta.volumen = volumen
        datos_venta.ppu = ppu
        datos_venta.fecha_fin = fecha_f
        datos_venta.sync = 3
        if datos_venta.manguera == 1:
            datos_venta.totales_fin_vol = t_volumen1
            datos_venta.totales_fin_din = t_dinero1
        elif datos_venta.manguera == 2:
            datos_venta.totales_fin_vol = t_volumen2
            datos_venta.totales_fin_din = t_dinero2
        elif datos_venta.manguera == 3:
            datos_venta.totales_fin_vol = t_volumen3
            datos_venta.totales_fin_din = t_dinero3
        datos_venta.save()
        totales = Totales.select().where(Totales.id == pos).get()
        totales.totales_vol_1 = t_volumen1
        totales.totales_din_1 = t_dinero1
        totales.totales_vol_2 = t_volumen2
        totales.totales_din_2 = t_dinero2
        totales.totales_vol_3 = t_volumen3
        totales.totales_din_3 = t_dinero3
        totales.save()
        estado = Estado.update(estado_dragon=variables.estado_venta).where(Estado.id == pos)
        estado.execute()
        db.close()

    def cargar_totales(self):
        db.connect()
        for i in range(1, 5):
            time.sleep(0.2)
            totales = Totales.select().where(Totales.id == i).get()
            t_dinero1, t_dinero2, t_dinero3, t_volumen1, t_volumen2, t_volumen3 = self.pedir_totales(i, 3)
            totales.totales_vol_1 = t_volumen1
            totales.totales_din_1 = t_dinero1
            totales.totales_vol_2 = t_volumen2
            totales.totales_din_2 = t_dinero2
            totales.totales_vol_3 = t_volumen3
            totales.totales_din_3 = t_dinero3
            totales.save()
        db.close()

    def cambiar_precios(self, pos):
        db.connect()
        precios = Precios.select().where(Precios.id == pos).get()
        self.cambiar_precio(pos, 1, precios.precio_1)
        self.cambiar_precio(pos, 2, precios.precio_2)
        self.cambiar_precio(pos, 3, precios.precio_3)
        db.close()

    def selec_caso(self, caso, pos):
        method_name = caso
        method = getattr(self, method_name, lambda: "error")
        return method(pos)

    def poll_surtidor(self, pos):
        self.new_estado = self.estado(pos)
        # print(self.new_estado)
        if self.new_estado != self.old_estado[pos]:
            self.old_estado[pos] = self.new_estado
            db.connect()
            estado = Estado.select().where(Estado.id == pos).get()
            estado.estado_surtidor = self.new_estado
            estado.save()
            db.close()
        if self.new_estado != 255:
            self.selec_caso(casos_surt[self.new_estado], pos)

    def poll_id(self, pos):
        if self.ver_id[pos] == 1:
            estado = self.estado_id(pos)
            if estado == 6:
                id = self.peticion_id(pos)
                self.ver_id[pos] = 0
                db.connect()
                autorizar = Autorizaciones.update(idenificador=id).where(Autorizaciones.id == pos)
                autorizar.execute()
                db.close()
                msg = variables.func_ok
                if pos == 1 or pos == 3:
                    self.out_lcd1_queque.put(msg)
                else:
                    self.out_lcd2_queque.put(msg)

    def run(self):
        while True:
            for i in range(1, 5):
                self.poll_surtidor(i)
                self.poll_id(i)
                ok_solicitud = self.in_mfc_queque.empty()
                if not ok_solicitud:
                    solicitud = self.in_mfc_queque.get()
                    if solicitud['funcion'] == variables.pedir_totales:
                        self.cargar_totales()
                        msg = variables.func_ok
                        if solicitud['fuente'] == 'xbee':
                            self.out_xbee_queque.put(msg)
                        elif solicitud['fuente'] == 'lcd1':
                            self.out_lcd1_queque.put(msg)
                        elif solicitud['fuente'] == 'lcd2':
                            self.out_lcd2_queque.put(msg)
                    elif solicitud['funcion'] == variables.cambiar_precios:
                        self.cambiar_precios(solicitud['pos'])
                        msg = variables.func_ok
                        self.out_xbee_queque.put(msg)
                    elif solicitud['funcion'] == variables.imprimir:
                        self.imprimir(solicitud['pos'], solicitud['size'], solicitud['copias'], solicitud['trama'])
                        msg = variables.func_ok
                        self.out_xbee_queque.put(msg)
                    elif solicitud['funcion'] == variables.pedir_id:
                        db.connect()
                        tipo_id = Autorizaciones.get_by_id(solicitud['pos']).tipo_id
                        db.close()
                        self.leer_id(solicitud['pos'], ord(tipo_id))
                        self.ver_id[solicitud['pos']] = 1
                    elif solicitud['funcion'] == variables.reset_id:
                        self.reset_id(solicitud['pos'])
