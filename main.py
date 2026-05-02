from fastapi import FastAPI

app = FastAPI()

@app.get("/scan")
def scan():
    return {
        "TSLA": {
            "price": 242.5,
            "signal": "CALL",
            "confidence": "HIGH"
        },
        "AAPL": {
            "price": 190.2,
            "signal": "PUT",
            "confidence": "MEDIUM"
        }
    }