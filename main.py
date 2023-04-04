import os
import json
import requests
import vk_api
from tqdm import tqdm

class VkToYandex:
    def __init__(self, app_id, login, password):
        self.app_id = app_id
        self.login = login
        self.password = password
        self.yandex_token = ""
        self.vk_session = None
        self.vk_id = ""
        self.photos = []
        self.file_names = []
        self.file_info = []

    def auth_vk(self):
        self.vk_session = vk_api.VkApi(self.app_id, self.login, self.password)
        try:
            self.vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            print(error_msg)
            exit()

    def get_photos(self):
        vk = self.vk_session.get_api()
        self.photos = vk.photos.get(owner_id=self.vk_id, album_id="profile", rev=1)["items"]

    def upload_to_yandex(self):
        progress_bar = tqdm(total=len(self.photos), desc="Uploading photos")
        for photo in self.photos:
            photo_url = photo["sizes"][-1]["url"]
            response = requests.get(photo_url)
            file_name = f"{photo['id']}.jpg"
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            headers = {"Authorization": f"OAuth {self.yandex_token}"}
            params = {"path": file_name}
            response = requests.get(upload_url, headers=headers, params=params)
            upload_url = response.json()["href"]
            response = requests.put(upload_url, headers=headers, data=response.content)
            self.file_names.append(file_name)
            progress_bar.update(1)

    def get_file_info(self):
        progress_bar = tqdm(total=len(self.file_names), desc="Getting file info")
        for file_name in self.file_names:
            file_url = f"https://cloud-api.yandex.net/v1/disk/resources/download?path={file_name}"
            headers = {"Authorization": f"OAuth {self.yandex_token}"}
            response = requests.get(file_url, headers=headers)
            size = response.headers["Content-Length"]
            self.file_info.append({"file_name": file_name, "size": size})
                                   