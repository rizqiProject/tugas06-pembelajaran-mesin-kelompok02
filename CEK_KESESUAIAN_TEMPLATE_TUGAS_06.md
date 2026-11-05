# CEK KESESUAIAN TEMPLATE DAN ARAHAN DOSEN — TUGAS 06

**Kelompok:** 02  
**Objek:** Kantor Notaris & PPAT Aries Buwana  
**Tanggal pemeriksaan:** 5 November 2026  
**Status:** Dokumen Word dan PDF sudah memakai Template Tugas 06; repositori publik sudah tersedia. Sisa satu item manual: tanda tangan Bagian F.

## 1. Sumber acuan yang dipakai

| Berkas lokal | SHA-256 | Status |
|---|---|---|
| `referensi/Panduan_Tugas_06_Pembelajaran_Mesin.pdf` | `c353f3231772cf395cae1d1689add986234cd094d72892192c45bf0bef30856e` | Dibaca; 3 halaman; memuat tenggat 5 November 2026, rubrik, dan checklist |
| `referensi/Template_Tugas_06_Pembelajaran_Mesin.docx` | `c00ae10c8c6cb1dcc4a216887441d0fa190109d7e7e13c3dd86ee8e7cf7a579b` | Dipakai sebagai basis dokumen; bagian A–F |
| `referensi/Slide_Materi_Minggu_06_Pembelajaran_Mesin.pdf` | `177f81f9ad14d21c88b7a58af07ce2c8569dae173988b0065ef749a47fb4c9fc` | Dibaca; 6 halaman |
| `referensi/CHEATSHEET_TUGAS_06_PEMBELAJARAN_MESIN.pdf` | `e1a5f4dd97b40dfdab9d0e55d5da95bec91df7626cdd837a518a43d8cc6e5933` | Dibaca; checklist OOF, threshold, Optuna |

Panduan lokal bertanggal pembuatan 27 Oktober 2026 dan memuat judul resmi
"Panduan Penugasan Minggu 06". Isinya cocok dengan arahan dosen yang dikutip:
satu dokumen, protokol OOF, minimal tiga threshold, Optuna 20–30 trial, dan
sintesis Bab I–III.

## 2. Catatan pemeriksaan OneDrive

Tautan OneDrive yang diberikan mengarah ke folder pribadi:

`Documents/DATA KERJA/#KAMPUS/Semester Gasal 2026-2027/S1/PEMBELAJARAN MESIN`

Hasil pemeriksaan dari lingkungan ini:

- Halaman folder dapat dimuat, tetapi daftar berkas dimuat oleh JavaScript dan
  memerlukan sesi login pengguna.
- Permintaan API OneDrive tanpa token mengembalikan **401 unauthenticated**.
- Unduhan folder diarahkan ke **login.live.com**, sehingga isi folder tidak dapat
  dibaca tanpa kredensial.

Karena itu, isi folder OneDrive tidak dapat saya pastikan dari sini. Yang saya
verifikasi adalah salinan lokal di `referensi/` yang dipakai untuk menyusun
laporan. Jika ingin memastikan versi di drive, buka folder tersebut saat login
lalu bandingkan nama dan tanggal berkasnya dengan tabel di atas.

## 3. Kesesuaian dengan Template Tugas 06

| Elemen template | Status | Bukti pada laporan |
|---|---|---|
| Judul dan identitas kelompok | Sesuai | Halaman sampul; Tabel 1 |
| A. Identitas dan konfirmasi baseline Tugas 04–05 | Sesuai | Bagian A; Tabel 1–5 |
| B. Matriks evaluasi lengkap dan confusion matrix | Sesuai | Bagian B; Tabel 6–11; Gambar 1–3 |
| C. Kalibrasi ambang batas | Sesuai | Bagian C; Tabel 12–13; Gambar 2 dan 4 |
| D. Optuna dan Stratified 5-Fold CV | Sesuai | Bagian D; Tabel 14–18; Gambar 5–8 |
| E. Draf konsolidasi Bab I–III | Sesuai | Bagian E; Tabel 19–23 |
| F. Lembar komitmen | Sesuai strukturnya; tanda tangan belum diisi | Bagian F; Tabel 24 |
| Lampiran dan daftar berkas | Sesuai | Lampiran A–F; Tabel 25–27; Gambar 9 |
| Satu dokumen Word dan PDF | Sesuai | DOCX dan PDF dari naskah yang sama |
| Nama berkas | Sesuai | `TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.docx/.pdf` |

## 4. Kesesuaian dengan arahan dosen

| Arahan dosen | Status | Bukti |
|---|---|---|
| Cukup satu dokumen tunggal, bukan dua laporan terpisah | Terpenuhi | Bagian A–D eksperimen dan Bagian E proposal berada dalam satu DOCX/PDF |
| Memakai `Template_Tugas_06_Pembelajaran_Mesin.docx` | Terpenuhi | Template lokal dipakai sebagai basis; struktur A–F dipertahankan |
| Threshold dipilih dari OOF train, bukan test | Terpenuhi | C.1; prediksi OOF dari `cross_val_predict` pada train |
| Gunakan `StratifiedKFold(5)` dan `predict_proba` | Terpenuhi | C.1 menyebut `cross_val_predict`, `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`, dan `method="predict_proba"` |
| Kunci threshold sebelum evaluasi test | Terpenuhi | C.1 dan C.2; Tabel 12 |
| Minimal tiga threshold, termasuk 0,50 | Terpenuhi | Empat threshold: 0,50; 0,25; 0,19; 0,05 (Tabel 12) |
| Jelaskan protokol OOF di Bagian C | Terpenuhi | C.1 |
| Bagian C: satu kurva ROC dan satu kurva PR dari model terbaik | Terpenuhi | Gambar 2 hanya model After Tuning; satu panel ROC dan satu panel PR |
| Tandai titik operasi 0,50 dan threshold optimal | Terpenuhi | Gambar 2 menandai 0,50; 0,19; dan 0,05 |
| Bagian D: before vs after memuat ROC-AUC, PR-AUC, F1, Log-Loss | Terpenuhi | Tabel 18 memuat F1, PR-AUC, ROC-AUC, dan Log-loss |
| Sitasi IEEE, minimal dua paper terverifikasi | Terpenuhi | Referensi [4] Saito & Rehmsmeier (2015) dan [5] Akiba et al. (2019), plus 10 referensi lain |
| Sintesis Bab I–III | Terpenuhi | E.1–E.3 |
| Kode dan artefak disertakan | Terpenuhi | Folder `eksperimen_tugas_06/`, model `.joblib`, grafik, riwayat trial |

## 5. Perbaikan yang dilakukan pada pemeriksaan ini

1. **Gambar 2** diubah dari dua model (before dan after) menjadi **satu kurva ROC
   dan satu kurva PR dari model After Tuning**, dengan titik operasi 0,50; 0,19;
   dan 0,05 ditandai. Ini mengikuti arahan dosen dan cheatsheet.
2. **Tabel 18** ditambah kolom **F1**, sehingga memuat F1, PR-AUC, ROC-AUC, dan
   Log-loss untuk before vs after.
3. **C.1** ditambah penjelasan implementasi `cross_val_predict` +
   `StratifiedKFold(5)` + `predict_proba`.
4. **C.2** ditambah rujukan eksplisit ke Gambar 2 agar titik operasi threshold
   terbaca di Bagian C.
5. **Lampiran B** ditambah tangkapan layar prototipe Tugas 05 sebagai bukti
   artefak antarmuka.
6. PDF dan DOCX diberi metadata judul/penulis.

## 6. Verifikasi angka kunci

| Metrik test @0,05 | Nilai | Sumber |
|---|---:|---|
| TP / FN / FP / TN | 5 / 2 / 19 / 8 | `metrik_test_terpilih.json` |
| Precision | 0,208 | idem |
| Recall | 0,714 | idem |
| F1 | 0,323 | idem |
| F2 | 0,481 | idem |
| Macro F1 | 0,378 | idem |
| ROC-AUC | 0,413 | idem |
| PR-AUC (AP) | 0,190 | idem |
| Log-loss | 1,155 | idem |
| Optuna best trial | #13; CV Macro F1 0,5532 | `informasi_study.json` |

Seluruh tabel laporan diperiksa ulang terhadap JSON/CSV: Tabel 12, 13, 16, 17,
18, 22, dan 26 cocok dengan hasil eksekusi.

## 7. Sisa pekerjaan manual

1. **Tautan repositori publik.** Sudah tersedia:
   `https://github.com/rizqiProject/tugas06-pembelajaran-mesin-kelompok02`
   (branch `main`, dapat dibuka tanpa login).
2. **Tanda tangan Bagian F.** Kolom sudah tersedia, tetapi belum ditandatangani
   basah oleh ketiga anggota.

## 8. Berkas hasil

- Word: `laporan_tugas_06/TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.docx`
- PDF: `laporan_tugas_06/TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.pdf` (32 halaman)
- README: `README_TUGAS_06.md`
- Audit: `AUDIT_FILE_PROYEK_TUGAS_06.md`
- Paket: `TUGAS_06_KELOMPOK_02_PAKET_LENGKAP.zip`
