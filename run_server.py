import uvicorn
import os
import sys

# Ensure backend directory is in python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("==================================================================")
    print("  SoyaSetu: Strategic Soybean Procurement Decision Support System")
    print("  Target Organization: ABT Consumer Products Division (ABT-CPD)")
    print("==================================================================")
    print("Starting enterprise server on http://localhost:8000...")
    print("API Documentation available at: http://localhost:8000/docs")
    
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
