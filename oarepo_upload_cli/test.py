import requests

url = 'https://localhost:5000/api/uct-theses/'
files_url = 'bj7gx-46s58/files'
headers = { "Content-Type": "application/json" }

response = requests.get(url=f'{url}{files_url}', headers=headers, verify=False)

payload = response.json()
print(payload['entries'][0]['updated'])