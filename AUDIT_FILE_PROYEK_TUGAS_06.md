# AUDIT FILE PROYEK TUGAS 06

**Mata kuliah:** Pembelajaran Mesin (3 SKS)  
**Kelas:** KG.043.10.A  
**Kelompok:** 02  
**Objek penelitian:** Kantor Notaris & PPAT Aries Buwana, Jakarta Barat  
**Tanggal audit:** 5 November 2026  
**Tenggat:** Kamis, 5 November 2026, pukul 23.59.59 WIB

## 1. Ringkasan audit

Seluruh berkas yang disebut dalam instruksi ditemukan di komputer, termasuk
`Template_Tugas_06_Pembelajaran_Mesin.docx`. Berkas tersebut sebelumnya tidak
berada di satu folder proyek, sehingga proyek ini disusun ulang tanpa mengubah
berkas asli di `Downloads`.

Tidak ditemukan kode atau laporan Tugas 06 yang sudah jadi. Yang tersedia adalah
materi Pertemuan 06, template resmi, laporan Tugas 04 dan Tugas 05, dataset, serta
paket kode Tugas 04 dan Tugas 05. Karena itu Tugas 06 dikerjakan sebagai
kelanjutan langsung pipeline Tugas 05, bukan sebagai proyek baru.

## 2. Struktur proyek yang digunakan

```text
PEMBELAJARAN_MESIN_KELOMPOK_02/
├── referensi/
├── data/
├── kode_tugas_sebelumnya/
│   ├── tugas_04/
│   └── tugas_05/
├── eksperimen_tugas_06/
└── laporan_tugas_06/
```

Berkas asli di `Downloads` tidak dipindahkan dan tidak diubah. Penyalinan
dilakukan agar eksperimen Tugas 06 memiliki satu folder kerja yang dapat
diperiksa ulang.

## 3. Berkas yang ditemukan dan fungsinya

### 3.1 Materi dan panduan

| Berkas | Fungsi | Status |
|---|---|---|
| `referensi/Panduan_Tugas_06_Pembelajaran_Mesin.pdf` | Panduan resmi Tugas 06, 3 halaman: metrik, threshold, Optuna, proposal UTS, rubrik, checklist | Dibaca |
| `referensi/Slide_Materi_Minggu_06_Pembelajaran_Mesin.pdf` | Modul materi Minggu 06: accuracy paradox, metrik, threshold, Optuna, integrasi Bab I–III | Dibaca |
| `referensi/CHEATSHEET_TUGAS_06_PEMBELAJARAN_MESIN.pdf` | Ringkasan alur OOF, threshold, Optuna, dan checklist | Dibaca |
| `referensi/Template_Tugas_06_Pembelajaran_Mesin.docx` | Template resmi laporan Tugas 06 dengan bagian A–F dan tabel | Ditemukan dan dipakai sebagai acuan susunan |

**Catatan:** template Tugas 06 memang ada. Tidak ada alasan untuk mengklaim
template tidak tersedia atau memakai template Tugas 04 sebagai pengganti resmi.

### 3.2 Laporan penelitian sebelumnya

| Berkas | Fungsi | Status |
|---|---|---|
| `referensi/TUGAS_04_KELOMPOK_02_NOTARIS_PPAT.pdf` | Laporan Tugas 04: tuning, feature importance, SHAP | Dibaca |
| `referensi/TUGAS_04_KELOMPOK_02_NOTARIS_PPAT.docx` | Versi Word laporan Tugas 04 | Dibaca |
| `referensi/TUGAS_05_KELOMPOK_02_NOTARIS_PPAT.pdf` | Laporan Tugas 05: serialisasi model dan prototipe inferensi | Dibaca |
| `referensi/TUGAS_05_KELOMPOK_02_NOTARIS_PPAT.docx` | Versi Word laporan Tugas 05 | Dibaca |

### 3.3 Dataset

| Berkas | Fungsi | Status |
|---|---|---|
| `data/berkas_notaris_terisi (2).csv` | Dataset sumber 169 berkas, 10 kolom | Dipakai apa adanya |
| `kode_tugas_sebelumnya/tugas_05/data/berkas_notaris_169.csv` | Salinan dataset yang dipakai paket Tugas 05 | Identik dengan sumber |
| `kode_tugas_sebelumnya/tugas_05/data/prediksi_tugas04.csv` | Prediksi 34 test Tugas 04 | Dipakai untuk validasi split |

SHA-256 dataset: `686aa269511d6eb26ad661ebfde499ffbfd64383de4e84e93ea54ab23905785b`

### 3.4 Kode dan artefak Tugas 04

| Berkas | Fungsi |
|---|---|
| `kode_tugas_sebelumnya/tugas_04/work/analisis_tugas04_asli.py` | Skrip analisis Tugas 04: split, GridSearchCV, nested CV, threshold, PFI, SHAP |
| `kode_tugas_sebelumnya/tugas_04/work/hasil_tugas04_asli/` | Hasil Tugas 04: metrik, prediksi, konfigurasi beku, grafik |
| `kode_tugas_sebelumnya/tugas_04/work/hasil_tugas04_asli/model_tuned_penelitian.joblib` | Model tuned Tugas 04 |
| `kode_tugas_sebelumnya/tugas_04/upload/berkas_notaris_ v5.csv` | Dataset versi Tugas 04 dengan kolom `sumber` dan fitur tambahan |

**Catatan penting:** dataset Tugas 04 (`berkas_notaris_ v5.csv`) dan dataset Tugas
05/Tugas 06 (`berkas_notaris_terisi (2).csv`) bukan versi yang sama. Tugas 06
mengikuti dataset dan artefak Tugas 05 agar konsisten dengan hasil yang diminta
dalam instruksi, yaitu 169 berkas, 33 terlambat, 136 tepat waktu, 135 train, dan
34 test.

### 3.5 Kode dan artefak Tugas 05

| Berkas | Fungsi |
|---|---|
| `kode_tugas_sebelumnya/tugas_05/fitur_notaris.py` | Transformer fitur: antrean, RUPS, bulan sin/cos, kategori, hari |
| `kode_tugas_sebelumnya/tugas_05/inference.py` | Kelas `NotarisRiskModel` untuk inferensi |
| `kode_tugas_sebelumnya/tugas_05/build_artifact.py` | Ekspor artefak Tugas 04 ke format inferensi |
| `kode_tugas_sebelumnya/tugas_05/evaluate.py` | Evaluasi holdout dan bukti regresi |
| `kode_tugas_sebelumnya/tugas_05/artifacts/model_final.joblib` | Model final Tugas 05 |
| `kode_tugas_sebelumnya/tugas_05/artifacts/model_metadata.json` | Metadata model, metrik, versi pustaka, hash |
| `kode_tugas_sebelumnya/tugas_05/data/` | Dataset, histori train, prediksi Tugas 04, request test |
| `kode_tugas_sebelumnya/tugas_05/evidence/` | Bukti eksekusi, tangkapan layar, log, hasil uji |
| `kode_tugas_sebelumnya/tugas_05/reports/` | Laporan Tugas 05 Word dan PDF |

### 3.6 Berkas Tugas 06 yang dibuat

| Berkas | Fungsi |
|---|---|
| `eksperimen_tugas_06/fitur_notaris.py` | Salinan transformer Tugas 05 untuk reproduksi mandiri |
| `eksperimen_tugas_06/eksperimen_tugas06.py` | Skrip utama: audit, Optuna, CV, OOF, threshold, evaluasi test, grafik, model |
| `eksperimen_tugas_06/hasil/data/` | Tabel metrik, prediksi, error analysis, bootstrap, JSON ringkasan |
| `eksperimen_tugas_06/hasil/optuna/` | Riwayat trial, parameter terbaik, kepentingan parameter |
| `eksperimen_tugas_06/hasil/grafik/` | Delapan gambar hasil eksekusi |
| `eksperimen_tugas_06/hasil/model/` | Model before/after tuning dan metadata |
| `eksperimen_tugas_06/hasil/log/` | Log eksekusi dan versi lingkungan |
| `laporan_tugas_06/` | Laporan Word, PDF, README, dan dokumen audit |

## 4. Berkas yang tidak ditemukan

Tidak ada berkas wajib yang hilang. Namun, beberapa hal berikut memang tidak
tersedia dan tidak dikarang:

1. **Kode Tugas 06 sebelumnya** — belum ada; eksperimen Tugas 06 dibuat baru.
2. **Data biaya operasional dan kapasitas pemeriksaan staf** — tidak tersedia.
   Karena itu analisis threshold tidak memakai fungsi biaya rupiah atau angka
   kapasitas kantor.
3. **Data periode baru setelah Tugas 05** — tidak tersedia. Evaluasi test memakai
   holdout 34 berkas yang sama dengan Tugas 04/05.
4. **Tanda tangan basah anggota** — belum dibubuhkan; template menyediakan kolom
   tanda tangan untuk diisi manual.
5. **Repositori publik GitHub/Google Colab** — belum ada tautan publik. Kode
   disertakan lokal; tautan publik perlu dibuat oleh kelompok sebelum unggah.

## 5. Kondisi kode dan model sebelumnya

Pipeline Tugas 05 yang dimuat ulang:

```text
FiturNotaris
→ ColumnTransformer
   ├── SimpleImputer(median) untuk fitur numerik
   ├── SimpleImputer(most_frequent) + OneHotEncoder untuk fitur kategorik
→ DecisionTreeClassifier(max_depth=4, min_samples_leaf=15, random_state=42)
```

Fitur yang dipakai:

- `jumlah_penghadap`
- `sla_hari`
- `antrean_berjalan`
- `ada_rups`
- `bulan_sin`
- `bulan_cos`
- `kategori_akta`
- `hari_masuk`

Kolom yang tidak dipakai sebagai prediktor: `tgl_selesai`, `durasi`, label
`terlambat`, `no_urut`, `no_bulanan`, dan `tgl_akta`.

## 6. Dataset dan konsistensi angka

### 6.1 Audit dataset

| Pemeriksaan | Hasil |
|---|---|
| Jumlah baris | 169 |
| Jumlah kolom | 10 |
| Terlambat (positif) | 33 (19,5%) |
| Tepat waktu (negatif) | 136 (80,5%) |
| Duplikasi `id_berkas` | 0 |
| Tanggal RUPS terisi | 13 |
| Tanggal RUPS setelah tanggal masuk | 0 |
| Rentang durasi | 4–40 hari |

Rumus label yang dipakai:

```text
terlambat = 1 jika (tgl_selesai - tgl_masuk) dalam hari > sla_hari
```

Label ini konsisten dengan 33 positif dan dengan hasil historis Tugas 05.

### 6.2 Pembagian data

```text
train_test_split(test_size=0.20, stratify=y, random_state=42)
```

| Partisi | Jumlah | Terlambat | Tepat waktu |
|---|---:|---:|---:|
| Train | 135 | 26 | 109 |
| Test | 34 | 7 | 27 |

Daftar ID test yang dihasilkan sama persis dengan
`kode_tugas_sebelumnya/tugas_05/data/prediksi_tugas04.csv`, termasuk urutannya.
Ini membuktikan pembagian data Tugas 06 konsisten dengan Tugas 05.

### 6.3 Reproduksi hasil historis Tugas 05

Model Tugas 05 dimuat dan diuji pada 34 berkas test dengan threshold 0,11.
Hasilnya:

| Metrik | Nilai |
|---|---:|
| TP | 4 |
| FN | 3 |
| FP | 18 |
| TN | 9 |
| Precision | 0,1818 |
| Recall | 0,5714 |
| F1 positif | 0,2759 |

Angka tersebut sama dengan laporan Tugas 05. Validasi ini disimpan di
`eksperimen_tugas_06/hasil/data/validasi_historis_tugas05.json`.

**Angka historis ini tidak dipakai sebagai hasil Tugas 06.** Angka tersebut hanya
menjadi bukti bahwa dataset, split, dan pipeline yang diwarisi sudah benar.

## 7. Rencana pekerjaan Tugas 06

| Tahap | Pekerjaan | Status |
|---|---|---|
| 1 | Audit seluruh berkas | Selesai |
| 2 | Pahami pipeline Tugas 04–05 | Selesai |
| 3 | Validasi dataset, label, dan split | Selesai |
| 4 | Evaluasi model mendalam pada test | Selesai |
| 5 | Threshold tuning dari OOF train | Selesai |
| 6 | Optuna + Stratified 5-Fold CV | Selesai |
| 7 | Grafik, tabel, dan analisis | Selesai |
| 8 | Sintesis Bab I–III | Selesai |
| 9 | Laporan Tugas 06 | Selesai |
| 10 | Ekspor Word dan PDF | Selesai |
| 11 | Pemeriksaan angka, referensi, dan kelengkapan | Selesai |

## 8. Batasan yang harus dicatat

1. **Holdout sudah pernah dilihat.** Test 34 berkas yang sama dipakai pada Tugas
   04 dan Tugas 05. Tugas 06 tidak memilih parameter atau threshold dari test,
   tetapi test bukan lagi holdout yang sepenuhnya buta. Karena itu hasil test
   dilaporkan sebagai evaluasi pada partisi yang sama, bukan sebagai validasi
   periode baru.
2. **Sampel kecil.** Hanya 7 keterlambatan pada test. Satu perubahan prediksi
   menggeser recall sekitar 14,3 poin persentase.
3. **Model lemah secara diskriminasi.** ROC-AUC dan PR-AUC rendah. Threshold
   tuning tidak dapat memperbaiki model yang skornya banyak bertumpuk.
4. **Tidak ada biaya FP/FN.** Analisis trade-off bersifat operasional kualitatif,
   bukan optimasi biaya rupiah.
5. **Versi pustaka berbeda.** Artefak Tugas 05 dibuat dengan scikit-learn 1.8.0;
   eksperimen Tugas 06 memakai scikit-learn 1.9.1. Pelatihan ulang baseline
   mereproduksi TP/FN/FP/TN historis, sehingga perbedaan versi tidak mengubah
   kesimpulan utama.
6. **Tidak ada data periode baru.** Klaim generalisasi harus menunggu data setelah
   Tugas 05.

## 9. Kesimpulan audit

Bahan Tugas 06 lengkap. Penelitian dapat dilanjutkan tanpa mengubah dataset,
label, atau hasil Tugas 04/05. Eksperimen Tugas 06 menggunakan pipeline dan split
yang sama, lalu menambahkan evaluasi mendalam, threshold tuning berbasis OOF,
Optuna dengan Stratified 5-Fold, dan sintesis proposal Bab I–III.
