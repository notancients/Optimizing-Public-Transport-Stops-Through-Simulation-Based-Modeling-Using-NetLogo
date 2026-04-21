

if [ ! -d "venv" ]; then
  echo "Installing venv"
  python3 -m venv venv
  pip install pynetlogo
fi

source ./venv/bin/activate