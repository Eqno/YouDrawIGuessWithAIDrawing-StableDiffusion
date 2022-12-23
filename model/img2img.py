import argparse
from stable_diffusion_tf.stable_diffusion import StableDiffusion
from PIL import Image

class Img2img:

    def __init__(self) -> None:
        
        self.args = None

        self.__create_generator__()

    def init_console_args(self):

        parser = argparse.ArgumentParser()

        parser.add_argument(
            "--prompt",
            type=str,
            nargs="?",
            required=True,
            help="the prompt to render",
        )

        parser.add_argument(
            "--negative-prompt",
            type=str,
            help="the negative prompt to use (if any)",
        )

        parser.add_argument(
            "--steps", 
            type=int, 
            default=50, 
            help="number of ddim sampling steps"
        )

        parser.add_argument(
            "--input",
            type=str,
            nargs="?",
            required=True,
            help="the input image filename",
        )

        parser.add_argument(
            "--output",
            type=str,
            nargs="?",
            default="img2img-out.jpeg",
            help="the output image filename",
        )

        self.args = parser.parse_args()

    def __create_generator__(self):

        self.generator = StableDiffusion(
            img_height=512,
            img_width=512,
            jit_compile=False,  # You can try True as well (different performance profile)
        )

    def generate_image_with_console_args(self):

        image = self.generator.generate(
            prompt=self.args.prompt,
            negative_prompt=self.args.negative_prompt,
            num_steps=self.args.steps,
            unconditional_guidance_scale=7.5,
            temperature=1,
            batch_size=1,
            input_image=self.args.input,
            input_image_strength=0.8
        )
        Image.fromarray(image[0]).save('server')

    def generate_image_with_func_params(self):
        
        pass