from fastapi import Body, FastAPI
from openai import AsyncOpenAI, OpenAI

app = FastAPI()

sync_client = OpenAI()
async_client = AsyncOpenAI()


@app.post("/sync-completion")
async def sync_completion(prompt: str = Body(...)):
    response = sync_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return {"response": response.choices[0].message.content}


@app.post("/async-completion")
async def async_completion(prompt: str = Body(...)):
    response = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return {"response": response.choices[0].message.content}
