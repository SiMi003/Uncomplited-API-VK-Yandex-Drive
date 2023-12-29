# from urllib.request import Request, urlopen
# import pyautogui
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
    with open('tokens.txt', 'w') as f:
        pass
    
    
def write_client_info():
    client_id = input('Please, input client ID:\n')
    vk_id = input('Please, input ID of your VK page:\n')
    with open('tokens.txt', 'a') as f:
        f.write(client_id + '\n' + vk_id + '\n')
    return

def get_token_vk(client_id):
    """ 
    VK token getting and writing it in the "tokens.txt" file
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
    input_token = input('Please, input VK token from an opened browser page:\n')
    with open('tokens.txt', 'a') as f:
        f.write(input_token + '\n')
    return


def get_token_yandex():
    """ 
    Yandex token getting and writing it in the "tokens.txt" file
    """
    oath_url_yandex = 'https://yandex.ru/dev/disk/poligon/'
    webbrowser.open(oath_url_yandex)
    time.sleep(5)
    input_token = input('Please, input Yandex Drive token from an opened browser page:\n')
    with open('tokens.txt', 'a') as f:
        f.write(input_token + '\n')
    return


class VKAPI:
    """
    https://dev.vk.com/ru/method/photos.get
    https://dev.vk.com/ru/api/api-requests
    """
    base_url = 'https://api.vk.com/method/'
    exact_method = 'photos.get'
    
    def __init__(self, token_vk, vk_id, version):
        self.id = vk_id
        self.version = version
        self.token = token_vk
        
    def __get_info_photos__(self):
        """
        Getting photos from an profile 
        """
        params = {'owner_id':self.id,
                  'album_id':'profile',
                  'rev':0,
                  'extended':1}
        response = requests.get(f'{self.base_url}{self.exact_method}?{urlencode(params)}'
                                f'&access_token={self.token}&v={self.version}')
        data = response.json()
        print(data)
        return data

    def links_photos(self, numbers_getting = 5):
        """
        Finding a name of 'photo_size' parameter for each photo in the response
        with the aim to find a photo with maximum size (width and height)
        https://dev.vk.com/ru/reference/objects/photo-sizes
        """
        data = self.__get_info_photos__()
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


class JSONinfo:
    """
    Creating json file with data about photo in below format: 
    [{"file_name": "34.jpg", "size": "z"}]
    """
    def __init__(self, dict_info, base_path, name_folder):
        self.base_path = base_path
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
        return 

    # def __json_saving_pc__(self):
    #     self.json_
    #     requests.post(..., headers = self.__headers__())


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
    # with open('tokens.txt', 'r') as f:  
    #     client_id = f.readline().rstrip('\n')
    # get_token_vk(client_id)
    # get_token_yandex()
    

    # Reading the complited file woth vk user and tokens info
    with open('tokens.txt', 'r') as f:
        lines = f.readlines() 
        vk_id = lines[1].rstrip('\n')
        token_vk = lines[2].rstrip('\n')
        token_yandex = lines[3].rstrip('\n')

     
    atributs = {'VK':   {'vk_id':vk_id,
                         'version':'5.199',
                         'token_vk':token_vk},
                'JSON': {'base_path': 'C:\\Users\\alexa\\OneDrive\\Рабочий стол\\',
                         'name_new_folder': 'photos VK'},
                'PC':   {'base_path': 'C:\\Users\\alexa\\OneDrive\\Рабочий стол\\',
                         'name_new_folder': 'photos VK'},
                'YD':   {'token_yandex': token_yandex,
                         'name_folder_yandex': 'photos VK'}
                }     
    vk = VKAPI(atributs['VK']['token_vk'],
               atributs['VK']['vk_id'],
               atributs['VK']['version'])
    dict_info = vk.links_photos()

    js = JSONinfo(dict_info,
                  atributs['JSON']['base_path'],
                  atributs['JSON']['name_new_folder'])
    json_data = js.json_writing()

    yandex = YDAPI(dict_info,
                   json_data,
                   atributs['YD']['token_yandex'],
                   atributs['YD']['name_folder_yandex'])
    yandex.folder_creating_yandex()
    
    yandex.saving_photos_yandex()
    pc = PCsave(dict_info,
                json_data,
                atributs['PC']['base_path'],
                atributs['PC']['name_new_folder'])
    pc.folder_creating()
    pc.saving_photos()



















