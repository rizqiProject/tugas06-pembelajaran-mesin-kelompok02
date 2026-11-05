#!/bin/zsh
# Ekspor laporan Word ke PDF memakai Microsoft Word (macOS).
# Jalankan dari folder mana pun: ./ekspor_pdf.sh
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
DOCX="$DIR/TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.docx"
PDF="$DIR/TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.pdf"

if [[ ! -f "$DOCX" ]]; then
  echo "DOCX tidak ditemukan: $DOCX" >&2
  exit 1
fi

osascript <<APPLESCRIPT
tell application "Microsoft Word"
  activate
  open POSIX file "$DOCX"
  set theDoc to active document
  save as theDoc file name "$PDF" file format format PDF
  close theDoc saving no
end tell
APPLESCRIPT

echo "PDF: $PDF"
