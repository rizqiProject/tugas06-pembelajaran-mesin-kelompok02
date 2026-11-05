# Tugas 06 Pembelajaran Mesin — Kelompok 02

**Objek penelitian:** Kantor Notaris & PPAT Aries Buwana, Jakarta Barat
**Mata kuliah:** Pembelajaran Mesin (KG.043.10.A) — Semester Gasal 2026/2027
**Anggota:** Muhammad Rizqi Saputra (12250158), Dian Nur Cahya (12250162), Dicky Handia (12250161)

Laporan lengkap tersedia dalam dua format dengan isi yang sama:

- `TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.docx`
- `TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.pdf`

## 1. Ringkasan hasil

| Komponen | Hasil |
|---|---|
| Dataset | `berkas_notaris_terisi (2).csv`, 169 berkas, 33 terlambat (19,5%) |
| Pembagian data | 135 train (26 positif) dan 34 test (7 positif), stratified 80:20, `random_state=42` |
| Model baseline | `DecisionTreeClassifier(max_depth=4, min_samples_leaf=15, min_samples_split=2, ccp_alpha=0)` |
| Model Tugas 06 | `gini`, `max_depth=6`, `min_samples_leaf=3`, `min_samples_split=16`, `ccp_alpha=0,0035355`, `class_weight=None`, `max_features=log2` |
| Optuna | 30 trial TPE, Stratified 5-Fold CV, objective Macro F1; trial terbaik #13, CV Macro F1 **0,5532** |
| Threshold terpilih | **0,05** (F2 maksimum pada prediksi OOF train) |
| Evaluasi test @0,05 | TP 5, FN 2, FP 19, TN 8; precision 0,208; recall 0,714; F1 0,323; F2 0,481 |
| Metrik tambahan @0,05 | accuracy 0,382; macro F1 0,378; weighted F1 0,410; ROC-AUC 0,413; PR-AUC 0,190; log-loss 1,155 |
| Beban alarm @0,05 | 24 dari 34 berkas (70,6%) |

### Perbandingan ambang pada data uji

| Ambang | Keterangan | TP | FN | FP | TN | Precision | Recall | F1 | F2 | Alarm |
|---|---|---|---|---|---|---|---|---|---|---|
| 0,50 | default | 0 | 7 | 3 | 24 | 0,000 | 0,000 | 0,000 | 0,000 | 3 |
| 0,25 | F1 OOF | 2 | 5 | 12 | 15 | 0,143 | 0,286 | 0,190 | 0,238 | 14 |
| 0,19 | operasional, alarm OOF ≤50% | 4 | 3 | 19 | 8 | 0,174 | 0,571 | 0,267 | 0,392 | 23 |
| 0,05 | F2 OOF (terpilih) | 5 | 2 | 19 | 8 | 0,208 | 0,714 | 0,323 | 0,481 | 24 |

Ambang **0,05** dipilih karena F2 OOF tertinggi (0,500) dan menekan false negative, sesuai posisi biaya FN yang lebih mahal daripada FP pada konteks penyaringan berkas. Konsekuensinya, beban alarm tinggi. Untuk kapasitas pemeriksaan terbatas, laporan merekomendasikan **0,19** sebagai titik operasional (recall 0,571; 23 alarm).

### Before vs after tuning (Stratified 5-Fold CV)

| Metrik | Before | After | Delta |
|---|---|---|---|
| Macro F1 | 0,4467 ± 0,0051 | 0,5532 ± 0,1182 | +0,1065 |
| F1 positif | 0,0000 ± 0,0000 | 0,2167 ± 0,2173 | +0,2167 |
| Precision | 0,0000 ± 0,0000 | 0,4000 ± 0,4346 | +0,4000 |
| Recall | 0,0000 ± 0,0000 | 0,1600 ± 0,1673 | +0,1600 |
| PR-AUC (AP) | 0,2313 ± 0,0662 | 0,3312 ± 0,1217 | +0,0999 |
| ROC-AUC | 0,5240 ± 0,1110 | 0,5535 ± 0,2080 | +0,0295 |
| Log-loss | 0,7978 ± 0,5825 | 1,4947 ± 1,1025 | +0,6969 |

### Validasi historis Tugas 05

Artefak Tugas 05 dimuat ulang dan diuji pada 34 berkas yang sama. Pada ambang historis 0,11 hasilnya TP 4, FN 3, FP 18, TN 9; precision 0,182; recall 0,571; F1 0,276. Angka ini sama dengan laporan Tugas 05, sehingga dataset, split, dan pipeline yang diwarisi tidak berubah. Angka tersebut **bukan** hasil Tugas 06 dan hanya dipakai sebagai pemeriksaan konsistensi.

## 2. Struktur folder

```text
PEMBELAJARAN_MESIN_KELOMPOK_02/
├── AUDIT_FILE_PROYEK_TUGAS_06.md
├── CEK_KESESUAIAN_TEMPLATE_TUGAS_06.md
├── README_TUGAS_06.md
├── data/
│   └── berkas_notaris_terisi (2).csv
├── eksperimen_tugas_06/
│   ├── eksperimen_tugas06.py
│   ├── fitur_notaris.py
│   └── hasil/
│       ├── data/       # metrik, threshold, prediksi, bootstrap, error analysis
│       ├── optuna/     # riwayat_trial.csv, informasi_study.json, importance
│       ├── grafik/     # 8 grafik hasil + 1 tangkapan layar prototipe
│       ├── model/      # model_tugas06_baseline.joblib, model_tugas06_tuned.joblib
│       └── log/        # eksekusi.log, environment.json
├── kode_tugas_sebelumnya/
│   ├── tugas_04/
│   └── tugas_05/
├── laporan_tugas_06/
│   ├── TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.docx
│   ├── TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.pdf
│   ├── buat_laporan.py
│   ├── laporan_lib.py
│   ├── bagian_a_b.py
│   ├── bagian_c_d.py
│   ├── bagian_e.py
│   ├── bagian_f_lampiran.py
│   └── ekspor_pdf.sh
├── referensi/          # panduan, template, Tugas 04–05, slide, cheatsheet
└── requirements_tugas_06.txt
```

## 3. Cara menjalankan ulang

Jalankan dari folder proyek. Virtualenv proyek ada di `.venv`.

```bash
cd eksperimen_tugas_06
../.venv/bin/python eksperimen_tugas06.py --trials 30

cd ../laporan_tugas_06
../.venv/bin/python buat_laporan.py
./ekspor_pdf.sh
```

Eksperimen memerlukan waktu sekitar satu menit pada mesin ini. Seluruh seed dikunci (`SEED=42`), sehingga angka inti akan sama bila versi pustaka tidak berubah. Versi yang dipakai: Python 3.12.0, numpy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1, optuna 5.0.0, matplotlib 3.11.2, joblib 1.6.0, python-docx 1.2.0.

Jika Word tidak tersedia, buka DOCX lalu ekspor manual ke PDF. Jika virtualenv dibuat ulang:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements_tugas_06.txt
```

## 4. Bukti eksekusi

- `eksperimen_tugas_06/hasil/data/ringkasan_eksekusi.json` — ringkasan seluruh hasil.
- `eksperimen_tugas_06/hasil/data/validasi_historis_tugas05.json` — bukti reproduksi T05.
- `eksperimen_tugas_06/hasil/optuna/riwayat_trial.csv` — 30 trial lengkap.
- `eksperimen_tugas_06/hasil/optuna/informasi_study.json` — parameter terbaik dan importance.
- `eksperimen_tugas_06/hasil/log/eksekusi.log` — log eksekusi terakhir.
- `eksperimen_tugas_06/hasil/log/environment.json` — versi pustaka dan platform.
- `eksperimen_tugas_06/hasil/model/uji_paritas.joblib.json` — max absolute error 0,0 dan prediksi identik.

Eksperimen Tugas 06 dijalankan ulang pada 5 November 2026 untuk verifikasi. Seluruh angka inti identik dengan eksekusi sebelumnya; hanya durasi dan timestamp yang berubah.

## 5. Menyiapkan tautan repositori publik

Folder ini sudah menjadi repositori Git lokal dengan satu commit. Untuk memenuhi komponen rubrik repositori, buat repositori kosong di GitHub (tanpa README), lalu jalankan:

```bash
git remote add origin https://github.com/<akun>/<nama-repo>.git
git branch -M main
git push -u origin main
```

Setelah repositori publik tersedia, tambahkan tautannya pada halaman Lampiran laporan (menggantikan catatan "belum tersedia") sebelum unggah ke LMS.

## 6. Batasan dan catatan pengumpulan

1. Data uji 34 berkas sudah pernah dipakai pada Tugas 04 dan Tugas 05. Tugas 06 tidak memilih parameter atau ambang dari data uji, tetapi data uji tersebut bukan lagi holdout yang sepenuhnya buta.
2. Model belum layak untuk keputusan otomatis. Model diposisikan sebagai alat bantu penyaringan dengan pemeriksaan staf.
3. Bagian F masih memerlukan tanda tangan basah seluruh anggota.
4. Repositori Git lokal sudah diinisialisasi dan di-commit. Tautan repositori publik GitHub/Google Colab belum tersedia karena akun kelompok belum dihubungkan; folder ini siap diunggah.
5. Dataset sumber tidak diubah. SHA-256 dataset: `686aa269511d6eb26ad661ebfde499ffbfd64383de4e84e93ea54ab23905785b`.
6. Checklist kesesuaian template dan arahan dosen ada di `CEK_KESESUAIAN_TEMPLATE_TUGAS_06.md`.

## 7. Berkas utama laporan

| Bagian | Isi |
|---|---|
| A | Identitas kelompok dan konfirmasi baseline Tugas 04–05 |
| B | Classification report, confusion matrix, ROC/PR, analisis FP/FN, paradoks akurasi |
| C | Threshold tuning dari OOF, empat ambang, justifikasi dan trade-off |
| D | Optuna 30 trial, Stratified 5-Fold CV, before vs after, kode optimasi |
| E | Draf konsolidasi Bab I–III proposal UTS |
| F | Lembar komitmen dan integritas akademik |
| Lampiran | Daftar berkas, tangkapan layar prototipe, cara menjalankan ulang, 10 trial terbaik, rubrik, catatan AI |
