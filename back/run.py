import logging

DEBUG = True

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.back.main:app", host="127.0.0.1", port=8000, reload=DEBUG)
