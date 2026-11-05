# Panduan koordinator untuk pengumpulan dan penjelasan

Gunakan PDF revisi yang berisi 20 halaman dan hanya 169 data asli. Word disediakan
untuk pengesahan. Setelah ada perubahan Word atau tanda tangan, ekspor kembali
ke PDF lalu periksa nomor halaman, tabel, dan grafik sebelum mengunggah.

## Hal yang sudah tersedia

Identitas mengikuti Tugas 03. Decision Tree dipertahankan. Tuning menguji lima
parameter dan 320 kandidat dengan 5-fold CV di dalam pipeline. Nested CV memberi
evaluasi prosedur seleksi pada train. Semua keputusan model dan threshold
dibekukan sebelum holdout pada eksperimen yang menghasilkan angka ini.
Perbandingan train/CV/test, confusion matrix, ROC/PR, bootstrap, PFI top10, SHAP
beeswarm, dan waterfall tersedia dengan hasil numerik pendamping.

## Jawaban untuk pertanyaan yang mungkin muncul

Mengapa hanya 169? Hanya baris berkode asli masuk eksperimen. Tidak ada
perluasan catatan observasi untuk memperbanyak sampel.

Mengapa T03 mencatat 33 terlambat, sekarang 35? Ada perbedaan versi sumber.
CSV asli T03 tidak disertakan, sehingga tidak dapat dipastikan ID mana yang
berubah. Hasil historis tetap ditulis sesuai T03. Efek tuning dihitung dari
baseline ulang dan tuned yang memakai data, fitur, dan partisi identik.

Apakah tuning selalu lebih baik? Pada test, AP berubah dari 0,347 ke 0,483.
F1 positif pada 0,50 berubah dari 0,200 ke 0,286. F1 outer CV pada 0,50
justru turun dari 0,339 ke 0,309, sehingga hasil belum stabil.

Bagaimana menindaklanjuti ambang 0,25? Pada test tuned, recall menjadi 4/7
dengan 15 FP, dibanding 3/7 dan 11 FP pada 0,50. Ambang OOF 0,11
menangkap 6/7 tetapi memberi 20 FP. Penentuan operasional membutuhkan
kapasitas staf dan pertimbangan biaya FN terhadap FP.

Apakah seluruh saran penambahan fitur sudah selesai? Indikator pengesahan,
pajak, kelengkapan biner, dan jumlah dokumen dipakai sesuai CSV. Instansi
tujuan dan rincian item ceklis belum tersedia. Isi form pendamping dari
arsip; jangan menganggap kolom form yang kosong sebagai hasil survei baru.

Mengapa SHAP atau PFI nol? Nilai nol berlaku pada model dan sampel evaluasi
saat ini. Nilai tersebut bukan bukti bahwa kegiatan pemeriksaan berkas
tidak penting. SHAP menjelaskan skor prediksi dan bukan hubungan sebab akibat.

## Sebelum mengumpulkan

Koordinator memeriksa isi dan memahami batas hasil, lalu mengesahkan Bagian F.
Tidak ada tanda tangan yang dibuat otomatis. Nama PDF mengikuti panduan
TUGAS_04_KELOMPOK_02_NOTARIS_PPAT.pdf. Batas pengumpulan yang tertulis pada
panduan adalah 22 Oktober 2026 pukul 23:59:59 WIB melalui LMS/EL-NUSA.
Penilaian ditetapkan dosen; jumlah halaman dan kenaikan satu metrik bukan
jaminan nilai penuh.
