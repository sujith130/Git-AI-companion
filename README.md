# 🚀 Git-AI-Companion

[![Build Status](https://img.shields.io/github/actions/workflow/status/sujith130/Git-AI-companion/ci.yml?branch=main)](https://github.com/sujith130/Git-AI-companion/actions)  
![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)  
![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen)  
![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue?logo=python)  

---

## 🔍 Overview

**Git-AI-Companion** is an **AI-powered assistant** that streamlines Git workflows by providing:

- Smart commit message suggestions  
- Pull request review assistance  
- Code quality & optimization recommendations  
- Project-level insights based on your repository  

It is built with a Python backend, a simple frontend, and Docker support for easy deployment.

---

## 🧱 Architecture

Here’s a high-level view of how the system is structured:



---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Commit Suggestions** | Generate meaningful commit messages from code diffs. |
| **PR Review Help** | Auto-analyze pull requests, highlight issues, suggest improvements. |
| **Project Insights** | Identify code smells, improve structure, recommend refactoring. |
| **Chat Interface** | Ask questions, get guidance about your repo internals. |

---

## 🔧 Tech Stack

- **Backend**: Python (Flask/FastAPI)  
- **Frontend**: HTML, CSS, JS  
- **AI Integration**: OpenAI API or custom model  
- **Deployment**: Docker, docker-compose  
- **CI/CD**: GitHub Actions  

---

## ⚙️ Setup & Installation

### 🔹 Prerequisites
- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/)  
- (Optional) API key for the AI model  

### 🔹 Run with Docker

```bash
git clone https://github.com/sujith130/Git-AI-companion.git
cd Git-AI-companion
docker-compose up --build


# Backend setup
cd backend
pip install -r requirements.txt
python app.py

# Frontend (open index.html in your browser)

### 🚀 Usage
- 🌐 Open the **frontend** in your browser  
- 💬 Start chatting with the **AI companion** about your project  
- 📝 Use it to **review PRs**, **suggest commits**, or **optimize code**  

---

### 📌 Roadmap
- 🔒 [ ] Add authentication & user sessions  
- 🤖 [ ] Better project-wide context for AI suggestions  
- 🔗 [ ] GitHub / GitLab API integration  
- ✅ [ ] Automated tests & coverage reports  
- ☁️ [ ] Deployment to cloud platforms (Heroku, DigitalOcean, Vercel)  

---

###🤝 Contributing
Contributions are welcome!  

1. 🍴 Fork this repo  
2. 🌱 Create a feature branch (`git checkout -b feature-name`)  
3. 💾 Commit changes (`git commit -m "Add feature"`)  
4. 📤 Push branch (`git push origin feature-name`)  
5. 🔀 Open a Pull Request  

