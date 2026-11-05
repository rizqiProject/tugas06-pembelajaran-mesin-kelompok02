"""Bagian F, referensi, dan lampiran."""
from __future__ import annotations

from laporan_lib import f, n


def tulis(lap, D):
    opt = D['opt']
    trials = D['trials']
    fig = D['fig']

    # ==================================================================
    # F. KOMITMEN
    # ==================================================================
    lap.halaman_putus()
    lap.h1('F. LEMBAR KOMITMEN & INTEGRITAS AKADEMIK TIM')
    lap.par('Kami seluruh anggota Kelompok 02 menyatakan dengan penuh kesadaran dan '
            'tanggung jawab ilmiah bahwa laporan Tugas 06 ini disusun berdasarkan '
            'penelitian yang sama dengan Tugas 04 dan Tugas 05. Dataset yang dipakai '
            'adalah berkas_notaris_terisi (2).csv dengan 169 baris. Tidak ada baris '
            'observasi yang ditambahkan, tidak ada label yang diubah, dan tidak ada '
            'nilai sumber yang dimodifikasi untuk memperbaiki skor.')
    lap.par('Seluruh angka evaluasi, confusion matrix, threshold, riwayat trial '
            'Optuna, dan grafik berasal dari kode yang disertakan dan benar-benar '
            'dijalankan. Angka historis Tugas 05 hanya dipakai untuk memeriksa '
            'konsistensi dan diberi label sebagai angka historis. Angka hasil Tugas '
            '06 dihitung ulang dari model yang dilatih pada train Tugas 06.')
    lap.par('Kami memahami bahwa model ini belum layak dipakai untuk keputusan '
            'otomatis. Laporan menyajikan keterbatasan, kasus yang terlewat, beban '
            'alarm, dan ketidakpastian sampel secara terbuka. Model diposisikan '
            'sebagai alat bantu penelitian dan penyaringan awal, bukan pengganti '
            'pemeriksaan staf atau kewenangan Notaris/PPAT.')
    lap.par('Pengembangan kode dan penyuntingan naskah memakai bantuan AI. Kelompok '
            'bertanggung jawab memeriksa ulang isi, memahami metode, dan mengesahkan '
            'laporan sebelum dikumpulkan. Tanda tangan basah belum dibubuhkan pada '
            'berkas ini dan akan diisi sebelum unggah.')
    lap.tabel(
        ['Peran', 'Nama Lengkap', 'NIM', 'Tanda Tangan'],
        [['Ketua Tim', 'Muhammad Rizqi Saputra', '12250158',
          '( ______________________________ )'],
         ['Anggota 1', 'Dian Nur Cahya', '12250162',
          '( ______________________________ )'],
         ['Anggota 2', 'Dicky Handia', '12250161',
          '( ______________________________ )']],
        widths=[1.0, 2.0, 1.0, 2.4], font=9,
        aligns=['l', 'l', 'c', 'c'],
        caption='Tabel 24. Lembar komitmen dan tanda tangan anggota Kelompok 02.')
    lap.par('', space_after=8)
    lap.par('Jakarta, 5 November 2026', rata='left', space_after=4)
    lap.par('Mengetahui Koordinator Tim,', rata='left', space_after=36)
    lap.par('Muhammad Rizqi Saputra  —  NIM 12250158', bold=True, rata='left')

    # ==================================================================
    # REFERENSI
    # ==================================================================
    lap.halaman_putus()
    lap.h1('REFERENSI')
    referensi = [
        'Kelompok 02, “Tugas 04 Pembelajaran Mesin: Hyperparameter Tuning, Feature '
        'Importance, dan Model Explainability,” Universitas Nusa Mandiri, Jakarta, '
        '2026.',
        'Kelompok 02, “Tugas 05 Pembelajaran Mesin: Serialisasi Model Terbaik dan '
        'Prototipe Inferensi Berkas Notaris,” Universitas Nusa Mandiri, Jakarta, '
        '2026.',
        'I. Saputra, “Panduan Penugasan Minggu 06: Evaluasi Kinerja Model, '
        'Kalibrasi Ambang Batas, Optimasi Hiperparameter, dan Integrasi Proposal '
        'UTS,” Universitas Nusa Mandiri, 2026.',
        'T. Saito and M. Rehmsmeier, “The precision-recall plot is more informative '
        'than the ROC plot when evaluating binary classifiers on imbalanced '
        'datasets,” PLoS ONE, vol. 10, no. 3, e0118432, 2015, doi: '
        '10.1371/journal.pone.0118432.',
        'T. Akiba, S. Sano, T. Yanase, T. Ohta, and M. Koyama, “Optuna: A '
        'next-generation hyperparameter optimization framework,” in Proc. 25th ACM '
        'SIGKDD Int. Conf. Knowledge Discovery & Data Mining, Anchorage, AK, USA, '
        '2019, pp. 2623–2631, doi: 10.1145/3292500.3330701.',
        'H. He and E. A. Garcia, “Learning from imbalanced data,” IEEE Trans. '
        'Knowledge and Data Engineering, vol. 21, no. 9, pp. 1263–1284, 2009, doi: '
        '10.1109/TKDE.2008.239.',
        'T. Fawcett, “An introduction to ROC analysis,” Pattern Recognition '
        'Letters, vol. 27, no. 8, pp. 861–874, 2006, doi: '
        '10.1016/j.patrec.2005.10.010.',
        'F. Pedregosa et al., “Scikit-learn: Machine learning in Python,” Journal '
        'of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.',
        'L. Breiman, J. H. Friedman, R. A. Olshen, and C. J. Stone, Classification '
        'and Regression Trees. Belmont, CA, USA: Wadsworth, 1984.',
        'Optuna, “Optuna: A hyperparameter optimization framework — documentation.” '
        '[Online]. Available: https://optuna.readthedocs.io/. [Accessed: Nov. 5, '
        '2026].',
        'Scikit-learn, “Tuning the decision threshold for class prediction.” '
        '[Online]. Available: https://scikit-learn.org/stable/modules/'
        'classification_threshold.html. [Accessed: Nov. 5, 2026].',
        'Scikit-learn, “Precision-Recall — metrics and scoring.” [Online]. '
        'Available: https://scikit-learn.org/stable/modules/model_evaluation.html. '
        '[Accessed: Nov. 5, 2026].',
    ]
    for i, teks in enumerate(referensi, 1):
        lap.nomor(f'[{i}]', teks, space_after=4)
    lap.par('Dokumentasi daring diakses 5 November 2026. Dataset: '
            'berkas_notaris_terisi (2).csv, 169 baris.', italic=True, ukuran=9)

    # ==================================================================
    # LAMPIRAN
    # ==================================================================
    lap.halaman_putus()
    lap.h1('LAMPIRAN')

    lap.h2('Lampiran A. Daftar berkas keluaran')
    lap.tabel(
        ['Berkas atau folder', 'Isi'],
        [['TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.docx', 'Laporan Word final'],
         ['TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.pdf', 'Laporan PDF final'],
         ['README_TUGAS_06.md', 'Ringkasan, hasil kunci, dan cara menjalankan'],
         ['AUDIT_FILE_PROYEK_TUGAS_06.md', 'Audit berkas dan konsistensi data'],
         ['eksperimen_tugas_06/eksperimen_tugas06.py', 'Skrip eksperimen utama'],
         ['eksperimen_tugas_06/fitur_notaris.py', 'Transformer fitur'],
         ['eksperimen_tugas_06/hasil/data/', 'Metrik, prediksi, threshold, error '
          'analysis, bootstrap, audit'],
         ['eksperimen_tugas_06/hasil/optuna/', 'Riwayat 30 trial dan parameter '
          'terbaik'],
         ['eksperimen_tugas_06/hasil/grafik/', 'Delapan grafik hasil eksekusi dan '
          'satu tangkapan layar prototipe'],
         ['eksperimen_tugas_06/hasil/model/', 'Model baseline dan tuned (.joblib)'],
         ['eksperimen_tugas_06/hasil/log/', 'Log eksekusi dan versi lingkungan'],
         ['requirements_tugas_06.txt', 'Daftar pustaka Python dan versinya']],
        widths=[2.8, 3.6], font=8.5, aligns=['l', 'l'],
        caption='Tabel 25. Berkas keluaran Tugas 06.')

    lap.halaman_putus()
    lap.h2('Lampiran B. Tangkapan layar prototipe Tugas 05')
    lap.par('Gambar 9 adalah tangkapan layar antarmuka prototipe yang dibangun '
            'pada Tugas 05 dan diwarisi sebagai artefak penelitian ini. Layar '
            'menampilkan formulir data penerimaan berkas, skor risiko, ambang '
            'pemeriksaan, dan kontribusi fitur. Tangkapan layar dibuat dari '
            'aplikasi yang benar-benar berjalan pada 5 November 2026.')
    lap.gambar(fig / '09_prototipe_tugas05.png', 6.25,
               'Gambar 9. Antarmuka prototipe Tugas 05: formulir penerimaan dan '
               'hasil pemeriksaan risiko. Ambang pada layar masih 0,11, yaitu '
               'ambang historis Tugas 05; rekomendasi Tugas 06 adalah 0,05 '
               '(optimum F2) atau 0,19 (operasional).')
    lap.par('Layar ini ditampilkan sebagai bukti artefak antarmuka, bukan sebagai '
            'hasil evaluasi Tugas 06. Angka pada layar berasal dari model Tugas 05 '
            'dan tidak dipakai untuk menghitung metrik Tugas 06. Model serialisasi '
            'Tugas 06 tersedia pada eksperimen_tugas_06/hasil/model/ dalam format '
            '.joblib dan telah diuji paritas prediksinya.')
    lap.par('Repositori Git lokal sudah diinisialisasi dan seluruh kode serta '
            'artefak sudah di-commit. Tautan repositori publik GitHub/Google Colab '
            'belum tersedia karena akun kelompok belum dihubungkan saat laporan '
            'disusun. Folder proyek siap diunggah; kelompok perlu membuat repositori '
            'publik dan menambahkan tautannya sebelum unggah agar komponen '
            'repositori terpenuhi.', italic=True)

    lap.h2('Lampiran C. Cara menjalankan ulang')
    lap.par('Dari folder proyek, jalankan perintah berikut. Virtualenv sudah berisi '
            'pustaka yang dipakai. Jika dibuat ulang, pasang numpy, pandas, '
            'scikit-learn, matplotlib, optuna, joblib, python-docx, scipy, dan '
            'openpyxl.')
    lap.kode(
        "cd /Users/admin/PEMBELAJARAN_MESIN_KELOMPOK_02\n"
        "cd eksperimen_tugas_06\n"
        "../.venv/bin/python eksperimen_tugas06.py --trials 30\n"
        "\n"
        "# Menyusun ulang laporan Word dari hasil yang sama\n"
        "cd ../laporan_tugas_06\n"
        "../.venv/bin/python buat_laporan.py")
    lap.par('Eksperimen memerlukan waktu kurang dari satu menit pada mesin ini. '
            'Hasil akan menimpa folder hasil dengan angka yang sama bila seed dan '
            'versi pustaka tidak berubah. Versi pustaka yang dipakai: Python 3.12.0, '
            'numpy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1, optuna 5.0.0, dan '
            'matplotlib 3.11.2.')

    lap.h2('Lampiran D. Sepuluh trial terbaik Optuna')
    top = trials.sort_values('value', ascending=False).head(10)
    baris = []
    for _, r in top.iterrows():
        baris.append([n(r['number']), f(r['value']), r['params_criterion'],
                      n(r['params_max_depth']), n(r['params_min_samples_leaf']),
                      n(r['params_min_samples_split']), f(r['params_ccp_alpha'], 4),
                      r['params_class_weight'], r['params_max_features']])
    lap.tabel(
        ['Trial', 'Macro F1', 'Criterion', 'Depth', 'Leaf', 'Split', 'ccp_alpha',
         'Class weight', 'Max features'],
        baris, widths=[0.5, 0.7, 0.7, 0.5, 0.5, 0.5, 0.7, 0.9, 0.8], font=7.5,
        aligns=['c'] * 9,
        caption='Tabel 26. Sepuluh trial dengan Macro F1 CV tertinggi. Riwayat '
                'lengkap ada pada hasil/optuna/riwayat_trial.csv.')

    lap.h2('Lampiran E. Pemetaan rubrik penilaian')
    lap.tabel(
        ['Komponen rubrik', 'Bobot', 'Bukti pada laporan', 'Lokasi'],
        [['Evaluasi & diagnosis', '25%', 'Classification report, confusion matrix, '
          'ROC/PR, analisis FP/FN, paradoks akurasi', 'Bagian B; Tabel 6–11; '
          'Gambar 1–3'],
         ['Threshold tuning', '25%', 'OOF, empat ambang, tabel TP/TN/FP/FN, '
          'justifikasi F2, rekomendasi operasional', 'Bagian C; Tabel 12–13; '
          'Gambar 4'],
         ['Optuna & 5-Fold', '25%', '30 trial TPE, ruang pencarian, riwayat, '
          'kepentingan parameter, CV before/after, test', 'Bagian D; Tabel 14–18; '
          'Gambar 5–8'],
         ['Sintesis & repositori', '25%', 'Bab I–III, dua paper, pemetaan tugas, '
          'komitmen, daftar berkas, tangkapan layar prototipe, model .joblib',
          'Bagian E–F; Tabel 19–25, 27; Gambar 9']],
        widths=[1.3, 0.55, 2.7, 1.85], font=8,
        aligns=['l', 'c', 'l', 'l'],
        caption='Tabel 27. Pemetaan bukti terhadap komponen rubrik Tugas 06.')

    lap.h2('Lampiran F. Catatan penggunaan bantuan AI')
    lap.par('Bantuan AI dipakai untuk menyusun kerangka kode, memeriksa konsistensi '
            'tabel, dan menyunting bahasa. Seluruh keputusan metodologis, pemilihan '
            'metrik, penafsiran hasil, dan tanggung jawab akademik tetap berada pada '
            'kelompok. Angka pada laporan dihasilkan oleh skrip yang disertakan, '
            'bukan oleh model bahasa. Kelompok wajib membaca ulang, memahami, dan '
            'memverifikasi hasil sebelum menandatangani Bagian F.')
