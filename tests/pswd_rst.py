import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

reset_password_data = {
    "email": "xtanley@gmail.com",
    "otp": "H1PJAS",
    "new_password": "NewPassword123!"
}

response = requests.post(
    f"{BASE_URL}/auth/reset-password",
    json=reset_password_data
)

print("Status Code:", response.status_code)

if response.ok:
    print("Password Reset Successful!")
    print(response.json())
else:
    print("Password Reset Failed!")
    print(response.text)