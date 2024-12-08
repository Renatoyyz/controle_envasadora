import time
from machine import Pin, I2C
from pico_i2c_lcd import I2cLcd

class TelaController:
    I2C_ADDR = 0x27
    I2C_NUM_ROWS = 4
    I2C_NUM_COLS = 20

    TELA_INICIAL = 0
    TELA_CONFIG_ESQUERDO = 1
    TELA_CONFIG_DIREITO = 2
    TELA_EXECUCAO = 3

    def __init__(self):
        self.tela_ativa = -1
        self.i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=400000)
        self.lcd = I2cLcd(self.i2c, self.I2C_ADDR, self.I2C_NUM_ROWS, self.I2C_NUM_COLS)
        time.sleep(0.5)
        self.lcd.clear()

    def tela_inicial(self):
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Iniciando Sistema...")
        time.sleep(1)
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Sistema Iniciado!")
        self.lcd.move_to(0, 1)
        self.lcd.putstr("Pressione o botao e ")
        self.lcd.move_to(0, 2)
        self.lcd.putstr("verifique a posicao ")
        self.lcd.move_to(0, 3)
        self.lcd.putstr("do Fuso...")
        self.tela_ativa = self.TELA_INICIAL
        return self.tela_ativa

    def tela_execucao(self):
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Executando...")
        self.lcd.move_to(0, 1)
        self.lcd.putstr("Pressione o botao")
        self.lcd.move_to(0, 2)
        self.lcd.putstr("para iniciar")
        self.tela_ativa = self.TELA_EXECUCAO
        return self.tela_ativa

    def tela_config_esquerdo(self):
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Acionar dosador 1")
        self.lcd.move_to(0, 1)
        self.lcd.putstr("Pressione o botao")
        self.lcd.move_to(0, 2)
        self.lcd.putstr("para iniciar")
        self.tela_ativa = self.TELA_CONFIG_ESQUERDO
        return self.tela_ativa

    def tela_config_direito(self):
        self.lcd.clear()
        self.lcd.move_to(0, 0)
        self.lcd.putstr("Acionar dosador 2")
        self.lcd.move_to(0, 1)
        self.lcd.putstr("Pressione o botao")
        self.lcd.move_to(0, 2)
        self.lcd.putstr("para iniciar")
        self.tela_ativa = self.TELA_CONFIG_DIREITO
        return self.tela_ativa

    def executa_tela(self, tela_ativa):
        if tela_ativa == self.TELA_INICIAL:
            self.tela_inicial()
            time.sleep_ms(5)
        elif tela_ativa == self.TELA_EXECUCAO:
            self.tela_execucao()
            time.sleep_ms(5)
        elif tela_ativa == self.TELA_CONFIG_ESQUERDO:
            self.tela_config_esquerdo()
            time.sleep_ms(5)
        elif tela_ativa == self.TELA_CONFIG_DIREITO:
            self.tela_config_direito()
            time.sleep_ms(5)
        else:
            self.tela_inicial()
            
        self.tela_ativa = tela_ativa
        return self.tela_ativa

if __name__ == "__main__":
    controller = TelaController()
    controller.tela_inicial()
