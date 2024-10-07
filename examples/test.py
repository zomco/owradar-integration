import aiohttp
from yarl import URL
import sys
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        url = URL.build(
            scheme="http", host="192.168.68.248", port=80, path="/api/device"
        )
        data = {"mqtt_state": 0}
        headers = {
            "Accept": "*/*",
        }
        await session.request(
            "POST", url, headers=headers, json=data, chunked=False, compress=False
        )


async def main1():
    url = URL.build(scheme="http", host="192.168.68.248", port=80, path="/api/device")
    data = {"mqtt_state": 0}
    headers = {"Accept": "*/*", "Transfer-Encoding": "deflate"}
    async with aiohttp.request("POST", url, headers=headers, json=data) as resp:
        print(await resp.text())


asyncio.run(main1())
