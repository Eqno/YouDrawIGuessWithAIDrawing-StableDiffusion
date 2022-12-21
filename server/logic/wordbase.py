import os

WORD_BASE_PATH = os.getcwd() + '/../data/wordbase/'

if not os.path.exists(WORD_BASE_PATH):
    os.makedirs(WORD_BASE_PATH)

print(WORD_BASE_PATH)

# 返回所有词集的名称
def get_set_list() -> list:
    return os.listdir(WORD_BASE_PATH)

def load_word_set(name:str):
    word_set = []
    try:
        with open(WORD_BASE_PATH + name, 'r') as f:
            word_set = f.read().split('\n')
            f.close()
    except:
        print('word set not exist')
    return word_set

def create_word_set(name:str, data:list):
    file_path = WORD_BASE_PATH + name
    if not os.path.exists(file_path):
        try:
            with open(file_path, 'w') as f:
                s = ''
                for i in data:
                    s += i + '\n'
                f.write(s)
                f.close()
        except:
            print('word set create failed')
    else: print('word set already exist')

def append_word_set(name:str, data:list):
    file_path = WORD_BASE_PATH + name
    if os.path.exists(file_path):
        try:
            with open(file_path, 'a') as f:
                s = ''
                for i in data:
                    s += i + '\n'
                f.write(s)
                f.close()
        except:
            print('word set append failed')
    else: print('word set not exist')
    pass