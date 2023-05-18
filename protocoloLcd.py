import threading
from base_datos import *
from funciones import *
import serial
import time
import variables

casos = {0: 'pantalla_inicial', 1: 'escoger_lado', 2: 'menu_inicial', 3: 'menu_tipo_venta', 4: 'escoger_producto',
         5: 'escoger_tipo_vehiculo', 6: 'presetear', 7: 'datos_cliente', 8: 'f_no_recibos', 9: 'subir_manija',
         10: 'escoger_id', 11: 'pedir_km', 12: 'esperar_autorizacion', 13: 'menu_turno', 14: 'elegir_id_t',
         15: 'cerrar_t', 16: 'clave_turno', 17: 'esperar_turno', 18: 'abrir_sin_sys'}

# botones
b_opcion_1 = 0x2131
b_opcion_2 = 0x4032
b_opcion_3 = 0x2333
b_devolver = 0x00F3
b_ladoA = 0x2536
b_ladoB = 0x2537
b_imprimir = 0xF3
b_si = 0x5373
b_no = 0x4E6E

# imagenes
img_fcs = 0
img_escoger_lado = 98
img_menu_inicial = 11
img_ventas = 12
img_tipo_venta = 62
img_dvf = 13
img_cre = 22
img_fide = 19
img_escoger_pro_3 = 70
img_escoger_pro_2 = 71
img_tipo_vehiculo = 73
img_subirmanija = 44
img_datos_venta = 17
img_no_recibos = 18
img_subir_manija = 44
img_elegir_id_credito = 56
img_ibutton = 41
img_km_venta_id = 54
img_esperando = 47
img_sumi_no_auto = 26
img_sumi_auto = 27
img_sel_turno = 29
img_sel_id_t = 30
img_confir_cerra_t = 34
img_clave_turno = 67
img_turno_abierto = 33
img_turno_cerrado = 31
img_abrir_sin_sis = 32

# Memoria LCD
vp_valor_dinero = 0x200
vp_valor_vol = 0x204
vp_valor_placa = 0x208
vp_valor_cedula = 0x214
vp_valor_nit = 0x224
vp_valor_km = 0x234
vp_valor_no_fuel = 0x244
vp_valor_tapsi = 0x414
vp_valor_clave_t = 0x234


class ProtocoloLcd(threading.Thread):
    def __init__(self, in_lcd_queque, out_mfc_queque):
        threading.Thread.__init__(self)
        self.funciones = Funciones()
        self.puerto = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        self.out_mfc_queque = out_mfc_queque
        self.in_lcd_queque = in_lcd_queque
        self.rxBufferLcd = list(range(100))
        self.rxBufferSize = 0
        self.caso_lcd = 0
        self.pos = 0
        self.read_vp = 0x83
        self.pantalla = 1
        self.tipo_venta = 0
        self.mangueras = 0
        self.manguera_venta = 0
        self.tipo_vehiculo = 0
        self.preset = 0
        self.tipo_preset = 0
        self.tipo_preset_auto = 0
        self.preset_auto = 0
        self.ppu_auto = 0
        self.placa = ''
        self.nit = ''
        self.km = ''
        self.cedula = ''
        self.print = 0
        self.tipoid = ''
        self.id = ''
        self.no_fuel = ''
        self.no_tapsi = ''
        self.comunicacion = 0
        self.tiempo_ini = 0
        self.tiempo_fin = 0
        self.id_vendedor = ''
        self.clave_vendedor = ''
        self.fuente = [0, 'lcd1', 'lcd2']

    def configurar_puerto(self, puerto, pantalla):
        self.pantalla = pantalla
        self.puerto = serial.Serial(puerto, 115200, timeout=1)

    def cambiar_imagen(self, imagen):
        trama = [0x5A, 0xA5, 0x04, 0x80, 0x03, 0x00, imagen]
        self.puerto.write(trama)
        print(trama)

    def leer_imagen(self):
        trama = [0x5A, 0xA5, 0x03, 0x81, 0x03, 0x02]
        self.puerto.write(trama)
        rx_buffer = self.puerto.read(8)
        if len(rx_buffer) == 8:
            imagen = rx_buffer[7]
            return imagen
        else:
            return 0xFF

    def leer_vp(self, vp, size):
        vp1 = vp & 0xFF
        vp2 = (vp % 0xFF00) >> 8
        trama = [0x5A, 0xA5, 0x04, 0x83, vp2, vp1, size]
        self.puerto.write(trama)
        rx_buffer = self.puerto.read(7 + (size * 2))
        if len(rx_buffer) == (7 + (size * 2)):
            return rx_buffer[7:(6 + (size * 2))]
        else:
            return 0

    def escribir_vp_num(self, vp, valor):
        vp1 = vp & 0xFF
        vp2 = (vp % 0xFF00) >> 8
        valor1 = valor & 0xFF
        valor2 = (valor & 0xFF00) >> 8
        trama = [0x5A, 0xA5, 0x05, 0x82, vp2, vp1, valor2, valor1]
        self.puerto.write(trama)

    def escribir_vp_texto(self, vp, texto, size):
        vp1 = vp & 0xFF
        vp2 = (vp % 0xFF00) >> 8
        trama = [0x5A, 0xA5, (size + 3), 0x82, vp2, vp1]
        for i in range(size):
            trama[i + 4] = texto[i]
        self.puerto.write(trama)

    def config_fecha(self, fecha, hora):
        trama = [0x5A, 0xA5, 0x0A, 0x80, 0x1F, 0x5A, 0, 0, 0, 0, 0, 0, 0]
        trama[6] = fecha[2]
        trama[7] = fecha[1]
        trama[8] = fecha[0]
        trama[10] = hora[2]
        trama[11] = hora[1]
        trama[12] = hora[0]
        self.puerto.write(trama)

    def leer_fecha(self):
        trama = [0x5A, 0xA5, 0x03, 0x81, 0x20, 0x07]
        self.puerto.write(trama)
        time.sleep(0.05)
        size = self.puerto.in_waiting
        if size == 13:
            self.rxBufferLcd = self.puerto.read(size)
            fecha = self.rxBufferLcd[6:9]
            hora = self.rxBufferLcd[10:13]
            hora = hora[::-1]
            fecha_t = format(str(fecha[0]), ">02s") + format(str(fecha[1]), ">02s") + format(str(fecha[2]), ">02s") \
                      + format(str(hora[0]), ">02s") + format(str(hora[1]), ">02s") + format(str(hora[2]), ">02s")
            return fecha_t

    @staticmethod
    def verificar_turno(pos):
        db.connect()
        if pos < 3:
            turno_activo = TurnosActivos.get(TurnosActivos.id == 1).id_turno
        else:
            turno_activo = TurnosActivos.get(TurnosActivos.id == 1).id_turno2
        if turno_activo != 0:
            estado_turno = Turnos.get(Turnos.id == turno_activo).estado_actual
        else:
            estado_turno = 0
        db.close()
        return estado_turno

    @staticmethod
    def verificar_estado(pos):
        db.connect()
        estado = Estado.get(Estado.id == pos).estado_dragon
        db.close()
        return estado

    @staticmethod
    def verificar_estado_sur(pos):
        db.connect()
        estado = Estado.get(Estado.id == pos).estado_surtidor
        db.close()
        return estado

    @staticmethod
    def actualizar_estado(pos, estado_up):
        db.connect()
        estado = Estado.update(estado_dragon=estado_up).where(Estado.id == pos)
        estado.execute()
        db.close()

    @staticmethod
    def consultar_mangueras(pos):
        db.connect()
        mangueras = Surtidor.get_by_id(pos).mangueras
        db.close()
        return mangueras

    def leer_puerto(self):
        size = self.puerto.in_waiting
        time.sleep(0.005)
        size_aux = self.puerto.in_waiting
        if (size == size_aux) and (size > 8):
            self.rxBufferSize = self.puerto.in_waiting
            self.rxBufferLcd = self.puerto.read(self.rxBufferSize)
            if self.rxBufferLcd[0] == 0x5A and self.rxBufferLcd[1] == 0xA5:
                return 1
            else:
                return 0
        else:
            return 0

    def pantalla_inicial(self):
        ok_solicitud = self.in_lcd_queque.empty()
        if ok_solicitud:
            if self.leer_puerto() == 1:
                pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
                lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
                if pos_vp == 0 and lcd_vp == 7:
                    self.escribir_vp_num(vp_valor_placa, 0)
                    self.escribir_vp_num(vp_valor_cedula, 0)
                    self.escribir_vp_num(vp_valor_km, 0)
                    self.escribir_vp_num(vp_valor_nit, 0)
                    self.placa = ''
                    self.nit = ''
                    self.km = ''
                    self.cedula = ''
                    self.caso_lcd = 1
                    self.cambiar_imagen(img_escoger_lado)
                    self.tiempo_ini = time.time()
        else:
            solicitud = self.in_lcd_queque.get()
            if solicitud['funcion'] == variables.estado_comuncacion:
                self.comunicacion = solicitud['com']

    def escoger_lado(self):
        self.tiempo_fin = time.time()
        conteo = self.tiempo_fin - self.tiempo_ini
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == b_ladoA:
                    self.pos = self.pantalla
                    estado = self.verificar_estado_sur(self.pos)
                    if estado == 6:
                        self.caso_lcd = 2
                        self.cambiar_imagen(img_menu_inicial)
                        self.tiempo_ini = time.time()
                elif lcd_vp == b_ladoB:
                    self.pos = self.pantalla + 2
                    estado = self.verificar_estado_sur(self.pos)
                    if estado == 6:
                        self.caso_lcd = 2
                        self.cambiar_imagen(img_menu_inicial)
                        self.tiempo_ini = time.time()
                elif lcd_vp == b_devolver:
                    self.caso_lcd = 0
                    self.cambiar_imagen(img_fcs)
        elif conteo > 20:
            self.caso_lcd = 0
            self.cambiar_imagen(img_fcs)

    def menu_inicial(self):
        self.tiempo_fin = time.time()
        conteo = self.tiempo_fin - self.tiempo_ini
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == img_ventas:
                    if self.verificar_turno(self.pos) == 1:
                        # self.actualizar_estado(self.pos, variables.estado_libre)
                        self.cambiar_imagen(img_tipo_venta)
                        self.caso_lcd = 3
                if lcd_vp == img_sel_turno:
                    # self.actualizar_estado(self.pos, variables.estado_libre)
                    self.cambiar_imagen(img_sel_turno)
                    self.caso_lcd = 13
        elif conteo > 20:
            self.caso_lcd = 0
            self.cambiar_imagen(img_fcs)

    def menu_tipo_venta(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == img_dvf:
                    self.tipo_venta = 0
                    self.tipoid = ''
                    self.id = ''
                    self.mangueras = self.consultar_mangueras(self.pos)
                    if self.mangueras > 1:
                        if self.mangueras == 3:
                            self.cambiar_imagen(img_escoger_pro_3)
                        elif self.mangueras == 2:
                            self.cambiar_imagen(img_escoger_pro_2)
                        self.caso_lcd = 4
                    else:
                        self.manguera_venta = 1
                        self.cambiar_imagen(img_tipo_vehiculo)
                        self.caso_lcd = 5
                elif lcd_vp == img_cre:
                    self.tipo_venta = 1
                    if self.mangueras > 1:
                        if self.mangueras == 3:
                            self.cambiar_imagen(img_escoger_pro_3)
                        elif self.mangueras == 2:
                            self.cambiar_imagen(img_escoger_pro_2)
                        self.caso_lcd = 4
                    else:
                        self.manguera_venta = 1
                        self.cambiar_imagen(img_elegir_id_credito)
                        self.caso_lcd = 10
                elif lcd_vp == img_fide:
                    self.caso_lcd = 4
                elif lcd_vp == b_devolver:
                    self.caso_lcd = 2
                    self.cambiar_imagen(img_menu_inicial)

    def escoger_producto(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == b_devolver:
                    self.caso_lcd = 2
                    self.cambiar_imagen(img_menu_inicial)
                elif lcd_vp == b_opcion_1:
                    self.manguera_venta = 1
                    if self.tipo_venta == 1:
                        self.cambiar_imagen(img_elegir_id_credito)
                        self.caso_lcd = 10
                    else:
                        self.cambiar_imagen(img_tipo_vehiculo)
                        self.caso_lcd = 5
                elif lcd_vp == b_opcion_2:
                    self.manguera_venta = 2
                    if self.tipo_venta == 1:
                        self.cambiar_imagen(img_elegir_id_credito)
                        self.caso_lcd = 10
                    else:
                        self.cambiar_imagen(img_tipo_vehiculo)
                        self.caso_lcd = 5
                elif lcd_vp == b_opcion_3:
                    self.manguera_venta = 3
                    if self.tipo_venta == 1:
                        self.cambiar_imagen(img_elegir_id_credito)
                        self.caso_lcd = 10
                    else:
                        self.cambiar_imagen(img_tipo_vehiculo)
                        self.caso_lcd = 5

    def escoger_tipo_vehiculo(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == b_devolver:
                    self.caso_lcd = 2
                    self.cambiar_imagen(img_menu_inicial)
                else:
                    self.tipo_vehiculo = lcd_vp & 0xFF
                    self.cambiar_imagen(img_dvf)
                    self.caso_lcd = 6

    def presetear(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == img_subirmanija:
                    self.preset = 9990000
                    self.tipo_preset = 3
                    if self.tipo_venta == 1:
                        self.preset = self.preset_auto
                        self.tipo_preset = self.tipo_preset_auto
                    self.cambiar_imagen(img_datos_venta)
                    self.caso_lcd = 7
                elif lcd_vp == b_devolver:
                    self.caso_lcd = 2
                    self.cambiar_imagen(img_menu_inicial)
            elif pos_vp == vp_valor_dinero:
                self.preset = (self.rxBufferLcd[12] << 16) | (self.rxBufferLcd[13] << 8) | self.rxBufferLcd[14]
                self.tipo_preset = 2
                if self.tipo_venta == 1:
                    if self.tipo_preset_auto == self.tipo_preset:
                        if self.preset >= self.preset_auto:
                            self.preset = self.preset_auto
                    else:
                        monto = (self.preset * 1000) / self.ppu_auto
                        self.preset = monto
                        if monto >= self.preset_auto:
                            self.tipo_preset = self.tipo_preset_auto
                            self.preset = self.preset_auto
                self.cambiar_imagen(img_datos_venta)
                self.caso_lcd = 7
            elif pos_vp == vp_valor_vol:
                self.preset = (self.rxBufferLcd[12] << 16) | (self.rxBufferLcd[13] << 8) | self.rxBufferLcd[14]
                self.tipo_preset = 1
                if self.tipo_venta == 1:
                    if self.tipo_preset_auto == self.tipo_preset:
                        if self.preset >= self.preset_auto:
                            self.preset = self.preset_auto
                    else:
                        monto = (self.preset * self.ppu_auto) / 1000
                        self.preset = monto
                        if monto >= self.preset_auto:
                            self.tipo_preset = self.tipo_preset_auto
                            self.preset = self.preset_auto
                self.cambiar_imagen(img_datos_venta)
                self.caso_lcd = 7

    def datos_cliente(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == b_imprimir:
                    if self.tipo_venta == 1:
                        total_vol_ini = 0
                        total_din_ini = 0
                        fecha_i = self.leer_fecha()
                        self.print = 2
                        db.connect()
                        fecha_in = FechaActual.update(fecha=fecha_i).where(FechaActual.id == self.pantalla)
                        fecha_in.execute()
                        totales = Totales.select().where(Totales.id == self.pos).get()
                        if self.manguera_venta == 1:
                            total_vol_ini = totales.totales_vol_1
                            total_din_ini = totales.totales_din_1
                        elif self.manguera_venta == 2:
                            total_vol_ini = totales.totales_vol_2
                            total_din_ini = totales.totales_din_2
                        elif self.manguera_venta == 3:
                            total_vol_ini = totales.totales_vol_3
                            total_din_ini = totales.totales_din_3
                        Ventas.create(km=self.km, nit=self.nit, cedula=self.cedula, tipo_preset=self.tipo_preset,
                                      preset=self.preset, manguera=self.manguera_venta, tipo_venta=self.tipo_venta,
                                      no_print=self.print, placa=self.placa, tipo_vehiculo=self.tipo_vehiculo,
                                      tipo_id=self.tipoid, id_cliente=self.id, ppu=self.ppu_auto, fecha_ini=fecha_i,
                                      totales_ini_vol=total_vol_ini, totales_ini_din=total_din_ini,
                                      tipo_id_vendedor='C', sync=1)
                        id_actual = Ventas.select().order_by(Ventas.id.desc()).get()
                        venta_activa = VentasActivas.update(id_venta=id_actual).where(VentasActivas.id == self.pos)
                        venta_activa.execute()
                        db.close()
                        self.tiempo_ini = time.time()
                        self.caso_lcd = 9
                        self.cambiar_imagen(img_subir_manija)
                    else:
                        self.cambiar_imagen(img_no_recibos)
                        self.caso_lcd = 8
            elif pos_vp == vp_valor_placa:
                self.placa = ''
                y = (self.rxBufferLcd[6] * 2) - 2
                for i in range(y):
                    if self.rxBufferLcd[7 + i] != 0xFF:
                        self.placa = self.placa + chr(self.rxBufferLcd[7 + i])
                self.cambiar_imagen(img_datos_venta)
            elif pos_vp == vp_valor_cedula:
                self.cedula = ''
                y = (self.rxBufferLcd[6] * 2) - 2
                for i in range(y):
                    if self.rxBufferLcd[7 + i] != 0xFF:
                        self.cedula = self.cedula + chr(self.rxBufferLcd[7 + i])
                self.cambiar_imagen(img_datos_venta)
            elif pos_vp == vp_valor_nit:
                self.nit = ''
                y = (self.rxBufferLcd[6] * 2) - 2
                for i in range(y):
                    if self.rxBufferLcd[7 + i] != 0xFF:
                        self.nit = self.nit + chr(self.rxBufferLcd[7 + i])
                self.cambiar_imagen(img_datos_venta)
            elif pos_vp == vp_valor_km:
                self.km = ''
                y = (self.rxBufferLcd[6] * 2) - 2
                for i in range(y):
                    if self.rxBufferLcd[7 + i] != 0xFF:
                        if self.tipo_venta != 1:
                            self.km = self.km + chr(self.rxBufferLcd[7 + i])
                self.cambiar_imagen(img_datos_venta)

    def f_no_recibos(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            if pos_vp == 1:
                ppu_v = 0
                total_vol_ini = 0
                total_din_ini = 0
                self.print = self.rxBufferLcd[8]
                fecha_i = self.leer_fecha()
                db.connect()
                fecha_in = FechaActual.update(fecha=fecha_i).where(FechaActual.id == self.pantalla)
                fecha_in.execute()
                totales = Totales.select().where(Totales.id == self.pos).get()
                if self.manguera_venta == 1:
                    ppu_v = Precios.get(Precios.id == self.pos).precio_1
                    total_vol_ini = totales.totales_vol_1
                    total_din_ini = totales.totales_din_1
                elif self.manguera_venta == 2:
                    ppu_v = Precios.get(Precios.id == self.pos).precio_3
                    total_vol_ini = totales.totales_vol_2
                    total_din_ini = totales.totales_din_2
                elif self.manguera_venta == 3:
                    ppu_v = Precios.get(Precios.id == self.pos).precio_3
                    total_vol_ini = totales.totales_vol_3
                    total_din_ini = totales.totales_din_3
                Ventas.create(km=self.km, nit=self.nit, cedula=self.cedula, tipo_preset=self.tipo_preset,
                              preset=self.preset, manguera=self.manguera_venta, tipo_venta=self.tipo_venta,
                              no_print=self.print, placa=self.placa, tipo_vehiculo=self.tipo_vehiculo, ppu=ppu_v,
                              totales_ini_vol=total_vol_ini, totales_ini_din=total_din_ini, fecha_ini=fecha_i,
                              tipo_id_vendedor='C', sync=1)
                id_actual = Ventas.select().order_by(Ventas.id.desc()).get()
                venta_activa = VentasActivas.update(id_venta=id_actual).where(VentasActivas.id == self.pos)
                venta_activa.execute()
                db.close()
                self.tiempo_ini = time.time()
                self.caso_lcd = 9
                self.cambiar_imagen(img_subir_manija)

    def subir_manija(self):
        self.tiempo_fin = time.time()
        conteo = self.tiempo_fin - self.tiempo_ini
        db.connect()
        estado = Estado.get(Estado.id == self.pos).estado_surtidor
        db.close()
        if estado == 9:
            db.connect()
            estado = Estado.update(estado_dragon=variables.estado_surtiendo).where(Estado.id == self.pos)
            estado.execute()
            db.close()
            self.caso_lcd = 0
            self.cambiar_imagen(img_fcs)
        elif conteo > 20:
            db.connect()
            if self.tipo_venta == 1:
                estado = Estado.update(estado_dragon=variables.estado_venta_cancelada).where(Estado.id == self.pos)
                estado.execute()
            venta_activa = VentasActivas.get(VentasActivas.id == self.pos).id_venta
            sync = Ventas.update(sync=6).where(Ventas.id == venta_activa)
            sync.execute()
            db.close()
            self.caso_lcd = 0
            self.cambiar_imagen(img_fcs)

    def escoger_id(self):
        ok_solicitud = self.in_lcd_queque.empty()
        if ok_solicitud:
            if self.leer_puerto() == 1:
                pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
                lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
                if pos_vp == 0:
                    if lcd_vp == b_devolver:
                        msg = {'funcion': variables.reset_id, 'pos': self.pos}
                        self.out_mfc_queque.put(msg)
                        self.caso_lcd = 2
                        self.cambiar_imagen(img_menu_inicial)
                    elif lcd_vp == 58:
                        self.tipoid = 'Z'
                        self.cambiar_imagen(img_ibutton)
                        db.connect()
                        autorizar = Autorizaciones.update(tipo_id='I', manguera=self.manguera_venta). \
                            where(Autorizaciones.id == self.pos)
                        autorizar.execute()
                        db.close()
                        msg = {'funcion': variables.pedir_id, 'pos': self.pos}
                        self.out_mfc_queque.put(msg)
                    elif lcd_vp == 41:
                        self.tipoid = 'I'
                        self.cambiar_imagen(img_ibutton)
                        db.connect()
                        autorizar = Autorizaciones.update(tipo_id=self.tipoid, manguera=self.manguera_venta). \
                            where(Autorizaciones.id == self.pos)
                        autorizar.execute()
                        db.close()
                        msg = {'funcion': variables.pedir_id, 'pos': self.pos}
                        self.out_mfc_queque.put(msg)
                    elif lcd_vp == 42:
                        self.tipoid = 'B'
                        self.cambiar_imagen(img_ibutton)
                        db.connect()
                        autorizar = Autorizaciones.update(tipo_id=self.tipoid, manguera=self.manguera_venta). \
                            where(Autorizaciones.id == self.pos)
                        autorizar.execute()
                        db.close()
                        msg = {'funcion': variables.pedir_id, 'pos': self.pos}
                        self.out_mfc_queque.put(msg)
                elif pos_vp == vp_valor_placa:
                    self.tipoid = 'P'
                    self.placa = ''
                    y = (self.rxBufferLcd[6] * 2) - 2
                    for i in range(y):
                        if self.rxBufferLcd[7 + i] != 0xFF:
                            self.placa = self.placa + chr(self.rxBufferLcd[7 + i])
                    db.connect()
                    autorizar = Autorizaciones.update(tipo_id=self.tipoid, manguera=self.manguera_venta,
                                                      idenificador=self.placa).where(Autorizaciones.id == self.pos)
                    autorizar.execute()
                    db.close()
                    self.caso_lcd = 11
                    self.cambiar_imagen(img_km_venta_id)
                elif pos_vp == vp_valor_cedula:
                    self.tipoid = 'C'
                    self.cedula = ''
                    y = (self.rxBufferLcd[6] * 2) - 2
                    for i in range(y):
                        if self.rxBufferLcd[7 + i] != 0xFF:
                            self.cedula = self.cedula + chr(self.rxBufferLcd[7 + i])
                    db.connect()
                    autorizar = Autorizaciones.update(tipo_id=self.tipoid, manguera=self.manguera_venta,
                                                      idenificador=self.cedula).where(Autorizaciones.id == self.pos)
                    autorizar.execute()
                    db.close()
                    self.caso_lcd = 11
                    self.cambiar_imagen(img_km_venta_id)
                elif pos_vp == vp_valor_no_fuel:
                    self.tipoid = 'F'
                    self.no_fuel = ''
                    y = (self.rxBufferLcd[6] * 2) - 2
                    for i in range(y):
                        if self.rxBufferLcd[7 + i] != 0xFF:
                            self.no_fuel = self.no_fuel + chr(self.rxBufferLcd[7 + i])
                    db.connect()
                    autorizar = Autorizaciones.update(tipo_id=self.tipoid, manguera=self.manguera_venta,
                                                      idenificador=self.no_fuel).where(Autorizaciones.id == self.pos)
                    autorizar.execute()
                    db.close()
                    self.caso_lcd = 11
                    self.cambiar_imagen(img_km_venta_id)
                elif pos_vp == vp_valor_tapsi:
                    self.tipoid = 'X'
                    self.no_tapsi = ''
                    y = (self.rxBufferLcd[6] * 2) - 2
                    for i in range(y):
                        if self.rxBufferLcd[7 + i] != 0xFF:
                            self.no_tapsi = self.no_tapsi + chr(self.rxBufferLcd[7 + i])
                    db.connect()
                    autorizar = Autorizaciones.update(tipo_id=self.tipoid, manguera=self.manguera_venta,
                                                      idenificador=self.no_tapsi).where(Autorizaciones.id == self.pos)
                    autorizar.execute()
                    db.close()
                    self.caso_lcd = 11
                    self.cambiar_imagen(img_km_venta_id)
        else:
            solicitud = self.in_lcd_queque.get()
            if solicitud == variables.func_ok:
                db.connect()
                autorizar = Autorizaciones.update(tipo_id=self.tipoid).where(Autorizaciones.id == self.pos)
                autorizar.execute()
                db.close()
                self.caso_lcd = 11
                self.cambiar_imagen(img_km_venta_id)

    def pedir_km(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == b_devolver:
                    self.caso_lcd = 2
                    self.cambiar_imagen(img_menu_inicial)
            elif pos_vp == vp_valor_km:
                self.km = ''
                y = (self.rxBufferLcd[6] * 2) - 2
                for i in range(y):
                    if self.rxBufferLcd[7 + i] != 0xFF:
                        self.km = self.km + chr(self.rxBufferLcd[7 + i])
                db.connect()
                autorizar = Autorizaciones.update(km=self.km, autorizacion=1).where(Autorizaciones.id == self.pos)
                autorizar.execute()
                estado = Estado.update(estado_dragon=variables.estado_pet_auto).where(Estado.id == self.pos)
                estado.execute()
                db.close()
                self.tiempo_ini = time.time()
                self.caso_lcd = 12
                self.cambiar_imagen(img_esperando)

    def esperar_autorizacion(self):
        db.connect()
        autorizacion = Autorizaciones.get(Autorizaciones.id == self.pos)
        db.close()
        self.tiempo_fin = time.time()
        espera = self.tiempo_fin - self.tiempo_ini
        if autorizacion.autorizacion == 3:
            size = len(autorizacion.msg_lcd)
            self.escribir_vp_texto(0x254, autorizacion.msg_lcd, size)
            self.cambiar_imagen(img_sumi_auto)
            self.tipo_preset_auto = autorizacion.tipo_preset
            self.preset_auto = autorizacion.cantidad_auto
            if self.manguera_venta == 1:
                self.ppu_auto = autorizacion.ppu_1
            elif self.manguera_venta == 2:
                self.ppu_auto = autorizacion.ppu_2
            elif self.manguera_venta == 3:
                self.ppu_auto = autorizacion.ppu_3
            self.id = autorizacion.idenificador
            time.sleep(1)
            self.cambiar_imagen(img_dvf)
            self.caso_lcd = 6
        elif autorizacion.autorizacion == 4:
            size = len(autorizacion.msg_lcd)
            self.escribir_vp_texto(0x254, autorizacion.msg_lcd, size)
            self.cambiar_imagen(img_sumi_no_auto)
            time.sleep(1)
            self.caso_lcd = 0
            self.cambiar_imagen(img_fcs)
        elif self.comunicacion == 0 or espera > 40:
            self.caso_lcd = 0
            self.cambiar_imagen(img_fcs)

    def menu_turno(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == b_devolver:
                    self.caso_lcd = 2
                    self.cambiar_imagen(img_menu_inicial)
                elif lcd_vp == img_sel_id_t:
                    if self.verificar_turno(self.pos) == 0:
                        self.caso_lcd = 14
                        self.cambiar_imagen(img_sel_id_t)
                elif lcd_vp == img_confir_cerra_t:
                    if self.verificar_turno(self.pos) == 1:
                        self.caso_lcd = 15
                        self.cambiar_imagen(img_confir_cerra_t)

    def elegir_id_t(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == b_devolver:
                    self.caso_lcd = 2
                    self.cambiar_imagen(img_menu_inicial)
            elif pos_vp == vp_valor_cedula:
                self.id_vendedor = ''
                y = (self.rxBufferLcd[6] * 2) - 2
                for i in range(y):
                    if self.rxBufferLcd[7 + i] != 0xFF:
                        self.id_vendedor = self.id_vendedor + chr(self.rxBufferLcd[7 + i])
                self.caso_lcd = 16
                self.cambiar_imagen(img_clave_turno)

    def clave_turno(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            if pos_vp == vp_valor_clave_t:
                self.clave_vendedor = ''
                y = (self.rxBufferLcd[6] * 2) - 2
                for i in range(y):
                    if self.rxBufferLcd[7 + i] != 0xFF:
                        self.clave_vendedor = self.clave_vendedor + chr(self.rxBufferLcd[7 + i])
                fecha = self.leer_fecha()
                self.cambiar_imagen(img_esperando)
                msg = {'funcion': variables.pedir_totales, 'fuente': self.fuente[self.pantalla]}
                self.out_mfc_queque.put(msg)
                ok_cambio = 0
                while ok_cambio != variables.func_ok:
                    ok_cambio = self.in_lcd_queque.get()
                db.connect()
                totales_1 = Totales.select().where(Totales.id == 1).get()
                totales_2 = Totales.select().where(Totales.id == 2).get()
                totales_3 = Totales.select().where(Totales.id == 3).get()
                totales_4 = Totales.select().where(Totales.id == 4).get()
                db.close()
                if self.pos == 1 or self.pos == 2:
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
                estado_actual = self.verificar_turno(self.pos)
                clave = self.clave_vendedor
                pos = self.pos
                tipo_id = 'C'
                cedula_vendedor = self.id_vendedor
                tipo_peticion = 1
                sync = 1
                db.connect()
                Turnos.create(tipo_peticion=tipo_peticion, estado_actual=estado_actual, tipo_id=tipo_id,
                              cedula_vendedor=cedula_vendedor, fecha=fecha, ppu_1_1=ppu_1_1,
                              totales_vol_1_1=totales_vol_1_1, totales_din_1_1=totales_din_1_1, ppu_1_2=ppu_1_2,
                              totales_vol_1_2=totales_vol_1_2, totales_din_1_2=totales_din_1_2, ppu_1_3=ppu_1_3,
                              totales_vol_1_3=totales_vol_1_3,  totales_din_1_3=totales_din_1_3, ppu_2_1=ppu_2_1,
                              totales_vol_2_1=totales_vol_2_1, totales_din_2_1=totales_din_2_1, ppu_2_2=ppu_2_2,
                              totales_vol_2_2=totales_vol_2_2, totales_din_2_2=totales_din_2_2, ppu_2_3=ppu_2_3,
                              totales_vol_2_3=totales_vol_2_3, totales_din_2_3=totales_din_2_3, password=clave,
                              pos=pos, sync=sync)
                id_actual = Turnos.select().order_by(Turnos.id.desc()).get()
                if self.pos < 3:
                    turno_activo = TurnosActivos.select().where(TurnosActivos.id == 1).get()
                    turno_activo.id_turno = id_actual
                    turno_activo.save()
                else:
                    turno_activo = TurnosActivos.select().where(TurnosActivos.id == 1).get()
                    turno_activo.id_turno2 = id_actual
                    turno_activo.save()
                estado = Estado.update(estado_dragon=variables.estado_pet_turno).where(Estado.id == self.pos)
                estado.execute()
                db.close()
                self.tiempo_ini = time.time()
                self.caso_lcd = 17

    def cerrar_t(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == b_si:
                    self.cambiar_imagen(img_esperando)
                    tipo_peticion = 0
                    fecha = self.leer_fecha()
                    msg = {'funcion': variables.pedir_totales, 'fuente': self.fuente[self.pantalla]}
                    self.out_mfc_queque.put(msg)
                    ok_cambio = 0
                    while ok_cambio != variables.func_ok:
                        ok_cambio = self.in_lcd_queque.get()
                    db.connect()
                    totales_1 = Totales.select().where(Totales.id == 1).get()
                    totales_2 = Totales.select().where(Totales.id == 2).get()
                    totales_3 = Totales.select().where(Totales.id == 3).get()
                    totales_4 = Totales.select().where(Totales.id == 4).get()
                    if self.pos == 1 or self.pos == 2:
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
                    if self.pos < 3:
                        id_turno = TurnosActivos.get_by_id(1).id_turno
                    else:
                        id_turno = TurnosActivos.get_by_id(1).id_turno2
                    turno = Turnos.select().where(Turnos.id == id_turno).get()
                    estado_act = turno.estado_actual
                    tipo_id = 'C'
                    cedula_vendedor = turno.cedula_vendedor
                    password = turno.password
                    pos = self.pos
                    sync = 1
                    Turnos.create(tipo_peticion=tipo_peticion, estado_actual=estado_act, tipo_id=tipo_id,
                                  cedula_vendedor=cedula_vendedor, fecha=fecha, ppu_1_1=ppu_1_1,
                                  totales_vol_1_1=totales_vol_1_1,
                                  totales_din_1_1=totales_din_1_1, ppu_1_2=ppu_1_2, totales_vol_1_2=totales_vol_1_2,
                                  totales_din_1_2=totales_din_1_2, ppu_1_3=ppu_1_3, totales_vol_1_3=totales_vol_1_3,
                                  totales_din_1_3=totales_din_1_3, ppu_2_1=ppu_2_1, totales_vol_2_1=totales_vol_2_1,
                                  totales_din_2_1=totales_din_2_1, ppu_2_2=ppu_2_2, totales_vol_2_2=totales_vol_2_2,
                                  totales_din_2_2=totales_din_2_2, ppu_2_3=ppu_2_3, totales_vol_2_3=totales_vol_2_3,
                                  totales_din_2_3=totales_din_2_3, password=password, pos=pos, sync=sync)
                    id_actual = Turnos.select().order_by(Turnos.id.desc()).get()
                    if self.pos < 3:
                        turno_activo = TurnosActivos.select().where(TurnosActivos.id == 1).get()
                        turno_activo.id_turno = id_actual
                        turno_activo.save()
                    else:
                        turno_activo = TurnosActivos.select().where(TurnosActivos.id == 1).get()
                        turno_activo.id_turno2 = id_actual
                        turno_activo.save()
                    estado = Estado.update(estado_dragon=variables.estado_pet_turno).where(Estado.id == self.pos)
                    estado.execute()
                    db.close()
                    self.tiempo_ini = time.time()
                    self.caso_lcd = 17
                elif lcd_vp == b_no:
                    self.caso_lcd = 0
                    self.cambiar_imagen(img_fcs)

    def esperar_turno(self):
        db.connect()
        if self.pos < 3:
            turno_activo = TurnosActivos.get(TurnosActivos.id == 1).id_turno
        else:
            turno_activo = TurnosActivos.get(TurnosActivos.id == 1).id_turno2
        id_turno = turno_activo
        turno = Turnos.select().where(Turnos.id == id_turno).get()
        self.tiempo_fin = time.time()
        espera = self.tiempo_fin - self.tiempo_ini
        if turno.sync == 4:
            if turno.estado_actual == 1:
                self.cambiar_imagen(img_turno_abierto)
                time.sleep(1)
            else:
                self.cambiar_imagen(img_turno_cerrado)
                time.sleep(1)
            self.caso_lcd = 0
            self.cambiar_imagen(img_fcs)
        elif turno.sync == 3:
            self.cambiar_imagen(75)
            time.sleep(1)
            self.caso_lcd = 0
            self.cambiar_imagen(img_fcs)
        elif self.comunicacion == 0 or espera > 40:
            turno.sync = 2
            if turno.tipo_peticion == 1:
                self.cambiar_imagen(img_abrir_sin_sis)
                self.caso_lcd = 18
            else:
                turno.estado_actual = 0
                self.cambiar_imagen(img_turno_cerrado)
                time.sleep(1)
                self.caso_lcd = 0
                self.cambiar_imagen(img_fcs)
            turno.save()
        db.close()

    def abrir_sin_sys(self):
        if self.leer_puerto() == 1:
            pos_vp = (self.rxBufferLcd[4] << 8) | self.rxBufferLcd[5]
            lcd_vp = (self.rxBufferLcd[7] << 8) | self.rxBufferLcd[8]
            if pos_vp == 0:
                if lcd_vp == b_si:
                    db.connect()
                    if self.pos < 3:
                        turno_activo = TurnosActivos.get(TurnosActivos.id == 1).id_turno
                    else:
                        turno_activo = TurnosActivos.get(TurnosActivos.id == 1).id_turno2
                    id_turno = turno_activo
                    turno = Turnos.select().where(Turnos.id == id_turno).get()
                    turno.estado_actual = 1
                    turno.save()
                    db.close()
                    self.cambiar_imagen(img_turno_abierto)
                    time.sleep(1)
                    self.caso_lcd = 0
                    self.cambiar_imagen(img_fcs)
                elif lcd_vp == b_no:
                    self.caso_lcd = 0
                    self.cambiar_imagen(img_fcs)

    def run(self):
        self.cambiar_imagen(img_fcs)
        self.tiempo_ini = time.time()
        while True:
            self.tiempo_fin = time.time()
            conteo = self.tiempo_fin - self.tiempo_ini
            if conteo > 50:
                fecha = self.leer_fecha()
                db.connect()
                fecha_in = FechaActual.update(fecha=fecha).where(FechaActual.id == self.pantalla)
                fecha_in.execute()
                db.close()
                self.tiempo_ini = time.time()
            else:
                method_name = casos[self.caso_lcd]
                method = getattr(self, method_name, lambda: "error")
                method()
