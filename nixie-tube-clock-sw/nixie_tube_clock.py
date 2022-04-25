
import board
import analogio, digitalio, pwmio, busio
#from adafruit_ble import BLERadio
import rtc
import time as t

class nixie_tube_clock:

    digit_dict = {   # bit of shift register
        0 : b'\x02\x00', # bit 9
        1 : b'\x00\x01', # bit 0 
        2 : b'\x00\x02', # bit 1
        3 : b'\x00\x04', # bit 2
        4 : b'\x00\x08', # bit 3
        5 : b'\x00\x10', # bit 4
        6 : b'\x00\x20', # bit 5
        7 : b'\x00\x40', # bit 6
        8 : b'\x00\x80', # bit 7
        9 : b'\x01\x00', # bit 8
        }  

    month_days = {
        1  : 30,
        2  : 30,
        3  : 30,
        4  : 30,
        5  : 30,
        6  : 30,
        7  : 30,
        8  : 30,
        9  : 30,
        10 : 30,
        11 : 30,
        12 : 30,
    }


    def __init__(self):
        #dio
        self.store = digitalio.DigitalInOut(board.D2)
        self.store.direction = digitalio.Direction.OUTPUT
        self.store.value = False

        self.clr_shift_n = digitalio.DigitalInOut(board.TX)
        self.clr_shift_n.direction = digitalio.Direction.OUTPUT
        self.clr_shift_n.value = True

        self.clr_store_n = digitalio.DigitalInOut(board.RX)
        self.clr_store_n.direction = digitalio.Direction.OUTPUT
        self.clr_store_n.value = True

        self.colon1 = digitalio.DigitalInOut(board.D10)
        self.colon1.direction = digitalio.Direction.OUTPUT
        self.colon1.value = True

        self.colon2 = digitalio.DigitalInOut(board.D9)
        self.colon2.direction = digitalio.Direction.OUTPUT
        self.colon2.value = True

        self.temp_led = digitalio.DigitalInOut(board.D7)
        self.temp_led.direction = digitalio.Direction.OUTPUT
        self.temp_led.value = False

        #pwm
        self.day_pwm = pwmio.PWMOut(board.A1)
        self.day_pwm.duty_cycle = 25

        self.week_pwm = pwmio.PWMOut(board.A2)
        self.week_pwm.duty_cycle = 0

        self.month_pwm = pwmio.PWMOut(board.A3)
        self.month_pwm.duty_cycle = 0

        self.year_pwm = pwmio.PWMOut(board.A4)
        self.year_pwm.duty_cycle = 0

        #ain
        self.temp_ntc = analogio.AnalogIn(board.A0)
        #temp = temp_ntc.value * x x x x x

        #ble

        #values
        self.time_value = {
            'hour':12,
            'min':0,
            'day':1,
            'month':1,
        }

        self.time_set(1,1,1,1)

    @property
    def time(self):
        return self.time_value
   
    def time_set(self, hour=None, min=None, day=None, month=None):
        if hour is not None: self.time['hour'] = hour
        if min is not None: self.time['min'] = min
        if day is not None: self.time['day'] = day
        if month is not None: self.time['month'] = month
        self.update_display()

    def update_display(self):
        #assemble bytearray
        mod_h = self.time['hour'] % 10
        mod_m = self.time['min'] % 10
        self.SEND_BUF = self.digit_dict[(self.time['hour'] - mod_h) / 10] + self.digit_dict[mod_h] + self.digit_dict[(self.time['hour'] - mod_m) / 10] + self.digit_dict[mod_m]
        print(self.SEND_BUF)
        self.write_74hc594d()
    
    def write_74hc594d(self):
        delay = 0.000001  #.1ms period, maybe make it do some bogus math to wait a super small amt of time?
        #re-init spi
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        while not spi.try_lock():
            pass
        spi.configure(baudrate = 9600)

        print(self.SEND_BUF)
        spi.write(self.SEND_BUF)
        spi.deinit()
        #t.sleep(delay)
        #self.store.value = True
        #t.sleep(delay)
        # may need to play w timing so this executes AFTER the data has been sent? # when does this execute ?
        self.store.value = False
        self.store.value = True
        self.store.value = False
        self.store.value = True
        self.store.value = False
        
