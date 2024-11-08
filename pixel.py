import machine
import neopixel
import time

class UV:
    NEO_PIXEL = None
    LEDS_COUNT = None
    LEDS_OFFSET = 0
    LEDS_INLINE = 0
    
    # Настройка пропорций для цветов (0-1)
    RED_RATIO = 0.5     # Пропорция красного
    GREEN_RATIO = 0.0   # Пропорция зеленого
    BLUE_RATIO = 1.0    # Пропорция синего

    
    def __init__(self, PIN_LED, LEDS_COUNT, LEDS_OFFSET=0):
        self.NEO_PIXEL = neopixel.NeoPixel(machine.Pin(PIN_LED), LEDS_COUNT)
        self.LEDS_COUNT = LEDS_COUNT
        self.LEDS_OFFSET = LEDS_OFFSET
        
        self.LEDS_INLINE = (LEDS_COUNT - LEDS_OFFSET) // 2

    def loop(self, analyzer):
        while True:
            left_brightness = min(int(analyzer.left_level / (4095 / self.LEDS_INLINE)), self.LEDS_INLINE)
            right_brightness = min(int(analyzer.right_level / (4095 / self.LEDS_INLINE)), self.LEDS_INLINE)

            # Очищаем все светодиоды
            for i in range(self.LEDS_COUNT): self.NEO_PIXEL[i] = (0, 0, 0)

            # Устанавливаем цвет для светодиодов на основе уровней звука
            # Левый канал
            for i in range(left_brightness):
                if self.LEDS_INLINE - 1 - i >= 0:  # Проверка, чтобы избежать выхода за пределы
                    color_intensity = int(255 * (i / left_brightness)) if left_brightness > 0 else 0
                    self.NEO_PIXEL[self.LEDS_INLINE - 1 - i + self.LEDS_OFFSET] = self.__colorize(color_intensity)

            # Правый канал
            for i in range(right_brightness):
                if self.LEDS_INLINE + i < self.LEDS_INLINE * 2:  # Проверка, чтобы избежать выхода за пределы
                    color_intensity = int(255 * (i / right_brightness)) if right_brightness > 0 else 0
                    self.NEO_PIXEL[self.LEDS_INLINE + i + self.LEDS_OFFSET] = self.__colorize(color_intensity)

            self.NEO_PIXEL.write()  # Обновление LED-ленты
            time.sleep(0.0001)  # Пауза для стабильности
    
    def __colorize(self, color_intensity):
        red_intensity = int(color_intensity * self.RED_RATIO)
        green_intensity = int(color_intensity * self.GREEN_RATIO)
        blue_intensity = int(color_intensity * self.BLUE_RATIO)
        return (red_intensity, green_intensity, blue_intensity)