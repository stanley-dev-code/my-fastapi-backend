import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

forgot_password_data = {
    "email": "xtanley@gmail.com"
}

response = requests.post(
    f"{BASE_URL}/auth/forgot-password",
    json=forgot_password_data
)

print("Status Code:", response.status_code)

if response.ok:
    print("OTP Sent Successfully!")
    print(response.json())
else:
    print("Request Failed!")
    print(response.text)