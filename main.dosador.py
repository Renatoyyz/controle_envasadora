import _thread
import time
from machine import Pin, I2C
from telas import TelaController
from Csv import Csv

class MotorController:
    

    def __init__(self):
        # Configuração dos pinos
        self.step_pin = Pin(1, Pin.OUT)
        self.enable_pin = Pin(0, Pin.OUT)
        self.digital_input1 = Pin(6, Pin.IN, Pin.PULL_UP)
        self.digital_input2 = Pin(5, Pin.IN, Pin.PULL_UP)
        self.stop_button = Pin(12, Pin.IN, Pin.PULL_UP)  # Botão para parar a thread
        self.output1 = Pin(4, Pin.OUT)
        self.output2 = Pin(3, Pin.OUT)
        self.botao_1 = Pin(7, Pin.IN, Pin.PULL_UP)
        self.botao_2 = Pin(10, Pin.IN, Pin.PULL_UP)

        self.VOLTA_COMPLETA = 96
        
        self.TEMPO_ENCHER = 2000
        self.TEMPO_PULSO = 500
        self.TEMPO_PULSO_MOTOR = 5
        self.contador = 0
        
        self.csv = Csv(labels=['contador'])
        try:
            self.contador = int(self.csv.get_value(1, 0))
        except:
            self.csv.save_value([f"{self.contador}"])

        self.output1.value(1)
        self.output2.value(1)

        # Variável global para sinalizar quando parar a thread
        self.stop_thread = False
        self.inicia_motor = False
        self.reset_botao_2 = False

        self.telas = TelaController()

        if self.botao_2.value() == 0:
            self.contador = 0
            self.csv.update_value(1, 0, f"{self.contador}")
            self.telas.executa_tela(0, msg="Contador zerado")
        else:
            self.telas.executa_tela(0, msg="Contador: " + str(self.contador))

        if self.botao_1.value() == 0:
            time.sleep_ms(100)
            while self.botao_1.value() == 0:
                pass
            time.sleep_ms(100)

    # Função para controlar o motor de passo
    def motor_control(self):
        self.enable_pin.value(0)  # Ativa o motor de passo
        while True:
            if self.inicia_motor:
                for _ in range(self.VOLTA_COMPLETA * 2):  # N passos para duas voltas completas
                    if self.stop_thread:
                        break
                    self.step_pin.value(1)
                    time.sleep_ms(self.TEMPO_PULSO_MOTOR)
                    self.step_pin.value(0)
                    time.sleep_ms(self.TEMPO_PULSO_MOTOR)
                self.inicia_motor = False
                print("Motor de passo completou duas voltas ou foi interrompido")

    # Função para monitorar os sinais digitais
    def monitor_signals(self):
        while True:
            if self.stop_button.value() == 0:  # Verifica se o botão de parada foi pressionado
                self.stop_thread = True
                break
            if self.botao_1.value() == 0:
                time.sleep_ms(100)
                while self.botao_1.value() == 0:
                    pass
                self.telas.tela_ativa += 1
                if self.telas.tela_ativa > 3:
                    self.telas.tela_ativa = 1
                    
                self.telas.executa_tela(self.telas.tela_ativa)
                
                if self.telas.tela_ativa == self.telas.TELA_EXECUCAO:
                    #self.inicia_motor = True
                    self.telas.atualiza_contador(self.contador)
                    
            if self.botao_2.value() == 0 and self.telas.tela_ativa == self.telas.TELA_EXECUCAO:
                time.sleep_ms(100)
                while self.botao_2.value() == 0:
                    pass
                self.reset_botao_2 = not self.reset_botao_2 # Reseta botao 2
                if self.reset_botao_2 == True:
                    self.inicia_motor = True
                    self.telas.executando_parado(True)
                else:
                    self.inicia_motor = False
                    self.telas.executando_parado(False)
                
            if self.telas.tela_ativa == self.telas.TELA_CONFIG_ESQUERDO:
                if self.botao_2.value() == 0:
                    while self.botao_2.value() == 0:
                        pass
                    self.output1.value(0)
                    time.sleep_ms(self.TEMPO_PULSO)
                    self.output1.value(1)
            if self.telas.tela_ativa == self.telas.TELA_CONFIG_DIREITO:
                if self.botao_2.value() == 0:
                    while self.botao_2.value() == 0:
                        pass
                    self.output2.value(0)
                    time.sleep_ms(self.TEMPO_PULSO)
                    self.output2.value(1)

            if self.telas.tela_ativa == self.telas.TELA_EXECUCAO and self.reset_botao_2 == True:
                time.sleep_ms(500)
                if self.digital_input1.value() == 0 and self.digital_input2.value() == 0 and self.inicia_motor == False:
                    self.output1.value(0)
                    self.output2.value(0)
                    time.sleep_ms(100)
                    self.output1.value(1)
                    self.output2.value(1)
                    self.espera_encher()
                    self.contador += 2
                    self.csv.update_value(1, 0, f"{self.contador}")
                    self.telas.atualiza_contador(self.contador)
                    
                elif self.digital_input1.value() == 0 and self.digital_input2.value() == 1 and self.inicia_motor == False:
                    self.output1.value(0)
                    time.sleep_ms(100)
                    self.output1.value(1)
                    self.espera_encher()
                    self.contador += 1
                    self.csv.update_value(1, 0, f"{self.contador}")
                    self.telas.atualiza_contador(self.contador)
                    
                elif self.digital_input1.value() == 1 and self.digital_input2.value() == 0 and self.inicia_motor == False:
                    self.output2.value(0)
                    time.sleep_ms(100)
                    self.output2.value(1)
                    self.espera_encher()
                    self.contador += 1
                    self.csv.update_value(1, 0, f"{self.contador}")
                    self.telas.atualiza_contador(self.contador)

                elif self.digital_input1.value() == 1 and self.digital_input2.value() == 1 and self.inicia_motor == False:
                    self.output2.value(1)
                    self.output2.value(1)
                    self.telas.atualiza_contador(self.contador)
                    self.inicia_motor = True
            elif self.telas.tela_ativa != self.telas.TELA_EXECUCAO:
                self.inicia_motor = False
                self.reset_botao_2 =  False
            
            time.sleep_ms(100)  # Pequena pausa para evitar uso excessivo da CPU
            
    def espera_encher(self):
        print("Enchendo....")
        time.sleep_ms(self.TEMPO_ENCHER)
        self.inicia_motor = True

    def start(self):
        # Inicia a thread para controlar o motor de passo no núcleo 1
        _thread.start_new_thread(self.motor_control, ())
        # Executa a função de monitoramento de sinais no núcleo 0
        self.monitor_signals()

if __name__ == "__main__":
    controller = MotorController()
    controller.start()