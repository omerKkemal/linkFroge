# FrogLink

<p align="center">
  <img src="screen_shot/logo.jpg" alt="FrogLink Logo" width="200">
</p>

---

## Because ngrok URLs are ugly and you know it.

FrogLink is a link management system that gives permanent, stable URLs for dynamic services like ngrok tunnels, local development servers, and other temporary endpoints.

**Basically:** You get a pretty link. It points to your ugly ngrok URL. When ngrok changes, you update it. No one notices. Magic. You're welcome.

---

## Showcase

<div align="center">

### Home Page
<img src="screen_shot/home.png" alt="Home Page" width="700">

*"Wow, this looks professional!"* – Someone who hasn't seen the code yet

<br><br>

### Dashboard
<img src="screen_shot/dashboard.jpg" alt="Dashboard" width="700">

*Numbers! Graphs! Stuff! You're basically a data analyst now.*

<br><br>

### Link Management
<img src="screen_shot/link_management.jpg" alt="Link Management" width="700">

*Create. Edit. Delete. Cry. The cycle of life.*

<br><br>

### Loading Animation
<img src="screen_shot/loading.png" alt="Loading Animation" width="700">

*Because waiting is fun. Especially with frogs.*

</div>

---

## The Fine Print (Read It Or Don't, I'm Not Your Mom)

This is a **legitimate tool**. Not a C2. Not a RAT. Not a Trojan horse. I swear. Mostly.

It's for managing links. That's it. Don't use it for illegal stuff. I don't have time for that. I have coffee to drink and code to break.

---

## What It Does (When It's Not Crashing)

- **Permanent Links** – Generate stable URLs that don't change. Revolutionary, I know.
- **CLI Agent** – Auto-starts ngrok, detects URL changes, sends heartbeats. Like a digital heartbeat. Creepy.
- **Web Dashboard** – User-friendly link management with statistics. Because numbers make you feel important.
- **REST API** – Full CRUD operations with token authentication. For the nerds.

---

## How It Works (Try To Keep Up)

1. CLI agent starts ngrok and monitors URL
2. URL changes detected -> backend updated automatically
3. Your permanent link always points to the right place
4. Users never see the ugly URL

**It's like magic. But with more code. And less rabbits.**

---

## Quick Start (Without Breaking Things)

```bash
git clone https://github.com/yourusername/linkfroge.git
cd linkfroge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
BASE_URL=http://localhost:5000
DATABASE_URL=sqlite:///linkfroge.db
```

Run the web app:

```bash
cd webApp
python app.py
```

Run the CLI agent:

```bash
cd desktop_app
python linkFroge.py --port 5000 --backend https://yourdomain.com/api/service/update --service-id YOUR_ID --token YOUR_TOKEN
```

---

## CLI Options (For The Brave)

| Option | What It Does | Default |
|--------|--------------|---------|
| `--port` | Local port to expose | 5000 |
| `--backend` | Backend API URL | https://yourdomain.com/api/service/update |
| `--service-id` | Unique service identifier | abc123 |
| `--token` | Authentication token | your_secure_token |
| `--verbose` | Enable verbose logging | False |

**Pro tip:** Don't lose your token. I'm not making you another one.

---

## Tech Stack (The Things That Make It Work)

- **Backend:** Flask, SQLAlchemy – because reinventing the wheel is for amateurs
- **Frontend:** TailwindCSS, Font Awesome – because looking good matters
- **Database:** SQLite (configurable) – where data goes to sleep
- **CLI:** Python, ngrok – the magic behind the curtain

---

## Project Structure (The Mess)

```
LinkFroge/
├── desktop_app/                # CLI agent
│   ├── linkFroge.py            # The main event
│   └── phishing/               # (Don't ask. Seriously.)
│
├── webApp/                     # Flask web app
│   ├── app.py                  # Start here
│   ├── api/                    # REST API (the talking part)
│   ├── database/               # Models & DB (where data sleeps)
│   ├── utility/                # Helpers (the helpful bits)
│   ├── view/                   # Routes (the actual bits)
│   └── templates/              # HTML files (the pretty bits)
├── screenshots/                # Screenshots (you're looking at them)
├── requirements.txt            # Things you need
├── .env.example                # Copy this. Don't skip it.
└── README.md                   # You're reading this
```

---

## The Legal Bit

It's mine. Don't steal it. Don't misuse it. Be a decent human.

---

<p align="center">
  <sub>Built with spite. Powered by sarcasm. Sustained by coffee.</sub>
  <br>
  <sub>No refunds. No regrets. No sleep.</sub>
  <br>
  <sub>Go outside. Touch grass. Or don't. I'm not your mom.</sub>
</p>

