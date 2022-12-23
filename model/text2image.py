import os
os.environ["CUDA_VISIBLE_DEVICES"] = "/device:CPU:0" # 指定 CPU
# os.environ["CUDA_VISIBLE_DEVICES"] = "0" # 指定显卡

# import tensorflow as tf
# config = tf.compat.v1.ConfigProto(allow_soft_placement=True)
# config.gpu_options.per_process_gpu_memory_fraction = 2
# config.gpu_options.allow_growth = True
# sess = tf.compat.v1.Session(config=config)

from tensorflow import keras
from .stable_diffusion_tf.stable_diffusion import StableDiffusion
import argparse
from PIL import Image
from PIL.PngImagePlugin import PngInfo

PLAYER_MAX_STORE_PIC_NUM = 1000
IMAGE_SAVE_PATH = os.getcwd() + '/server/data/pic/'

class Text2image:
    
    def __init__(self, image_height:int=64, image_width:int=64, use_mixed_precision:bool=False) -> None:

        self.args = None

        self.image_height = image_height
        self.image_width = image_width

        if use_mixed_precision:

            print("Using mixed precision.")
            keras.mixed_precision.set_global_policy("mixed_float16")

        self.__create_generator__()

    def init_console_args(self):

        parser = argparse.ArgumentParser()

        parser.add_argument(
            "--prompt",
            type=str,
            nargs="?",
            default="serafuku, direct looking, eyeball, hair flower, close-up, gentle eyes, Hanfu pure wind, beauty, atmosphere light, shadow, detail, high quality, master works",
            help="the prompt to render",
        )

        parser.add_argument(
            "--negative-prompt",
            type=str,
            help="the negative prompt to use (if any)",
        )

        parser.add_argument(
            "--output",
            type=str,
            nargs="?",
            default="output.png",
            help="where to save the output image",
        )

        parser.add_argument(
            "--H",
            type=int,
            default=512,
            help="image height, in pixels",
        )

        parser.add_argument(
            "--W",
            type=int,
            default=512,
            help="image width, in pixels",
        )

        parser.add_argument(
            "--scale",
            type=float,
            default=7.5,
            help="unconditional guidance scale: eps = eps(x, empty) + scale * (eps(x, cond) - eps(x, empty))",
        )

        parser.add_argument(
            "--steps", type=int, default=50, help="number of ddim sampling steps"
        )

        parser.add_argument(
            "--seed",
            type=int,
            help="optionally specify a seed integer for reproducible results",
        )

        parser.add_argument(
            "--mp",
            default=False,
            action="store_true",
            help="Enable mixed precision (fp16 computation)",
        )

        self.args = parser.parse_args()

        if self.args.mp:

            print("Using mixed precision.")
            keras.mixed_precision.set_global_policy("mixed_float16")

    def __create_generator__(self):

        if self.args:
            self.generator = StableDiffusion(
                img_height=self.args.H, 
                img_width=self.args.W, 
                jit_compile=False,
                download_weights=False
            )
        else:
            self.generator = StableDiffusion(
                img_height=self.image_height, 
                img_width=self.image_width, 
                jit_compile=False,
                download_weights=False
            )

    def generate_image_with_console_args(self):
        
        image = self.generator.generate(
            self.args.prompt,
            negative_prompt=self.args.negative_prompt,
            num_steps=self.args.steps,
            unconditional_guidance_scale=self.args.scale,
            temperature=1,
            batch_size=1,
            seed=self.args.seed,
        )

        pnginfo = PngInfo()
        pnginfo.add_text('prompt', self.args.prompt)
        Image.fromarray(image[0]).save(self.args.output, pnginfo=pnginfo)
        print(f"saved at {self.args.output}")

    def generate_image_with_func_params(self, positive:str, negtive:str, name:str, rand_seed:int=0):

        image = self.generator.generate(
            prompt=positive,
            negative_prompt=negtive,
            num_steps=self.args.steps,
            unconditional_guidance_scale=self.args.scale,
            temperature=1,
            batch_size=1,
            seed=rand_seed,
        )

        for i in range(0, PLAYER_MAX_STORE_PIC_NUM):
            path = IMAGE_SAVE_PATH + name + '/' + i + '.png'
            if not os.path.exists(path):
                Image.fromarray(image[0]).save(path)
                return path

        print('player could not store any more pic')
        return None

generator = Text2image(64, 64, True)

def generate_image(positive:str, negtive:str, name:str, rand_seed:int=0):

    generator.generate_image_with_func_params(positive, negtive, name, rand_seed)