#!/bin/bash
# Deploy to Hugging Face Spaces
# Run from project root with HF_TOKEN already exported in your shell

set -e

# Load token from file if not already in environment
if [ -z "$HF_TOKEN" ] && [ -f /tmp/.hf_token ]; then
  HF_TOKEN=$(cat /tmp/.hf_token | tr -d '[:space:]')
fi

if [ -z "$HF_TOKEN" ]; then
  echo "ERROR: HF_TOKEN not set. Run: echo 'hf_yourtoken' > /tmp/.hf_token"
  exit 1
fi

SPACE="Mayaihcuilolliztli"
USER="wilbertsmdo"
REPO="https://user:${HF_TOKEN}@huggingface.co/spaces/${USER}/${SPACE}"

echo "=== Verifying HF token ==="
curl -sf https://huggingface.co/api/whoami \
  -H "Authorization: Bearer $HF_TOKEN" | python3 -c "import sys,json; print('Logged in as:', json.load(sys.stdin).get('name'))"

echo ""
echo "=== Creating Space: ${USER}/${SPACE} ==="
curl -sf -X POST https://huggingface.co/api/repos/create \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"type\":\"space\",\"name\":\"${SPACE}\",\"sdk\":\"gradio\",\"private\":false}" \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print('Space URL:', r.get('url', r))" || echo "(Space may already exist — continuing)"

echo ""
echo "=== Pushing to HF Space ==="
cd /storage/self/primary/PY_Projects/Macehualtlahtol/Mayaihcuilolliztli
git remote remove huggingface 2>/dev/null || true
git remote add huggingface "$REPO"
git push huggingface master:main --force

echo ""
echo "=== Done ==="
echo "Live at: https://huggingface.co/spaces/${USER}/${SPACE}"
