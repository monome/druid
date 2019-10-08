set -ex
python -m venv .
pip install -r requirements.txt
set +x
echo "ready. run:"
echo "  source Scripts/activate"
echo "in this folder before running druid when you've opened a new shell"
