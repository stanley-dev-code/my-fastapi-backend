import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMmU1NjRjMS1mYTIyLTQ1M2QtYjE3YS0wZWYzMDEzMGE5MDUiLCJlbWFpbCI6Inh0YW5sZXlAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3ODQwNDMxMTEsInR5cGUiOiJhY2Nlc3MifQ.vCIQNxAJkeeaGX9YfK7ujqFHtO_sfmf1cbDKh1rYRh8"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

data = {
  "old_password": "Newpassword123",
  "new_password": "Password123"
}



response = requests.patch(
    f"{BASE_URL}/users/change-password",
    headers=headers,
    json=data
)

print("Status Code:", response.status_code)
if response.ok:
    print("password changed Successful!")   
else:
    print("change Failed!")
print(response.text)