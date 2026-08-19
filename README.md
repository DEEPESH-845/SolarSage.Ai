# 🌞 SolarSage – AI Agents for Solar Panel Cleaning Optimization

**SolarSage** is a cutting-edge AI system designed to optimize solar panel cleaning operations by combining advanced computer vision, economic intelligence, and autonomous control. Developed for the **Qualcomm Edge AI Developer Hackathon 2025**, it leverages NPU-accelerated Edge AI to make real-time, cost-effective decisions for maintaining solar efficiency.


![Pros/cons](assets/1.png)
---
## ✨ Key Features

- 🧠 **Advanced Computer Vision** – Multi-spectral dust detection using 6 deep analysis algorithms  
- 🤖 **CrewAI Multi-Agent System** – Collaboration between specialized AI agents for smart decisions  
- ⚡ **NPU Acceleration** – Ultra-fast edge AI processing on Qualcomm hardware  
- 📊 **Economic Intelligence** – ROI analysis and cost-benefit decision modeling  
- 🔄 **Automated Execution** – Smart control and real-time cleaning operation management  
- 📈 **Real-Time Analytics** – Live monitoring, forecasting, and reporting  
- 🌍 **Location-Aware Intelligence** – Adapts to varying solar conditions by geography  


![SolarSage Features](assets/2.png)

---

## 🧪 Production Pipeline demo

🔍 Stage 1: AI Image Analysis
✅ Image analysis completed: HIGH risk detected

🔮 Stage 2: Solar Forecasting
✅ Forecast completed: 4.7 kWh daily loss predicted

🧠 Stage 3: Intelligent Decision Making
✅ Decision completed: EXECUTE_IMMEDIATE with 87.3% confidence

🚿 Stage 4: Automated Execution
✅ Execution completed: EXECUTED status

✅ PIPELINE EXECUTION COMPLETED!

📊 KEY RESULTS:
🔍- Dust Level: 72.3% (HIGH)
⚡- Power Loss: 4.7 kWh/day (18.3%)
🧠- Decision: EXECUTE_IMMEDIATE (87.3% confidence)
🚿 -Execution: EXECUTED
💰- Cost: $24.50
💎- Recovery: 4.2 kWh
📈- ROI: 127.3%

⚡ PERFORMANCE: 2,671 images/hour capacity
🎉 Production pipeline demo completed successfully!

![Pipeline](assets/3.png)
---

## 🛠️ System Architecture

1. **🔍 Image Analysis Engine**


2. **🔮 Solar Forecasting System**


3. **🧠 Intelligent Decision Engine**

4. **🚿 Automated Execution Controller**


![Architecture](assets/4.png)
---

## 🤖 CrewAI Agentic System

SolarSage employs 4 specialized AI agents that collaborate to optimize solar panel maintenance:

1. **Senior Solar Panel Image Analyst**

-->**Role:** Computer vision and NPU-accelerated image analysis

-->**Expertise:** Multi-spectral dust detection, condition assessment

-->**Output:** Comprehensive dust level analysis with confidence scores

---


2. **Llama-Enhanced Solar Forecast Specialist**

-->**Role:** Solar power forecasting and economic modeling

-->**Expertise:** Weather integration, power loss prediction, economic optimization

-->**Output:** 48-hour forecasts with economic impact analysis

---



3. **AI-Powered Decision Optimization Expert**

-->**Role:** Multi-criteria decision making using machine learning

-->**Expertise:** Cost-benefit analysis, risk assessment, ROI optimization

-->**Output:** Intelligent cleaning recommendations with detailed reasoning


---

4. **Automated Execution & Control Manager**

-->**Role:** Real-time operation control and quality monitoring

-->**Expertise:** Robotics integration, process optimization, performance tracking

-->**Output:** Execution reports with comprehensive automation insights


![Agentic Workflow](assets/5.png)
---

## 📊 Performance Metrics

- ⚙️ Processing Speed: 2,671+ images/hour

- 🎯 Detection Accuracy: 89.2% confidence

- ⚡ Pipeline Latency: <1.5 seconds

- 🔁 Industrial Throughput: Suitable for large solar farms

- 🌎 Geographic Flexibility: Works across diverse climate zones

- 📈 ROI Optimized: Up to 127% ROI per operation

![Metrics](assets/6.png)
---
---

## 🗂️ Project Structure

```
├── app.py                     # WSGI entrypoint (Vercel + `python app.py`)
├── run_system.py              # Local launcher: FastAPI backend + Flask frontend
├── requirements.txt           # Runtime dependencies
├── vercel.json                # Serverless function config
├── Backend/
│   ├── services.py            # Business logic — the single source of truth
│   ├── agents/
│   │   └── image_classifier.py    # Adapter onto the CV pipeline in Agents/crew.py
│   ├── api/main.py            # FastAPI: thin HTTP layer over services
│   ├── config/settings.py     # Deployment config (paths, ports, tank capacity)
│   └── database/              # SQLAlchemy models + session handling
├── Frontend/
│   ├── app.py                 # Flask UI, calls services in-process
│   └── templates/             # Dashboard, panels, reports, settings
├── Agents/crew.py             # CV → forecast → decision → execution pipeline
├── Hardware/                  # ESP32 firmware, MQTT tooling, captured telemetry
└── tests/test_system.py       # End-to-end checks against a temp database
```

**How the pieces connect.** `Backend/services.py` holds every operation; both the
FastAPI backend and the Flask frontend are thin layers over it. The frontend
therefore needs no running backend — it calls the same functions in-process,
which is what lets the whole app deploy as a single serverless function. The
FastAPI service remains available for hardware and external API clients.

Analysis flows: `Frontend` → `services.analyze_panel` →
`Backend/agents/image_classifier` → `Agents/crew.py`
(computer vision → 48h forecast → economic decision) → SQLite.

---

## 🚀 Quick Start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python run_system.py           # backend :8000 + frontend :5000
```

| Service | URL |
|---|---|
| Dashboard | http://localhost:5000 |
| REST API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

Run either half on its own:

```bash
python app.py                                        # frontend only
python -m uvicorn Backend.api.main:app --reload      # backend only
```

> **macOS:** AirPlay Receiver occupies port 5000. Either disable it under
> System Settings → General → AirDrop & Handoff, or run
> `FRONTEND_PORT=5001 python run_system.py`.

---

## ⚙️ Configuration

Deployment settings come from the environment (or a `.env` file); operational
settings are edited on the Settings page and stored in the database.

| Variable | Default | Purpose |
|---|---|---|
| `DATA_DIR` | `Backend/data` (`/tmp/solarsage` on serverless) | Writable storage for the database and decision files |
| `SQLITE_DATABASE_PATH` | `<DATA_DIR>/solar_panel_system.db` | Explicit database path |
| `FRONTEND_PORT` / `API_PORT` | `5000` / `8000` | Server ports |
| `BACKEND_URL` | unset | Set it to call a remote FastAPI backend over HTTP instead of in-process |
| `SECRET_KEY` | dev fallback | Flask session signing — set this in production |
| `CORS_ORIGINS` | `http://localhost:5000` | Comma-separated origins allowed to call the API |
| `WATER_TANK_CAPACITY_ML` | `5000` | Tank size used for water-level reporting |

Runtime settings (dust thresholds, spray duration, water pressure, auto-clean,
notifications, schedule, paused/active mode) live in the `system_settings`
table and are editable from the UI.

---

## 🧪 Testing

```bash
pip install -r requirements-dev.txt
python tests/test_system.py
```

Covers the CV pipeline against the bundled image fixtures, threshold-driven
decisions, auto-clean gating, water-tank and pause guards, hardware telemetry
parsing, and every FastAPI and Flask route. It runs against a temporary
database and never touches the real one.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Water level, camera status, temperature from telemetry |
| `GET` | `/panels` | All panels with status, dust level and last cleaning |
| `GET` | `/panels/{id}/history` | Analysis and cleaning history |
| `POST` | `/analyze` | Run the CV + forecast + decision pipeline for a panel |
| `POST` | `/spray` | Execute a cleaning cycle |
| `GET` | `/latest-decision` | Most recent decision with its economic analysis |
| `GET` | `/system/stats` | Totals, average dust level, water usage, uptime |
| `GET` | `/system/logs` | Recent system log entries |
| `GET`/`PUT` | `/settings` | Read or update runtime settings |
| `POST` | `/settings/reset` | Restore default settings |
| `POST` | `/system/refill-tank` | Reset the water-tank counter |
| `GET` | `/hardware/telemetry` | Latest ESP32 capture from `Hardware/` |

---

## ☁️ Deployment (Vercel)

Live: **https://solarsage-ai.vercel.app**

```bash
npm i -g vercel
vercel link
vercel env add SECRET_KEY production     # generate with: python -c "import secrets;print(secrets.token_hex(32))"
vercel --prod
```

Vercel serves `app.py` as a single Python function. `DATA_DIR` defaults to
`/tmp/solarsage` automatically when the `VERCEL` environment variable is
present, because serverless filesystems are read-only apart from `/tmp`.

**Storage caveat:** `/tmp` is per-instance and cleared when an instance
recycles, so the deployed database is ephemeral — fine for a demo, but point
`SQLITE_DATABASE_PATH` at persistent storage (or move to Postgres) for real
deployments. Panel images and hardware captures ship with the bundle and are
read-only, so they always work.


## 📎 License
This project was developed for the Qualcomm Edge AI Developer Hackathon 2025. For academic or non-commercial use only. Contact maintainers for other licensing.

## 🤝 Contributing
Contributions, feature suggestions, and pull requests are welcome.
Please open an issue before submitting large changes.

## 👨‍💻 Developed By
SolarSage Team – Finalists of Qualcomm Edge AI Developer Hackathon 2025 🌞
