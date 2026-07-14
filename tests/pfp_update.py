import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMmU1NjRjMS1mYTIyLTQ1M2QtYjE3YS0wZWYzMDEzMGE5MDUiLCJlbWFpbCI6Inh0YW5sZXlAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3ODQwNDMxMTEsInR5cGUiOiJhY2Nlc3MifQ.vCIQNxAJkeeaGX9YfK7ujqFHtO_sfmf1cbDKh1rYRh8"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

data = {
    "full_name": "xtanley xantiago",
    "email": "xtanley@gmail.com"
}

with open(r"C:\Users\user\OneDrive\Pictures\Camera Roll\IMG_20260518_201248_873.jpg", "rb") as image:
    files = {
        "profile_photo": image
    }

    response = requests.patch(
        f"{BASE_URL}/users/me",
        headers=headers,
        data=data,
        files=files
    )

print("Status Code:", response.status_code)
if response.ok:
    print("your profile pic is Successfully uploaded chief✋🤚!")   
else:
    print("upload Failed!")
print(response.text)