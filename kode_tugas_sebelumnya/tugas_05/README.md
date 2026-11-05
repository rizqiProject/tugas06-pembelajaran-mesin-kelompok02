# Tugas 05 Kelompok 02 Kantor Notaris dan PPAT Aries Buwana

Prototipe ini melanjutkan model Tugas 04 pada 169 berkas: 33 terlambat dan 136 tepat
waktu. Model yang diekspor adalah Decision Tree dengan depth 4, leaf minimal 15,
dan threshold awal 0,11. Tidak ada penalaan atau pelatihan ulang pada Tugas 05.

## Menjalankan di komputer sendiri

Gunakan Python 3.12. Dari folder utama paket, jalankan:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port 8505
```

Buka http://localhost:8505. Model sudah disertakan di folder artifacts sehingga
GridSearchCV Tugas 04 tidak perlu dijalankan kembali.

Di terminal kedua, aktifkan lingkungan yang sama, lalu jalankan API:

```bash
source .venv/bin/activate
python -m uvicorn api:app --host 127.0.0.1 --port 8005
```

Dokumentasi API tersedia di http://localhost:8005/docs. Contoh permintaan:

```bash
curl -X POST http://127.0.0.1:8005/predict \
  -H "Content-Type: application/json" \
  --data-binary @tests/fixtures/BRK_0024.json
```

Pada Windows, aktivasi lingkungan menggunakan `.venv\Scripts\activate`.

## Menggunakan form

Pilih contoh berkas atau masukkan ID, tanggal penerimaan, kategori akta, jumlah
penghadap, SLA, serta tanggal RUPS bila tercatat. Tekan Periksa risiko. Skor model,
ambang, antrean yang terbaca, dan kontribusi SHAP ditampilkan pada bagian hasil.
Ambang awal 0,11 dapat diubah untuk mencoba pengaruhnya terhadap keputusan.

Label "Tidak terpicu alarm" tidak memastikan berkas akan selesai tepat waktu.
Skor belum dikalibrasi menjadi peluang nyata. Pemeriksaan staf tetap diperlukan.
Checkbox pemeriksaan dan unduhan JSON menyediakan catatan konfirmasi pengguna.

## Histori antrean

Histori awal berisi 135 catatan train. Hitungan tersebut terbatas pada snapshot,
belum seluruh antrean kantor. Form dapat memuat snapshot CSV lain dengan kolom:

```text
id_berkas,tgl_masuk,tgl_selesai
```

Tanggal selesai boleh kosong untuk berkas yang masih terbuka. API menerima struktur
yang sama pada field history. Histori yang diberikan hanya berlaku untuk request
tersebut; encoder dan pohon tidak di-fit ulang. Jumlah maksimal 5.000 catatan dan ID
harus unik. Berkas yang baru masuk pada hari yang sama belum dihitung dalam antrean
awal hari.

## Kontrak endpoint

POST /predict menerima field record, threshold opsional, history opsional, dan
explain. Field record berisi id_berkas, tgl_masuk, kategori_akta, jumlah_penghadap,
sla_hari, serta tgl_rups opsional. Tanggal selesai berkas yang sedang diprediksi
tidak diminta. Schema menolak field tambahan, numerik yang salah tipe, serta nilai
di luar batas teknis. Kesalahan dikembalikan sebagai HTTP 422 tanpa menghentikan API.

Batas 100 penghadap dan 365 hari adalah batas teknis prototipe, bukan ketentuan
layanan kantor. Nilai sah yang berada di luar rentang train tetap diberi peringatan.
Kategori baru ditangani oleh encoder dengan handle_unknown=ignore dan diberi
penanda pemeriksaan. Tanggal RUPS setelah tanggal penerimaan tidak dipakai sebagai
informasi awal.

## Pengujian

```bash
python -m pytest tests/test_inference.py -q
```

Untuk merekam ulang benchmark dan browser, tambahkan dependensi pengujian browser:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium --only-shell
python run_evidence.py
```

Script tersebut menjalankan API dan Streamlit lokal, menguji request, merekam UI,
memanggil cURL, lalu menghentikan kedua server. Jalankan saat port 8005 dan 8505
tidak sedang dipakai oleh instance lain. Seluruh keluaran disimpan di evidence.
Hasil latensi akan berubah sesuai mesin dan beban komputer.

Sebanyak 100 indeks sampel diambil ulang dari 34 holdout Tugas 04 dan dijalankan
tiga putaran pada setiap jalur. Ini merupakan 300 pengukuran per jalur, bukan 100
observasi kantor baru. Skenario berawalan UJI adalah fixture perangkat lunak dan
tidak menjadi data pelatihan atau bukti akurasi pada periode baru.

## Artefak dan bukti

- artifacts/model_final.joblib: pipeline, threshold, background SHAP, dan informasi
  referensi dalam objek NotarisRiskModel.
- artifacts/model_metadata.json: tanggal pelatihan dan ekspor, parameter, metrik,
  versi pustaka, schema, serta hash model dan sumber.
- data/berkas_notaris_169.csv: salinan sumber tanpa perubahan isi byte.
- data/history_train_reference.csv: histori train yang tersimpan di transformer.
- data/requests_test_34.json: request yang dibentuk dari 34 holdout lama.
- evidence/serialization_check.json: kesamaan skor dan label sebelum/sesudah ekspor.
- evidence/holdout_replay_34.csv: skor dan jenis kesalahan pada holdout lama.
- evidence/benchmark.json dan latency_all_requests.csv: seluruh hasil pengukuran.
- evidence/edge_cases.json: hasil 13 skenario invalid atau di luar cakupan.
- evidence/error_cases.json: FP BRK_0110 serta FN BRK_0075 dan BRK_0168, termasuk
  kontribusi SHAP, dukungan daun, dan percabangan pohon.
- evidence/screenshots: rekaman browser aplikasi yang benar-benar berjalan.
- reports: PDF dan Word laporan.

Hasil uji regresi tetap TP 4, FN 3, FP 18, TN 9 pada ambang 0,11. Model belum layak
untuk prioritas otomatis. Instansi tujuan dan ceklis awal belum tersedia dalam
sumber dan tidak diberi nilai perkiraan.

## Membuat ulang artefak dan naskah

```bash
python build_artifact.py --source-root source_tugas04
python prepare_report_data.py
python -m pip install -r requirements-report.txt
python build_report.py
```

Ekspor Word ke PDF dan periksa halaman setelah ada perubahan. Tanggal pelatihan
mengikuti eksperimen Tugas 04 pada 22 Oktober 2026; waktu fit persis tidak direkam.
Rekap dosen menyebut depth 3 dan leaf 5, sedangkan artefak dan tabel parameter Tugas
04 memuat depth 4 dan leaf 15. Implementasi mengikuti artefak yang tervalidasi;
perbedaan ini dijelaskan di laporan.

## Pengumpulan

Unggah PDF dan ZIP melalui slot Pertemuan 05 pada LMS EL-NUSA, serta cadangkan ke
Google Drive penugasan kelompok sesuai instruksi dosen. Tenggat yang tercantum:
Kamis, 29 Oktober 2026, pukul 23:59:59 WIB. Koordinator memeriksa isi dan menandatangani
Bagian F. Tanda tangan belum dibubuhkan pada berkas yang disiapkan.
