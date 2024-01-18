import requests
import os
import time

path = os.getcwd()
files = os.listdir(path)

input_file_name ='lama_300px.png'
output_file_name ='lama_600px.png'
input_file_path = str(os.path.join(path, input_file_name))
output_file_path = str(os.path.join(path, output_file_name))


data = requests.post('http://127.0.0.1:5000/upscale',
                     json={'input_file_path': input_file_path,
                     'output_file_path':output_file_path})

task_id = data.json()['task_id']
print(task_id)

status = 'PENDING'
while status == 'PENDING':
    data = requests.get(f'http://127.0.0.1:5000/tasks/{task_id}')
    print(data.json())
    status = data.json()['status']
    time.sleep(10)

data = requests.get(f'http://127.0.0.1:5000/processed/{output_file_path}')