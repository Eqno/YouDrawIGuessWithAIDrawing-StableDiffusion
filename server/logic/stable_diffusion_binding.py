# -*- coding: utf-8 -*-

import os
import sys
import time
import hashlib
import threading

sys.path.append(os.path.dirname(__file__))
from kv_queue import KVqueue

from . import consts

sys.path.append(str(consts.cwd / 'model'))
import server_binding as stable_diffusion

generated_img_size = 256
default_positive_prompt = ['detail', 'high quality', 'master works']
default_negative_prompt = ['nsfw', 'aldult', 'porn']


def prompt_str_to_list(prompts: str) -> list:
    splited_result = (p.strip() for p in prompts.split(','))
    non_empty_result = list(filter(lambda s: len(s) > 0, splited_result))
    return non_empty_result


def generate_image(model_instance,
                   filename_prefix: str,
                   positive_str: str,
                   negative_str: str,
                   random_seed: int = -1):
    positive = prompt_str_to_list(positive_str)
    negative = prompt_str_to_list(negative_str)
    for p in default_positive_prompt:
        positive.append(p)
    for p in default_negative_prompt:
        negative.append(p)

    raw_filename = '{}-{}'.format(filename_prefix, int(time.time()))
    filename = hashlib.md5(raw_filename.encode()).hexdigest()
    print('{} -> {}'.format(raw_filename, filename))
    status, _ = model_instance.generate_image_with_func_params(
        positive, negative, filename, rand_seed=random_seed)
    if status:
        return filename
    return None


def stable_diffusion_thread(model_instance, task_queue: KVqueue,
                            img_queue: KVqueue):
    while True:
        time.sleep(1)
        if task_queue.is_empty():
            continue
        username, task = task_queue.pop()
        if task is None:
            continue
        print('sd-thread working')
        ret = generate_image(model_instance, username, task['positive'],
                             task['negative'], task['rand_seed'])
        print('sd-thread done, ret=', ret)
        # Node that the `ret` could be `None`
        img_queue.push(username, ret)


def stable_diffusion_init(task_queue: KVqueue, img_queue: KVqueue):
    model_instance = stable_diffusion.Text2image(generated_img_size,
                                                 generated_img_size)

    main_thread = threading.Thread(
        target=stable_diffusion_thread,
        args=[model_instance, task_queue, img_queue])
    main_thread.daemon = True
    main_thread.start()

    return main_thread


def selftest_thread(tq: KVqueue, iq: KVqueue):
    prompt = 'serafuku, direct looking, eyeball, hair flower, close-up, gentle eyes, Hanfu pure wind, beauty, atmosphere light, shadow, detail, high quality, master works'

    while True:
        print(
            'tq.push, test1:',
            tq.push('test1', {
                'positive': prompt,
                'negative': '',
                'rand_seed': -1
            }))
        tq.dump()
        print(
            'tq.push, test1:',
            tq.push('test1', {
                'positive': prompt,
                'negative': '',
                'rand_seed': -1
            }))
        tq.dump()
        time.sleep(10)
        print(
            'tq.push, test1:',
            tq.push('test1', {
                'positive': prompt,
                'negative': '',
                'rand_seed': -1
            }))
        tq.dump()
        time.sleep(10)
        print(
            'tq.push, test2:',
            tq.push('test2', {
                'positive': prompt,
                'negative': '',
                'rand_seed': -1
            }))
        tq.dump()

        for _ in range(18):
            iq.dump()
            print(iq.pop())
            time.sleep(10)


def selftest():
    tq = KVqueue()
    iq = KVqueue()

    #sd_thread = stable_diffusion_init(tq, iq)
    st_thread = threading.Thread(target=selftest_thread, args=[tq, iq])
    st_thread.daemon = True
    st_thread.start()
    #sd_thread.join()
    st_thread.join()


if __name__ == '__main__':
    selftest()
