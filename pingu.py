#!/usr/bin/env python3

import asyncio
import aioping
from kasa import SmartPlug

ip = "192.168.1.155"
internet = "8.8.8.8"

check_delay = 30
reboot_delay = 5
post_reboot_delay = 300

ping_timeout = 10

min_failures_for_reboot = 3

async def power_cycle(plug):
    await plug.turn_off()
    await asyncio.sleep(reboot_delay)
    await plug.turn_on()

async def internet_online():
    try:
        delay = await aioping.ping(internet, timeout=ping_timeout)
        return True
    except TimeoutError:
        return False

async def main():
    plug = SmartPlug(ip)

    await plug.update()

    num_failures = 0

    while True:
        success = await internet_online()
        if not success:
            print("ping failed")
            num_failures += 1

            if num_failures >= min_failures_for_reboot:
                print(f"outage detected, {num_failures} failures in a row")
                print("rebooting router")
                num_failures = 0
                await power_cycle(plug)
                print(f"done, sleeping for {post_reboot_delay} seconds")
                await asyncio.sleep(post_reboot_delay)
        else:
            print("ping succeeded")
            num_failures = 0
            await asyncio.sleep(check_delay)

if __name__ == "__main__":
    asyncio.run(main())
