import asyncio
import time
from threading import Thread


class AsyncLoopThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()


async def main(time):
    async def task(time):
        print("start sleeping", time)
        await asyncio.sleep(time)
        print("end sleeping", time)
        print(input(":"))

    # await asyncio.create_task(task(time))
    asyncio.run_coroutine_threadsafe(task(time), loop_handler.loop)


async def run_m():
    # asyncio.create_task(main(1))
    # asyncio.create_task(main(2))
    # asyncio.create_task(main(3))
    await main(1)
    await main(2)
    await main(3)


if __name__ == '__main__':
    loop_handler = AsyncLoopThread()
    loop_handler.start()
    # asyncio.get_event_loop().run_until_complete(run_m())
    asyncio.get_event_loop().create_task(run_m())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run())
    asyncio.get_event_loop().run_forever()
    # time.sleep(15)
