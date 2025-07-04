from gemini import create_gemini
import sys

if __name__ == "__main__":
    proxy = None
    if len(sys.argv) > 1:
        proxy = "proxy"
    create_gemini(proxy)
