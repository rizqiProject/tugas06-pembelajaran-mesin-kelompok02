"""Bagian judul, ringkasan eksekutif, A, dan B."""
from __future__ import annotations

from docx.shared import Pt

from laporan_lib import f, n, pct


def _catatan_fp(selisih):
    if selisih == 0:
        return 'Tepat pada SLA'
    if selisih >= -2:
        return 'Sangat dekat SLA'
    if selisih >= -4:
        return 'Dekat SLA'
    return 'Masih jauh dari SLA'


def tulis(lap, D):
    met = D['met']
    rep = D['rep']
    boot = D['boot']
    hist = D['hist']
    audit = D['audit']
    split = D['split']
    naif = D['naif']
    fp = D['fp']
    fn = D['fn']
    fig = D['fig']

    # ==================================================================
    # HALAMAN JUDUL
    # ==================================================================
    lap.par('', space_after=24)
    lap.judul('LAPORAN PENUGASAN MINGGU 06', 20, space_after=4)
    lap.judul('PEMBELAJARAN MESIN', 18, space_after=10)
    lap.subjudul('Evaluasi Kinerja Model, Kalibrasi Ambang Batas, Optimasi Hiperparameter, '
                 'dan Integrasi Proposal UTS (Bab I–III)', 12, italic=True, space_after=18)
    lap.par('Prediksi Keterlambatan Penyelesaian Berkas pada Kantor Notaris & PPAT '
            'Aries Buwana Menggunakan Machine Learning', bold=True, rata='center',
            ukuran=12, space_after=24)

    lap.par('Disusun oleh:', rata='center', space_after=4)
    for nama, nim in [('Muhammad Rizqi Saputra', '12250158'),
                      ('Dian Nur Cahya', '12250162'),
                      ('Dicky Handia', '12250161')]:
        lap.par(f'{nama}  —  {nim}', rata='center', space_after=2)

    lap.par('', space_after=18)
    lap.par('Kelompok 02  |  Kelas KG.043.10.A  |  S1, 3 SKS', rata='center',
            space_after=2)
    lap.par('Semester Gasal 2026/2027', rata='center', space_after=2)
    lap.par('Universitas Nusa Mandiri', rata='center', space_after=18)
    lap.par('Dosen Pengampu: Dr. Irwansyah Saputra, M.Kom. (NIP 201909149)',
            rata='center', space_after=18)
    lap.par('Jakarta, 5 November 2026', rata='center', space_after=0)
    lap.halaman_putus()

    # ==================================================================
    # RINGKASAN EKSEKUTIF
    # ==================================================================
    lap.h1('RINGKASAN EKSEKUTIF')
    lap.par('Laporan ini melanjutkan penelitian Tugas 04 dan Tugas 05 pada Kantor '
            'Notaris & PPAT Aries Buwana. Dataset tetap 169 berkas: 33 berkas '
            'terlambat dan 136 berkas tepat waktu. Pembagian data juga tetap 135 '
            'berkas latih dan 34 berkas uji. Tidak ada perubahan label, nilai '
            'sumber, atau penambahan data untuk memperbaiki hasil.')
    lap.par('Tugas 06 menambahkan empat hal yang belum dikerjakan pada tugas '
            'sebelumnya: evaluasi metrik secara lengkap, pemilihan ambang keputusan '
            'dari prediksi out-of-fold (OOF) pada data latih, optimasi '
            'hiperparameter dengan Optuna dan Stratified 5-Fold Cross Validation, '
            'serta sintesis proposal Bab I–III. Seluruh angka dalam laporan berasal '
            'dari eksekusi kode yang disertakan.')
    lap.par('Temuan utamanya sebagai berikut.', bold=True, space_after=4)
    for teks in [
        'Pada ambang 0,50, model tidak menemukan satu pun dari tujuh berkas '
        'terlambat. Akurasi 79,4% hanya mencerminkan dominasi kelas tepat waktu.',
        'Ambang optimal F2 dari OOF train adalah 0,05. Pada data uji, ambang ini '
        'menghasilkan TP 5, FN 2, FP 19, dan TN 8; precision 0,208, recall 0,714, '
        'F1 0,323, dan F2 0,481.',
        'Optuna meningkatkan Macro F1 validasi silang dari 0,447 menjadi 0,553 dan '
        'PR-AUC dari 0,231 menjadi 0,331. Pada data uji, F1 positif naik dari '
        '0,276 menjadi 0,323 dan recall dari 0,571 menjadi 0,714, tetapi PR-AUC '
        'sedikit turun dari 0,196 menjadi 0,190.',
        'ROC-AUC data uji sebesar 0,413 dan PR-AUC 0,190. Keduanya menunjukkan daya '
        'pisah model masih lemah. Threshold tuning hanya menggeser titik potong; '
        'ia tidak memperbaiki peringkat skor.',
        'Secara operasional, ambang 0,05 menandai 24 dari 34 berkas. Jika kapasitas '
        'pemeriksaan staf terbatas, ambang 0,19 atau 0,25 lebih realistis, dengan '
        'konsekuensi recall yang lebih rendah.',
    ]:
        lap.bullet(teks)
    lap.par('Kesimpulan teknisnya: model belum layak dipakai untuk keputusan '
            'otomatis. Model dapat dipakai sebagai alat bantu penyaringan dengan '
            'pemeriksaan staf, asalkan beban alarm dan kasus yang terlewat '
            'dipantau. Validasi pada periode baru tetap diperlukan.')
    lap.halaman_putus()

    # ==================================================================
    # A. IDENTITAS
    # ==================================================================
    lap.h1('A. IDENTITAS KELOMPOK & KONFIRMASI MODEL BASELINE (TUGAS 04–05)')
    lap.par('Penelitian ini menggunakan objek yang sama dengan Tugas 04 dan Tugas '
            '05, yaitu Kantor Notaris & PPAT Aries Buwana, Jakarta Barat. Fokus '
            'masalahnya adalah keterlambatan penyelesaian berkas terhadap batas '
            'waktu layanan (SLA) yang tercatat pada dataset. Model dasar yang '
            'diwarisi adalah Decision Tree dengan kedalaman 4 dan minimal 15 '
            'sampel per daun.')

    lap.tabel(
        ['No', 'NIM', 'Nama Mahasiswa', 'Peran / Pembagian Tugas Teknis'],
        [['1', '12250158', 'Muhammad Rizqi Saputra',
          'Koordinator tim, integrasi laporan, pemeriksaan akhir, dan penyusunan Bab I'],
         ['2', '12250162', 'Dian Nur Cahya',
          'Audit data, pipeline preprocessing, evaluasi confusion matrix, analisis kesalahan, dan Bab II'],
         ['3', '12250161', 'Dicky Handia',
          'Optuna, Stratified 5-Fold CV, threshold tuning, grafik, dan Bab III']],
        widths=[0.4, 1.0, 2.0, 3.0], font=8.5,
        aligns=['c', 'c', 'l', 'l'],
        caption='Tabel 1. Identitas anggota Kelompok 02 dan pembagian tugas Tugas 06.')

    lap.tabel(
        ['Komponen', 'Data'],
        [['Objek penelitian', 'Kantor Notaris & PPAT Aries Buwana, Jakarta Barat'],
         ['Judul/topik', 'Prediksi Keterlambatan Penyelesaian Berkas pada Kantor '
          'Notaris & PPAT Aries Buwana Menggunakan Machine Learning'],
         ['Dataset', 'berkas_notaris_terisi (2).csv; 169 baris; 10 kolom'],
         ['Target', 'terlambat = 1 bila (tgl_selesai − tgl_masuk) hari > sla_hari'],
         ['Model baseline', 'DecisionTreeClassifier(max_depth=4, min_samples_leaf=15, '
          'min_samples_split=2, ccp_alpha=0, class_weight=None, random_state=42)'],
         ['Pembagian data', '135 train (26 terlambat) dan 34 test (7 terlambat); '
          'stratified 80:20; random_state=42'],
         ['Threshold historis', '0,11 dari OOF train Tugas 04']],
        widths=[1.9, 4.5], font=9, aligns=['l', 'l'],
        caption='Tabel 2. Konfirmasi objek, dataset, dan model baseline.')

    lap.par('Dataset yang dipakai adalah versi yang menyertai Tugas 05. Versi ini '
            'memuat 33 berkas terlambat dari 169 berkas. Dataset Tugas 04 versi v5 '
            'memuat 35 berkas terlambat karena komposisinya berbeda. Tugas 06 tidak '
            'mencampur kedua versi. Seluruh angka pada laporan ini mengacu pada '
            'dataset Tugas 05 agar model, split, dan hasil historis dapat '
            'dibandingkan secara adil.')

    lap.tabel(
        ['Pemeriksaan', 'Hasil'],
        [['Jumlah baris', f'{audit["n_baris"]} berkas'],
         ['Jumlah kolom', f'{audit["n_kolom"]} kolom (10 sumber + 2 turunan label)'],
         ['Kelas terlambat', f'{audit["positif_terlambat"]} berkas '
          f'({pct(audit["proporsi_positif"])})'],
         ['Kelas tepat waktu', f'{audit["negatif_tepat_waktu"]} berkas '
          f'({pct(1 - audit["proporsi_positif"])})'],
         ['Duplikasi id_berkas', f'{audit["duplikat_id"]}'],
         ['Tanggal RUPS terisi', f'{audit["tanggal_rups_terisi"]} berkas'],
         ['Rentang tanggal masuk', '18 April 2024 – 2 Oktober 2026'],
         ['Rentang SLA', f'{audit["sla_min"]}–{audit["sla_maks"]} hari'],
         ['Rentang jumlah penghadap', '1–14 orang'],
         ['Rumus label', 'selisih hari kalender tgl_selesai − tgl_masuk > sla_hari']],
        widths=[2.1, 4.3], font=8.5, aligns=['l', 'l'],
        caption='Tabel 3. Audit dataset Tugas 06.')

    lap.tabel(
        ['Partisi', 'Jumlah', 'Terlambat', 'Tepat waktu', 'Keterangan'],
        [['Train', str(split['n_train']), str(split['positif_train']),
          str(split['n_train'] - split['positif_train']),
          'Untuk pemilihan parameter dan threshold'],
         ['Test', str(split['n_test']), str(split['positif_test']),
          str(split['n_test'] - split['positif_test']),
          'Hanya untuk evaluasi setelah keputusan dikunci']],
        widths=[1.1, 0.9, 1.0, 1.1, 2.3], font=9,
        aligns=['l', 'c', 'c', 'c', 'l'],
        caption='Tabel 4. Pembagian data Tugas 06.')

    lap.par('Pembagian data menghasilkan daftar ID test yang sama persis dengan '
            'prediksi Tugas 04, termasuk urutannya. Model Tugas 05 juga dimuat '
            'ulang dan diuji pada 34 berkas yang sama. Hasilnya mengembalikan '
            'TP 4, FN 3, FP 18, dan TN 9 pada ambang 0,11. Angka itu sama dengan '
            'laporan Tugas 05, sehingga dapat dipastikan dataset, split, dan '
            'pipeline yang diwarisi tidak berubah.')

    lap.tabel(
        ['Metrik pada ambang 0,11', 'Nilai', 'Catatan'],
        [['TP', str(hist.get('tp', '')), 'Terlambat dan terdeteksi'],
         ['FN', str(hist.get('fn', '')), 'Terlambat tetapi tidak terdeteksi'],
         ['FP', str(hist.get('fp', '')), 'Tepat waktu tetapi menjadi alarm'],
         ['TN', str(hist.get('tn', '')), 'Tepat waktu dan tidak menjadi alarm'],
         ['Precision', f(hist.get('precision', 0)), 'Kualitas alarm positif'],
         ['Recall', f(hist.get('recall', 0)), 'Kemampuan menemukan keterlambatan'],
         ['F1 positif', f(hist.get('f1', 0)), 'Keseimbangan precision dan recall']],
        widths=[2.2, 1.1, 3.1], font=9, aligns=['l', 'c', 'l'],
        caption='Tabel 5. Reproduksi hasil historis Tugas 05 pada data uji yang sama.')

    lap.par('Angka pada Tabel 5 bukan hasil Tugas 06. Angka tersebut hanya dipakai '
            'sebagai pemeriksaan konsistensi. Seluruh metrik Tugas 06 dihitung '
            'ulang dari model yang dilatih pada train Tugas 06 dengan pipeline yang '
            'sama.', italic=True)

    # ==================================================================
    # B. EVALUASI
    # ==================================================================
    lap.halaman_putus()
    lap.h1('B. MATRIKS EVALUASI KINERJA LENGKAP & CONFUSION MATRIX')

    lap.h2('B.1 Definisi metrik dan konteks keputusan')
    lap.par('Kelas positif adalah berkas terlambat (y = 1). Kelas negatif adalah '
            'berkas tepat waktu (y = 0). Model menghasilkan skor probabilitas, lalu '
            'berkas dianggap positif bila skornya lebih besar atau sama dengan '
            'ambang keputusan. Empat sel confusion matrix didefinisikan sebagai '
            'berikut: TP adalah berkas terlambat yang benar menjadi alarm; FN '
            'adalah berkas terlambat yang lolos tanpa alarm; FP adalah berkas tepat '
            'waktu yang menjadi alarm; TN adalah berkas tepat waktu yang tidak '
            'menjadi alarm.')
    lap.par('Precision mengukur seberapa tepat alarm yang diberikan. Recall '
            'mengukur seberapa banyak keterlambatan yang berhasil ditemukan. F1 '
            'menyeimbangkan keduanya. F2 memberi bobot lebih besar pada recall. '
            'Macro F1 merata-ratakan F1 setiap kelas tanpa memedulikan jumlah '
            'sampel, sedangkan weighted F1 membobotnya dengan jumlah sampel.')
    lap.rumus('Precision = TP / (TP + FP)')
    lap.rumus('Recall = TP / (TP + FN)')
    lap.rumus('F1 = 2 × (Precision × Recall) / (Precision + Recall)')
    lap.rumus('F2 = 5 × (Precision × Recall) / (4 × Precision + Recall)')
    lap.par('ROC-AUC mengukur kemampuan model mengurutkan berkas positif di atas '
            'berkas negatif pada seluruh ambang. PR-AUC di sini dihitung dengan '
            'average precision (AP), yaitu rata-rata precision pada setiap titik '
            'recall, bukan luas trapesium kurva precision–recall. Perbedaan '
            'definisi ini penting karena keduanya dapat menghasilkan angka yang '
            'berbeda. Log-loss mengukur kualitas probabilitas; nilainya makin '
            'kecil makin baik.')
    lap.par('Konteks keputusannya adalah penyaringan berkas di kantor notaris. '
            'Berkas yang ditandai akan diperiksa lebih awal oleh staf. False '
            'negative berarti berkas terlambat tidak masuk prioritas pemeriksaan. '
            'False positive berarti staf memeriksa berkas yang sebenarnya akan '
            'selesai tepat waktu. Karena keputusan akhir tetap di tangan staf dan '
            'Notaris/PPAT, biaya FN dan FP di sini bersifat operasional, bukan '
            'otomatis finansial.')

    lap.h2('B.2 Classification report pada ambang terpilih')
    lap.par(f'Evaluasi utama memakai ambang {f(met["threshold"], 2)} yang dipilih '
            'dari prediksi OOF train dengan F2 maksimum. Ambang ini dikunci '
            'sebelum data uji dibaca. Pada 34 berkas uji, model menandai '
            f'{n(met["alarm"])} berkas. Dari jumlah itu, {met["tp"]} benar '
            f'terlambat dan {met["fp"]} tepat waktu. Dua berkas terlambat tidak '
            'terdeteksi.')
    lap.tabel(
        ['Kelas / Label', 'Precision', 'Recall', 'F1-Score', 'Support'],
        [['Tepat Waktu (0)', f(rep['Tepat Waktu']['precision']),
          f(rep['Tepat Waktu']['recall']), f(rep['Tepat Waktu']['f1-score']),
          n(rep['Tepat Waktu']['support'])],
         ['Terlambat (1)', f(rep['Terlambat']['precision']),
          f(rep['Terlambat']['recall']), f(rep['Terlambat']['f1-score']),
          n(rep['Terlambat']['support'])],
         ['Accuracy', '–', '–', f(rep['accuracy']), n(34)],
         ['Macro Average', f(rep['macro avg']['precision']),
          f(rep['macro avg']['recall']), f(rep['macro avg']['f1-score']), n(34)],
         ['Weighted Average', f(rep['weighted avg']['precision']),
          f(rep['weighted avg']['recall']), f(rep['weighted avg']['f1-score']), n(34)]],
        widths=[2.0, 1.1, 1.0, 1.1, 1.0], font=9,
        aligns=['l', 'c', 'c', 'c', 'c'],
        caption='Tabel 6. Classification report model After Tuning pada data uji, '
                f'ambang {f(met["threshold"], 2)}.')

    lap.tabel(
        ['Metrik agregat', 'Nilai', 'Interpretasi singkat'],
        [['Accuracy', f(met['accuracy']), 'Rendah karena banyak alarm palsu'],
         ['Precision (Terlambat)', f(met['precision']), 'Sekitar satu dari lima alarm benar'],
         ['Recall (Terlambat)', f(met['recall']), 'Lima dari tujuh keterlambatan tertangkap'],
         ['F1 (Terlambat)', f(met['f1']), 'Keseimbangan precision dan recall'],
         ['F2 (Terlambat)', f(met['f2']), 'Metrik pemilihan ambang'],
         ['Macro F1', f(met['macro_f1']), 'Rata-rata setara antar kelas'],
         ['Weighted F1', f(met['weighted_f1']), 'Dipengaruhi dominasi kelas negatif'],
         ['ROC-AUC', f(met['roc_auc']), 'Di bawah 0,5 pada data uji ini'],
         ['PR-AUC (Average Precision)', f(met['average_precision']),
          'Sedikit di bawah prevalensi 0,206'],
         ['Log-loss', f(met['log_loss']), 'Probabilitas belum terkalibrasi'],
         ['Alarm', f'{n(met["alarm"])} dari 34 ({pct(met["alert_rate"])})',
          'Beban pemeriksaan tambahan']],
        widths=[2.1, 1.8, 2.5], font=8.5, aligns=['l', 'c', 'l'],
        caption='Tabel 7. Metrik agregat model After Tuning pada ambang terpilih.')

    lap.par('Macro F1 0,378 dan weighted F1 0,410 berbeda karena weighted F1 '
            'didominasi 27 berkas tepat waktu. Macro F1 lebih jujur untuk menilai '
            'keseimbangan antar kelas pada data yang tidak seimbang. Keduanya tetap '
            'perlu dibaca bersama precision dan recall kelas terlambat, karena '
            'macro F1 dapat terlihat wajar walaupun kelas minoritas tetap lemah.')
    lap.tabel(
        ['Metrik', 'Rata-rata bootstrap', '95% CI bawah', '95% CI atas'],
        [[k, f(v['mean']), f(v['low']), f(v['high'])]
         for k, v in [('F1', boot['f1']), ('Recall', boot['recall']),
                      ('Precision', boot['precision']), ('F2', boot['f2']),
                      ('PR-AUC (AP)', boot['average_precision']),
                      ('ROC-AUC', boot['roc_auc'])]],
        widths=[1.7, 1.5, 1.3, 1.3], font=9,
        aligns=['l', 'c', 'c', 'c'],
        caption='Tabel 8. Interval bootstrap 95% (2.000 ulangan terstratifikasi) '
                'pada data uji.')

    lap.par('Interval bootstrap lebar. Recall berkisar 0,429 sampai 1,000, sedangkan '
            'F1 berkisar 0,188 sampai 0,452. Lebar ini muncul karena hanya ada tujuh '
            'berkas terlambat di data uji. Satu perubahan prediksi dapat menggeser '
            'recall sekitar 14,3 poin persentase. Karena itu angka titik pada Tabel '
            '6–7 tidak boleh dibaca sebagai estimasi yang presisi.')

    lap.h2('B.3 Confusion matrix dan makna operasional')
    lap.gambar(fig / '01_confusion_matrix_tuned.png', 4.9,
               f'Gambar 1. Confusion matrix model After Tuning pada ambang '
               f'{f(met["threshold"], 2)} (TP {met["tp"]}, FN {met["fn"]}, '
               f'FP {met["fp"]}, TN {met["tn"]}).')
    lap.par(f'Confusion matrix menunjukkan {met["tp"]} berkas terlambat tertangkap '
            f'dan {met["fn"]} berkas terlambat terlewat. Di sisi lain, '
            f'{met["fp"]} berkas tepat waktu ikut menjadi alarm, sedangkan '
            f'{met["tn"]} berkas tepat waktu tidak menjadi alarm. Dengan demikian '
            f'staf akan menerima {n(met["alarm"])} alarm dari 34 berkas, dan hanya '
            f'{met["tp"]} di antaranya yang benar-benar terlambat.')
    lap.par('Angka ini menunjukkan bahwa model belum bisa dipakai untuk memutuskan '
            'prioritas secara otomatis. Model masih berguna sebagai penyaring awal '
            'bila staf memang punya kapasitas memeriksa sekitar dua pertiga berkas. '
            'Jika kapasitas lebih kecil, ambang harus dinaikkan dan sebagian '
            'keterlambatan akan terlewat. Keputusan itu bersifat kebijakan '
            'operasional, bukan keputusan statistik semata.')

    lap.h2('B.4 ROC-AUC dan PR-AUC')
    lap.par(f'ROC-AUC pada data uji adalah {f(met["roc_auc"])}. Nilai di bawah 0,5 '
            'berarti, pada partisi ini, urutan skor model sedikit lebih buruk '
            'daripada urutan acak. PR-AUC (AP) sebesar '
            f'{f(met["average_precision"])} juga berada sedikit di bawah prevalensi '
            'kelas terlambat, yaitu 0,206. Artinya, berkas dengan skor tertinggi '
            'belum tentu lebih banyak berisi keterlambatan.')
    lap.gambar(fig / '02_roc_pr.png', 6.25,
               'Gambar 2. Kurva ROC dan Precision–Recall model Before dan After '
               'Tuning pada data uji. Titik merah menandai ambang 0,50, 0,25, dan '
               '0,05 untuk model After Tuning.')
    lap.par('Kurva ROC dan PR dihitung dari skor yang sama untuk semua ambang. '
            'Mengubah ambang tidak mengubah ROC-AUC atau PR-AUC; yang berubah '
            'hanya titik potong dan confusion matrix. Karena itu kenaikan F1 setelah '
            'threshold tuning bukan bukti bahwa model menjadi lebih pintar '
            'memisahkan kelas. Ia hanya bukti bahwa titik operasi digeser ke arah '
            'yang lebih sesuai dengan tujuan recall.')
    lap.par('Nilai ROC-AUC yang rendah juga perlu dibaca bersama hasil validasi '
            'silang. Pada CV train, ROC-AUC model After Tuning adalah 0,554 ± 0,208, '
            'sedikit di atas acak. Pada data uji, nilainya 0,413. Perbedaan arah ini '
            'menunjukkan ketidakstabilan pada sampel kecil. Klaim generalisasi tidak '
            'boleh dibuat dari salah satu angka saja.')

    lap.h2('B.5 Analisis kesalahan: false positive dan false negative')
    lap.par(f'Pada ambang {f(met["threshold"], 2)}, terdapat {len(fp)} false '
            f'positive dan {len(fn)} false negative. Tabel 9 dan Tabel 10 memuat '
            'seluruh kasus, bukan hanya contoh. Kolom selisih hari dihitung sebagai '
            'durasi aktual dikurangi SLA. Nilai negatif berarti berkas selesai '
            'sebelum SLA; nilai nol berarti tepat pada SLA; nilai positif berarti '
            'terlambat.')
    baris_fp = []
    for _, r in fp.iterrows():
        baris_fp.append([r['id_berkas'], r['kategori_akta'], n(r['sla_hari']),
                         n(r['durasi_hari']), f"{int(r['selisih_hari']):+d}",
                         f(r['p_tuned']), _catatan_fp(int(r['selisih_hari']))])
    lap.tabel(
        ['ID', 'Kategori', 'SLA', 'Durasi', 'Selisih', 'Skor', 'Catatan'],
        baris_fp, widths=[0.95, 1.35, 0.5, 0.6, 0.6, 0.6, 1.6], font=8,
        aligns=['l', 'l', 'c', 'c', 'c', 'c', 'l'],
        caption='Tabel 9. Seluruh false positive pada ambang terpilih (19 berkas).')

    baris_fn = []
    for _, r in fn.iterrows():
        baris_fn.append([r['id_berkas'], r['kategori_akta'], n(r['sla_hari']),
                         n(r['durasi_hari']), f"{int(r['selisih_hari']):+d}",
                         f(r['p_tuned']), f"Terlambat {int(r['selisih_hari'])} hari"])
    lap.tabel(
        ['ID', 'Kategori', 'SLA', 'Durasi', 'Selisih', 'Skor', 'Catatan'],
        baris_fn, widths=[0.95, 1.35, 0.5, 0.6, 0.6, 0.6, 1.6], font=8,
        aligns=['l', 'l', 'c', 'c', 'c', 'c', 'l'],
        caption='Tabel 10. Seluruh false negative pada ambang terpilih (2 berkas).')

    lap.gambar(fig / '08_test_scores.png', 6.2,
               'Gambar 3. Sebaran skor model After Tuning pada 34 berkas uji. '
               'Skor kelas terlambat dan tepat waktu saling bertumpuk.')
    lap.par('Pola false positive cukup jelas. Sebanyak 12 dari 19 alarm palsu '
            'berkategori PKR_PT. Tiga alarm palsu berkategori PPJB dan semuanya '
            'selesai dua hari sebelum SLA. Dua alarm palsu berkategori '
            'Waris_Wasiat dan selesai enam hari sebelum SLA. Sebelas dari 19 alarm '
            'palsu selesai paling lambat empat hari sebelum SLA atau tepat pada '
            'SLA. Dengan kata lain, sebagian besar alarm palsu berada dekat batas '
            'waktu, bukan berkas yang masih jauh dari tenggat.')
    lap.par('Kedekatan dengan SLA membuat sebagian alarm palsu masih masuk akal '
            'untuk diperiksa. Namun, jumlahnya tetap membebani staf. Model juga '
            'cenderung memberi skor tinggi pada PKR_PT karena kategori itu '
            'merupakan kategori terbanyak (66 dari 169 berkas) dan memiliki laju '
            'keterlambatan 21,2%, sedikit di atas laju keseluruhan 19,5%. Model '
            'belum cukup halus untuk membedakan berkas PKR_PT yang benar-benar '
            'berisiko dari yang tidak.')
    lap.par('False negative lebih mengkhawatirkan. BRK_0001 berkategori Kuasa '
            'terlambat 5 hari dengan skor 0,0455. BRK_0075 berkategori PKR_PT '
            'terlambat 4 hari dengan skor 0,0. Skor nol berarti berkas tersebut '
            'berada pada daun yang seluruh contoh latihnya tepat waktu; ambang '
            'positif apa pun tidak akan menangkapnya. Menurunkan ambang ke 0,04 '
            'memang menangkap BRK_0001, tetapi menambah empat alarm palsu dan '
            'menghasilkan TP 6, FN 1, FP 23, TN 4. Angka 0,04 ini hanya ilustrasi '
            'sensitivitas setelah evaluasi, bukan dasar pemilihan ambang.')
    lap.par('Akar kesalahannya bukan semata-mata threshold. Fitur yang tersedia '
            'saat berkas diterima belum mencakup kelengkapan dokumen, instansi '
            'tujuan, kebutuhan pengesahan, beban staf, dan respons klien. Pohon '
            'keputusan juga hanya dapat memotong satu fitur pada satu waktu, '
            'sehingga batas keputusannya berbentuk tangga dan skornya mengumpul '
            'pada beberapa nilai daun. Pada sampel 169 berkas, daun dengan '
            'dukungan kecil mudah menghasilkan skor yang tidak stabil.')

    lap.h2('B.6 Paradoks akurasi')
    lap.par('Tabel 11 membandingkan model dengan dua aturan naif. Aturan pertama '
            'selalu menebak tepat waktu; aturan kedua selalu menebak terlambat. '
            'Keduanya tidak memakai informasi apa pun, tetapi aturan pertama '
            'mencapai akurasi 79,4%. Model pada ambang 0,05 hanya mencapai akurasi '
            '38,2%, lebih rendah daripada aturan naif tersebut.')
    baris_naif = []
    for _, r in naif.iterrows():
        baris_naif.append([r['model'], f(r['accuracy']), f(r['precision']),
                           f(r['recall']), f(r['f1']), n(r['tp']), n(r['fn']),
                           n(r['fp']), n(r['tn'])])
    baris_naif.append(['Model After Tuning @ 0,05', f(met['accuracy']),
                       f(met['precision']), f(met['recall']), f(met['f1']),
                       n(met['tp']), n(met['fn']), n(met['fp']), n(met['tn'])])
    lap.tabel(
        ['Aturan / model', 'Acc', 'Prec', 'Recall', 'F1', 'TP', 'FN', 'FP', 'TN'],
        baris_naif, widths=[1.8, 0.65, 0.65, 0.65, 0.6, 0.45, 0.45, 0.45, 0.45],
        font=8, aligns=['l', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c'],
        caption='Tabel 11. Paradoks akurasi: aturan naif dan model pada data uji.')
    lap.par('Aturan selalu tepat waktu memiliki akurasi tertinggi, tetapi recall '
            '0 dan F1 0. Aturan selalu terlambat memiliki recall 1, tetapi 27 alarm '
            'palsu. Model berada di antara keduanya: recall 0,714 dengan 19 alarm '
            'palsu. Akurasi saja akan memilih aturan yang sama sekali tidak berguna '
            'untuk menemukan keterlambatan. Karena itu evaluasi Tugas 06 memakai '
            'confusion matrix, F1, F2, ROC-AUC, dan PR-AUC secara bersama.')
