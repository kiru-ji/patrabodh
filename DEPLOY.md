# DigitalOcean Deployment Guide

## Option 1: GPU Droplet (Full Offline Demo)

Best for demonstrating self-hosted open-weight model at the hackathon.

### Prerequisites
- DigitalOcean account with credits
- doctl CLI installed and authenticated

### Steps

```bash
# 1. Create GPU Droplet
doctl compute droplet create patrabodh-demo \
  --region blr1 \
  --size gpu-h100x1-80gb \
  --image ubuntu-24-04-x64 \
  --ssh-keys YOUR_SSH_KEY_ID

# 2. SSH into the droplet
ssh root@<DROPLET_IP>

# 3. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 4. Pull Gemma 4 model
ollama pull gemma4:12b

# 5. Clone and run PatraBodh
git clone <your-repo-url>
cd patrabodh
pip install -r requirements.txt
export INFERENCE_MODE=ollama
python app.py
```

### Cost Estimate
- GPU Droplet (H100): ~$3.39/hr
- 4-hour hackathon demo: ~$13.56
- Well within $200 MLH credit

## Option 2: App Platform (Cloud API Mode)

Simpler deployment using Gemini API free tier.

```bash
# Deploy via doctl
doctl apps create --spec app.yaml
```

Create `app.yaml`:
```yaml
name: patrabodh
services:
  - name: web
    source_dir: /
    github:
      repo: your-username/patrabodh
      branch: main
    run_command: python app.py
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xs
    envs:
      - key: GEMINI_API_KEY
        value: ${GEMINI_API_KEY}
      - key: INFERENCE_MODE
        value: gemini
```

## Option 3: Docker Compose (One-Click)

```bash
# On any DO Droplet with Docker
docker compose up -d
# Wait for Ollama to pull the model (~5 min)
# Access at http://<DROPLET_IP>:8000
```

## Post-Hackathon Cleanup

```bash
# Delete droplet to stop charges
doctl compute droplet delete patrabodh-demo --force

# Or delete app
doctl apps delete <APP_ID> --force
```
