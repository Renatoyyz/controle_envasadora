import _thread
import time
from machine import Pin, I2C, PWM
from telas import TelaController
from Csv import Csv

class MotorController:
    

    def __init__(self):
        # Configuração dos pinos
        self.step_pin = Pin(1, Pin.OUT)
        self.enable_pin = Pin(0, Pin.OUT)

        self.digital_input1 = Pin(6, Pin.IN, Pin.PULL_UP) # Sensor otico envasador 1
        self.digital_input2 = Pin(5, Pin.IN, Pin.PULL_UP) # Sensor otico envasador 2
        self.stop_button = Pin(13, Pin.IN, Pin.PULL_UP)  # Botão para parar a thread
        self.output1 = Pin(4, Pin.OUT) # Aciona rele que ativa envasadora 1
        self.output2 = Pin(3, Pin.OUT) # Aciona rele que ativa envasadora 2

        self.servo1_pin = Pin(11, Pin.OUT)  # Ajuste o pino conforme necessário
        self.servo1_pwm = PWM(self.servo1_pin)

        self.servo2_pin = Pin(12, Pin.OUT)  # Ajuste o pino conforme necessário
        self.servo2_pwm = PWM(self.servo2_pin)
        
        self.botao_1 = Pin(7, Pin.IN, Pin.PULL_UP) # Entrada do botão 1
        self.botao_2 = Pin(10, Pin.IN, Pin.PULL_UP) # Entrada do botão 2

        self.VOLTA_COMPLETA = 200
        self.ANTI_PINGO_AMBOS = 0 # Se for 0 aciona anti pingo nas duas bombas
        self.ANTI_PINGO_E1 = 1 # Se for 1 aciona anti pingo na envasadora 1
        self.ANTI_PINGO_E2 = 2 # Se for 2 aciona anti pingo na envasadora 2

        
        self.TEMPO_ENCHER = 500
        self.TEMPO_PULSO = 250
        self.TEMPO_PULSO_MOTOR = 1
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
                for _ in range(self.VOLTA_COMPLETA * (3+(1/2))*2):  # N passos para duas voltas completas
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
                    time.sleep_ms(self.TEMPO_PULSO)
                    self.output1.value(1)
                    self.output2.value(1)
                    self.espera_encher(acao=self.ANTI_PINGO_AMBOS)
                    self.contador += 2
                    self.csv.update_value(1, 0, f"{self.contador}")
                    self.telas.atualiza_contador(self.contador)
                    
                elif self.digital_input1.value() == 0 and self.digital_input2.value() == 1 and self.inicia_motor == False:
                    self.output1.value(0)
                    time.sleep_ms(self.TEMPO_PULSO)
                    self.output1.value(1)
                    self.espera_encher(acao=self.ANTI_PINGO_E1)
                    self.contador += 1
                    self.csv.update_value(1, 0, f"{self.contador}")
                    self.telas.atualiza_contador(self.contador)
                    
                elif self.digital_input1.value() == 1 and self.digital_input2.value() == 0 and self.inicia_motor == False:
                    self.output2.value(0)
                    time.sleep_ms(self.TEMPO_PULSO)
                    self.output2.value(1)
                    self.espera_encher(acao=self.ANTI_PINGO_E2)
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
            
    def espera_encher(self, acao):
        print("Enchendo....")
        time.sleep_ms(self.TEMPO_ENCHER)
        self.inicia_motor = True

        if acao == self.ANTI_PINGO_AMBOS:
            self.controla_servos(90, 90)
        elif acao == self.ANTI_PINGO_E1:
            self.controla_servos(90, 0)
        elif acao == self.ANTI_PINGO_E2:
            self.controla_servos(0, 90)
    
    def controla_servos(self, angulo1, angulo2, habilita1=True, habilita2=True):
        # Servo 1
        if not hasattr(self, 'servo1_pwm'):
            self.servo1_pwm.freq(50)
        # Servo 2
        if not hasattr(self, 'servo2_pwm'):
            self.servo2_pwm.freq(50)

        min_us = 500
        max_us = 2500

        if habilita1:
            us1 = min_us + (max_us - min_us) * angulo1 / 180
            duty1 = int(us1 * 65535 // 20000)
            self.servo1_pwm.duty_u16(duty1)
        if habilita2:
            us2 = min_us + (max_us - min_us) * angulo2 / 180
            duty2 = int(us2 * 65535 // 20000)
            self.servo2_pwm.duty_u16(duty2)

        time.sleep_ms(500)

        # Retorna ambos para 0 grau se habilitados
        if habilita1:
            duty1_init = int(min_us * 65535 // 20000)
            self.servo1_pwm.duty_u16(duty1_init)
        if habilita2:
            duty2_init = int(min_us * 65535 // 20000)
            self.servo2_pwm.duty_u16(duty2_init)

        time.sleep_ms(500)
        

    def start(self):
        # Inicia a thread para controlar o motor de passo no núcleo 1
        _thread.start_new_thread(self.motor_control, ())
        # Executa a função de monitoramento de sinais no núcleo 0
        self.monitor_signals()

if __name__ == "__main__":
    controller = MotorController()
    controller.start()



