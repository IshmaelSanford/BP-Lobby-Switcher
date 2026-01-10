import sys
try:
    import pytesseract
    print("Import successful")
    print(f"File: {pytesseract.__file__}")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Other error: {e}")
