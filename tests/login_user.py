import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

login_data = {
    "email": "xtanley@gmail.com",
    "password": "Password123!"
}

response = requests.post(
    f"{BASE_URL}/auth/login",
    json=login_data
)

print("Status Code:", response.status_code)

if response.ok:
    tokens = response.json()

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    print("\nLogin Successful!")

    print("\nAccess Token:")
    print(access_token)

    print("\nRefresh Token:")
    print(refresh_token)

else:
    print("Login Failed!")
    print(response.text)