from tqdm import tqdm
from urllib.parse import quote, urlencode
import pyperclip
import time
import requests 
from pprint import pprint
from PIL import Image
from io import BytesIO
import os
import json


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

