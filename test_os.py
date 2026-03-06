from outscraper import ApiClient
import os

api_client = ApiClient(api_key=os.environ.get("OUTSCRAPER_API_KEY", "dummy"))
print(dir(api_client))
