import asyncio
import time


def sync_task():
    print("Start of sync task")
    time.sleep(5)
    print("Task resumed after 5 seconds")


async def async_task():
    print("Start of async task")
    await asyncio.sleep(5)
    print("Task resumed after 5 seconds")


start_time = time.time()
for _ in range(3):
    sync_task()
end_time = time.time()
print(f"\nTime taken for sync tasks: {end_time - start_time} seconds")


# would've taken 50 (5 seconds x 10 tasks) seconds to complete if we had not used asyncio.gather
async def spawn_tasks():
    await asyncio.gather(
        async_task(),
        async_task(),
        async_task(),
        async_task(),
        async_task(),
        async_task(),
        async_task(),
        async_task(),
        async_task(),
        async_task(),
    )


start_time = time.time()
asyncio.run(spawn_tasks())
end_time = time.time()

print(f"\nTime taken for async tasks: {end_time - start_time} seconds")
