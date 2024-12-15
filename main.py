import json
import network
import time  # Не забудьте импортировать time

import _thread

from adc import Analyzer
from adc import ReAnalyzer

from beacon import Beacon
from pixel import UV


with open('pymakr.conf') as likeENV:
    env = json.load(likeENV)

# похоже нельзя использвать ADC2_* и WIFI одновременно пробуем 34 - 36 они от ADC1_*
MIC_PIN_LEFT = 34  # Левый канал
MIC_PIN_RIGHT = 35  # Правый канал

# Настройки
PIN_LED = 12
LEDS_COUNT = 60
LEDS_OFFSET = 12


if env['mode'] == 'master': 
    beacon = Beacon()
    analyzer = Analyzer(MIC_PIN_LEFT, MIC_PIN_RIGHT)
else:
    beacon = None
    analyzer = ReAnalyzer()

uv = UV(PIN_LED, LEDS_COUNT, LEDS_OFFSET)

# Запуск потоков
if beacon:
    _thread.start_new_thread(beacon.loop, ())  # Запуск Beacon в отдельном потоке
    
_thread.start_new_thread(analyzer.loop, ())  # Запуск анализа в отдельном потоке
_thread.start_new_thread(uv.loop, (analyzer, beacon,))  # Запуск UV в отдельном потоке

# Главный поток может быть свободен для других задач
while True:
    time.sleep(1)  # Ожидание
