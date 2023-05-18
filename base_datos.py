
from peewee import *

db = SqliteDatabase('dragon.db')


class Precios(Model):
    precio_1 = IntegerField()
    precio_2 = IntegerField()
    precio_3 = IntegerField()

    class Meta:
        database = db


class Estado(Model):
    estado_surtidor = IntegerField()
    estado_dragon = IntegerField()

    class Meta:
        database = db


class Productos(Model):
    producto_1 = TextField(default='0')
    producto_2 = TextField(default='0')
    producto_3 = TextField(default='0')

    class Meta:
        database = db


class Consignaciones(Model):
    valor = IntegerField(default=0)
    fecha = TextField(default='0')
    id_vendedor = TextField(default='0')

    class Meta:
        database = db


class Surtidor(Model):
    mangueras = IntegerField(default=3)
    ppux10 = IntegerField(default=0)
    placa_ob = IntegerField(default=0)
    decimales_din = IntegerField(default=0)
    decimales_vol = IntegerField(default=3)
    decimales_ppu = IntegerField(default=0)
    nombre_estacion = TextField(default='0')
    direccion_estacion = TextField(default='0')
    lema_1 = TextField(default='GRACIAS POR SU COMPRA')
    lema_2 = TextField(default='VUELVA PRONTO')
    p1 = IntegerField(default=5000)
    p2 = IntegerField(default=10000)
    p3 = IntegerField(default=20000)
    mfc_name = TextField(default='0')
    nit_estacion = TextField(default='0')

    class Meta:
        database = db


class Totales(Model):
    ppu_1 = IntegerField(default=0)
    totales_vol_1 = BigIntegerField(default=0)
    totales_din_1 = BigIntegerField(default=0)
    ppu_2 = IntegerField(default=0)
    totales_vol_2 = BigIntegerField(default=0)
    totales_din_2 = BigIntegerField(default=0)
    ppu_3 = IntegerField(default=0)
    totales_vol_3 = BigIntegerField(default=0)
    totales_din_3 = BigIntegerField(default=0)

    class Meta:
        database = db


class Autorizaciones(Model):
    tipo_id = CharField(default='0')
    idenificador = TextField(default='0')
    km = TextField(default='0')
    tipo_venta = IntegerField(default=0)
    combustible = IntegerField(default=0)
    manguera = IntegerField(default=0)
    tipo_preset = IntegerField(default=0)
    msg_lcd = TextField(default='0')
    autorizacion = IntegerField(default=0)
    cantidad_auto = IntegerField(default=0)
    is_auto_man_1 = IntegerField(default=0)
    is_auto_man_2 = IntegerField(default=0)
    is_auto_man_3 = IntegerField(default=0)
    ppu_1 = IntegerField(default=0)
    ppu_2 = IntegerField(default=0)
    ppu_3 = IntegerField(default=0)
    indice_canasta = IntegerField(default=0)

    class Meta:
        database = db


class Turnos(Model):
    tipo_peticion = IntegerField()
    estado_actual = IntegerField()
    tipo_id = CharField()
    cedula_vendedor = TextField()
    fecha = TextField()
    ppu_1_1 = IntegerField()
    totales_vol_1_1 = BigIntegerField()
    totales_din_1_1 = BigIntegerField()
    ppu_1_2 = IntegerField()
    totales_vol_1_2 = BigIntegerField()
    totales_din_1_2 = BigIntegerField()
    ppu_1_3 = IntegerField()
    totales_vol_1_3 = BigIntegerField()
    totales_din_1_3 = BigIntegerField()
    ppu_2_1 = IntegerField()
    totales_vol_2_1 = BigIntegerField()
    totales_din_2_1 = BigIntegerField()
    ppu_2_2 = IntegerField()
    totales_vol_2_2 = BigIntegerField()
    totales_din_2_2 = BigIntegerField()
    ppu_2_3 = IntegerField()
    totales_vol_2_3 = BigIntegerField()
    totales_din_2_3 = BigIntegerField()
    password = TextField()
    pos = IntegerField()
    sync = IntegerField()

    class Meta:
        database = db


class Ventas(Model):
    manguera = IntegerField(default=0)
    dinero = IntegerField(default=0)
    volumen = IntegerField(default=0)
    ppu = IntegerField(default=0)
    placa = TextField(default='')
    tipo_id = CharField(default='')
    id_cliente = TextField(default='')
    km = TextField(default='0')
    fecha_ini = TextField(default='')
    fecha_fin = TextField(default='')
    tipo_venta = IntegerField(default=0)
    tipo_preset = IntegerField(default=0)
    preset = IntegerField(default=0)
    tipo_id_vendedor = CharField(default='')
    id_vendedor = TextField(default='')
    totales_ini_vol = BigIntegerField(default=0)
    totales_ini_din = BigIntegerField(default=0)
    totales_fin_vol = BigIntegerField(default=0)
    totales_fin_din = BigIntegerField(default=0)
    nit = TextField(default='')
    cedula = TextField(default='')
    no_print = IntegerField(default=0)
    volumen_redimido = IntegerField(default=0)
    tipo_vehiculo = IntegerField(default=0)
    sync = IntegerField(default=0)

    class Meta:
        database = db


class VentaCanasta(Model):
    fecha = TextField(default='0')
    id_prod_1 = TextField(default='0')
    can_prod_1 = IntegerField(default=0)
    val_prod_1 = IntegerField(default=0)
    val_total_prod_1 = IntegerField(default=0)
    nom_prod_1 = TextField(default='0')
    ok_pro_1 = IntegerField(default=0)
    id_prod_2 = TextField(default='0')
    can_prod_2 = IntegerField(default=0)
    val_prod_2 = IntegerField(default=0)
    val_total_prod_2 = IntegerField(default=0)
    nom_prod_2 = TextField(default='0')
    ok_pro_2 = IntegerField(default=0)
    id_prod_3 = TextField(default='0')
    can_prod_3 = IntegerField(default=0)
    val_prod_3 = IntegerField(default=0)
    val_total_prod_3 = IntegerField(default=0)
    nom_prod_3 = TextField(default='0')
    ok_pro_3 = IntegerField(default=0)
    id_prod_4 = TextField(default='0')
    can_prod_4 = IntegerField(default=0)
    val_prod_4 = IntegerField(default=0)
    val_total_prod_4 = IntegerField(default=0)
    nom_prod_4 = TextField(default='0')
    ok_pro_4 = IntegerField(default=0)
    tipo_id_cliente = CharField(default='0')
    id_cliente = TextField(default='0')
    id_vendedor = TextField(default='0')
    no_impresiones = IntegerField(default=0)
    tipo_venta = IntegerField(default=0)

    class Meta:
        database = db


class VentasActivas(Model):
    id_venta = IntegerField()

    class Meta:
        database = db


class TurnosActivos(Model):
    id_turno = IntegerField(default=0)
    id_turno2 = IntegerField(default=0)

    class Meta:
        database = db


class FechaActual(Model):
    fecha = TextField(default='0')

    class Meta:
        database = db


def initDb():
    db.connect()
    db.create_tables([Precios, Estado, Productos, Consignaciones, Surtidor, Totales, Autorizaciones, Turnos, Ventas,
                      VentaCanasta, VentasActivas, TurnosActivos, FechaActual], safe=True)

    query = Precios.select()
    if len(query) != 4:
        Precios.delete()
        precios_init = [
            {'precio_1': 0, 'precio_2': 0, 'precio_3': 0},
            {'precio_1': 0, 'precio_2': 0, 'precio_3': 0},
            {'precio_1': 0, 'precio_2': 0, 'precio_3': 0},
            {'precio_1': 0, 'precio_2': 0, 'precio_3': 0},
        ]
        with db.atomic():
            for precios in precios_init:
                Precios.create(**precios)

    query = Estado.select()
    if len(query) != 4:
        Estado.delete()
        estados_init = [
            {'estado_surtidor': 0, 'estado_dragon': 0},
            {'estado_surtidor': 0, 'estado_dragon': 0},
            {'estado_surtidor': 0, 'estado_dragon': 0},
            {'estado_surtidor': 0, 'estado_dragon': 0},
        ]
        with db.atomic():
            for estado in estados_init:
                Estado.create(**estado)

    query = Productos.select()
    if len(query) != 4:
        Productos.delete()
        productos_init = [
            {'producto_1': '0'},
            {'producto_1': '0'},
            {'producto_1': '0'},
            {'producto_1': '0'},
        ]
        with db.atomic():
            for producto in productos_init:
                Productos.create(**producto)

    query = Consignaciones.select()
    if len(query) != 4:
        Consignaciones.delete()
        consignaciones_init = [
            {'valor': 0},
            {'valor': 0},
            {'valor': 0},
            {'valor': 0},
        ]
        with db.atomic():
            for consignacion in consignaciones_init:
                Consignaciones.create(**consignacion)

    query = Surtidor.select()
    if len(query) != 4:
        Surtidor.delete()
        surtidor_init = [
            {'mangueras': 3},
            {'mangueras': 3},
            {'mangueras': 3},
            {'mangueras': 3},
        ]
        with db.atomic():
            for surtidor in surtidor_init:
                Surtidor.create(**surtidor)

    query = Totales.select()
    if len(query) != 4:
        Totales.delete()
        totales_init = [
            {'mangueras': 3},
            {'mangueras': 3},
            {'mangueras': 3},
            {'mangueras': 3},
        ]
        with db.atomic():
            for totales in totales_init:
                Totales.create(**totales)

    query = Autorizaciones.select()
    if len(query) != 4:
        Autorizaciones.delete()
        autorizaciones_init = [
            {'tipo_id': '0'},
            {'tipo_id': '0'},
            {'tipo_id': '0'},
            {'tipo_id': '0'},
        ]
        with db.atomic():
            for autorizaciones in autorizaciones_init:
                Autorizaciones.create(**autorizaciones)

    query = VentaCanasta.select()
    if len(query) != 4:
        VentaCanasta.delete()
        ventacanasta_init = [
            {'fecha': '0'},
            {'fecha': '0'},
            {'fecha': '0'},
            {'fecha': '0'},
        ]
        with db.atomic():
            for ventaCanasta in ventacanasta_init:
                VentaCanasta.create(**ventaCanasta)

    query = VentasActivas.select()
    if len(query) != 4:
        VentasActivas.delete()
        ventasactivas_init = [
            {'id_venta': 0},
            {'id_venta': 0},
            {'id_venta': 0},
            {'id_venta': 0},
        ]
        with db.atomic():
            for ventasactivas in ventasactivas_init:
                VentasActivas.create(**ventasactivas)

    query = TurnosActivos.select()
    if len(query) != 4:
        TurnosActivos.delete()
        turnosactivos_init = [
            {'id_turno': 0},
            {'id_turno': 0},
            {'id_turno': 0},
            {'id_turno': 0},
        ]
        with db.atomic():
            for turnosactivos in turnosactivos_init:
                TurnosActivos.create(**turnosactivos)

    query = FechaActual.select()
    if len(query) != 2:
        FechaActual.delete()
        fecha_init = [
            {'fecha': '0'},
        ]
        with db.atomic():
            for fecha in fecha_init:
                FechaActual.create(**fecha)

    db.close()


initDb()
