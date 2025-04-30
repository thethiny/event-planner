import os

CUR_ENV = os.environ.get("CURRENT_ENV", "local")
ENV_PATH = "env"

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(ENV_PATH, f"{CUR_ENV}.env"))
except ImportError:
    print(f"dotenv lib doesn't exist, make sure environments are exported correctly")
    pass

print(f"Current Environment: {CUR_ENV}")