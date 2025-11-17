#!/bin/bash
cd "$(dirname "$0")"
python3 generate_invoice_notes_enabled.py
read -n 1 -s -r -p "Press any key to close"
