import os
from dotenv import load_dotenv

print("CWD:", os.getcwd())
print(".env exists:", os.path.exists(".env"))

print("Before load_dotenv, DATABASE_URL:", repr(os.getenv("DATABASE_URL")))
load_dotenv()
print("After load_dotenv, DATABASE_URL:", repr(os.getenv("DATABASE_URL")))

print("HELLO FROM TEST_ENV")
