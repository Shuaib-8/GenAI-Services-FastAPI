import bentoml
from PIL import Image

from models import load_image_model


@bentoml.service(
    resources={
        "cpu": 4,
    },
    traffic={"timeout": 120},
    http={
        "port": 5001
    },  # BentoML default port is 5000 - 5001 to not clash with mac OS default port 5000 control center
)
class ImageGenerationService:
    def __init__(self):
        self.image_model = load_image_model()

    @bentoml.api(route="/generate/image")
    def generate_image(self, prompt: str) -> Image.Image:
        output = self.image_model(prompt, num_inference_steps=10).images[0]
        return output
