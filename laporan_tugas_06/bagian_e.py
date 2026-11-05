"""Bagian E: sintesis proposal Bab I–III."""
from __future__ import annotations

from laporan_lib import f, n, pct


def tulis(lap, D):
    met = D['met']
    sel = D['sel']
    cv = D['cv']
    opt = D['opt']

    lap.h1('E. DRAF KONSOLIDASI NASKAH PROPOSAL RISET UTS (BAB I–III)')
    lap.par('Bagian ini adalah sintesis yang menghubungkan hasil Tugas 01 sampai '
            'Tugas 06 menjadi draf Bab I, Bab II, dan Bab III proposal UTS. Isinya '
            'bukan proposal final. Angka dan temuan mengacu pada eksperimen Tugas 06 '
            'yang benar-benar dijalankan. Referensi ditulis dalam gaya IEEE.')

    # ==================================================================
    # BAB I
    # ==================================================================
    lap.h2('E.1 BAB I — PENDAHULUAN')
    lap.h3('1.1 Latar Belakang')
    lap.par('Kantor Notaris & PPAT Aries Buwana melayani pembuatan akta dan '
            'perbuatan hukum lain yang memerlukan kehadiran notaris atau pejabat '
            'pembuat akta tanah. Setiap berkas memiliki rangkaian pekerjaan yang '
            'tidak selalu pendek: pemeriksaan identitas dan dokumen, penyusunan '
            'akta, pengesahan, pendaftaran, serta koordinasi dengan instansi lain. '
            'Batas waktu layanan atau SLA dicatat untuk menjaga agar pekerjaan tidak '
            'tertunda tanpa kendali. Pada dataset penelitian ini, SLA berkisar 5 '
            'sampai 40 hari tergantung jenis layanan.')
    lap.par('Dataset kantor memuat 169 berkas yang diterima antara April 2024 dan '
            'Oktober 2026. Sebanyak 33 berkas (19,5%) melewati SLA, sedangkan 136 '
            'berkas (80,5%) selesai tepat waktu. Kategori terbanyak adalah PKR_PT '
            '(66 berkas), diikuti AJB_Saham (24), Waris_Wasiat (14), Kuasa (13), '
            'dan PPJB (9). Laju keterlambatan berbeda antar kategori, tetapi '
            'perbedaan itu tidak dengan sendirinya menjelaskan penyebab keterlambatan '
            'karena jumlah berkas per kategori tidak seimbang.')
    lap.par('Keterlambatan berkas berpotensi menimbulkan beberapa dampak. Klien '
            'harus menunggu lebih lama dan mungkin kembali lagi ke kantor. Staf '
            'harus mengulang koordinasi dengan instansi tujuan. Notaris/PPAT '
            'menghadapi risiko reputasi dan keluhan. Dampak-dampak itu belum diukur '
            'dalam satuan biaya pada penelitian ini, tetapi cukup menjadi alasan '
            'untuk mencari cara mendeteksi berkas berisiko lebih awal. Deteksi awal '
            'memungkinkan staf memeriksa kelengkapan, menagih dokumen yang kurang, '
            'atau mengatur ulang prioritas sebelum tenggat terlewat.')
    lap.par('Pemantauan saat ini masih mengandalkan pengalaman staf dan tumpukan '
            'berkas. Cara itu sulit diskalakan ketika jumlah berkas bertambah dan '
            'jenis layanan beragam. Data historis yang sudah tercatat dapat dipakai '
            'untuk membangun model pembelajaran mesin yang memberi skor risiko pada '
            'saat berkas diterima. Fitur yang tersedia pada tahap awal meliputi '
            'kategori akta, jumlah penghadap, SLA, jumlah antrean berjalan, ada '
            'tidaknya RUPS, bulan masuk, dan hari masuk. Targetnya adalah status '
            'terlambat, yaitu berkas yang durasi penyelesaiannya melebihi SLA.')
    lap.par('Tugas 04 dan Tugas 05 sudah membangun Decision Tree dan prototipe '
            'inferensi. Namun, model dengan akurasi tinggi belum tentu berguna pada '
            'data tidak seimbang. Pada data uji Tugas 06, model baseline pada ambang '
            '0,50 mencapai akurasi 79,4% tetapi tidak menemukan satu pun dari tujuh '
            'berkas terlambat. Fenomena ini dikenal sebagai paradoks akurasi. Karena '
            'itu, penelitian ini bergerak melampaui akurasi: memeriksa confusion '
            'matrix, precision, recall, F1, F2, ROC-AUC, dan PR-AUC; memilih ambang '
            'dari prediksi OOF; serta mengoptimalkan hiperparameter dengan Optuna.')
    lap.par('Penelitian ini juga menjadi dasar proposal UTS. Bab I merumuskan '
            'masalah dan batasan. Bab II membahas teori algoritma, metrik, threshold '
            'tuning, Optuna, dan dua paper rujukan. Bab III menjelaskan metodologi '
            'CRISP-DM, preprocessing, feature engineering, validasi silang, '
            'optimasi, dan evaluasi. Dengan demikian, Tugas 06 bukan dokumen '
            'terpisah dari tugas sebelumnya, melainkan jembatan menuju proposal yang '
            'utuh.')

    lap.h3('1.2 Identifikasi Masalah')
    for i, teks in enumerate([
        'Kelas terlambat hanya 33 dari 169 berkas (19,5%). Akurasi tinggi dapat '
        'dicapai dengan mengabaikan kelas minoritas, sehingga akurasi saja tidak '
        'cukup untuk menilai model.',
        'Pada ambang default 0,50, model tidak menemukan satu pun keterlambatan '
        'pada data uji. Ambang keputusan perlu dipilih dengan prosedur yang tidak '
        'menggunakan data uji.',
        'Daya pisah model masih lemah. PR-AUC 0,190 sedikit di bawah prevalensi '
        '0,206, dan ROC-AUC data uji 0,413. Threshold tuning tidak dapat '
        'memperbaiki masalah ini sendirian.',
        'Hiperparameter Tugas 04 belum dioptimalkan untuk Macro F1. Diperlukan '
        'pencarian yang lebih efisien daripada grid manual, dengan validasi silang '
        'yang menjaga proporsi kelas.',
        'Beban alarm dan kapasitas pemeriksaan staf belum diukur. Pemilihan ambang '
        'harus disajikan sebagai trade-off, bukan sebagai satu angka yang berlaku '
        'untuk semua kondisi.',
        'Data uji 34 berkas sudah pernah dipakai pada Tugas 04 dan Tugas 05. '
        'Validasi pada periode baru belum tersedia, sehingga klaim generalisasi '
        'harus dibatasi.',
    ], 1):
        lap.nomor(i, teks)

    lap.h3('1.3 Rumusan Masalah')
    for i, teks in enumerate([
        'Bagaimana kinerja model Decision Tree pada data uji ketika dievaluasi '
        'dengan confusion matrix, precision, recall, F1 per kelas, Macro F1, '
        'Weighted F1, ROC-AUC, dan PR-AUC?',
        'Ambang keputusan mana yang optimal menurut prediksi OOF train, dan bagaimana '
        'perbandingannya dengan ambang 0,50, ambang optimal F1, serta ambang '
        'operasional dengan batas beban alarm?',
        'Apakah optimasi hiperparameter dengan Optuna dan Stratified 5-Fold CV '
        'meningkatkan kinerja model dibanding baseline Tugas 04–05?',
        'Bagaimana hasil Tugas 06 dipetakan menjadi draf Bab I–III proposal UTS '
        'yang konsisten dengan seluruh tugas sebelumnya?',
    ], 1):
        lap.nomor(i, teks)

    lap.h3('1.4 Tujuan Penelitian')
    for i, teks in enumerate([
        'Mengukur kinerja model secara lengkap pada data uji, termasuk metrik per '
        'kelas dan metrik yang tidak bergantung pada ambang.',
        'Memilih ambang keputusan dari prediksi OOF train dan menjelaskan '
        'trade-off antara false positive dan false negative.',
        'Mengoptimalkan hiperparameter Decision Tree dengan Optuna dan Stratified '
        '5-Fold CV, lalu membandingkan before dan after tuning secara adil.',
        'Menyusun sintesis Bab I–III proposal UTS berdasarkan hasil Tugas 01–06.',
    ], 1):
        lap.nomor(i, teks)

    lap.h3('1.5 Batasan Penelitian')
    for teks in [
        'Objek penelitian hanya Kantor Notaris & PPAT Aries Buwana, Jakarta Barat.',
        'Dataset 169 berkas berasal dari rekap kantor dan tidak mewakili seluruh '
        'kantor notaris di Indonesia.',
        'Target hanya status terlambat terhadap SLA; tingkat keparahan keterlambatan '
        'dan biaya kerugian tidak dimodelkan.',
        'Prediktor dibatasi pada informasi yang tersedia saat berkas diterima. '
        'Tanggal selesai, durasi aktual, dan label tidak dipakai sebagai prediktor.',
        'Model yang dioptimalkan adalah Decision Tree agar konsisten dengan Tugas '
        '04–05. Algoritma lain tidak diuji pada Tugas 06.',
        'Data uji 34 berkas sudah pernah dilihat pada Tugas 04–05. Hasil Tugas 06 '
        'bukan validasi pada periode baru.',
        'Biaya rupiah dan kapasitas pemeriksaan staf tidak tersedia, sehingga '
        'analisis ambang bersifat skenario operasional.',
    ]:
        lap.bullet(teks)

    lap.h3('1.6 Manfaat Penelitian')
    lap.bullet('Manfaat teoretis: memberi contoh evaluasi model yang tidak '
               'bertumpu pada akurasi pada data administrasi yang tidak seimbang.')
    lap.bullet('Manfaat praktis: memberi kantor gambaran tentang beban alarm, '
               'kasus yang terlewat, dan titik operasional yang mungkin dipakai '
               'untuk penyaringan awal.')
    lap.bullet('Manfaat metodologis: mendokumentasikan alur OOF, threshold tuning, '
               'dan Optuna yang dapat diulang pada data kantor berikutnya.')

    # ==================================================================
    # BAB II
    # ==================================================================
    lap.h2('E.2 BAB II — TINJAUAN PUSTAKA')
    lap.h3('2.1 Machine Learning dan Klasifikasi Biner')
    lap.par('Pembelajaran mesin adalah proses membangun fungsi prediksi dari data '
            'contoh. Pada klasifikasi biner, setiap berkas memiliki vektor fitur x '
            'dan label y yang bernilai 0 atau 1. Model mempelajari fungsi f(x) yang '
            'memperkirakan probabilitas y = 1. Keputusan akhir dibuat dengan '
            'membandingkan probabilitas itu terhadap ambang t. Dengan demikian, '
            'kualitas model tidak hanya ditentukan oleh f, tetapi juga oleh t dan '
            'oleh biaya kesalahan di domain aplikasi.')
    lap.par('Pada penelitian ini, y = 1 berarti berkas terlambat. Fitur x dibatasi '
            'pada informasi yang tersedia saat berkas diterima. Tujuannya agar model '
            'dapat dipakai pada tahap awal, bukan setelah berkas selesai. Batasan ini '
            'penting untuk mencegah kebocoran informasi dari masa depan.')

    lap.h3('2.2 Decision Tree')
    lap.par('Decision Tree adalah model pohon yang membagi ruang fitur secara '
            'rekursif. Setiap simpul memilih satu fitur dan satu batas yang paling '
            'banyak mengurangi ketidakmurnian. Untuk klasifikasi, ketidakmurnian '
            'dapat diukur dengan Gini atau entropy.')
    lap.rumus('Gini(t) = 1 − Σ p(i|t)²')
    lap.rumus('Entropy(t) = − Σ p(i|t) log₂ p(i|t)')
    lap.par('Information gain adalah selisih ketidakmurnian simpul induk dengan '
            'rata-rata ketidakmurnian anak setelah pemisahan. Pohon tumbuh sampai '
            'mencapai batas kedalaman, jumlah sampel minimum per daun, atau aturan '
            'pemangkasan. Probabilitas di daun dihitung dari proporsi kelas positif '
            'pada daun tersebut. Pada pohon kecil, probabilitas ini mengumpul pada '
            'beberapa nilai diskret, sehingga ambang keputusan juga efektif hanya '
            'pada beberapa titik.')
    lap.par('Hiperparameter utama pada penelitian ini adalah max_depth, '
            'min_samples_leaf, min_samples_split, ccp_alpha, class_weight, '
            'max_features, dan criterion. max_depth membatasi panjang aturan. '
            'min_samples_leaf dan min_samples_split mengatur dukungan minimum agar '
            'daun tidak terlalu kecil. ccp_alpha melakukan cost-complexity pruning. '
            'class_weight dapat memberi bobot lebih besar pada kelas minoritas. '
            'max_features membatasi jumlah fitur yang dipertimbangkan pada setiap '
            'pemisahan.')
    lap.par('Kelebihan Decision Tree adalah interpretasinya mudah, dapat menangani '
            'fitur numerik dan kategorik, dan tidak memerlukan standardisasi skala. '
            'Kekurangannya adalah ketidakstabilan terhadap perubahan kecil pada data, '
            'kecenderungan overfitting pada pohon dalam, dan probabilitas yang belum '
            'tentu terkalibrasi. Pada data 169 berkas, pohon dangkal lebih mudah '
            'dipertanggungjawabkan, tetapi pohon yang terlalu dangkal dapat menghasilkan '
            'prediksi konstan seperti yang terjadi pada baseline ambang 0,50.')

    lap.h3('2.3 Evaluasi pada Data Tidak Seimbang')
    lap.par('Data penelitian ini memiliki rasio 136 berkas tepat waktu terhadap 33 '
            'berkas terlambat, sekitar 4,1:1. Rasio itu tidak ekstrem, tetapi cukup '
            'untuk membuat akurasi menyesatkan. Model yang selalu menebak tepat waktu '
            'mencapai akurasi 79,4% tanpa menemukan satu pun keterlambatan. Oleh '
            'karena itu, evaluasi harus memisahkan kelas dan melihat biaya kesalahan.')
    lap.par('Confusion matrix membagi prediksi menjadi TP, TN, FP, dan FN. Precision '
            'mengukur ketepatan alarm; recall mengukur cakupan keterlambatan. F1 '
            'menyeimbangkan keduanya, sedangkan F2 memberi bobot lebih besar pada '
            'recall. Macro F1 merata-ratakan skor setiap kelas, sehingga kelas '
            'minoritas tidak tenggelam oleh kelas mayoritas. Weighted F1 membobot '
            'skor dengan jumlah sampel, sehingga lebih dekat ke kinerja agregat.')
    lap.par('ROC-AUC mengukur kemampuan mengurutkan positif di atas negatif pada '
            'seluruh ambang. PR-AUC mengukur hal serupa dengan fokus pada precision '
            'dan recall kelas positif. Pada data tidak seimbang, PR-AUC lebih peka '
            'terhadap perubahan di kelas minoritas. Definisi PR-AUC yang dipakai di '
            'sini adalah average precision (AP), yaitu rata-rata precision pada '
            'setiap titik recall, bukan luas trapesium. Log-loss mengukur kualitas '
            'probabilitas; nilainya makin kecil makin baik.')
    lap.par('Saito dan Rehmsmeier menunjukkan bahwa kurva precision–recall lebih '
            'informatif daripada kurva ROC ketika kelas tidak seimbang, karena '
            'kurva ROC dapat terlihat baik walaupun model gagal pada kelas '
            'minoritas [4]. Temuan itu relevan dengan penelitian ini: ROC-AUC 0,413 '
            'dan AP 0,190 menunjukkan bahwa model belum berhasil memberi peringkat '
            'risiko yang baik, meskipun akurasi pada ambang 0,50 terlihat tinggi.')

    lap.h3('2.4 Decision Threshold Tuning')
    lap.par('Threshold tuning memindahkan batas keputusan tanpa mengubah skor '
            'model. Jika skor model tetap, ROC-AUC dan PR-AUC juga tetap; yang '
            'berubah adalah label prediksi dan confusion matrix. Pada data tidak '
            'seimbang, ambang 0,50 jarang menjadi pilihan terbaik karena model '
            'cenderung memprediksi kelas mayoritas. Menurunkan ambang menaikkan '
            'recall tetapi juga menaikkan false positive. Menaikkan ambang '
            'mengurangi alarm tetapi berisiko melewatkan kasus positif.')
    lap.par('Pemilihan ambang harus dilakukan pada data yang tidak dipakai untuk '
            'evaluasi akhir. Pada penelitian ini, ambang dipilih dari prediksi OOF '
            'train. Setiap baris train diprediksi oleh model yang tidak melihat baris '
            'itu saat latih. Dengan cara ini, ambang dapat dipilih tanpa menyentuh '
            'data uji. Metrik pemilihan adalah F2, dengan pertimbangan bahwa false '
            'negative lebih mahal secara operasional daripada false positive.')

    lap.h3('2.5 Optuna dan Bayesian Optimization')
    lap.par('Pencarian hiperparameter dapat dilakukan dengan grid, random, atau '
            'Bayesian optimization. Grid mencoba semua kombinasi dan cepat menjadi '
            'mahal. Random sampling lebih murah, tetapi tidak belajar dari trial '
            'sebelumnya. Bayesian optimization membangun model probabilistik dari '
            'hasil trial dan memilih kandidat berikutnya berdasarkan model tersebut.')
    lap.par('Optuna menggunakan Tree-structured Parzen Estimator (TPE). TPE '
            'memodelkan distribusi parameter untuk trial yang berkinerja baik dan '
            'buruk, lalu memilih kandidat yang diharapkan memperbaiki nilai '
            'objektif. Optuna juga mendukung ruang pencarian define-by-run, sehingga '
            'parameter yang berbeda dapat diuji dalam satu studi. Pada penelitian '
            'ini, Optuna dijalankan 30 trial dengan objective Macro F1 dan '
            'Stratified 5-Fold CV [5].')
    lap.par('Validasi silang stratifikasi menjaga proporsi kelas pada setiap '
            'lipatan. Hal ini penting karena hanya ada 26 berkas terlambat di train. '
            'Tanpa stratifikasi, satu lipatan bisa kehilangan terlalu banyak positif '
            'dan skor menjadi tidak stabil. Prediksi OOF dari lipatan yang sama '
            'kemudian dipakai untuk memilih ambang.')

    lap.h3('2.6 Penelitian Terdahulu')
    lap.par('Dua paper berikut dipakai sebagai rujukan utama karena keduanya '
            'langsung berkaitan dengan metode Tugas 06. Ringkasannya disajikan pada '
            'Tabel 19.')
    lap.tabel(
        ['Penulis (tahun)', 'Fokus', 'Metode', 'Temuan utama', 'Relevansi dan perbedaan'],
        [['Saito & Rehmsmeier (2015) [4]',
          'Evaluasi classifier biner pada data tidak seimbang',
          'Simulasi dan data nyata; perbandingan kurva ROC dan precision–recall',
          'Kurva PR lebih informatif daripada ROC ketika kelas tidak seimbang; ROC '
          'dapat memberi kesan performa yang terlalu baik',
          'Mendukung penggunaan PR-AUC/AP dan pembacaan per kelas. Tidak membahas '
          'berkas notaris, threshold OOF, atau Optuna.'],
         ['Akiba et al. (2019) [5]',
          'Kerangka optimasi hiperparameter generasi baru',
          'Optuna dengan TPE, define-by-run, pruning, dan evaluasi empiris',
          'Optuna efisien dan fleksibel untuk ruang pencarian campuran; TPE '
          'memanfaatkan histori trial',
          'Menjadi dasar prosedur Optuna 30 trial dan Stratified 5-Fold. Tidak '
          'khusus data administrasi notaris.']],
        widths=[1.35, 1.25, 1.5, 1.35, 1.35], font=7.5,
        aligns=['l', 'l', 'l', 'l', 'l'],
        caption='Tabel 19. Dua paper rujukan utama dan posisinya terhadap penelitian ini.')
    lap.par('Kedua paper tersebut tidak meneliti keterlambatan berkas notaris. '
            'Saito dan Rehmsmeier memberi dasar mengapa PR-AUC dan metrik per kelas '
            'perlu dilaporkan. Akiba et al. memberi dasar mengapa Optuna dan TPE '
            'dipakai untuk mencari hiperparameter. Celah penelitian yang diisi '
            'penelitian ini adalah penerapan kedua gagasan pada data berkas kantor '
            'notaris yang kecil, tidak seimbang, dan memiliki keterbatasan fitur '
            'awal. Penelitian ini juga menambahkan prosedur OOF untuk memilih ambang '
            'tanpa data uji.')
    lap.par('Rujukan pendukung lain dipakai untuk memperkuat teori. He dan Garcia '
            'merangkum berbagai pendekatan untuk data tidak seimbang, termasuk '
            'metrik dan strategi biaya [6]. Fawcett menjelaskan dasar analisis ROC '
            '[7]. Breiman et al. menjelaskan Classification and Regression Trees '
            'yang menjadi dasar pohon keputusan [9].')

    lap.h3('2.7 Kerangka Pemikiran dan Research Gap')
    lap.par('Alur pemikiran penelitian ini adalah: data berkas diterima → audit dan '
            'pembersihan → pembentukan fitur awal → pelatihan Decision Tree → skor '
            'probabilitas → pemilihan ambang dari OOF → keputusan alarm → evaluasi '
            'dan umpan balik. Setiap tahap dapat diperiksa ulang karena parameter, '
            'split, dan ambang disimpan.')
    lap.par('Celah yang ingin diisi bukan sekadar “membuat model”. Banyak model '
            'dapat mencapai akurasi tinggi pada data tidak seimbang tanpa berguna '
            'untuk kelas minoritas. Celah metodologisnya adalah cara mengevaluasi '
            'dan memilih titik operasi secara jujur pada sampel kecil. Celah '
            'praktisnya adalah belum adanya alat bantu penyaringan berkas notaris '
            'yang mempertimbangkan beban pemeriksaan staf. Tugas 06 menjawab sebagian '
            'celah itu dengan evaluasi lengkap, threshold OOF, dan Optuna, sekaligus '
            'menunjukkan batas yang masih tersisa.')

    # ==================================================================
    # BAB III
    # ==================================================================
    lap.h2('E.3 BAB III — METODOLOGI DAN EKSPERIMEN')
    lap.h3('3.1 Metode CRISP-DM')
    lap.par('Penelitian memakai CRISP-DM karena alurnya cocok untuk proyek data '
            'yang dimulai dari masalah operasional, bukan dari algoritma. Enam fase '
            'CRISP-DM dipetakan pada kegiatan Tugas 06 seperti Tabel 20.')
    lap.tabel(
        ['Fase CRISP-DM', 'Kegiatan pada penelitian ini', 'Luaran'],
        [['Business understanding', 'Merumuskan masalah keterlambatan berkas, '
          'tujuan recall/F2, dan batasan operasional', 'Rumusan masalah dan kriteria '
          'keberhasilan'],
         ['Data understanding', 'Audit 169 berkas, label, kategori, tanggal, dan '
          'kualitas data', 'Tabel audit dan statistik deskriptif'],
         ['Data preparation', 'Pembentukan target, fitur awal, split stratifikasi, '
          'imputasi, one-hot encoding', 'Pipeline dan split 135/34'],
         ['Modeling', 'Decision Tree baseline, Optuna 30 trial, Stratified 5-Fold CV',
          'Parameter terbaik dan riwayat trial'],
         ['Evaluation', 'Confusion matrix, metrik per kelas, ROC/PR, threshold OOF, '
          'analisis FP/FN', 'Tabel dan grafik evaluasi'],
         ['Deployment', 'Prototipe Tugas 05; Tugas 06 menilai kesiapan pakai',
          'Rekomendasi operasional dan batasan']],
        widths=[1.35, 3.1, 1.95], font=8.5,
        aligns=['l', 'l', 'l'],
        caption='Tabel 20. Pemetaan CRISP-DM pada penelitian Tugas 06.')

    lap.h3('3.2 Dataset dan Variabel')
    lap.tabel(
        ['Variabel', 'Tipe', 'Peran', 'Ketersediaan saat prediksi'],
        [['id_berkas', 'Teks', 'Identitas', 'Ada, tetapi tidak menjadi prediktor'],
         ['tgl_masuk', 'Tanggal', 'Turunan fitur', 'Ada'],
         ['tgl_selesai', 'Tanggal', 'Pembentuk target', 'Tidak boleh dipakai'],
         ['tgl_rups', 'Tanggal', 'Fitur ada_rups', 'Ada, boleh kosong'],
         ['kategori_akta', 'Kategorik', 'Prediktor', 'Ada'],
         ['jumlah_penghadap', 'Numerik', 'Prediktor', 'Ada'],
         ['sla_hari', 'Numerik', 'Prediktor', 'Ada'],
         ['no_urut, no_bulanan', 'Numerik', 'Identitas', 'Tidak dipakai'],
         ['tgl_akta', 'Tanggal', 'Tidak dipakai', 'Tidak dipakai'],
         ['durasi, terlambat', 'Numerik', 'Turunan target', 'Tidak boleh dipakai']],
        widths=[1.35, 1.0, 1.6, 2.45], font=8.5,
        aligns=['l', 'l', 'l', 'l'],
        caption='Tabel 21. Variabel dataset dan perannya dalam model.')
    lap.par('Dataset memuat 169 berkas dengan 33 positif. Kategori PKR_PT '
            'merupakan kategori terbanyak (66 berkas), diikuti AJB_Saham (24), '
            'Waris_Wasiat (14), Kuasa (13), dan PPJB (9). Rentang tanggal masuk '
            'adalah 18 April 2024 sampai 2 Oktober 2026. Jumlah penghadap berkisar '
            '1–14 orang, dan SLA berkisar 5–40 hari. Seluruh nilai dipertahankan '
            'seperti pada CSV sumber.')

    lap.h3('3.3 Preprocessing')
    lap.par('Pipeline preprocessing terdiri atas tiga bagian. Fitur numerik '
            '(jumlah_penghadap, sla_hari, antrean_berjalan, ada_rups, bulan_sin, '
            'bulan_cos) diimputasi dengan median. Fitur kategorik (kategori_akta, '
            'hari_masuk) diimputasi dengan nilai paling sering, lalu di-one-hot '
            'dengan handle_unknown=ignore. Decision Tree tidak memerlukan '
            'standardisasi, sehingga scaling tidak dipakai.')
    lap.par('Seluruh preprocessing berada di dalam Pipeline. Pada setiap lipatan '
            'CV, imputer dan encoder hanya dipelajari dari lipatan latih. Data uji '
            'tidak dipakai untuk mempelajari kategori, median, atau parameter apa '
            'pun. Kolom tgl_selesai, durasi, terlambat, no_urut, no_bulanan, dan '
            'tgl_akta tidak masuk matriks prediktor.')

    lap.h3('3.4 Feature Engineering')
    lap.par('Empat kelompok fitur diturunkan dari tanggal dan histori. Pertama, '
            'antrean_berjalan menghitung jumlah berkas historis yang masuk sebelum '
            'hari penerimaan dan belum selesai pada awal hari itu. Berkas yang '
            'selesai pada hari yang sama masih dihitung terbuka pada awal hari. '
            'Kedua, ada_rups bernilai 1 bila tanggal RUPS tersedia dan tidak '
            'melewati tanggal masuk. Ketiga, bulan_sin dan bulan_cos mengubah bulan '
            'menjadi dua koordinat siklik. Keempat, hari_masuk mengubah tanggal '
            'menjadi nama hari.')
    lap.par('Antrean dihitung dari snapshot histori yang tersedia saat model '
            'di-fit. Pada Tugas 05, snapshot train berisi 135 catatan. Snapshot itu '
            'bukan inventaris seluruh antrean kantor, sehingga fitur antrean perlu '
            'dibaca sebagai proxy beban, bukan angka resmi. Jika kantor memberikan '
            'snapshot yang lebih lengkap, transformer dapat memakai snapshot itu '
            'tanpa melatih ulang pohon.')

    lap.h3('3.5 Model dan Ruang Hiperparameter')
    lap.par('Model yang dipakai tetap DecisionTreeClassifier agar hasil Tugas 06 '
            'dapat dibandingkan dengan Tugas 04–05. Baseline memakai max_depth=4, '
            'min_samples_leaf=15, min_samples_split=2, ccp_alpha=0, dan '
            'class_weight=None. Ruang pencarian Optuna memperluas nilai tersebut '
            'seperti pada Tabel 14. Algoritma lain tidak diuji karena pertanyaan '
            'penelitian adalah apakah optimasi hiperparameter meningkatkan model '
            'yang sudah dipilih, bukan apakah algoritma lain lebih baik.')
    lap.par('Pemilihan Decision Tree juga mempertimbangkan interpretasi. Staf '
            'kantor perlu memahami mengapa suatu berkas ditandai. Pohon dapat '
            'diterjemahkan menjadi aturan if–then, walaupun pada pohon yang lebih '
            'dalam aturan itu menjadi lebih panjang. Pada penelitian lanjutan, '
            'perbandingan dengan Random Forest atau gradient boosting dapat '
            'dilakukan asalkan memakai split dan metrik yang sama.')

    lap.h3('3.6 Strategi Validasi')
    lap.par('Data dibagi 80:20 secara stratifikasi dengan random_state=42. Hasilnya '
            '135 train (26 positif) dan 34 test (7 positif). Pembagian ini sama '
            'dengan Tugas 05. Pada train, Stratified 5-Fold CV dengan shuffle dan '
            'random_state=42 dipakai untuk evaluasi dan Optuna. Prediksi OOF dari '
            'lima lipatan dipakai memilih ambang. Data test hanya dipakai setelah '
            'parameter dan ambang dikunci.')
    lap.par('Karena data test sudah pernah dipakai pada Tugas 04–05, hasilnya bukan '
            'validasi yang sepenuhnya independen. Untuk mengurangi risiko '
            'overclaim, laporan menyajikan CV dan test secara terpisah, tidak '
            'memilih parameter dari test, dan tidak mengubah ambang setelah melihat '
            'test. Validasi yang lebih kuat memerlukan data periode baru.')

    lap.h3('3.7 Prosedur Optuna')
    lap.par(f'Optuna dijalankan 30 trial dengan TPE, seed 42, dan 8 trial awal '
            f'acak. Setiap trial dinilai dengan Stratified 5-Fold CV pada train dan '
            f'objective Macro F1. Trial terbaik adalah trial ke-{opt["best_trial"]} '
            f'dengan Macro F1 {f(opt["best_value_cv_macro_f1"])}. Parameter terbaik '
            'disimpan dan dipakai untuk melatih ulang model pada seluruh train. '
            'Riwayat 30 trial disimpan dalam CSV agar dapat diperiksa ulang.')

    lap.h3('3.8 Prosedur Threshold Tuning')
    lap.par('Skor OOF train diuji pada ambang 0,01–0,99. Untuk setiap ambang '
            'dihitung TP, TN, FP, FN, precision, recall, F1, F2, dan proporsi alarm. '
            'Ambang dengan F2 tertinggi dipilih; jika seri, precision lebih tinggi '
            'dan ambang lebih besar dipilih. Empat ambang dilaporkan: 0,50, 0,25 '
            '(F1 OOF), 0,19 (F2 OOF dengan alarm ≤50%), dan 0,05 (F2 OOF). Setelah '
            'ambang dikunci, barulah data uji dievaluasi.')

    lap.h3('3.9 Metrik dan Kriteria Keberhasilan')
    lap.par('Kriteria berikut dipakai untuk membaca apakah model cukup berguna '
            'sebagai alat penyaringan awal. Kriteria ini bersifat operasional, '
            'bukan uji statistik. Tabel 22 membandingkan target dengan hasil pada '
            'ambang 0,05 dan 0,19.')
    lap.tabel(
        ['Kriteria', 'Target', 'Hasil @0,05', 'Hasil @0,19', 'Status'],
        [['Recall keterlambatan', '≥ 0,70', f(met['recall']), '0,571',
          'Terpenuhi hanya pada 0,05'],
         ['Precision keterlambatan', '≥ 0,30', f(met['precision']), '0,174',
          'Belum terpenuhi'],
         ['F1 keterlambatan', '≥ 0,40', f(met['f1']), '0,267',
          'Belum terpenuhi'],
         ['Proporsi alarm', '≤ 0,50', pct(met['alert_rate']), '67,6%',
          'Belum terpenuhi'],
         ['PR-AUC (AP)', '> 0,306', f(met['average_precision']), '0,190',
          'Belum terpenuhi'],
         ['ROC-AUC', '≥ 0,65', f(met['roc_auc']), '0,413',
          'Belum terpenuhi']],
        widths=[1.55, 0.9, 1.0, 1.0, 1.95], font=8.5,
        aligns=['l', 'c', 'c', 'c', 'l'],
        caption='Tabel 22. Kriteria keberhasilan penyaringan dan hasil Tugas 06.')
    lap.par('Hanya kriteria recall yang terpenuhi, itu pun pada ambang 0,05. '
            'Precision, F1, proporsi alarm, PR-AUC, dan ROC-AUC belum memenuhi '
            'target. Kesimpulannya, model belum layak untuk keputusan otomatis. '
            'Model masih dapat dipakai untuk penelitian dan uji terbatas dengan '
            'pemeriksaan staf, tetapi tidak untuk menggantikan penilaian staf.')

    lap.h3('3.10 Reproduksibilitas')
    lap.par('Seluruh eksperimen dijalankan dengan seed 42. Dataset memiliki SHA-256 '
            '686aa269511d6eb26ad661ebfde499ffbfd64383de4e84e93ea54ab23905785b. '
            'Skrip utama adalah eksperimen_tugas_06/eksperimen_tugas06.py. Hasil '
            'trial, parameter, threshold, prediksi, metrik, dan gambar disimpan di '
            'folder hasil. Model disimpan dalam format joblib. Versi pustaka dicatat '
            'pada hasil/log/environment.json. Perintah menjalankan ulang ada pada '
            'Lampiran C.', rata='left')
    lap.par('Laporan memakai angka dari file JSON dan CSV hasil eksekusi. Tidak ada '
            'angka yang diketik manual tanpa rujukan file. Jika eksperimen dijalankan '
            'ulang pada versi pustaka yang berbeda, angka dapat sedikit berubah; '
            'karena itu versi lingkungan ikut dicatat.')

    lap.h3('3.11 Etika, Privasi, dan Batasan')
    lap.par('Data yang dianalisis adalah rekap berkas kantor. Laporan tidak '
            'menampilkan nama klien atau isi akta. ID berkas dipakai untuk '
            'penelusuran teknis. Model diposisikan sebagai alat bantu, bukan '
            'pengganti kewenangan Notaris/PPAT. Tidak ada keputusan hukum atau '
            'penolakan layanan yang diotomatiskan.')
    lap.par('Batasan utama penelitian ini adalah sampel kecil (169 berkas, 7 positif '
            'di test), data uji yang sudah pernah dilihat, fitur awal yang terbatas, '
            'dan tidak adanya data biaya serta kapasitas. Model juga hanya satu '
            'keluarga, yaitu Decision Tree. Hasil pada kantor ini tidak dapat '
            'langsung digeneralisasi ke kantor lain. Pengembangan berikutnya perlu '
            'menambah fitur kelengkapan dokumen, instansi tujuan, dan waktu '
            'pemrosesan, serta menguji pada periode baru.')

    lap.h3('3.12 Pemetaan ke Tugas dan Bukti')
    lap.par('Tabel 23 menunjukkan bagaimana bahan Tugas 01–06 dipakai dalam '
            'proposal dan di mana buktinya dapat diperiksa.')
    lap.tabel(
        ['Bab', 'Substansi', 'Sumber tugas', 'Bukti pada Tugas 06'],
        [['Bab I', 'Latar belakang, identifikasi masalah, rumusan, tujuan, batasan',
          'Tugas 01–02 dan Tugas 05', 'Bagian E.1; audit dataset; hasil evaluasi'],
         ['Bab II', 'Teori Decision Tree, metrik, threshold, Optuna, dua paper',
          'Tugas 04 dan materi P01–P05', 'Bagian E.2; Tabel 19; referensi IEEE'],
         ['Bab III', 'CRISP-DM, preprocessing, fitur, CV, Optuna, OOF, threshold, '
          'evaluasi', 'Tugas 03–06', 'Bagian E.3; Tabel 20–22; kode dan hasil']],
        widths=[0.65, 2.2, 1.55, 2.0], font=8.5,
        aligns=['c', 'l', 'l', 'l'],
        caption='Tabel 23. Pemetaan Bab I–III ke tugas sebelumnya dan bukti Tugas 06.')
