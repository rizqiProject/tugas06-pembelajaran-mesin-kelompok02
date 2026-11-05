"""Bagian C (threshold) dan D (Optuna)."""
from __future__ import annotations

from laporan_lib import f, n, pct


def _row(df, t):
    return df.iloc[(df['threshold'] - t).abs().argsort()[:1]].iloc[0]


def tulis(lap, D):
    met = D['met']
    sel = D['sel']
    th = D['th_test']
    oof = D['th_oof']
    ba = D['ba']
    cv = D['cv']
    opt = D['opt']
    fig = D['fig']

    # ==================================================================
    # C. THRESHOLD
    # ==================================================================
    lap.h1('C. KALIBRASI AMBANG BATAS KLASIFIKASI (DECISION THRESHOLD TUNING)')

    lap.h2('C.1 Prosedur pemilihan ambang dari OOF train')
    lap.par('Ambang keputusan tidak dipilih dari data uji. Prosedur yang dipakai '
            'adalah sebagai berikut. Pertama, data dibagi menjadi 135 train dan 34 '
            'test dengan stratifikasi dan random_state 42. Kedua, hanya train yang '
            'dibagi menjadi lima lipatan stratified. Setiap lipatan menjadi '
            'validasi sekali, sedangkan empat lipatan lain menjadi latih. Model '
            'pada setiap fold dilatih dari nol, termasuk imputasi, one-hot '
            'encoding, dan transformer antrean. Prediksi untuk baris validasi '
            'dikumpulkan sehingga setiap baris train mendapat satu skor OOF dari '
            'model yang tidak melihat baris tersebut saat latih.')
    lap.par('Ketiga, seluruh ambang dari 0,01 sampai 0,99 diuji pada skor OOF. '
            'Metrik utama adalah F2. F2 dipilih karena false negative dinilai lebih '
            'mahal secara operasional: berkas terlambat yang tidak masuk prioritas '
            'pemeriksaan dapat memperpanjang proses dan menimbulkan risiko '
            'keterlambatan lebih lanjut, sedangkan false positive hanya menambah '
            'pemeriksaan. Bobot recall pada F2 lebih besar daripada precision. '
            'Jika terjadi seri, aturan memilih precision lebih tinggi, lalu ambang '
            'lebih besar agar alarm tidak berlebihan.')
    lap.par('Keempat, ambang dikunci sebelum data uji dibaca. Data uji hanya dipakai '
            'untuk mengevaluasi ambang yang sudah dikunci. Sebagai pembanding, '
            'laporan juga menyajikan ambang 0,50 (default), ambang optimal F1 dari '
            'OOF, dan ambang operasional dengan batas beban alarm OOF 50%. Batas '
            '50% adalah skenario perencanaan kapasitas, bukan angka kapasitas '
            'aktual kantor. Kantor belum memberikan data kapasitas pemeriksaan.')

    lap.h2('C.2 Perbandingan ambang pada data uji')
    urutan = [0.50, 0.25, 0.19, 0.05]
    label = {0.50: 'Default; tidak ada TP',
             0.25: 'Optimal F1 OOF',
             0.19: 'Operasional; alarm OOF ≤ 50%',
             0.05: 'Optimal F2 OOF (terpilih)'}
    baris = []
    for t in urutan:
        r = _row(th, t)
        baris.append([f(t, 2), label[t], n(r['tp']), n(r['fn']), n(r['fp']),
                      n(r['tn']), f(r['precision']), f(r['recall']),
                      f(r['f1']), f(r['f2']),
                      f"{n(r['alarm'])}/34 ({pct(r['alert_rate'])})"])
    lap.tabel(
        ['Ambang', 'Keterangan', 'TP', 'FN', 'FP', 'TN', 'Prec', 'Recall',
         'F1', 'F2', 'Alarm'],
        baris, widths=[0.55, 1.25, 0.4, 0.4, 0.4, 0.4, 0.55, 0.55, 0.5, 0.5, 0.9],
        font=8, aligns=['c', 'l', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c'],
        caption='Tabel 12. Perbandingan ambang pada data uji. Semua ambang sudah '
                'dikunci dari OOF train sebelum data uji dibaca.')
    lap.par('Tabel 12 memuat empat ambang yang berbeda. Ambang 0,50 adalah default '
            'scikit-learn. Ambang 0,25 adalah titik dengan F1 OOF tertinggi. Ambang '
            '0,19 adalah titik dengan F2 tertinggi di antara ambang yang membebani '
            'paling banyak 50% data latih. Ambang 0,05 adalah titik dengan F2 OOF '
            'tertinggi secara keseluruhan. Keempatnya berasal dari data latih, bukan '
            'dari data uji.')

    lap.h2('C.3 Kurva pemilihan ambang dari OOF')
    lap.gambar(fig / '03_threshold_tuning_oof.png', 6.25,
               'Gambar 4. Precision, recall, F1, dan F2 pada OOF train, serta '
               'proporsi alarm. Garis putus-putus merah adalah ambang F2 terpilih '
               '0,05; garis titik-titik hitam adalah default 0,50.')
    baris_oof = []
    for t in urutan:
        r = _row(oof, t)
        baris_oof.append([f(t, 2), n(r['tp']), n(r['fn']), n(r['fp']), n(r['tn']),
                          f(r['precision']), f(r['recall']), f(r['f1']),
                          f(r['f2']), f"{n(r['alarm'])}/135 ({pct(r['alert_rate'])})"])
    lap.tabel(
        ['Ambang', 'TP', 'FN', 'FP', 'TN', 'Prec', 'Recall', 'F1', 'F2', 'Alarm OOF'],
        baris_oof, widths=[0.6, 0.5, 0.5, 0.5, 0.5, 0.65, 0.65, 0.6, 0.6, 1.0],
        font=8.5, aligns=['c'] * 10,
        caption='Tabel 13. Kinerja pada OOF train untuk ambang yang diuji. Tabel ini '
                'menjadi dasar pemilihan, bukan Tabel 12.')
    lap.par('Tabel 13 memperlihatkan mengapa 0,05 terpilih. Pada OOF train, ambang '
            '0,05 memberi F2 0,500 dengan recall 0,846 dan precision 0,190. Ambang '
            '0,19 memberi F2 0,446 dengan recall 0,577 dan precision 0,234. Ambang '
            '0,25 memberi F2 0,396 dengan recall 0,423 dan precision 0,314. Ambang '
            '0,50 memberi F2 0,214 dengan recall 0,192. Kenaikan F2 dari 0,19 ke '
            '0,05 memang nyata, tetapi harus dibayar dengan kenaikan alarm OOF dari '
            '47,4% menjadi 85,9%.')

    lap.h2('C.4 Justifikasi ambang dan trade-off operasional')
    lap.par('Pada data uji, ambang 0,50 hanya menandai 3 berkas dan tidak satu pun '
            'benar terlambat. Accuracy-nya 79,4%, tetapi recall 0. Ini contoh '
            'langsung paradoks akurasi. Ambang 0,25 menandai 14 berkas dan '
            'menangkap 2 dari 7 keterlambatan. Ambang 0,19 menandai 23 berkas dan '
            'menangkap 4 dari 7. Ambang 0,05 menandai 24 berkas dan menangkap 5 '
            'dari 7.')
    lap.par('Secara metrik F2, ambang 0,05 adalah yang terbaik: F2 0,481, F1 0,323, '
            'dan recall 0,714. Namun, beban alarmnya tinggi. Dua puluh empat dari 34 '
            'berkas harus diperiksa, dan 19 di antaranya tidak terlambat. Model ini '
            'lebih tepat diposisikan sebagai penyaring awal untuk staf yang memang '
            'memiliki kapasitas memeriksa sebagian besar berkas, bukan sebagai '
            'penentu prioritas otomatis.')
    lap.par('Jika kapasitas pemeriksaan lebih terbatas, ambang 0,19 atau 0,25 lebih '
            'masuk akal. Ambang 0,19 memberi recall 0,571 dengan 23 alarm, hampir '
            'sama dengan hasil historis Tugas 05 pada ambang 0,11 (recall 0,571, 22 '
            'alarm). Ambang 0,25 memberi 14 alarm, tetapi recall turun menjadi '
            '0,286. Tidak ada ambang yang memenuhi sekaligus recall tinggi, '
            'precision memadai, dan alarm rendah. Inilah trade-off yang harus '
            'diputuskan kantor berdasarkan kapasitas dan toleransi risiko.')
    lap.par('Rekomendasi penulisan: untuk uji coba terbatas, gunakan ambang 0,19 '
            'sebagai titik operasional karena beban alarm OOF-nya paling mendekati '
            '50% dan recall-nya masih di atas 0,5. Untuk penelitian yang menekankan '
            'sensitivitas, laporkan 0,05 sebagai optimum F2. Jangan memakai 0,50 '
            'hanya karena itu default, karena ambang itu tidak menemukan satu pun '
            'keterlambatan pada data uji.')

    lap.h2('C.5 Batas interpretasi threshold tuning')
    lap.par('Threshold tuning tidak mengubah skor model. ROC-AUC dan PR-AUC tetap '
            'sama untuk semua ambang. Yang berubah hanya label keputusan dan '
            'confusion matrix. Karena itu threshold tuning tidak dapat menyembuhkan '
            'model yang daya pisahnya lemah. Pada laporan ini, AP 0,190 dan ROC-AUC '
            '0,413 menunjukkan bahwa masalah utamanya ada pada kualitas skor dan '
            'fitur, bukan hanya pada titik potong.')
    lap.par('Data uji 34 berkas juga sudah pernah dipakai pada Tugas 04 dan Tugas '
            '05. Tugas 06 tidak memilih parameter atau ambang dari data uji, tetapi '
            'data uji tersebut bukan lagi holdout yang sepenuhnya buta. Hasilnya '
            'harus dibaca sebagai evaluasi pada partisi yang sama, bukan sebagai '
            'validasi periode baru. Validasi yang lebih kuat memerlukan data setelah '
            'Tugas 05 yang belum pernah dilihat.')

    # ==================================================================
    # D. OPTUNA
    # ==================================================================
    lap.h1('D. HASIL OPTIMASI HIPERPARAMETER (OPTUNA) & STRATIFIED 5-FOLD CV')

    lap.h2('D.1 Desain optimasi')
    lap.par('Optimasi memakai Optuna dengan sampler Tree-structured Parzen '
            'Estimator (TPE). Berbeda dengan GridSearchCV yang mencoba semua '
            'kombinasi, TPE membangun model probabilistik dari trial sebelumnya dan '
            'memilih kandidat yang paling menjanjikan. Pendekatan ini lebih efisien '
            'untuk ruang pencarian campuran antara bilangan bulat, bilangan riil, '
            'dan kategori. Jumlah trial ditetapkan 30, sesuai rentang 20–30 trial '
            'pada panduan.')
    lap.par('Setiap trial dinilai dengan Stratified 5-Fold CV pada 135 data latih. '
            'Objektifnya adalah rata-rata Macro F1. Pipeline lengkap dimasukkan ke '
            'dalam CV, sehingga imputasi, one-hot encoding, dan transformer antrean '
            'di-fit hanya pada lipatan latih. Data uji tidak pernah masuk ke proses '
            'Optuna. Random state untuk model, split, dan sampler diset 42.')
    lap.tabel(
        ['Hiperparameter', 'Tipe dan rentang', 'Baseline', 'Terbaik'],
        [['criterion', 'Kategorik: gini, entropy', 'gini (default)', 'gini'],
         ['max_depth', 'Integer 2–10', '4', '6'],
         ['min_samples_leaf', 'Integer 2–30', '15', '3'],
         ['min_samples_split', 'Integer 2–40', '2', '16'],
         ['ccp_alpha', 'Float 0,0–0,02', '0,0', '0,0035355'],
         ['class_weight', 'Kategorik: none, balanced', 'none', 'none'],
         ['max_features', 'Kategorik: none, sqrt, log2', 'none (default)', 'log2'],
         ['random_state', 'Tetap', '42', '42']],
        widths=[1.35, 2.35, 1.25, 1.15], font=8.5,
        aligns=['l', 'l', 'c', 'c'],
        caption='Tabel 14. Ruang pencarian Optuna dan nilai terbaik.')

    lap.h2('D.2 Hasil studi Optuna')
    lap.tabel(
        ['Komponen', 'Hasil'],
        [['Jumlah trial', f'{opt["n_trials"]}'],
         ['Trial selesai', f'{opt["n_selesai"]}'],
         ['Trial terbaik', f'{opt["best_trial"]}'],
         ['Macro F1 CV terbaik', f(opt['best_value_cv_macro_f1'])],
         ['Sampler', 'TPESampler(seed=42, n_startup_trials=8)'],
         ['Durasi optimasi', f'{f(opt["durasi_detik"], 1)} detik'],
         ['Objektif', 'Macro F1, Stratified 5-Fold pada train']],
        widths=[2.2, 4.2], font=9, aligns=['l', 'l'],
        caption='Tabel 15. Ringkasan studi Optuna.')
    p = opt['best_params']
    lap.par(f'Parameter terbaik adalah criterion {p["criterion"]}, max_depth '
            f'{p["max_depth"]}, min_samples_leaf {p["min_samples_leaf"]}, '
            f'min_samples_split {p["min_samples_split"]}, ccp_alpha '
            f'{f(p["ccp_alpha"], 6)}, class_weight {p["class_weight"]}, dan '
            f'max_features {p["max_features"]}. Kombinasi ini menghasilkan Macro F1 '
            f'CV {f(opt["best_value_cv_macro_f1"])}. Dibanding baseline, pohon '
            'menjadi lebih dalam (6 versus 4) dan daunnya jauh lebih kecil (3 versus '
            '15). Pohon yang lebih dalam dapat menangkap interaksi yang tidak '
            'tertangkap baseline, tetapi juga lebih mudah menghafal data kecil.')
    lap.gambar(fig / '04_optuna_history.png', 5.9,
               'Gambar 5. Riwayat nilai objektif per trial dan nilai terbaik '
               'kumulatif. Trial terbaik adalah trial ke-13.')
    imp = opt.get('parameter_importance', {})
    if imp:
        urut = sorted(imp.items(), key=lambda x: -x[1])
        teks = ', '.join(f'{k} {f(v, 3)}' for k, v in urut)
        lap.par(f'Kepentingan parameter relatif adalah {teks}. Nilai ini menunjukkan '
                'seberapa besar pengaruh setiap parameter terhadap variasi skor '
                'trial, bukan arah pengaruhnya. min_samples_leaf dan ccp_alpha '
                'mendominasi, sedangkan criterion hampir tidak berpengaruh. Hasil '
                'ini masuk akal karena pada data kecil, ukuran daun dan pemangkasan '
                'lebih menentukan stabilitas daripada pilihan fungsi impurity.')
    lap.gambar(fig / '05_optuna_importance.png', 5.7,
               'Gambar 6. Kepentingan relatif hiperparameter pada studi Optuna.')

    lap.h2('D.3 Perbandingan Stratified 5-Fold CV: before vs after')
    baris_cv = []
    for kunci, judul in [('macro_f1', 'Macro F1'), ('f1_positif', 'F1 positif'),
                         ('precision', 'Precision'), ('recall', 'Recall'),
                         ('average_precision', 'PR-AUC (AP)'),
                         ('roc_auc', 'ROC-AUC'), ('log_loss', 'Log-loss')]:
        b = cv['baseline'][kunci]
        a = cv['tuned'][kunci]
        delta = a['mean'] - b['mean']
        baris_cv.append([judul, f'{f(b["mean"])} ± {f(b["std"])}',
                         f'{f(a["mean"])} ± {f(a["std"])}',
                         f'{delta:+.3f}'.replace('.', ',')])
    lap.tabel(
        ['Metrik CV', 'Before Tuning', 'After Tuning', 'Delta'],
        baris_cv, widths=[1.8, 1.7, 1.7, 1.0], font=9,
        aligns=['l', 'c', 'c', 'c'],
        caption='Tabel 16. Rata-rata dan simpangan baku lima lipatan pada train. '
                'Log-loss makin kecil makin baik.')
    lap.gambar(fig / '06_cv_before_after.png', 6.2,
               'Gambar 7. Perbandingan metrik Stratified 5-Fold CV before dan after '
               'tuning. Galat batang adalah simpangan baku antar-fold.')
    lap.par('Macro F1 naik dari 0,447 menjadi 0,553, F1 positif dari 0 menjadi '
            '0,217, PR-AUC dari 0,231 menjadi 0,331, dan ROC-AUC dari 0,524 menjadi '
            '0,554. Namun, log-loss memburuk dari 0,798 menjadi 1,495. Artinya, '
            'model hasil tuning lebih baik dalam label keputusan pada ambang 0,50, '
            'tetapi probabilitasnya kurang terkalibrasi. Ini konsekuensi wajar dari '
            'pohon yang lebih dalam dan daun yang lebih kecil.')
    lap.par('Simpangan baku Macro F1 baseline sangat kecil (0,005) karena baseline '
            'pada ambang 0,50 hampir selalu memprediksi kelas negatif di semua '
            'fold. Stabilitas itu bukan tanda model bagus; ia justru tanda model '
            'degenerat. Setelah tuning, simpangan baku naik menjadi 0,118 karena '
            'model mulai membuat prediksi positif dan variasi antar-fold muncul. '
            'Kenaikan variasi ini perlu dibaca bersama kenaikan skor rata-rata.')

    lap.h2('D.4 Perbandingan pada data uji')
    def ambil(model, t):
        return ba[(ba['model'] == model) & ((ba['threshold'] - t).abs() < 1e-9)].iloc[0]

    kombinasi = [
        ('Before Tuning', 0.50, 'Default 0,50'),
        ('After Tuning', 0.50, 'Default 0,50'),
        ('Before Tuning', 0.06, 'OOF F2 (0,06)'),
        ('After Tuning', 0.05, 'OOF F2 (0,05)'),
        ('After Tuning', 0.19, 'Operasional (0,19)'),
    ]
    baris_ba = []
    for model, t, ket in kombinasi:
        r = ambil(model, t)
        baris_ba.append([model, ket, f(r['threshold'], 2), n(r['tp']), n(r['fn']),
                         n(r['fp']), n(r['tn']), f(r['precision']),
                         f(r['recall']), f(r['f1']), f(r['f2']), n(r['alarm'])])
    lap.tabel(
        ['Model', 'Skenario', 'Ambang', 'TP', 'FN', 'FP', 'TN', 'Prec', 'Recall',
         'F1', 'F2', 'Alarm'],
        baris_ba, widths=[1.0, 1.05, 0.65, 0.34, 0.34, 0.34, 0.34, 0.5, 0.5, 0.45,
                          0.45, 0.45],
        font=7.5, aligns=['l', 'l', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c', 'c'],
        caption='Tabel 17. Perbandingan before vs after pada data uji. Baris OOF '
                'memakai ambang yang dipilih dari OOF masing-masing model.')

    baris_meta = []
    for model, t, ket in [('Before Tuning', 0.06, 'Sebelum tuning'),
                          ('After Tuning', 0.05, 'Sesudah tuning')]:
        r = ambil(model, t)
        baris_meta.append([ket, f(r['average_precision']), f(r['roc_auc']),
                           f(r['log_loss'])])
    lap.tabel(
        ['Model', 'PR-AUC (AP)', 'ROC-AUC', 'Log-loss'],
        baris_meta, widths=[2.2, 1.4, 1.3, 1.3], font=9,
        aligns=['l', 'c', 'c', 'c'],
        caption='Tabel 18. Metrik yang tidak bergantung pada ambang pada data uji.')
    lap.gambar(fig / '07_confusion_compare.png', 5.9,
               'Gambar 8. Confusion matrix before dan after tuning pada ambang 0,50 '
               'dan ambang OOF masing-masing.')

    lap.par('Pada ambang 0,50, kedua model tidak menemukan satu pun keterlambatan. '
            'Model after tuning hanya menambah tiga alarm palsu. Jadi, pada default '
            '0,50, tuning tidak memberi manfaat praktis. Manfaat baru terlihat '
            'setelah ambang diturunkan: F1 positif naik dari 0,276 menjadi 0,323, '
            'recall dari 0,571 menjadi 0,714, dan F2 dari 0,400 menjadi 0,481. '
            'Kenaikan recall itu dibayar dengan satu alarm palsu tambahan (18 '
            'menjadi 19).')
    lap.par('PR-AUC justru sedikit turun, dari 0,196 menjadi 0,190, dan ROC-AUC naik '
            'dari 0,381 menjadi 0,413. Keduanya masih sangat rendah. Dengan demikian, '
            'tuning memperbaiki titik operasi dan keseimbangan label, tetapi belum '
            'memperbaiki kemampuan model memberi peringkat risiko. Ini temuan yang '
            'harus disampaikan apa adanya. Klaim bahwa tuning membuat model siap '
            'produksi tidak didukung data.')

    lap.h2('D.5 Pembahasan: CV versus test')
    lap.par('Hasil CV dan hasil test tidak sepenuhnya searah. CV menunjukkan '
            'kenaikan PR-AUC +0,100, sedangkan test menunjukkan penurunan -0,006. '
            'CV menunjukkan kenaikan ROC-AUC +0,030, test menunjukkan +0,032. '
            'Perbedaan ini dapat terjadi karena data uji hanya memuat tujuh positif, '
            'sedangkan CV memakai 26 positif di seluruh train. Satu atau dua '
            'prediksi yang berubah dapat membalik arah metrik pada test.')
    lap.par('Karena itu, pemilihan model tidak boleh hanya melihat test. CV dipakai '
            'untuk memilih parameter, lalu test dipakai untuk memeriksa apakah '
            'perbaikan itu terbawa ke data yang tidak dipakai memilih. Pada kasus '
            'ini, perbaikan F1 dan recall terbawa, tetapi perbaikan PR-AUC tidak. '
            'Kesimpulan yang jujur adalah: tuning berguna untuk menggeser model ke '
            'titik operasi yang lebih sensitif, bukan untuk mengubah kualitas '
            'diskriminasi secara meyakinkan.')
    lap.par('Model after tuning juga lebih kompleks: depth 6 dengan leaf minimum 3. '
            'Pada 135 data latih, daun sekecil itu rentan terhadap variasi sampel. '
            'Jika nanti ada data periode baru, model ini perlu diuji ulang dan '
            'mungkin perlu dibatasi. Pilihan baseline yang lebih sederhana masih '
            'memiliki keunggulan interpretasi dan kalibrasi, walaupun lemah dalam '
            'mendeteksi kelas positif pada ambang 0,50.')

    lap.h2('D.6 Potongan kode optimasi')
    lap.par('Kode berikut adalah inti prosedur yang dijalankan. Versi lengkap '
            'tersedia pada eksperimen_tugas_06/eksperimen_tugas06.py.', rata='left')
    lap.kode(
        "import optuna\n"
        "from optuna.samplers import TPESampler\n"
        "from sklearn.model_selection import StratifiedKFold, cross_validate\n"
        "\n"
        "def objective(trial):\n"
        "    params = {\n"
        "        'criterion': trial.suggest_categorical('criterion', ['gini', 'entropy']),\n"
        "        'max_depth': trial.suggest_int('max_depth', 2, 10),\n"
        "        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 2, 30),\n"
        "        'min_samples_split': trial.suggest_int('min_samples_split', 2, 40),\n"
        "        'ccp_alpha': trial.suggest_float('ccp_alpha', 0.0, 0.02),\n"
        "        'class_weight': trial.suggest_categorical('class_weight', ['none', 'balanced']),\n"
        "        'max_features': trial.suggest_categorical('max_features', ['none', 'sqrt', 'log2']),\n"
        "    }\n"
        "    params['class_weight'] = None if params['class_weight'] == 'none' else params['class_weight']\n"
        "    params['max_features'] = None if params['max_features'] == 'none' else params['max_features']\n"
        "    pipe = buat_pipeline(params)  # FiturNotaris -> imputer/one-hot -> DecisionTree\n"
        "    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)\n"
        "    skor = cross_validate(pipe, X_train, y_train, cv=cv,\n"
        "                          scoring='f1_macro', n_jobs=1)['test_score']\n"
        "    return float(skor.mean())\n"
        "\n"
        "study = optuna.create_study(direction='maximize',\n"
        "    sampler=TPESampler(seed=42, n_startup_trials=8))\n"
        "study.optimize(objective, n_trials=30)")

    lap.h2('D.7 Artefak optimasi')
    lap.par('Seluruh riwayat trial disimpan pada hasil/optuna/riwayat_trial.csv. '
            'Parameter terbaik dan ringkasan studi disimpan pada '
            'hasil/optuna/informasi_study.json. Model hasil tuning disimpan pada '
            'hasil/model/model_tugas06_tuned.joblib, sedangkan baseline disimpan '
            'pada hasil/model/model_tugas06_baseline.joblib. Metadata model memuat '
            'parameter, threshold, ukuran data, hash dataset, dan versi pustaka. Uji '
            'paritas setelah pemuatan model memastikan prediksi tidak berubah.',
            rata='left')
