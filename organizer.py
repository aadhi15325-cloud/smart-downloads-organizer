import os, shutil, time
from urllib.parse import urlparse

folders = [r"C:\Users\acer\Downloads"]

types = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".webm", ".3gp"],
    "PDFs": [".pdf"],
    "APK": [".apk"],
    "Excel": [".xls", ".xlsx", ".xlsm", ".csv"],
    "Documents": [".doc", ".docx", ".ppt", ".pptx", ".txt"],
    "Audio": [".mp3", ".wav", ".m4a", ".opus"],
    "Zips": [".zip", ".rar", ".7z"],
    "Programs": [".exe", ".msi"],
}
reserved = set(types.keys()) | {"Movies", "Screenshots", "Others", "Folders"}
skip = [".crdownload", ".tmp", ".part"]

sites = {
    "chatgpt": "ChatGPT", "openai": "ChatGPT",
    "gemini": "Gemini", "google": "Google",
    "whatsapp": "WhatsApp", "youtube": "YouTube",
    "instagram": "Instagram", "telegram": "Telegram",
    "canva": "Canva", "pinterest": "Pinterest",
    "linkedin": "LinkedIn", "github": "GitHub",
}

def clean(text):
    for c in '<>:"/\\|?*':
        text = text.replace(c, "")
    return text.strip() or "Unknown Source"

def is_screenshot(name):
    n = name.lower()
    return "screenshot" in n or "screen shot" in n or "snip" in n

def source_from_name(name):
    n = name.lower()
    if "whatsapp" in n: return "WhatsApp"
    if "gemini" in n: return "Gemini"
    if "chatgpt" in n: return "ChatGPT"
    return None

def source_from_web(path):
    try:
        with open(path + ":Zone.Identifier", encoding="utf-8", errors="ignore") as f:
            data = f.read()
    except Exception:
        return None
    for key in ("ReferrerUrl=", "HostUrl="):
        for line in data.splitlines():
            if line.startswith(key):
                host = urlparse(line[len(key):]).netloc.lower().replace("www.", "")
                if not host:
                    continue
                for word, label in sites.items():
                    if word in host:
                        return label
                return host
    return None

def get_source(path, name):
    return source_from_name(name) or source_from_web(path) or "Unknown Source"

def is_movie(path, name):
    n = name.lower()
    words = ["1080p", "720p", "480p", "bluray", "brrip", "webrip", "web-dl",
             "hdrip", "dvdrip", "x264", "x265", "hevc", "movie"]
    big = os.path.getsize(path) > 700 * 1024 * 1024
    return big or any(w in n for w in words)

def unique(dest):
    base, ext = os.path.splitext(dest)
    i = 1
    while os.path.exists(dest):
        dest = f"{base}_{i}{ext}"
        i += 1
    return dest

def move(path, target):
    os.makedirs(target, exist_ok=True)
    try:
        shutil.move(path, unique(os.path.join(target, os.path.basename(path))))
    except Exception:
        pass

def organize(folder):
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if time.time() - os.path.getmtime(path) < 5:
            continue

        if os.path.isdir(path):
            if file not in reserved:
                move(path, os.path.join(folder, "Folders"))
            continue

        ext = os.path.splitext(file)[1].lower()
        if ext in skip:
            continue

        category = "Others"
        for name, exts in types.items():
            if ext in exts:
                category = name
                break

        if category == "Images" and is_screenshot(file):
            move(path, os.path.join(folder, "Screenshots"))
            continue

        if category == "Videos" and is_movie(path, file):
            category = "Movies"

        source = clean(get_source(path, file))
        move(path, os.path.join(folder, category, source))

while True:
    for f in folders:
        organize(f)
    time.sleep(10)