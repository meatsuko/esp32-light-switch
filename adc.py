import machine
import time

class Analyzer:
    ADC_LEFT = None
    ADC_RIGHT = None
    LOW_PASS = 200
    ADC_ATTN = None
    left_level = 0
    right_level = 0
    silent = True
    
    def __init__(self, PIN_LEFT, PIN_RIGHT, lp=0, ATTN=machine.ADC.ATTN_11DB, WDTH=machine.ADC.WIDTH_12BIT):
        self.ADC_LEFT = machine.ADC(machine.Pin(PIN_LEFT, mode=machine.Pin.IN, pull=machine.Pin.PULL_DOWN)) # похоже что pull_up pull_down не работают
        self.ADC_RIGHT = machine.ADC(machine.Pin(PIN_RIGHT, mode=machine.Pin.IN, pull=machine.Pin.PULL_DOWN)) # похоже что pull_up pull_down не работают
        self.attn(ATTN)
        self.width(WDTH)
        self.LOW_PASS = lp  # Устанавливаем LOW_PASS
        self.SILENT_COUNTER = 0
        
    def attn(self, ATTN):
        self.ADC_LEFT.atten(ATTN)
        self.ADC_RIGHT.atten(ATTN)
    
    def width(self, WDTH=machine.ADC.WIDTH_12BIT):
        self.ADC_LEFT.width(WDTH)
        self.ADC_RIGHT.width(WDTH)
        
    def loop(self, ticks=80):
        while True:
            max_left_level = 0
            max_right_level = 0

            for _ in range(ticks):  # Считываем уровни звука ticks раз
                loop_left_level = self.ADC_LEFT.read()
                loop_right_level = self.ADC_RIGHT.read()

                if max_left_level < loop_left_level: 
                    max_left_level = loop_left_level
                if max_right_level < loop_right_level: 
                    max_right_level = loop_right_level

            
            # temp for 11db attenuation
            max_left_level = self.__map(max_left_level, self.LOW_PASS, 2720, 0, 4095)
            max_right_level = self.__map(max_right_level, self.LOW_PASS, 2720, 0, 4095)

            self.left_level = max_left_level
            self.right_level = max_right_level

            if self.left_level < 20 and self.right_level < 20:
                if self.SILENT_COUNTER < 20:
                    self.SILENT_COUNTER += 1
                else:
                    self.silent = True
            else:
                if self.SILENT_COUNTER > 1:
                    self.SILENT_COUNTER = self.SILENT_COUNTER -1
                else:
                    self.silent = False
        
    def __map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min
