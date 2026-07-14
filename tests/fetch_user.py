import requests
BASE_URL = "http://127.0.0.1:8000/api/v1"

ACCESS_TOKEN ='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ZmI2YWVlOS1hZjU0LTRmMmUtOWJlNC0wMGQ2MGU4NjdmNDQiLCJlbWFpbCI6Inh0YW5sZXlAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3ODM1MjcxNDAsInR5cGUiOiJhY2Nlc3MifQ.OP5PIvkV9RXMAWGYiEmHPI0cS9Xx7P3_eo8j5a0n7CE'

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

response = requests.get(
    f"{BASE_URL}/users/me",
    headers=headers
)

print("Status Code:", response.status_code)
if response.ok:
    main = response.json()


    print("id:", main.get("id"))
    print("full_name:", main.get("full_name"))
    print("email:",main.get("email"))
    print("profile_photo_url:", main.get("profile_photo_url"))
    print("bio:", main.get("bio"))
    print("date_of_birth:", main.get("date_of_birth"))
    print("gender:", main.get("gender"))
    print("nationality:", main.get("nationality"))
    print("phone_number:",main.get("phone_number"))
    print("address:",main.get("address"))
    print("role:",main.get("role"))
    print("is_active:",main.get("is_active"))
    print("created_at:", main.get("created_at"))

else:
    print("Failed to fetch data.")
    print("Error Details:", response.text)