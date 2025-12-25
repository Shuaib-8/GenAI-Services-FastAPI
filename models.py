import numpy as np
import torch
from accelerate import Accelerator
from transformers import (
    AutoModel,
    AutoProcessor,
    BarkModel,
    BarkProcessor,
    Pipeline,
    pipeline,
)

from schemas import VoicePresets

accelerator = Accelerator()
device = torch.device(
    accelerator.device.type if accelerator.device.type == "mps" else "cpu"
)

prompt = "How to set up a FastAPI project?"
system_prompt = """Your name is FastAPI bot, and are a helpful
chatbot responsible for teaching FastAPI to your users.
Always respond in markdown format."""


def load_text_model() -> Pipeline:
    """Load the text model and return a pipeline."""
    pipe = pipeline(
        "text-generation",
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        torch_dtype=torch.float16,
        device=device,
    )
    return pipe


def load_audio_model() -> tuple[BarkProcessor, BarkModel]:
    """Load the audio model and return a tuple of processor and model."""
    processor = AutoProcessor.from_pretrained("suno/bark-small", device=device)
    model = AutoModel.from_pretrained("suno/bark-small").to(device)
    return processor, model


def generate_text(
    pipe: Pipeline, prompt: str, temperature: float = 0.7, top_p: float = 0.95
) -> str:
    """Generate text using the model."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    prompt = pipe.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    preds = pipe(
        prompt,
        max_new_tokens=256,
        temperature=temperature,
        do_sample=True,
        top_k=50,
        top_p=top_p,
    )
    output = preds[0]["generated_text"].split("</s>\n<|assistant|>\n")[-1]
    return output


def generate_audio(
    processor: BarkProcessor, model: BarkModel, prompt: str, preset: VoicePresets
) -> tuple[np.array, int]:
    """Generate audio using the model and return the audio array and the number of tokens."""
    inputs = processor(text=[prompt], return_tensors="pt", voice_preset=preset)
    # Move inputs to the same device as the model
    inputs = {
        k: v.to(model.device) if hasattr(v, "to") else v for k, v in inputs.items()
    }
    output = model.generate(**inputs, do_sample=True).cpu().numpy().squeeze()
    sample_rate = model.generation_config.sample_rate
    return output, sample_rate
