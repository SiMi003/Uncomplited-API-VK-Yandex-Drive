import configparser
from urllib.parse import urlencode
import webbrowser
import time


def tokens_folder():
    """
    The function clean the folder with tokens and id
    for writing new informations in this folder
    """
    with open('config.ini', 'w') as f:
        pass
    
def write_client_info():
    client_id = input('Please, input client ID:\n')
    vk_id = input('Please, input ID of your VK page:\n')
    with open('config.ini', 'a') as f:
        f.write('[VK]'  + '\n' + 'client_id=' + client_id + '\n' + 'vk_id=' + vk_id + '\n')
    return

def get_token_vk(client_id):
    """ 
    VK token getting and writing it in the 'config.ini' file
    """
    oath_base_url = 'https://oauth.vk.com/authorize'
    params = {'client_id':client_id,
              'redirect_uri':'https://oauth.vk.com/blank.html',
              'display':'page',
              'scope':'photos',
              'response_type':'token'} 
    # The method of urlencode allows to form url from params 
    oath_url = f'{oath_base_url}?{urlencode(params)}'
    # Openning the link in a random browser
    webbrowser.open(oath_url)
    time.sleep(5)
    input_token = input('Please, input VK token from an opened browser page (Note, that you\n' + 
                        'need to copy only part of the URL after words "access_token="):\n')
    with open('config.ini', 'a') as f:
        f.write('token_vk=' + input_token + '\n')
    return

def get_token_yandex():
    """ 
    Yandex token getting and writing it in the 'config.ini file
    """
    oath_url_yandex = 'https://yandex.ru/dev/disk/poligon/'
    webbrowser.open(oath_url_yandex)
    time.sleep(5)
    input_token = input('Please, input Yandex Drive token from an opened browser page:\n')
    with open('config.ini', 'a') as f:
        f.write('[Yandex Drive]'  + '\n' + 'token_yandex=' + input_token + '\n')
    return

def write_pc_path():
    """
    Function save an input path on your PC, 
    IF you need to save photos not only into Yandex Drive
    """
    agreement = input('Please, input "yes", if you would like to save photos to your PC:\n')
    with open('config.ini', 'a', encoding='utf-8') as f:
        f.write('[PC]'  + '\n' + 'agreement=' + agreement + '\n')
        if agreement == "yes":
            path_pc = input('Please, input path for saving photos into the PC:\n')
            f.write('path_pc=' + path_pc)
    return



if __name__ == '__main__':
    tokens_folder()
    write_client_info()
    config = configparser.ConfigParser()
    config.read('config.ini')  
    client_id = config["VK"]["client_id"]
    get_token_vk(client_id)
    get_token_yandex()
    write_pc_path()
