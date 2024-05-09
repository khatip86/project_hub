import netifaces
import ipaddress
from Crypto.PublicKey import RSA
import requests
from dataclasses import dataclass
from random import randint
import json
import os
from datetime import time
from pathlib import Path
from .objects import encrypt_object, decrypt_object, encrypt_data, decrypt_data, find_in_object
from .settings import * 
@dataclass
class User:

  # initial 
  def __init__(self, name: str):
    self.__name = name
    self.__ip = self.__get_local_ip()
    self.__generate_keys()
    # self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.__user_info = USER_INFO
    self.__user_info["user_name"] = str(self.__name)
    self.__user_info["user_ip"] = str(self.__ip)
    self.__user_info["user_pub_key"]= str(self.public_key)

    with open('objects/self/user-info.json', 'w') as f:
      f.write(json.dumps(encrypt_object(self.__user_info, self.public_key), sort_keys=True))
      f.close()

    with open('objects/self/users-online.json', 'w+') as f:
      f.write(json.dumps(encrypt_object(USERS_ONLINE, self.private_key), sort_keys=True))
      f.close()

  # methods
  def __generate_keys(self):
    key = RSA.generate(2048)
    self.__private_key = key.export_key(format='PEM',
                                        passphrase=None,
                                        pkcs=8,
                                        protection='PBKDF2WithHMAC-SHA512AndAES256-CBC',
                                        prot_params={'iteration_count': 21000})

    self.__public_key = key.public_key().export_key(format='PEM')   



  def __get_local_ip(self): 
    for interface in netifaces.interfaces():
        if netifaces.AF_INET in netifaces.ifaddresses(interface):
            for address_info in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                address_object = ipaddress.IPv4Address(address_info['addr'])
                if not address_object.is_loopback:
                   return address_info['addr']

  def send_message(self, reciever_ip, reciever_name: str, message):
    chat = CHAT 
    chat_object = CHAT_OBJECT
    chat_object["user_name"] = str(self.name)
    chat_object["user_ip"] = str(self.ip)
    chat_object["time"] = f"{time.hour}:{time.minute}"
    chat_object["message"] = str(message)

    if not os.path.exists(os.getcwd() + f'/objects/chat/{reciever_name}_{reciever_ip}'):

      os.makedirs(os.getcwd() + f'/objects/chat/{reciever_name}_{reciever_ip}')

      with open(os.getcwd() + f'/objects/chat/{reciever_name}_{reciever_ip}', 'w') as f:
        f.write(json.dumps(encrypt_object(chat["chat"].append(chat_object), self.public_key), sort_keys=True))
        f.close()

    else:

      with open(f'objects/chat/{reciever_name}_{reciever_ip}', 'r') as f:
        chat = decrypt_object(json.load(f), self.private_key)
        f.close()

      with open('objects/self/users-online.json', 'r') as f, open(f'objects/chat/{reciever_name}_{reciever_ip}', 'w') as f2:
        f2.write(json.dumps(encrypt_object(chat["chat"].append(chat_object), self.public_key), sort_keys=True))
        users_online = decrypt_object(json.load(f), self.private_key)
        reciever = find_in_object(users_online, reciever_ip)
        message = {
          'data' : str(encrypt_object(chat_object, reciever["user_pub_key"]))
        }
        requests.post(f'http://' + reciever_ip + ':9091/message', data = message) #in progress
        f2.close()
        f.close()

  def __recv_message(self, data: dict):
    data = decrypt_object(data, self.private_key)
    chat = CHAT
    chat_object = CHAT_OBJECT
    chat_object["user_name"] = data["user_name"]
    chat_object["user_ip"] = data["user_ip"]
    chat_object["time"] = f"{time.hour}:{time.minute}"
    chat_object["message"] = data["message"]
    
    if not os.path.exists(os.getcwd() + f'/objects/chat/{chat_object["user_name"]}_{chat_object["user_ip"]}'):
      os.makedirs(os.getcwd() + f'/objects/chat/{chat_object["user_name"]}_{chat_object["user_ip"]}')
      with open(os.getcwd() + f'/objects/self/{chat_object["user_name"]}_{chat_object["user_ip"]}', 'w') as f:
        f.write(json.dumps(encrypt_object(chat["chat"].append(chat_object), self.public_key), sort_keys=True))
        f.close()
    else:

      with open(f'objects/chat/{chat_object["user_name"]}_{chat_object["user_ip"]}', 'r') as f:
        chat = decrypt_object(json.load(f), self.private_key)
        f.close()

      with open(f'objects/chat/{chat_object["user_name"]}_{chat_object["user_ip"]}', 'w') as f:
        f.write(json.dumps(encrypt_object(chat["chat"].append(chat_object), self.public_key), sort_keys=True))
        f.close()
    
  def __chat_info(self, user_name, user_ip):
    if os.path.exists(os.getcwd() + f'/objects/chat/{user_name}_{user_ip}'):
      with open(f'objects/chat/{user_name}_{user_ip}', 'r') as f:
        chat = decrypt_object(json.load(f), self.__private_key)
        return chat["chat"]
    else:
      return "С данным пользователем нет переписок"


  def __initial(self):
    net_ip = '.'.join(self.__ip.split('.')[:3]) + '.'
    i = 2
    users_to_ping = list()
    # used_id = list()

    while i < 255:
      try:
        if f'{net_ip}{i}' != self.__ip:
          if len(users_to_ping) < 4:
            resp = requests.get(f'http://{net_ip}{i}:{9091}/', timeout=0.1)
            if resp.ok:
              # if len(users_to_ping) <= 4:
              users_to_ping.append(f'{net_ip}' + str(i))
              resp = requests.get(f'http://{net_ip}{i}:{9091}/user')
              self.__add_user(eval(resp.text))
              # used_id.append(resp['user_id'])
              with open('objects/self/user-info.json', 'r') as f1, open('objects/self/users-online.json', 'r') as f2:
                user_info = decrypt_object(json.load(f1), self.private_key)
                users_online = decrypt_object(json.load(f2), self.private_key)
                requests.post(
                  f'http://{net_ip}{i}:{9091}/user',
                  data = { 'data' : str(encrypt_object(user_info, find_in_object(users_online['users_online'], f'{net_ip}{i}')['user_pub_key']))})
                f1.close()
                f2.close()
              i += 1
              continue
          else:
            break
        else:
          i += 1
          continue
      except requests.exceptions.ConnectionError:
        i += 1
        continue
    
  # TODO
  # def __generate_user_id(self, data: tuple[list, set, tuple]):
  #   id = str(randint(1, 10000))
  #   if id in data:
  #     self.__generate_user_id(data)
  #   else:
  #     self.__user_info['user_id'] = str(id)

  def __remove_user(self, removed_user: dict):
    file_data = None
    with open('objects/self/users-online.json', 'r') as f:
      file_data = decrypt_object(json.load(f), self.private_key)
      f.close()
    if find_in_object(file_data, removed_user) != None:
      with open('objects/self/users-online.json', 'w') as f:
        f.write(json.dumps(encrypt_object(file_data['users_online'].remove(removed_user), self.public_key)))
        f.close()
    else:
      print('Пользователь не найден...')

  def call_to_remove_user(self):
    try:
      with open('objects/self/users-online.json', 'r') as f1, open('objects/self/user-info.json', 'r') as f2:
        users_online = decrypt_object(json.load(f1), self.private_key)
        user_info = decrypt_object(json.load(f2), self.private_key)
        for i in users_online['users_online']:
          user_ip = i['user_ip'] 
          requests.post(f'http://{user_ip}:{9091}/remove-user', data = {"data" : str(encrypt_object(user_info, i['user_pub_key']))})
        f1.close()
        f2.close()
        os.remove('objects/self/user-info.json')
        os.remove('objects/self/users-online.json')
    except:
      print("Connection error")
      self.call_to_remove_user()

  def __add_user(self, data: dict):
    file_data = None 
    with open('objects/self/users-online.json', 'r') as f:
      file_data = decrypt_object(json.load(f), self.private_key)
      f.close()
    print(file_data)
    for i in file_data['users_online']:
      print("File data content type:" , type(i))
    if find_in_object(file_data, data) == None:
      file_data['users_online'].append(data)
      with open('objects/self/users-online.json', 'w') as f:
        f.write(json.dumps(encrypt_object(file_data, self.public_key)))
        f.close()
    else:
      print('Пользователь уже существует')
  
  # getters
  @property
  def user_info(self):
    with open('objects/self/user-info.json', 'r') as f:
      return decrypt_object(json.load(f), self.private_key)
  
  @property
  def users_online(self):
    try:
      with open('objects/self/users-online.json', 'r') as f:
        data = json.load(f)
        return decrypt_object(data, self.private_key)
    except FileNotFoundError:
      return None
  
  @property
  def ip(self):
    return self.__ip
  
  @property
  def name(self):
    return self.__name

  @property
  def public_key(self):
    return self.__public_key.decode()

  @property
  def private_key(self):
    return self.__private_key.decode()

  @property
  def remove_user(self):
    pass

  @remove_user.setter
  def remove_user(self, data: dict):
    return self.__remove_user(data)

  @property
  def add_user(self):
    pass
  
  @add_user.setter
  def add_user(self, data: dict):
    self.__add_user(data)

  @property
  def initial(self):
    self.__initial()

  @property
  def recv_message(self):
    pass 

  @recv_message.setter
  def recv_message(self, data: dict):
    return self.__recv_message(data)

  @property
  def chat_info(self):
    pass 

  @chat_info.setter
  def chat_info(self, user_name: str, user_ip: str):
    return self.__chat_info(user_name, user_ip)

  # @property
  # def id(self):
  #   return self.__id
