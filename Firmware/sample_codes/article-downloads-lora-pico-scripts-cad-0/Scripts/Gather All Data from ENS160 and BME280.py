# Read air quality metrics from the PiicoDev Air Quality Sensor ENS160 and PiicoDev Atmospheric Sensor BME280
# ENS160 Shows three metrics: AQI, TVOC and eCO2
# ENS160 also shows Sensor Operational Mode (has it recorded for a while or (less accurately) just started recording)
# BME280 Shows three metrics: Temperature, Pressure and Humidity


from PiicoDev_ENS160 import PiicoDev_ENS160 # import the device driver ENS160
from PiicoDev_BME280 import PiicoDev_BME280	# import the device driver BME280
from PiicoDev_Unified import sleep_ms       # a cross-platform sleep function

sensor1 = PiicoDev_ENS160()   # Initialise the ENS160 module
sensor2 = PiicoDev_BME280()   # Initialise the BME280 module	

#zeroAlt = sensor.altitude() # take an initial altitude reading for BME280 [[[[Dont Think I Need]]]]


while True:
    # Read from Sensor 1 (ENS160)
    aqi = sensor1.aqi
    tvoc = sensor1.tvoc
    eco2 = sensor1.eco2
    
    # Print air quality metrics from Sensor 1 (ENS160)
    
    print('Air Quality Sensor')
    print('   AQI: ' + str(aqi.value) + ' [' + str(aqi.rating) +']')
    print('   TVOC: ' + str(tvoc) + ' ppb')
    print('   eCO2: ' + str(eco2.value) + ' ppm [' + str(eco2.rating) +']')
    print('Operational Mode Status: ' + str(sensor1.operation))
    
    print('--------------------------------')
    
    #Small timeout to avoid spamming shell
    sleep_ms(1000)
    
    # Read Weather Data Metrics from Sensor 2 (BME280)
    
    tempC, presPa, humRH = sensor2.values()
    
    # Convert air pressure Pascals -> hPa (or mbar, if you prefer)
    
    pres_hPa = presPa / 100
    
    # Print Weather Metrics from Sensor 2 (BME280)
    
    print('Atmospheric Weather Sensor')
    print('   Temperture: ' + str(tempC)+' °C')
    print('   Pressure: ' + str(pres_hPa)+' hPa')
    print('   Humidity: ' + str(humRH)+' %RH')
    
    print('--------------------------------')
    
    #Small timeout to avoid spamming shell
    sleep_ms(1000)
    