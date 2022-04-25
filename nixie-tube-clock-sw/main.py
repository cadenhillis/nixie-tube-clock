
import time
from nixie_tube_clock import nixie_tube_clock



ntc = nixie_tube_clock()
while True:
    ntc.ble_connect()
