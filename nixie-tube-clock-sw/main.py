
import board
import analogio, digitalio, pwmio, busio
import time
from nixie_tube_clock import nixie_tube_clock



ntc = nixie_tube_clock()
i = 11
p = 1
while True:
    print(i)
    ntc.time_set(hour=i, min = i)
    ntc.day_pwm.duty_cycle = int((p/100) * 65535)
    ntc.week_pwm.duty_cycle = int((p/100) * 65535)
    ntc.month_pwm.duty_cycle = int((p/100) * 65535)
    ntc.year_pwm.duty_cycle = int((p/100) * 65535)
    i+= 11
    if i >= 100: i = 11
    p += 1
    time.sleep(.25)
    if p >= 100: p = 1
    
