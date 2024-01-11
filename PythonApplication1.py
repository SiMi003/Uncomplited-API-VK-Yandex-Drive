# from urllib.request import Request, urlopen
# import pyautogui
# from progress.bar import IncrementalBar
# from progress.bar import Bar
import configparser
from tqdm import tqdm
from token import NUMBER
from urllib import request
from urllib.parse import quote, urlencode
import webbrowser
import pyperclip
import time
import requests 
from pprint import pprint
from PIL import Image
from io import BytesIO
import os
import json


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
    with open('config.ini', 'a') as f:
        f.write('[PC]'  + '\n' + 'agreement=' + agreement + '\n')
        if agreement == "yes":
            path_pc = input('Please, input path for saving photos into the PC:\n')
            f.write('path_pc=' + path_pc + '\n')
    return

class VKAPI:
    """
    https://dev.vk.com/ru/method/photos.get
    https://dev.vk.com/ru/api/api-requests
    """
    base_url = 'https://api.vk.com/method/'
    exact_methods = ['photos.get', 'photos.getAlbums']
    
    def __init__(self, token_vk, vk_id, version):
        self.id = vk_id
        self.version = version
        self.token = token_vk
        
    def __get_info_photos__(self, album_id):
        """
        Getting photos from an profile 
        """
        params = {'owner_id': self.id,
                  'album_id': album_id,
                  'rev':0,
                  'extended':1}
        response = requests.get(f'{self.base_url}{self.exact_methods[0]}?{urlencode(params)}'
                                f'&access_token={self.token}&v={self.version}')
        data = response.json()
        return data

    def links_photos(self, album_id, numbers_getting):
        """
        Finding a name of 'photo_size' parameter for each photo in the response
        with the aim to find a photo with maximum size (width and height)
        https://dev.vk.com/ru/reference/objects/photo-sizes
        """
        data = self.__get_info_photos__(album_id)
        numbers = min(data.get('response', {}).get('count'), numbers_getting)
        info_photos = {}
        for item in data.get('response', {}).get('items'):
            if len(info_photos) == numbers_getting:
                break
            likes = item.get('likes', {}).get('count')
            if likes in info_photos:
                likes = f"{likes}_{item.get('data', {})}"
            max_size = 0
            for element in item.get('sizes'):
                size = element.get('height')*element.get('width')
                if size > max_size:
                    max_size = size
            info_photos[likes] = [element.get('url'), max_size]       
        return info_photos
    
    def __alboms_list__(self):
        """
        Getting alboms id from a VK profile 
        """
        params = {'owner_id': self.id}
        response = requests.get(f'{self.base_url}{self.exact_methods[1]}?{urlencode(params)}'
                                f'&access_token={self.token}&v={self.version}')
        data = response.json()
        names_alboms = []
        for el in data.get('response').get('items'):
            names_alboms.append(el['title'])
        return pprint(names_alboms)    


class JSONinfo:
    """
    Creating json file with data about photo in below format: 
    [{"file_name": "34.jpg", "size": "z"}]
    """
    def __init__(self, dict_info, name_folder):
        self.folder = name_folder
        self.information_dict = dict_info
        
    def json_writing(self):
        """
        Function for forming a json file
        """
        json_data = {}
        number = 1
        for name, others in self.information_dict.items():
            json_data[number] = {"file_name": name, "size": others[1]}
            number += 1
        return json_data   
    

class YDAPI:
    """
    https://yandex.ru/dev/disk/api/reference/upload-ext.html
    """
    base_link = 'https://cloud-api.yandex.net/v1/disk/resources'
    
    def __init__(self, dict_info, json_data, token, name_folder):
        self.token = token
        self.folder = name_folder
        self.dict_ = dict_info
        self.json_ = json_data
        
    def __headers__(self):
        return {'Authorization': f'OAuth {self.token}'}
        
    def folder_creating_yandex(self):
        """
        Creating "name_folder" folder in "base_link" path, headers include only OAuth 
        """
        params = {'path': self.folder}
        url_full = f'{self.base_link}?{urlencode(params)}'
        responce = requests.put(url_full, headers = self.__headers__())
        print(responce.status_code)
        return 
    
    def __json_saving__(self):
        """
        The function allows to save file in the folder with Python code 
        """
        name_json = 'photo discription'
        with open(f'{name_json}.json', 'w') as file:
            json.dump(self.json_, file, indent=4)
        return name_json
    
    def __post_json_yandex__(self):
        """ 
        The function post the JSON file to the yandex drive to the same folder with photos
        """
        name_file = self.__json_saving__()
        path = f'{self.folder}/{name_file}.json'
        params = {
            'path': path}
        put_url = f'{self.base_link}/upload?{urlencode(params)}'
        local_path = f'{name_file}.json'
        with open(local_path, 'rb') as file:
            files = {'file': (local_path, file)}
            response = requests.post(put_url, headers=self.__headers__(), files=files)
        print(response.status_code)
        return 
                
    def saving_photos_yandex(self):
        """
        Saving photos by their URL on a Yandex Drive
        URL of each photo are included in the "dict_info" file 
        headers include only OAuth of Yandex Drive
        """
        for key, value  in self.dict_.items():
            path_photo = f'{self.folder}/{key}.jpg'
            url_photo = value[0]
            params = {'path': path_photo,
                        'url': url_photo}
            get_url = f'{self.base_link}/upload?{urlencode(params)}'
            response = requests.post(get_url, headers = self.__headers__())
            print(response.status_code)
            for i in tqdm(range(10)):
                pass
        self.__post_json_yandex__()
        return 


class PCsave: 
    """
    Saving photo from VK into your PC
    """
    def __init__(self, dict_info, json_data, base_path, name_folder):
        self.dict_ = dict_info
        self.json = json_data
        self.base_path = base_path
        self.folder = name_folder
        
    def folder_creating(self):
        # Use os.makedirs to create the folder and any necessary parent directories
        # 'exist_ok=True' ensures that the function does not raise an error if the folder already exists
        path = f'{self.base_path}{self.folder}'
        os.makedirs(path, exist_ok=True)
        return
    
    def __saving_photo__(self, photo, name_photo):
        path = f'{self.base_path}{self.folder}\\{name_photo}.jpg'
        photo.save(path)
        return
    
    def saving_photos(self):
        for name, info_photo  in list(self.dict_.items()):
            # .content allows to return content of responce in bytes (espetially for images)
            # BytesIO allow to convert 
            photo = Image.open(BytesIO(requests.get(info_photo[0]).content))
            self.__saving_photo__(photo, name)
            self.__json_saving_pc__()
        return
    
    def __json_saving_pc__(self):
        path = f'{self.base_path}{self.folder}\\ photo discription.json'
        with open(path, 'w') as file:
            # The indent parameter is optional and is used to format the JSON 
            # with indentation for better readability.
            json.dump(self.json, file, indent=4)





if __name__ == '__main__':
    
    # # !!Comment bellow functions after using it ones!!
    # tokens_folder()
    # write_client_info()
    # config = configparser.ConfigParser()
    # config.read('config.ini')  
    # client_id = config["VK"]["client_id"]
    # get_token_vk(client_id)
    # get_token_yandex()
    # write_pc_path()

    # Reading the complited file woth vk user and tokens info
    config = configparser.ConfigParser()
    config.read('config.ini') 
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

















