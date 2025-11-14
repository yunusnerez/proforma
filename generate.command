#!/bin/bash
cd "$(dirname "$0")"
source ~/myenv/bin/activate
python3 tp.py
read -n 1 -s -r -p "Press any key to close"
