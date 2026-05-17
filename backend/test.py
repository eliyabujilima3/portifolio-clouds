import requests

url = "http://127.0.0.1:5000/api/contact"

data = {
    "name": "Eliya",
    "email": "test@gmail.com",
    "message": "Hello"
}

res = requests.post(url, json=data)

print(res.json())