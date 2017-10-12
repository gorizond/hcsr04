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
    result = 0
    sample_size = 3
    skip_items = 50
    skipped_items = 0
    while True:
        await asyncio.sleep(0.03)
        try:
            send = False
            new_result = value.distance_metric(value.raw_distance(sample_size=sample_size, sample_wait=0.03))
            sample_size = 3
            send_result = new_result
            if new_result < 50:
                send_result = round(new_result)
            if new_result >= 50:
                send_result = 50
            if new_result >= 100:
                sample_size = 4
                send_result = 100
            if new_result >= 150:
                sample_size = 5
                send_result = 150
            if new_result >= 200:
                send_result = 200
            if new_result >= 250:
                send_result = 250
            if new_result >= 300:
                send_result = 300
            if new_result >= 365:
                send_result = 365
            if result != send_result:
                result = send_result
                send = True
            else:
                skipped_items += 1
                if skipped_items > skip_items:
                    print(f'{skip_items} skipped items!')
                    send = True
            if send:
                result = send_result
                skipped_items = 0
                await ws.send_str(str(result))
            else:
                sample_size = 5
        except Exception as e:
            print(e)


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
