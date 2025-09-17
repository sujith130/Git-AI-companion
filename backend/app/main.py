from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os, httpx, json, hmac, hashlib
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env if present
app = FastAPI(title="AI Dev Companion")

# Mount static frontend
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# CORS (allow local dev origins; tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ui")
def ui_index():
    return FileResponse("frontend/static/index.html")

@app.get("/")
def root():
    return FileResponse("frontend/static/index.html")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not set. Chat and review will fail without it.")

# Simple Chat endpoint
@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "").strip()
    mode = body.get("mode", "general")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    system_msg = "You are an expert software engineer and project contributor. Provide concise, actionable suggestions focused on code quality, performance, architecture, and developer experience."
    if mode == "optimize":
        system_msg = "You are a senior performance engineer. Give pragmatic optimization advice, trade-offs, and code-level suggestions."
    elif mode == "review":
        system_msg = "You are a helpful code reviewer. Focus on bugs, security issues, style, and improvements."

    # Call OpenAI Chat Completions
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 600,
        "temperature": 0.4
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            msg = ""
            if "choices" in data and len(data["choices"])>0:
                msg = data["choices"][0].get("message", {}).get("content", "") or data["choices"][0].get("text","")
            else:
                msg = data.get("text", "")
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else 502
            try:
                err_json = e.response.json()
                detail = err_json.get("error") or err_json
            except Exception:
                detail = e.response.text if e.response is not None else str(e)
            raise HTTPException(status_code=status, detail=f"OpenAI error ({status}): {detail}")
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"OpenAI request failed: {e}")

    return {"response": msg}

# PR review webhook endpoint
@app.post("/pr-review/webhook")
async def pr_webhook(request: Request):
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=500, detail="GITHUB_TOKEN not configured in environment")

    # Verify GitHub webhook signature if secret is configured
    if GITHUB_WEBHOOK_SECRET:
        signature = request.headers.get("X-Hub-Signature-256", "")
        body_bytes = await request.body()
        mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=body_bytes, digestmod=hashlib.sha256)
        expected = "sha256=" + mac.hexdigest()
        if not hmac.compare_digest(expected, signature or ""):
            raise HTTPException(status_code=401, detail="Invalid signature")
        try:
            payload = json.loads(body_bytes)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
    else:
        payload = await request.json()
    pr = payload.get("pull_request") or payload.get("pullRequest") or {}
    pr_url = pr.get("url") or pr.get("html_url")
    comments_url = pr.get("comments_url") or (pr.get("issue_url") + "/comments" if pr.get("issue_url") else None)
    files_url = pr.get("url") + "/files" if pr.get("url") else None
    if not pr_url or not files_url:
        raise HTTPException(status_code=400, detail="No pull_request object in payload")

    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            r = await client.get(files_url, headers=headers)
            r.raise_for_status()
            files = r.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch PR files: {e}")

        diffs = []
        for f in files:
            patch = f.get("patch")
            filename = f.get("filename")
            if patch:
                diffs.append(f"//// FILE: {filename} ////\n{patch}\n")

        if not diffs:
            review_text = "No text diffs found in the PR to review."
        else:
            full_diff = "\n".join(diffs)[:15000]
            system_msg = "You are an expert code reviewer. Provide a concise review pointing out bugs, style issues, security concerns, and suggestions."
            prompt = f"Review the following pull request diff and provide review comments. Be concise and actionable:\n\n{full_diff}"

            openai_payload = {
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 800,
                "temperature": 0.2
            }
            try:
                r2 = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                    json=openai_payload,
                )
                r2.raise_for_status()
                review_resp = r2.json()
                review_text = ""
                if "choices" in review_resp and len(review_resp["choices"])>0:
                    review_text = review_resp["choices"][0].get("message", {}).get("content", "") or review_resp["choices"][0].get("text","")
                else:
                    review_text = "AI returned no review content."
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"OpenAI review failed: {e}")

        if not comments_url:
            repo = payload.get("repository", {})
            owner = repo.get("owner", {}).get("login") or repo.get("owner")
            repo_name = repo.get("name")
            issue_number = pr.get("number")
            if owner and repo_name and issue_number:
                comments_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}/comments"

        if not comments_url:
            return {"status": "review_generated", "review": review_text}

        try:
            post = await client.post(comments_url, headers=headers, json={"body": review_text})
            post.raise_for_status()
        except Exception as e:
            return {"status": "review_generated_but_post_failed", "error": str(e), "review": review_text}

    return {"status": "review_posted", "review": review_text}
