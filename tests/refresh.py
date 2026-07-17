import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

user_data = {
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMmU1NjRjMS1mYTIyLTQ1M2QtYjE3YS0wZWYzMDEzMGE5MDUiLCJlbWFpbCI6Inh0YW5sZXlAZ21haWwuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3ODQ4NDU3MzEsInR5cGUiOiJyZWZyZXNoIn0.7M1tk7Q9294uL_Cjxgc1X5mnkSAY6ie6vL8ukhh5yIY"
}    

response = requests.post(
    f"{BASE_URL}/auth/refresh",
    json=user_data
)

print("Status Code:", response.status_code)

if response.ok:
    print("Refreshed!")
    print(response.json())
else:
    print("Retry!")
    print(response.text)


