class Funciones:
    def __init__(self):
        self.caracteres = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'A': 0x0A,
                           'B': 0x0B, 'C': 0x0C, 'D': 0x0D, 'E': 0x0E, 'F': 0x0F}
        self.numeros = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 0x0A: 'A',
                        0x0B: 'B', 0x0C: 'C', 0x0D: 'D', 0x0E: 'E', 0x0F: 'F'}

    @staticmethod
    def convertir_entero(trama, inicio, size):
        valor = 0
        for i in range(inicio, (inicio + size)):
            valor = (trama[i] * (10 ** (i - inicio))) + valor
        return valor

    @staticmethod
    def convertir_string(trama, inicio, size):
        lista = list()
        for i in range(size):
            lista[i] = chr(trama[inicio + i])
        lista_a_string = ''.join(map(str, lista))
        return lista_a_string

    def convertir_string_to_ibutton(self, string_ibutton):
        trama = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        trama[0] = (self.caracteres[string_ibutton[0]] << 4) | self.caracteres[string_ibutton[1]]
        trama[1] = (self.caracteres[string_ibutton[2]] << 4) | self.caracteres[string_ibutton[3]]
        trama[2] = (self.caracteres[string_ibutton[4]] << 4) | self.caracteres[string_ibutton[5]]
        trama[3] = (self.caracteres[string_ibutton[6]] << 4) | self.caracteres[string_ibutton[7]]
        trama[4] = (self.caracteres[string_ibutton[8]] << 4) | self.caracteres[string_ibutton[9]]
        trama[5] = (self.caracteres[string_ibutton[10]] << 4) | self.caracteres[string_ibutton[11]]
        trama[6] = (self.caracteres[string_ibutton[11]] << 4) | self.caracteres[string_ibutton[13]]
        trama[7] = (self.caracteres[string_ibutton[12]] << 4) | self.caracteres[string_ibutton[15]]
        return trama

    def convertir_ibutton_to_string(self, ibutton):
        trama = list(range(16))
        trama[0] = self.numeros[ibutton[0] >> 4]
        trama[1] = self.numeros[ibutton[0] & 0x0F]
        trama[2] = self.numeros[ibutton[1] >> 4]
        trama[3] = self.numeros[ibutton[1] & 0x0F]
        trama[4] = self.numeros[ibutton[2] >> 4]
        trama[5] = self.numeros[ibutton[2] & 0x0F]
        trama[6] = self.numeros[ibutton[3] >> 4]
        trama[7] = self.numeros[ibutton[3] & 0x0F]
        trama[8] = self.numeros[ibutton[4] >> 4]
        trama[9] = self.numeros[ibutton[4] & 0x0F]
        trama[10] = self.numeros[ibutton[5] >> 4]
        trama[11] = self.numeros[ibutton[5] & 0x0F]
        trama[12] = self.numeros[ibutton[6] >> 4]
        trama[13] = self.numeros[ibutton[6] & 0x0F]
        trama[14] = self.numeros[ibutton[7] >> 4]
        trama[15] = self.numeros[ibutton[7] & 0x0F]
        string_ibutton = "".join(trama)
        return string_ibutton

    def convertir_fecha_to_lista(self, string_fecha):
        trama = [0, 0, 0, 0, 0, 0, 0]
        trama[0] = (self.caracteres[string_fecha[0]] << 4) | self.caracteres[string_fecha[1]]
        trama[1] = (self.caracteres[string_fecha[2]] << 4) | self.caracteres[string_fecha[3]]
        trama[2] = (self.caracteres[string_fecha[4]] << 4) | self.caracteres[string_fecha[5]]
        trama[3] = (self.caracteres[string_fecha[6]] << 4) | self.caracteres[string_fecha[7]]
        trama[4] = (self.caracteres[string_fecha[8]] << 4) | self.caracteres[string_fecha[9]]
        trama[5] = (self.caracteres[string_fecha[10]] << 4) | self.caracteres[string_fecha[11]]
        return trama
