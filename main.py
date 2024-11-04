import _thread
import time  # Не забудьте импортировать time

from adc import Analyzer
from pixel import UV

MIC_PIN_LEFT = 2  # Левый канал
MIC_PIN_RIGHT = 4  # Правый канал

# Настройки
PIN_LED = 12
LEDS_COUNT = 60
LEDS_OFFSET = 12

# Создание экземпляров классов
analyzer = Analyzer(MIC_PIN_LEFT, MIC_PIN_RIGHT)
uv = UV(PIN_LED, LEDS_COUNT, LEDS_OFFSET)

# Запуск потоков
_thread.start_new_thread(analyzer.loop, ())  # Запуск анализа в отдельном потоке
_thread.start_new_thread(uv.loop, (analyzer,))  # Запуск UV в отдельном потоке

# Главный поток может быть свободен для других задач
while True:
    time.sleep(1)  # Ожидание
