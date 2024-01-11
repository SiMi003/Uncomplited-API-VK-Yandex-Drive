import configparser
from tqdm import tqdm
#from token import NUMBER
#from urllib import request
from urllib.parse import quote, urlencode
#import webbrowser
import pyperclip
import time
import requests 
from pprint import pprint
from PIL import Image
from io import BytesIO
import os
import json


import module3


if __name__ == '__main__':

    # Reading the complited file woth vk user and tokens info
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8') 
    vk_id = config["VK"]["vk_id"]
    token_vk = config["VK"]["token_vk"]
    token_yandex = config["Yandex Drive"]["token_yandex"]
    agreement = config["PC"]["agreement"]

    alboms_ids = ['profile', 'wall', 'saved']
    answer = input(f'Please, choose the locate of photos for saving.\n'
                   f'- Input "0" if you would like to save {alboms_ids[0]} photos.\n'
                   f'- Input "1" if you would like to save {alboms_ids[1]} photos.\n'
                   f'- Input "2" if you would like to save {alboms_ids[2]} photos.\n'
                   f'Your answer:')
    
    atributs = {'VK':   {'vk_id':vk_id,
                         'version':'5.199',
                         'token_vk':token_vk},
                'JSON': {'name_new_folder': 'photos VK'},
                'YD':   {'token_yandex': token_yandex,
                         'name_folder_yandex': 'photos VK'}
                }
    
    vk = VKAPI(atributs['VK']['token_vk'],
               atributs['VK']['vk_id'],
               atributs['VK']['version'])
    dict_info = vk.links_photos(album_id = alboms_ids[int(answer)], numbers_getting = 20)
    
    # # Just for checking how it works, latter I impruve this: 
    # print('the list of your VK alboms:', end = '\n')
    # vk.__alboms_list__()

    js = JSONinfo(dict_info,
                  atributs['JSON']['name_new_folder'])
    json_data = js.json_writing()

    yandex = YDAPI(dict_info,
                   json_data,
                   atributs['YD']['token_yandex'],
                   atributs['YD']['name_folder_yandex'])
    yandex.folder_creating_yandex()
    yandex.saving_photos_yandex()
    
    if agreement == "yes":
        base_path = config["PC"]["path_pc"]
        name_new_folder = 'photos VK'
        pc = PCsave(dict_info,
                    json_data,
                    atributs['PC']['base_path'],
                    atributs['PC']['name_new_folder'])
        pc.folder_creating()
        pc.saving_photos()

















