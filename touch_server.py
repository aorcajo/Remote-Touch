import asyncio
from touch_binding import makeTouch, POINTER_FLAGS


async def make_touch(finguer, state, x, y):
    makeTouch(x, y, finguer, POINTER_FLAGS[state])


async def message_control(data):    
    if len(data) == 4:
        state = data[0] & 0b11
        finguer = data[0] >> 2 & 0b11

        x = (data[1] * 2**3) + (data[0] & 0b111)
        y = (data[3] * 2**3) + (data[2] & 0b111)

        await make_touch(finguer, state, x, y)
        
        return True
    
    else:
        return False



async def control_server(reader, writer):
    buffer = bytearray(b'')
    
    while not reader.at_eof():
        data = await reader.read(1)
        if  data == b'\n':
            await message_control(buffer)
            buffer.clear()
            #reader._buffer.clear()

        elif data:
            buffer.append(data[0])
            
        #await writer.drain()

    writer.close()

loop = asyncio.get_event_loop()
coro = asyncio.start_server(control_server, '0.0.0.0', 7800, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
