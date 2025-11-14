#!/bin/bash
cd "$(dirname "$0")"
source ~/myenv/bin/activate
python3 proforma_with_deposit.py
read -n 1 -s -r -p "Press any key to close"
