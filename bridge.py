"""ESP32 serial -> localhost websocket; serves the game page."""
import argparse
import asyncio
import json
from pathlib import Path
from aiohttp import web
import serial

ROOT = Path(__file__).resolve().parent
clients = set()
roles = {}
latest_state = None
GM_COMMANDS = {"bell", "remove_error", "skip", "reset", "time30", "time15", "sim_next", "sim_hold", "sim_release"}

async def index(request):
    return web.FileResponse(ROOT / 'index.html')

async def ws_handler(request):
    global latest_state
    ws = web.WebSocketResponse(heartbeat=20)
    await ws.prepare(request)
    clients.add(ws)
    roles[ws] = "viewer"
    print(f'[WEB] Browser connected; clients={len(clients)}', flush=True)
    try:
        async for msg in ws:
            if msg.type != web.WSMsgType.TEXT:
                continue
            if msg.data == 'ping':
                await ws.send_str('pong')
                continue
            try:
                data = json.loads(msg.data)
            except (ValueError, TypeError):
                continue
            if data.get('type') == 'role' and data.get('role') in ('gm','player'):
                roles[ws] = data['role']
                if data['role'] == 'gm' and latest_state is not None:
                    await ws.send_str(json.dumps({'type':'state','state':latest_state}))
                if data['role'] == 'player':
                    for client in tuple(clients):
                        if not client.closed and roles.get(client) == 'gm':
                            await client.send_str(json.dumps({'type':'player_online','online':True}))
            elif data.get('type') == 'state' and roles.get(ws) == 'player':
                latest_state = data.get('state')
                if isinstance(latest_state, dict):
                    for client in tuple(clients):
                        if not client.closed and roles.get(client) == 'gm':
                            await client.send_str(json.dumps({'type':'state','state':latest_state}))
            elif data.get('type') == 'gm' and roles.get(ws) == 'gm' and data.get('command') in GM_COMMANDS:
                cmd = data['command']
                outgoing = {'type':'gm','command':cmd}
                if cmd in ('sim_hold','sim_release'):
                    number = data.get('button')
                    if type(number) is not int or not 1 <= number <= 16:
                        continue
                    outgoing['button'] = number
                print(f'[GM] {cmd} {outgoing.get("button", "")}', flush=True)
                for client in tuple(clients):
                    if not client.closed and roles.get(client) == 'player':
                        await client.send_str(json.dumps(outgoing))
    finally:
        clients.discard(ws)
        role = roles.pop(ws, None)
        if role == 'player':
            latest_state = None
            for client in tuple(clients):
                if not client.closed and roles.get(client) == 'gm':
                    await client.send_str(json.dumps({'type':'player_online','online':False}))
        print(f'[WEB] Browser disconnected; clients={len(clients)}', flush=True)
    return ws

async def serial_reader(app):
    port = app['port']
    baud = app['baud']
    while True:
        ser = None
        try:
            print(f'[SERIAL] Connecting to {port} @ {baud}...')
            ser = serial.Serial(port, baud, timeout=0.12)
            await asyncio.sleep(1.0)  # ESP32 resets when COM port opens
            print('[SERIAL] Connected — press a button to check incoming data', flush=True)
            while True:
                raw = await asyncio.to_thread(ser.readline)
                if not raw:
                    await asyncio.sleep(0.01)
                    continue
                line = raw.decode('utf-8', errors='ignore').strip()
                print(f'[RAW] {line!r}', flush=True)
                if line == 'READY,16':
                    print('[ESP32] Ready')
                    continue
                parts = line.split(',')
                if len(parts)!=3 or parts[0]!='BTN' or parts[2] not in ('DOWN','UP'):
                    continue
                try:
                    button=int(parts[1])
                except ValueError:
                    continue
                if not 1 <= button <= 16:
                    continue
                payload=json.dumps({'type':'button','button':button,'down':parts[2]=='DOWN'})
                for ws in tuple(clients):
                    if not ws.closed:
                        await ws.send_str(payload)
                print(f'[BUTTON] {button:02d} {parts[2]} -> {len(clients)} browser(s)', flush=True)
        except (serial.SerialException, OSError) as e:
            print(f'[SERIAL] {e} — retry in 2 seconds')
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            raise
        finally:
            if ser is not None:
                ser.close()

async def serial_context(app):
    task=asyncio.create_task(serial_reader(app))
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--port', default='COM7')
    parser.add_argument('--baud', type=int, default=115200)
    parser.add_argument('--http-port', type=int, default=8765)
    args=parser.parse_args()
    app=web.Application()
    app['port']=args.port
    app['baud']=args.baud
    app.router.add_get('/', index)
    app.router.add_get('/gm', lambda request: web.FileResponse(ROOT / 'gm.html'))
    app.router.add_get('/gm.html', lambda request: web.FileResponse(ROOT / 'gm.html'))
    app.router.add_get('/私库榜书.woff2', lambda request: web.FileResponse(ROOT / '私库榜书.woff2') if (ROOT / '私库榜书.woff2').exists() else web.Response(status=404))
    app.router.add_get('/ws', ws_handler)
    async def health(request):
        return web.json_response({'server':'ok','browser_connections':len(clients),'port':app['port']})
    app.router.add_get('/health', health)
    app.cleanup_ctx.append(serial_context)
    print(f'Open http://localhost:{args.http_port} in Chrome or Edge')
    web.run_app(app, host='127.0.0.1', port=args.http_port)
