import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

user_data = {
    "full_name": "xtanley xantiago",
    "email": "xtanley@gmail.com",
    "password": "Password123!"
}

response = requests.post(
    f"{BASE_URL}/auth/register",
    json=user_data
)

print("Status Code:", response.status_code)

if response.ok:
    print("Registration Successful!")
    print(response.json())
else:
    print("Registration Failed!")
    print(response.text)


