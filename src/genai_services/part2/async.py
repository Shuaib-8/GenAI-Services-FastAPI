import asyncio
import time


async def task():
    print("Start of async task")
    await asyncio.sleep(5)
    print("Task resumed after 5 seconds")


# would've taken 50 (5 seconds x 10 tasks) seconds to complete if we had not used asyncio.gather
async def spawn_tasks():
    await asyncio.gather(
        task(), task(), task(), task(), task(), task(), task(), task(), task(), task()
    )


start_time = time.time()
asyncio.run(spawn_tasks())
end_time = time.time()

print(f"Time taken: {end_time - start_time} seconds")
