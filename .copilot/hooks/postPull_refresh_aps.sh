#!/bin/bash
echo "[Copilot Hook] Refrescando APS YAML tras pull..."
python3 scripts/md2aps_v35.py --md-dir OLD/nuevo/swarm_nuevo_v3.5 --out-dir swarm/aps
python3 scripts/validate_aps_v35.py --dir swarm/aps || echo "[WARN] Validación APS fallida"