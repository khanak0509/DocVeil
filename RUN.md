# 🚀 How to Run DocVeil

## Pre-requisites

✅ Python virtual environment activated
✅ Ollama running with llama3.1:8b model

---

## Step 1: Start Backend API

**Terminal 1:**

```bash
cd backend
python api.py
```

**Expected output:**

```
🚀 Starting DocVeil API Server...
📡 Server will be available at: http://localhost:8000
📖 API docs: http://localhost:8000/docs
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Keep this terminal open - the backend must stay running!

---

## Step 2: Start Flutter App

**Terminal 2 (new terminal):**

```bash
cd frontend
flutter run -d chrome
```

**Or for macOS:**

```bash
cd frontend
flutter run -d macos
```

**Expected output:**

```
Launching lib/main.dart on Chrome in debug mode...
Building application for the web...
Application now running in browser
```

---

## Step 3: Use the App

1. **Upload Screen** will open automatically
2. Click **"Select PDF File"**
3. Choose a PDF from your computer
4. Click **"Start Processing"**
5. Watch summaries appear one by one with animations! ✨

---

## Troubleshooting

### Backend won't start?

```bash
# Check if port 8000 is already in use
lsof -ti:8000 | xargs kill -9

# Try starting again
python api.py
```

### Flutter errors?

```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter run -d chrome
```

### Can't connect to backend from Flutter?

- Make sure backend is running (should show "Uvicorn running on...")
- Check `lib/services/api_service.dart` line 8: baseUrl should be `http://localhost:8000`

---

## Quick Test Commands

**Test backend is running:**

```bash
curl http://localhost:8000/
```

**Expected:** `{"status":"ok","service":"DocVeil API","version":"1.0.0"}`

---

## Stop the Application

**Terminal 1 (Backend):**

- Press `Ctrl+C`

**Terminal 2 (Flutter):**

- Press `q` in terminal or close browser window
