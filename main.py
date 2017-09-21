import os
import aiohttp
import asyncio
from hcsr04sensor import sensor

async def start_client(loop, url):
    session = aiohttp.ClientSession()
    was_connect = False
    try:
        ws = await session.ws_connect(url)
        was_connect = True
        print('Connected to server:')
    except Exception as e:
        print(e)
    else:
        send_task = loop.create_task(send_to_server(ws))
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                pass
            elif msg.type == aiohttp.WSMsgType.CLOSE:
                break
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break
        send_task.cancel()
    finally:
        session.close()
        if was_connect:
            print('Disconnected...')
    return


async def send_to_server(ws):
    value = sensor.Measurement(int(os.getenv('TRIG_PIN', 23)), int(os.getenv('ECHO_PIN', 24)))
    while True:
        await asyncio.sleep(1)
        ws.send_str(value.distance_metric(value.raw_distance()))
#        ws.send_str('test')


async def main(loop):
    url = os.getenv('CORE_URL', 'ws://core:8080/hcsr04')

    while True:
        await asyncio.sleep(1)
        print('Connecting to server...')
        session_task = loop.create_task(start_client(loop, url))
        await session_task

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()
