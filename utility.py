import base64

def decode(data:str) -> str:
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

def extract_body(payload: dict) -> str:
    if payload.get("parts"):
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                return decode(part["body"]["data"])
            
        for part in payload["parts"]:
            text = extract_body(part)
            if text:
                return text
        return ""
    
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}.get("data")):
        return decode(payload["body"]["data"])
    
    return ""