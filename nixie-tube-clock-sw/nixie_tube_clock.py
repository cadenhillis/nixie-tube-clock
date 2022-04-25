
import board
import microcontroller
import analogio, digitalio, pwmio, busio
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import SolicitServicesAdvertisement
from adafruit_ble.services.standard import CurrentTimeService
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet
import rtc
import time as t
from datetime import date

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
        self.day_pwm.duty_cycle = 0
        self.week_pwm = pwmio.PWMOut(board.A2)
        self.week_pwm.duty_cycle = 0
        self.month_pwm = pwmio.PWMOut(board.A3)
        self.month_pwm.duty_cycle = 0
        self.year_pwm = pwmio.PWMOut(board.A4)
        self.year_pwm.duty_cycle = 0

        #ain
        #self.temp_ntc = analogio.AnalogIn(board.A0)
        #temp = temp_ntc.value * x x x x x

        #ble
        self.ble = BLERadio()
        self.uart = UARTService()
        self.advertisement = SolicitServicesAdvertisement()
        self.advertisement.complete_name = "TimePlease:-)"
        self.advertisement.solicited_services.append(CurrentTimeService)
        self.ble.start_advertising(self.advertisement)

        #values
        # time init
        r = rtc.RTC()
        #look for file
        r.datetime = t.struct_time((2022, 4, 25, 13, 30, 0, 0, -1, -1))

    @property
    def time(self):
        return self.r.datetime
   
    def time_set(self, hour=None, min=None, day=None, month=None, year = None):
        if hour is not None: self.r.datetime[3] = hour
        if min is not None: self.r.datetime[4] = min
        if day is not None: self.r.datetime[2] = day
        if month is not None: self.r.datetime[1] = month
        if year is not None: self.r.datetime[0] = year
        self.update_display()

    def update_display(self):
        #assemble bytearray
        mod_h = self.r.datetime[3] % 10
        if self.r.datetime[3] > 12:
            temp = self.r.datetime[3]-12
        else:
            temp = self.r.datetime[3]
        mod_m = self.r.datetime[4] % 10
        self.SEND_BUF = self.digit_dict[(temp - mod_h) / 10] + self.digit_dict[mod_h] + self.digit_dict[(self.r.datetime[4] - mod_m) / 10] + self.digit_dict[mod_m]
        print(self.SEND_BUF)
        self.write_74hc594d()
        self.write_pwm()
    
    def write_74hc594d(self):
        #re-init spi
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        while not spi.try_lock():
            pass
        spi.configure(baudrate = 9600)
        #send data
        print(self.SEND_BUF)
        spi.write(self.SEND_BUF)
        spi.deinit()
        #pulse storage clk to store shift values
        self.store.value = False
        self.store.value = True
        self.store.value = False
        
    def write_pwm(self):
        #get yday
        leapday = self.r.datetime[7]
        year = self.r.datetime[0]
        #detect leap year
        if self.r.datetime[7] == 59:
            if float.is_integer((self.r.datetime[0] - 2020) / 4):
                self.r.datetime[7] = 60
                if self.r.datetime[6] == 0: self.r.datetime[6] = 6
                else: self.r.datetime[6] -= 1
        # write values
        self.day_pwm.duty_cycle = int(((self.r.datetime[3] * 60 + self.r.datetime[4])/1440) * 65535)
        self.week_pwm.duty_cycle = int(((self.r.datetime[3] * 60 + self.r.datetime[4] + (self.r.datetime[6]+ 1) * 24 * 60) / 10080) * 65535)
        self.month_pwm.duty_cycle = int(self.r.datetime[2]/31 * 65535) #assuming 31 days a month bec im lazy
        self.year_pwm.duty_cycle = int(self.r.datetime[7]/366 * 65535)

    def ble_connect(self):
        self.ble.start_advertising(self.advertisement)
        i = 0
        while not self.ble.connected:
            self.update_display()
            #print(ntc.r.datetime)
            pass
        self.ble.stop_advertising()
        print("connected")

        while self.ble.connected:
            for connection in self.ble.connections:
                if not connection.paired:
                    connection.pair()
                    print("paired")
            cts = connection[CurrentTimeService]
            self.r.datetime = cts
            self.update_display(self)
                