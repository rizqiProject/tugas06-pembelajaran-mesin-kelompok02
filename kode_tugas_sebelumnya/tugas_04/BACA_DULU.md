# Tugas 04 Kelompok 02 menggunakan sumber asli

Laporan: output/TUGAS_04_KELOMPOK_02_NOTARIS_PPAT.pdf
Word: output/TUGAS_04_KELOMPOK_02_NOTARIS_PPAT.docx

## Dasar data dan perubahan versi

Analisis memakai 169 baris yang ditandai sumber=asli pada CSV v5 yang diberikan kelompok.
Baris dengan kode sumber lain tidak masuk analisis. Nilai pada baris terpilih dan labelnya
tidak diubah. Tidak ada tambahan instansi tujuan atau skor kelengkapan yang dibuat acak.
Fitur baru hanya hari masuk, koordinat bulan, dan indikator RUPS tersedia saat masuk.

Menurut keterangan kelompok, CSV berasal dari pendataan kantor Notaris dan PPAT.
Laporan tidak menambahkan rincian pelaksanaan survei, tanggal wawancara, atau pengukuran
lain yang tidak terdapat pada bahan yang diberikan.

Tugas 03 mencatat 33 positif dari 169 berkas, sedangkan subset sumber=asli v5 mempunyai
35 positif. Karena versinya berbeda, delta tuning memakai baseline yang dilatih ulang
dan tuned pada data, fitur, serta partisi yang sama. Hasil T03 tetap dicantumkan terpisah.

## Status final sesuai panduan dan catatan dosen

Laporan final berisi 20 halaman dan memakai struktur A sampai F pada template resmi.
Lampiran 3 memetakan setiap catatan dosen ke bukti serta status penyelesaiannya.
Instansi tujuan aktual dan skor ceklis awal belum dapat dilengkapi dari kolom CSV.
Form data/FORM_VERIFIKASI_FITUR_TAMBAHAN_169.csv memuat 169 ID, dengan kolom tambahan
masih kosong. Form bukan data pelatihan saat ini dan perlu diisi berdasarkan arsip kantor.
BPN, AHU, KPP Pratama, dan Bapenda tidak disimpulkan hanya dari jenis akta atau perlu_pajak.

Dataset pemodelan bersih tersedia di data/berkas_notaris_asli_169.csv. CSV v5 lengkap
pada upload adalah berkas sumber audit; skrip memfilter sumber=asli dan memeriksa
jumlah tepat 169. Tidak ada baris lain pada pelatihan, CV, test, PFI, atau SHAP.

Riwayat T03 memuat 18 fitur encoded, sedangkan v5 yang dipakai sekarang menjadi 36.
Antrean berjalan pada T03 bukan otomatis sama dengan beban tujuh hari. Matriks
mentah T03 tidak disertakan; hasil T03 disajikan sebagai riwayat terpisah dan
delta tuning memakai baseline ulang serta tuned pada data dan partisi yang sama.

## Temuan penting

- Train 135 berkas dengan 28 terlambat. Test 34 berkas dengan 7 terlambat.
- Pada ambang 0,50, AP test meningkat dari sekitar 0,347 ke 0,483.
- F1 positif pada 0,50 meningkat dari 0,200 ke 0,286.
- Pada ambang 0,25, model menangkap 4 dari 7 keterlambatan dengan 15 alarm palsu.
- Ambang OOF 0,11 menangkap 6 dari 7 keterlambatan dengan 20 alarm palsu.
- Test hanya memiliki tujuh positif, sehingga satu prediksi menggeser recall 14,3 pp.
- Nilai kelengkapan tetap dimasukkan. Pohon final tidak menggunakannya untuk percabangan;
  hal itu tidak membuktikan bahwa pemeriksaan kelengkapan tidak penting.
- SHAP dihitung dengan pustaka asli, background efektif 100 dari train, dan additivity
  diperiksa pada seluruh test. Semua nilai tersedia dalam CSV.

## Menjalankan ulang

Pilihan Colab:
1. Buka Jalankan_Tugas04_Colab.ipynb.
2. Jalankan sel instalasi. Bila Colab meminta restart setelah pergantian NumPy, restart
   lalu lanjutkan sel berikutnya.
3. Unggah satu CSV v5 dari folder upload. Selanjutnya jalankan sel secara berurutan.
4. Notebook memfilter sumber=asli dan menghitung semua angka dari awal.

Pilihan lokal dengan Python 3.12, dari folder utama paket:

    python -m pip install -r requirements.txt
    python work/analisis_tugas04_asli.py --csv "upload/berkas_notaris_ v5.csv" --out work/hasil_tugas04_asli --jobs 2

Untuk membuat Word kembali:

    python -m pip install python-docx pillow
    python work/buat_laporan_asli.py

Ekspor Word ke PDF dan periksa kembali tampilan setelah perubahan.
Notebook ini disediakan tanpa klaim telah dieksekusi. Bukti eksekusi laporan adalah
work/analisis_asli_eksekusi.log serta seluruh hasil pada work/hasil_tugas04_asli.

## Model terlatih dan verifikasi

- work/hasil_tugas04_asli/model_baseline.joblib: pipeline baseline, threshold 0,50.
- work/hasil_tugas04_asli/model_tuned_penelitian.joblib: pipeline tuned dan threshold OOF 0,11.
- Threshold 0,11 adalah hasil penelitian; beban 26 alarm dari 34 test perlu dipertimbangkan.
- Jalankan python work/verifikasi_konsistensi_asli.py setelah memasang dependensi.
  Skrip memeriksa nilai data, ID, probabilitas, TP/FN/FP/TN, F1, AP, serta form kosong.
- classification_report_test.json menyimpan metrik kedua kelas dan rata-ratanya.

## Berkas audit

- audit_data.json: filter, jumlah data, label, duplikasi, dan hash input.
- partisi_dan_fold.csv: ID train/test serta fold CV.
- hasil_gridsearch_320_kandidat.csv: seluruh kandidat pencarian final.
- nested_cv_per_fold.csv dan prediksi_nested_oof.csv: hasil outer CV.
- konfigurasi_dibekukan_sebelum_test.json: parameter dan ambang sebelum test.
- metrik_train_test.csv dan prediksi_test_34_berkas.csv: hasil prediksi per berkas.
- bootstrap_delta_paired.json: ketidakpastian delta pada test yang sama.
- permutation_importance_100_ulangan.csv dan file NPY: seluruh hasil pengacakan.
- shap_semua_34_berkas.csv, shap_global_semua_fitur.csv, kasus_lokal_shap.json:
  kontribusi dan kasus lokal yang dapat diperiksa ulang.
- berkas_notaris_asli_dengan_fitur_tanggal.csv: data terpilih beserta fitur tanggal;
  nomor baris asal disimpan agar dapat dicocokkan dengan CSV input.
- grafik/: enam gambar laporan.

## Pengumpulan

Nama dan NIM mengikuti Tugas 03. Koordinator memeriksa isi, memahami hasil, dan mengesahkan
bagian F sebelum mengunggah PDF. Tanda tangan tidak dibubuhkan secara otomatis.
Tenggat sesuai panduan: Kamis, 22 Oktober 2026 pukul 23:59:59 WIB pada LMS/EL-NUSA.
Nama file: TUGAS_04_KELOMPOK_02_NOTARIS_PPAT.pdf.
