# Proposal UTS Pembelajaran Mesin — Kelompok 02

**Judul:** Prediksi Keterlambatan Penyelesaian Akta pada Kantor Notaris & PPAT
Aries Buwana Menggunakan Decision Tree Terpruning dengan Optimasi Optuna dan
Kalibrasi Ambang Batas

**Mata kuliah:** Pembelajaran Mesin (KG.043.10.A) — Semester Gasal 2026/2027
**Anggota:** Muhammad Rizqi Saputra (12250158), Dian Nur Cahya (12250162),
Dicky Handia (12250161)

## Berkas hasil

| Berkas | Keterangan |
|---|---|
| `PROPOSAL_UTS_ML_KELOMPOK_02_NOTARIS_PPAT.docx` | Naskah Word, 34 halaman |
| `PROPOSAL_UTS_ML_KELOMPOK_02_NOTARIS_PPAT.pdf` | PDF final, 34 halaman |
| `buat_proposal.py` | Penyusun naskah dari template |
| `analisis_proposal.py` | Benchmark baseline, EDA, sensitivitas ambang |
| `perbarui_halaman.py` | Penyelaras nomor halaman daftar isi |
| `ekspor_pdf.sh` | Ekspor Word ke PDF via Microsoft Word |
| `template_proposal_uts.docx` | Salinan template resmi |
| `hasil/analisis_proposal.json` | Angka mentah benchmark dan ambang |
| `gambar/` | Gambar 3.1 dan 3.2 yang dihasilkan skrip |

## Cara membangun ulang

```bash
cd /Users/admin/PEMBELAJARAN_MESIN_KELOMPOK_02/proposal_uts

# 1. Hitung ulang angka pendukung (opsional, hasil sudah tersimpan)
../.venv/bin/python analisis_proposal.py

# 2. Susun DOCX dan ekspor PDF
../.venv/bin/python buat_proposal.py
./ekspor_pdf.sh

# 3. Selaraskan nomor halaman daftar isi
../.venv/bin/python perbarui_halaman.py
../.venv/bin/python buat_proposal.py
./ekspor_pdf.sh
```

Catatan: `buat_proposal.py` membaca `halaman.json` bila tersedia. Setelah dua
kali jalan, nomor halaman daftar isi stabil.

## Angka kunci

| Komponen | Nilai |
|---|---|
| Dataset | 169 berkas; 33 terlambat (19,5%) |
| Split | 135 latih (26 positif) / 34 uji (7 positif), seed 42 |
| Model terbaik | Decision Tree, trial Optuna #13 |
| Hiperparameter | gini; depth 6; leaf 3; split 16; ccp_alpha 0,003536; log2 |
| CV Macro F1 | 0,4467 → 0,5532 (+23,8% relatif) |
| CV ROC-AUC | 0,5240 → 0,5535 |
| Ambang terpilih | 0,05 (F2 maksimum OOF) |
| Ambang guardrail | 0,19 (alarm ≤ 50%) |
| Uji @0,05 | TP 5, FN 2, FP 19, TN 8 |
| Precision / Recall / F1 | 0,208 / 0,714 / 0,323 |
| F2 / Macro F1 | 0,481 / 0,378 |
| ROC-AUC / PR-AUC | 0,413 / 0,190 |

## Struktur naskah

- **Bab I** — latar belakang, enam identifikasi masalah, tiga research
  questions, tujuan, manfaat, ruang lingkup dan batasan.
- **Bab II** — Tabel 2.1 berisi lima jurnal terverifikasi (Lessmann et al.,
  Saito & Rehmsmeier, He & Garcia, Lipton et al., Akiba et al.), teori model,
  pra-pemrosesan, metrik, dan Optuna TPE.
- **Bab III** — CRISP-DM, dataset, EDA, pipeline bebas kebocoran, skema
  validasi, baseline vs ensemble, Optuna, kalibrasi ambang, cetak biru
  deployment.
- **Lampiran** — repositori GitHub, notebook Colab, model, log Optuna, dan
  pernyataan integritas data.

## Batasan

Data uji 34 berkas sudah pernah dipakai pada Tugas 04–05 sehingga bukan
holdout yang sepenuhnya buta. Dataset berasal dari satu kantor dan berukuran
kecil. Model diposisikan sebagai alat bantu penyaringan, bukan pengganti
keputusan staf, Notaris, atau PPAT.
