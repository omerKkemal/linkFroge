# LinkFroge – because ngrok URLs are ugly and you know it

---

## Behold. The Link Manager.

You know what's annoying? Ngrok URLs. They're long, ugly, and change every time you restart.  
You know what's worse? Telling your clients "oh sorry, the URL changed again."  

LinkFroge fixes that. Permanent links. Dynamic updates. Less embarrassment.  
Built for developers who are tired of explaining why their API endpoint keeps changing.

---

## The Fine Print (Read It Or Don't, I'm Not Your Mom)

This is a **legitimate tool**. Not a C2. Not a RAT. Not a Trojan horse.  
It's for managing links. That's it.  
Don't use it for illegal stuff. I don't have time for that.

---

## What Is This Abomination?

LinkFroge is a link management system that gives permanent, stable URLs for dynamic services like ngrok tunnels, local development servers, and other temporary endpoints.  
The system creates persistent links that remain active even when the underlying service URL changes, with automatic CLI updates when links expire.

**Basically:** You get a pretty link. It points to your ugly ngrok URL. When ngrok changes, you update it. No one notices. Magic.

---

## The Repository (It's A Mess)

```
LinkFroge/
├── desktop_app/                # CLI agent (the brains)
│   ├── linkFroge.py            # The main event
|   └── phishing                # 
|       ├── templates/          #
|       └── phishing.py         #


│
├── webApp/                     # Flask web app (the face)
│   ├── app.py                  # Start here
│   ├── api/                    # The talking part
│   ├── database/               # Where data sleeps
│   ├── utility/                # The helpful bits
│   ├── view/                   # The actual bits
│   └── templates/              # HTML files (the pretty bits)
├── requirements.txt            # Things you need
├── .env.example                # Copy this, don't skip it
└── README.md                   # You're reading this
```

---

## Features That Actually Work

### Permanent Links (The Whole Point)
- Generate stable URLs that don't change
- Update destination URL without changing the link
- Perfect for ngrok, localhost, dev servers, anything dynamic

### Desktop CLI Agent (The Magic)
- Starts ngrok automatically (you're welcome)
- Detects URL changes and updates backend
- Sends heartbeats to keep links alive
- Auto-recovery when things break

### Web Dashboard (The Pretty Face)
- User-friendly link management
- Track all your permanent links
- View usage statistics
- Manage API tokens

### REST API (For The Nerds)
- Full CRUD operations
- Token authentication
- JSON responses
- Programmatic link management

### Email Notifications (Because You'll Forget)
- Professional HTML emails
- White and gold theme (fancy)
- Link expiry warnings
- Status change notifications

---

## The CLI Agent – How It Works

1. **Auto-Start ngrok**
   - Downloads ngrok automatically (no effort required)
   - Starts it on your specified port
   - Handles process lifecycle

2. **URL Detection**
   - Monitors ngrok API for URL changes
   - Detects when URL changes (ngrok restart)
   - Immediately sends updated URL to backend

3. **Heartbeat System**
   - Sends periodic updates to keep link active
   - Maintains link status in backend
   - Prevents link expiration due to inactivity

4. **Auto-Recovery**
   - Restarts ngrok if it crashes
   - Retries with exponential backoff
   - Updates backend with new URL on recovery

---

## Getting It Running (Without Crying)

### 1. Clone The Thing

```bash
git clone https://github.com/yourusername/linkfroge.git
cd linkfroge
```

### 2. Hide Your Dependencies

```bash
# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install The Noise

```bash
pip install -r requirements.txt
```

### 4. Configure Stuff

Create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
BASE_URL=http://localhost:5000
DATABASE_URL=sqlite:///linkfroge.db

# Email (if you want notifications)
SMTP_LINK=smtp.gmail.com
SMTP_PORT=587
EMAIL=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

DEFAULT_LINK_EXPIRY=30
AUTO_UPDATE_ON_EXPIRY=True
```

### 5. Create The Database

```bash
cd webApp
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. Run The Web App

```bash
python app.py
```

### 7. Run The CLI Agent (The Real Magic)

```bash
cd desktop_app
python linkFroge.py --port 5000 --backend https://yourdomain.com/api/service/update --service-id abc123 --token your_secure_token
```

---

## CLI Agent Commands (The Fun Part)

| Option | What It Does | Default |
|--------|--------------|---------|
| `--port` | Local port to expose | 5000 |
| `--backend` | Backend API URL | https://yourdomain.com/api/service/update |
| `--service-id` | Unique service identifier | abc123 |
| `--token` | Authentication token | your_secure_token |
| `--install-dir` | Ngrok install directory | ~/.linkforge |
| `--no-download` | Disable auto-download | False |
| `--verbose` | Enable verbose logging | False |

---

## Web Dashboard (The Pretty Parts)

Once logged in, you can:

- **Create permanent links** – Give your ugly URLs a pretty face
- **Manage your links** – View, edit, delete, cry
- **Update destination URL** – When ngrok changes, update it here
- **View statistics** – See how many times your links were clicked
- **API Token Management** – Generate, revoke, copy

---

## REST API (For The Nerds)

All endpoints require token authentication.

| Method | Endpoint | What It Does |
|--------|----------|--------------|
| GET | `/api/links` | Get all your links |
| POST | `/api/links` | Create a new link |
| PUT | `/api/links/{slug}` | Update destination URL |
| DELETE | `/api/links/{slug}` | Delete a link |
| GET | `/api/links/{slug}/status` | Check if it's alive |
| GET | `/api/links/{slug}/stats` | Get statistics |
| POST | `/api/service/update` | Update from CLI agent |

---

## Email Templates (Fancy)

The system sends emails for:

1. Welcome Email
2. Link Created
3. URL Updated
4. Service Status Change
5. Password Reset
6. Link Accessed
7. Link Expiring (7, 3, 1 day warnings)
8. Link Expired
9. Link Deleted
10. API Token Generated

White and gold theme. Because why not.

---

## Deployment (For The Brave)

### Linux/Mac (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "webApp.app:app"
```

### Windows (Waitress)

```bash
pip install waitress
waitress-serve --port=8000 "webApp.app:app"
```

### Docker (If You Hate Yourself)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=webApp/app.py
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
```

---

## Troubleshooting (When It Breaks)

**Database connection error:**
```bash
# Recreate database
python -c "from webApp.app import app, db; app.app_context().push(); db.create_all()"
```

**Email sending fails:**
- Check your SMTP credentials
- Make sure port 587 is open

**Link not redirecting:**
- Check if it's active
- Verify the destination URL is accessible
- Check if it expired

**Ngrok issues:**
- Check internet connection
- Try `--no-download` and install manually

---

## Author

**Omer Kemal** – developer, caffeine addict, link enthusiast.

---

<p align="center">
  <sub>Built with spite. Powered by sarcasm. Sustained by coffee.</sub>
  <br>
  <sub>No refunds. No regrets. No sleep.</sub>
  <br>
  <sub>Go outside. Touch grass. Or don't. I'm not your mom.</sub>
</p>