from sma_speedwire import SMA_SPEEDWIRE, smaError

api = SMA_SPEEDWIRE("192.168.2.100", '0000')

try:
    api.init()
    print("serial", api.serial)
    print("model", api.inv_class)
    print("device", api.inv_type)
    api.update()
    for sensor_name in api.sensors:
        print("%s: %g %s" % (sensor_name, float(api.sensors[sensor_name]['value']or 0.0), api.sensors[sensor_name]['unit']))
except smaError as e:
    print("Error", e)
