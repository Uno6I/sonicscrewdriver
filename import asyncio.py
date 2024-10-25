import asyncio
from kasa import Discover

async def discover_devices():
    devices = await Discover.discover()
    for addr, dev in devices.items():
        print(f"Found device: {dev.alias} at {addr}")

asyncio.run(discover_devices())
