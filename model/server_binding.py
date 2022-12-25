import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "/device:CPU:0"  # 指定 CPU
import time
import traceback
from pathlib import Path

from PIL import Image
from tensorflow import keras

from stable_diffusion_tf.stable_diffusion import StableDiffusion

CWD = Path(os.getcwd())
if os.path.basename(CWD) == 'model' or os.path.basename(CWD) == 'server':
    CWD = CWD.parent
IMAGE_SAVE_PATH = CWD / 'data' / 'pic'

if not IMAGE_SAVE_PATH.exists():
    os.mkdir(IMAGE_SAVE_PATH)


class Text2image(object):

    def __init__(self,
                 image_height: int = 64,
                 image_width: int = 64,
                 steps: int = 50,
                 scale: float = 7.5,
                 use_mixed_precision: bool = False) -> None:

        self.image_height = image_height
        self.image_width = image_width
        self.steps = steps
        self.scale = scale

        if use_mixed_precision:
            keras.mixed_precision.set_global_policy("mixed_float16")

        self.init_stable_diffusion()

    def init_stable_diffusion(self):
        self.generator = StableDiffusion(img_height=self.image_height,
                                         img_width=self.image_width,
                                         jit_compile=False,
                                         download_weights=False)

    def __generate_image_with_func_params(self,
                                          positive_list: list,
                                          negative_list: list,
                                          name: str,
                                          rand_seed: int = -1):
        filename = '{name}.png'.format(name=name)
        path = IMAGE_SAVE_PATH / filename
        if os.path.exists(path):
            return False, 'File Exists!'

        positive = None
        negative = None

        # positive prompt must exist
        if not isinstance(positive_list, list):
            return False, 'Invalid type for "positive_list"'
        positive = ', '.join(positive_list)

        # negative prompt can be empty
        if isinstance(negative_list, list) and len(negative_list) > 0:
            negative = ', '.join(negative)

        # use current timestamp as random seed
        if rand_seed < 0:
            rand_seed = int(time.time())

        image = self.generator.generate(
            prompt=positive,
            negative_prompt=negative,
            num_steps=self.steps,
            unconditional_guidance_scale=self.scale,
            temperature=1,
            batch_size=1,
            seed=rand_seed,
        )

        Image.fromarray(image[0]).save(path)
        return True, path

    def generate_image_with_func_params(self,
                                        positive_list: list,
                                        negative_list: list,
                                        name: str,
                                        rand_seed: int = -1):
        try:
            return self.__generate_image_with_func_params(
                positive_list, negative_list, name, rand_seed)
        except Exception as e:
            traceback.print_exc()
            return False, 'Unknown problem'


def main():
    '''Just for test'''

    param_capoo = [
        'blue cat', 'single cat', 'fat', 'comic', 'six foots', 'full body',
        'white background', 'black eyes', 'short legs', 'detail',
        'high quality', 'master works'
    ]
    #param_def = ['serafuku', 'direct looking', 'eyeball', 'hair flower', 'close-up', 'gentle eyes', 'Hanfu pure wind', 'beauty', 'atmosphere light', 'shadow', 'detail', 'high quality', 'master works']
    param = param_capoo

    img_size = 256
    steps = 50
    scale = 7.5
    mixed_precision = False

    seed = int(time.time())
    filename = 'size_{size}-step_{step}-scale_{scale}-{time}'.format(
        size=img_size, step=steps, scale=scale, time=seed)

    generator = Text2image(img_size,
                           img_size,
                           steps=steps,
                           scale=scale,
                           use_mixed_precision=mixed_precision)

    ret = generator.generate_image_with_func_params(param,
                                                    None,
                                                    filename,
                                                    rand_seed=seed)


if __name__ == '__main__':
    main()
