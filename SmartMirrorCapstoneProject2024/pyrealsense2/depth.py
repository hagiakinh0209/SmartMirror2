import pyrealsense2 as rs

def find_cameras(ctx):
    devices = ctx.devices

    data = {}

    for dev in devices:
        name = dev.get_info(rs.camera_info.name)
        serial_number = dev.get_info(rs.camera_info.serial_number)

        data[name] = serial_number
        print(
            f"found camera with name: {name} and serial number: {serial_number}"
        )

    return data

x = rs.context()
y = find_cameras(x)
print(y)
