#!/usr/bin/env python3
"""Menyusun Proposal UTS Pembelajaran Mesin Kelompok 02.

Masukan : referensi/Template_Proposal_UTS (disalin ke folder ini)
Keluaran: PROPOSAL_UTS_ML_KELOMPOK_02_NOTARIS_PPAT.docx

Seluruh angka diambil dari:
- eksperimen_tugas_06/hasil/data/*.json
- proposal_uts/hasil/analisis_proposal.json (benchmark baseline & ambang)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import (WD_ALIGN_PARAGRAPH, WD_LINE_SPACING,
                            WD_TAB_ALIGNMENT, WD_TAB_LEADER)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

BASE = Path(__file__).resolve().parent
PROYEK = BASE.parent
TEMPLATE = BASE / 'template_proposal_uts.docx'
OUT = BASE / 'PROPOSAL_UTS_ML_KELOMPOK_02_NOTARIS_PPAT.docx'
HASIL = json.loads((BASE / 'hasil' / 'analisis_proposal.json').read_text())
GAMBAR = BASE / 'gambar'
GRAFIK = PROYEK / 'eksperimen_tugas_06' / 'hasil' / 'grafik'

JUDUL = ('Prediksi Keterlambatan Penyelesaian Akta pada Kantor Notaris & PPAT '
         'Aries Buwana Menggunakan Decision Tree Terpruning dengan Optimasi '
         'Optuna dan Kalibrasi Ambang Batas')
JUDUL_BARIS = ('PROPOSAL RISET REKAYASA MODEL MACHINE LEARNING:\n'
               'Prediksi Keterlambatan Penyelesaian Akta pada Kantor Notaris & '
               'PPAT Aries Buwana Menggunakan Decision Tree Terpruning dengan '
               'Optimasi Optuna dan Kalibrasi Ambang Batas')

TNR = 'Times New Roman'


# ---------------------------------------------------------------------------
# Utilitas tata letak
# ---------------------------------------------------------------------------
def _hapus_run(p):
    for r in list(p.runs):
        r._r.getparent().remove(r._r)


def fmt(p, text='', size=12, bold=False, italic=False,
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=1.27, space_before=0,
        space_after=6, line=1.5, warna=None):
    _hapus_run(p)
    run = p.add_run(text)
    run.font.name = TNR
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), TNR)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if warna:
        run.font.color.rgb = RGBColor(*warna)
    pf = p.paragraph_format
    pf.alignment = align
    pf.left_indent = None
    pf.first_line_indent = Cm(indent) if indent else None
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    return p


def tautan(par, url):
    r_id = par.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement('w:hyperlink')
    h.set(qn('r:id'), r_id)
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    font = OxmlElement('w:rFonts')
    font.set(qn('w:ascii'), TNR)
    font.set(qn('w:hAnsi'), TNR)
    warna = OxmlElement('w:color')
    warna.set(qn('w:val'), '0563C1')
    u = OxmlElement('w:u')
    u.set(qn('w:val'), 'single')
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), '20')
    rPr.append(font)
    rPr.append(warna)
    rPr.append(u)
    rPr.append(sz)
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = url
    r.append(rPr)
    r.append(t)
    h.append(r)
    par._p.append(h)


def par_baru(anchor):
    el = OxmlElement('w:p')
    anchor._p.addnext(el)
    return Paragraph(el, anchor._parent)


def sisip_blok(anchor, blok, sebelum=False):
    """Sisipkan daftar blok setelah (atau sebelum) sebuah paragraf."""
    kursor = anchor
    hasil = []
    for b in blok:
        jenis = b[0]
        if jenis == 'p':
            p = par_baru(kursor)
            fmt(p, b[1])
        elif jenis == 'pc':
            p = par_baru(kursor)
            fmt(p, b[1], align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)
        elif jenis == 'b':
            p = par_baru(kursor)
            fmt(p, '• ' + b[1], indent=0)
            p.paragraph_format.left_indent = Cm(1.27)
            p.paragraph_format.first_line_indent = Cm(-0.63)
        elif jenis == 'n':
            p = par_baru(kursor)
            fmt(p, b[1], indent=0)
            p.paragraph_format.left_indent = Cm(1.27)
            p.paragraph_format.first_line_indent = Cm(-0.63)
        elif jenis == 'img':
            p = par_baru(kursor)
            fmt(p, '', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0,
                space_before=6, space_after=3)
            p.add_run().add_picture(str(b[1]), width=Cm(b[2]))
        elif jenis == 'cap':
            p = par_baru(kursor)
            fmt(p, b[1], size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER,
                indent=0, space_after=10, line=1.0)
        elif jenis == 'rumus':
            p = par_baru(kursor)
            fmt(p, b[1], italic=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                indent=0, space_before=2, space_after=4, line=1.0)
        elif jenis == 'link':
            p = par_baru(kursor)
            fmt(p, '', indent=0, space_after=4, line=1.15)
            tautan(p, b[1])
        elif jenis == 'h':
            p = par_baru(kursor)
            fmt(p, b[1], size=12, bold=True,
                align=WD_ALIGN_PARAGRAPH.LEFT, indent=0,
                space_before=10, space_after=4)
        elif jenis == 'note':
            p = par_baru(kursor)
            fmt(p, b[1], size=9, italic=True,
                align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=0, space_after=8,
                line=1.0)
        elif jenis == 'pagebreak':
            p = par_baru(kursor)
            p.add_run().add_break(6)  # WD_BREAK.PAGE
        else:
            raise ValueError(jenis)
        kursor = p
        hasil.append(p)
    return kursor


def sisip_setelah_tabel(t, blok):
    el = OxmlElement('w:p')
    t._tbl.addnext(el)
    anchor = Paragraph(el, t._parent)
    return ganti_blok(anchor, blok)


def ganti_blok(anchor, blok):
    """Ganti paragraf anchor dengan blok; blok pertama mengisi anchor."""
    jenis, isi = blok[0][0], blok[0][1]
    if jenis == 'p':
        fmt(anchor, isi)
    elif jenis == 'pc':
        fmt(anchor, isi, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)
    elif jenis == 'b':
        fmt(anchor, '• ' + isi, indent=0)
        anchor.paragraph_format.left_indent = Cm(1.27)
        anchor.paragraph_format.first_line_indent = Cm(-0.63)
    elif jenis == 'n':
        fmt(anchor, isi, indent=0)
        anchor.paragraph_format.left_indent = Cm(1.27)
        anchor.paragraph_format.first_line_indent = Cm(-0.63)
    else:
        fmt(anchor, '', indent=0, space_after=0, line=1.0)
        return sisip_blok(anchor, blok)
    return sisip_blok(anchor, blok[1:])


def cari(teks, mulai=0):
    for p in DOC.paragraphs[mulai:]:
        if p.text.strip().startswith(teks):
            return p
    raise LookupError(teks[:60])


def isi_tabel(t, data, lebar=None, font=9, header=True, tengah=()):
    while len(t.rows) < len(data):
        t.add_row()
    while len(t.rows) > len(data):
        t._tbl.remove(t.rows[-1]._tr)
    for i, baris in enumerate(data):
        for j, nilai in enumerate(baris):
            sel = t.cell(i, j)
            sel.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = sel.paragraphs[0]
            fmt(p, str(nilai), size=font,
                bold=(header and i == 0),
                align=(WD_ALIGN_PARAGRAPH.CENTER if (i == 0 or j in tengah)
                       else WD_ALIGN_PARAGRAPH.LEFT),
                indent=0, space_before=1, space_after=1, line=1.0)
            if header and i == 0:
                _shade(sel, 'DCE6F1')
            if lebar:
                sel.width = Cm(lebar[j])
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    _bingkai(t)


def _shade(sel, warna):
    tcPr = sel._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), warna)
    tcPr.insert_element_before(
        shd, 'w:noWrap', 'w:tcMar', 'w:textDirection', 'w:tcFitText',
        'w:vAlign', 'w:hideMark')


def _bingkai(t):
    tblPr = t._tbl.tblPr
    for lama in tblPr.findall(qn('w:tblBorders')):
        tblPr.remove(lama)
    b = OxmlElement('w:tblBorders')
    for tepi in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{tepi}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '4')
        el.set(qn('w:space'), '0')
        el.set(qn('w:color'), '808080')
        b.append(el)
    tblPr.insert_element_before(
        b, 'w:shd', 'w:tblLayout', 'w:tblCellMar', 'w:tblLook',
        'w:tblCaption', 'w:tblDescription')


def hapus_tabel_petunjuk():
    n = 0
    for t in list(DOC.tables):
        if 'PETUNJUK PENYUSUNAN' in t._tbl.xml or '💡' in t._tbl.xml:
            t._tbl.getparent().remove(t._tbl)
            n += 1
    return n


def nomor_halaman_footer():
    for sec in DOC.sections:
        for p in sec.footer.paragraphs:
            fmt(p, '', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0,
                space_after=0, line=1.0)
            run = p.add_run()
            run.font.name = TNR
            run.font.size = Pt(9)
            f1 = OxmlElement('w:fldChar')
            f1.set(qn('w:fldCharType'), 'begin')
            it = OxmlElement('w:instrText')
            it.set(qn('xml:space'), 'preserve')
            it.text = ' PAGE '
            f2 = OxmlElement('w:fldChar')
            f2.set(qn('w:fldCharType'), 'end')
            run._r.append(f1)
            run._r.append(it)
            run._r.append(f2)


# ---------------------------------------------------------------------------
# Isi
# ---------------------------------------------------------------------------
def bab_1():
    p = cari('[Tuliskan uraian Latar Belakang')
    ganti_blok(p, [
        ('p', 'Kantor Notaris dan Pejabat Pembuat Akta Tanah (PPAT) Aries Buwana '
              'di Jakarta Barat melayani pembuatan akta otentik untuk kebutuhan '
              'perseroan, peralihan hak atas tanah, waris, kuasa, dan perjanjian '
              'lain. Setiap berkas yang diterima memiliki tenggat layanan yang '
              'berbeda menurut jenis dan kompleksitas aktanya. Dari 169 berkas, '
              '144 berkas memiliki SLA 5 sampai 14 hari, sedangkan 25 berkas '
              'yang melibatkan proses panjang memiliki SLA 21 sampai 40 hari. '
              'Tenggat ini tertuang dalam komitmen layanan kantor dan, pada '
              'banyak transaksi, terkait langsung dengan tenggat bank, notaris '
              'mitra, atau instansi tempat akta akan digunakan.'),
        ('p', 'Dalam praktik, penyelesaian berkas tidak hanya ditentukan oleh '
              'kelengkapan dokumen. Antrean berkas yang sedang berjalan, jumlah '
              'penghadap yang harus hadir, jadwal RUPS, dan pola kedatangan pada '
              'hari atau bulan tertentu turut memengaruhi lama pengerjaan. '
              'Selama ini prioritas ditentukan oleh pengalaman staf dan '
              'pemeriksaan daftar kerja harian. Cara tersebut efektif untuk '
              'berkas yang sudah diketahui mendesak, tetapi belum memberikan '
              'peringatan dini terhadap berkas yang berpotensi melewati tenggat '
              'sejak hari pertama diterima. Akibatnya, keterlambatan baru '
              'disadari ketika tenggat sudah dekat atau telah terlewati.'),
        ('p', 'Data operasional yang dihimpun dari 169 berkas pada periode 18 '
              'April 2024 sampai 12 Oktober 2026 menunjukkan bahwa 33 berkas '
              '(19,5 persen) melewati tenggat layanan, sedangkan 136 berkas '
              '(80,5 persen) selesai tepat waktu. Ketidakseimbangan kelas ini '
              'membuat akurasi menjadi ukuran yang menyesatkan. Model yang selalu '
              'memprediksi "tepat waktu" akan memperoleh akurasi 80,5 persen, '
              'tetapi tidak menemukan satu pun berkas terlambat; inilah bentuk '
              'nyata accuracy paradox pada data administrasi. Oleh karena itu, '
              'evaluasi harus bertumpu pada precision, recall, F1, F2, ROC-AUC, '
              'dan PR-AUC, bukan pada akurasi semata.'),
        ('p', 'Pada Tugas 04 sampai Tugas 06, kelompok ini telah membangun '
              'pipeline prediksi berbasis Decision Tree dengan cost-complexity '
              'pruning dan optimasi hiperparameter Optuna. Hasil validasi silang '
              'Stratified 5-Fold menunjukkan kenaikan Macro F1 dari 0,4467 '
              'menjadi 0,5532. Meskipun demikian, pada ambang keputusan default '
              '0,50 model tidak menandai satu pun dari tujuh berkas terlambat di '
              'data uji. Probabilitas keluaran model terkonsentrasi pada nilai '
              'rendah sehingga ambang 0,50 terlalu konservatif untuk konteks '
              'keterlambatan akta. Fakta ini menunjukkan bahwa peningkatan '
              'kualitas peringkat model belum otomatis menghasilkan keputusan '
              'operasional yang berguna.'),
        ('p', 'Proposal ini mengangkat masalah tersebut menjadi penelitian '
              'terpadu dengan tiga kontribusi. Pertama, pipeline pra-pemrosesan '
              'dirancang bebas kebocoran data, termasuk pembentukan fitur antrean '
              'yang hanya memakai histori data latih. Kedua, optimasi '
              'hiperparameter dilakukan dengan Bayesian optimization berbasis '
              'Tree-structured Parzen Estimator (TPE) dan validasi silang '
              'bertatar, bukan pencarian manual. Ketiga, ambang keputusan '
              'dikalibrasi dari prediksi out-of-fold data latih dengan '
              'mempertimbangkan biaya asimetris antara false negative dan false '
              'positive, lalu dikunci sebelum data uji dievaluasi. Dengan '
              'demikian, penelitian tidak berhenti pada model yang "lebih tinggi '
              'skornya", tetapi menghasilkan prosedur keputusan yang dapat '
              'dipertanggungjawabkan dan siap diuji pada tahap UAS.'),
    ])

    p = cari('[Tuliskan identifikasi masalah teknis')
    ganti_blok(p, [
        ('p', 'Berdasarkan konteks di atas, masalah teknis yang diidentifikasi '
              'dalam penelitian ini adalah sebagai berikut.'),
        ('n', '1. Ketidakseimbangan kelas. Hanya 33 dari 169 berkas (19,5 persen) '
              'berlabel terlambat. Pada kondisi ini, model yang mengandalkan '
              'akurasi akan condong ke kelas mayoritas dan gagal menangkap '
              'keterlambatan.'),
        ('n', '2. Ambang keputusan tidak sesuai konteks. Ambang default 0,50 '
              'menghasilkan recall 0,000 pada data uji, artinya tujuh berkas '
              'terlambat tidak terdeteksi sama sekali. Di sisi lain, ambang yang '
              'terlalu rendah dapat membanjiri staf dengan alarm palsu.'),
        ('n', '3. Risiko kebocoran data. Fitur turunan seperti antrean berkas dan '
              'durasi penyelesaian berpotensi memakai informasi masa depan bila '
              'dihitung dari seluruh dataset. Tanpa pembatasan, skor validasi '
              'akan terlalu optimistis dan tidak dapat direproduksi.'),
        ('n', '4. Hiperparameter belum dioptimasi secara sistematis. Konfigurasi '
              'pohon pada Tugas 04 dan Tugas 05 ditetapkan secara manual. Pada '
              'data kecil, kedalaman dan jumlah minimum sampel per daun sangat '
              'menentukan kestabilan model, sehingga pencarian Bayesian menjadi '
              'diperlukan.'),
        ('n', '5. Pemilihan ambang berpotensi memakai data uji. Bila ambang '
              'dipilih dengan memaksimalkan skor pada data uji, laporan akan '
              'mengalami optimistic bias. Penelitian ini menetapkan bahwa '
              'pemilihan ambang hanya boleh memakai prediksi out-of-fold data '
              'latih.'),
        ('n', '6. Hasil model belum diterjemahkan menjadi prosedur kerja. '
              'Kantor membutuhkan ambang yang dapat dioperasikan, besaran beban '
              'alarm yang realistis, dan rencana integrasi ke antarmuka '
              'pelayanan, bukan sekadar berkas model.'),
    ])

    p = cari('Berdasarkan latar belakang masalah yang telah diuraikan')
    ganti_blok(p, [
        ('p', 'Berdasarkan latar belakang dan identifikasi masalah, rumusan '
              'masalah penelitian ini dijabarkan melalui tiga pertanyaan '
              'penelitian (Research Questions) berikut.'),
        ('p', 'RQ1: Bagaimana merancang pipeline pra-pemrosesan dan pemodelan '
              'yang bebas kebocoran data untuk memprediksi keterlambatan '
              'penyelesaian akta pada 169 berkas Kantor Notaris & PPAT Aries '
              'Buwana, dan algoritma manakah yang memberikan Macro F1 terbaik '
              'pada validasi silang Stratified 5-Fold?'),
        ('p', 'RQ2: Seberapa besar peningkatan Macro F1 dan ROC-AUC yang '
              'diperoleh dari optimasi hiperparameter Decision Tree menggunakan '
              'Optuna TPE dengan 30 trial dibandingkan konfigurasi default pada '
              'Tugas 04/05?'),
        ('p', 'RQ3: Ambang keputusan manakah yang memberikan kompromi terbaik '
              'antara recall kelas terlambat dan beban alarm pada kapasitas '
              'pemeriksaan kantor, dan bagaimana kinerjanya ketika diuji pada '
              '34 berkas yang tidak dipakai memilih ambang?'),
    ])

    p = cari('Tujuan yang hendak dicapai dalam penelitian ini')
    ganti_blok(p, [
        ('p', 'Tujuan yang hendak dicapai dalam penelitian ini adalah sebagai '
              'berikut.'),
        ('n', '1. Membangun pipeline pra-pemrosesan dan pemodelan yang bebas '
              'kebocoran data untuk klasifikasi keterlambatan akta, termasuk '
              'pembentukan fitur antrean, indikator RUPS, dan encoding siklik '
              'bulan (menjawab RQ1).'),
        ('n', '2. Membandingkan performa model baseline (Logistic Regression dan '
              'Decision Tree) dengan model ensemble (Random Forest, Gradient '
              'Boosting, dan Histogram Gradient Boosting) pada protokol evaluasi '
              'yang sama (menjawab RQ1).'),
        ('n', '3. Mengoptimasi hiperparameter Decision Tree dengan Optuna TPE dan '
              'Stratified 5-Fold Cross Validation, lalu mengukur peningkatan '
              'Macro F1 dan ROC-AUC terhadap konfigurasi default (menjawab RQ2).'),
        ('n', '4. Mengkalibrasi ambang keputusan dari prediksi out-of-fold data '
              'latih, mengevaluasi beberapa ambang alternatif, dan menguji '
              'ambang terpilih pada data uji yang belum pernah dipakai memilih '
              'ambang (menjawab RQ3).'),
        ('n', '5. Menyusun cetak biru deployment model ke antarmuka Streamlit '
              'beserta rencana pemantauan, agar hasil penelitian dapat '
              'dilanjutkan pada Bab IV dan Bab V menuju UAS.'),
    ])

    p = cari('Hasil penelitian rekayasa model pembelajaran mesin ini')
    ganti_blok(p, [
        ('p', 'Hasil penelitian rekayasa model pembelajaran mesin ini diharapkan '
              'memberikan kontribusi nyata pada tiga ranah berikut.'),
        ('b', 'Manfaat teoretis: memberikan bukti empiris bahwa pada dataset '
              'tabular berukuran kecil dengan kelas minoritas di bawah 20 persen, '
              'pohon keputusan yang dipangkas dan dioptimasi secara Bayesian '
              'dapat menandingi model ensemble yang lebih kompleks, serta '
              'menegaskan bahwa kualitas peringkat (ROC-AUC/PR-AUC) dan kualitas '
              'keputusan (F1/F2 pada ambang tertentu) adalah dua hal yang berbeda.'),
        ('b', 'Manfaat metodologis: menyediakan contoh protokol evaluasi yang '
              'memisahkan pemilihan ambang (out-of-fold data latih) dari '
              'pengujian akhir (data uji terkunci), sehingga dapat dipakai sebagai '
              'acuan bagi penelitian serupa yang rentan terhadap optimistic bias.'),
        ('b', 'Manfaat terapan: menghasilkan daftar prioritas berkas berisiko '
              'yang dapat dipakai staf kantor untuk melakukan pemeriksaan awal, '
              'beserta perkiraan beban alarm pada setiap ambang, sehingga '
              'keputusan penambahan kapasitas dapat dibahas dengan angka, bukan '
              'perkiraan.'),
    ])

    p = cari('Agar penelitian terarah dan terukur')
    ganti_blok(p, [
        ('p', 'Agar penelitian terarah dan terukur, ruang lingkup penelitian '
              'dibatasi pada hal-hal berikut.'),
        ('n', '1. Dataset berasal dari rekapitulasi internal Kantor Notaris & PPAT '
              'Aries Buwana sebanyak 169 berkas, terdiri atas 10 atribut mentah '
              'dan 2 atribut turunan (durasi dan label). Data mencakup periode '
              '18 April 2024 sampai 12 Oktober 2026.'),
        ('n', '2. Label ditetapkan secara deterministik, yaitu terlambat = 1 bila '
              'selisih hari antara tanggal selesai dan tanggal masuk lebih besar '
              'dari SLA hari pada berkas tersebut. Label tidak diubah, tidak '
              'diseimbangkan ulang, dan tidak direvisi manual.'),
        ('n', '3. Fitur yang dipakai model hanya fitur yang tersedia pada saat '
              'berkas masuk, yaitu jumlah penghadap, SLA hari, antrean berjalan, '
              'indikator RUPS, encoding siklik bulan, kategori akta, dan hari '
              'masuk. Fitur tanggal selesai dan durasi hari tidak dipakai karena '
              'merupakan akibat dari label.'),
        ('n', '4. Pembagian data memakai train-test split 80:20 dengan stratifikasi '
              'dan random_state 42, menghasilkan 135 berkas latih (26 positif) '
              'dan 34 berkas uji (7 positif). Pembagian ini sama dengan Tugas 04 '
              'sampai Tugas 06 agar hasil dapat dibandingkan.'),
        ('n', '5. Optimasi hiperparameter dibatasi pada ruang pencarian Decision '
              'Tree (criterion, max_depth, min_samples_leaf, min_samples_split, '
              'ccp_alpha, class_weight, max_features) dengan 30 trial Optuna TPE '
              'dan Stratified 5-Fold Cross Validation pada data latih.'),
        ('n', '6. Ambang keputusan yang dievaluasi adalah 0,50; 0,30; 0,25; 0,19; '
              'dan 0,05. Ambang 0,05 dipilih dari kurva F2 out-of-fold, sedangkan '
              '0,19 adalah guardrail operasional dengan beban alarm di bawah 50 '
              'persen. Data uji tidak dipakai untuk memilih ambang.'),
        ('p', 'Penelitian ini memiliki batasan yang perlu dinyatakan terbuka. Data '
              'uji 34 berkas sudah pernah dipakai pada Tugas 04 dan Tugas 05, '
              'sehingga bukan holdout yang sepenuhnya buta; hasilnya harus dibaca '
              'sebagai evaluasi konsistensi, bukan uji generalisasi independen. '
              'Jumlah data kecil dan berasal dari satu kantor, sehingga temuan '
              'tidak dapat langsung digeneralisasi ke kantor lain. Model juga '
              'diposisikan sebagai alat bantu penyaringan, bukan pengganti '
              'pertimbangan staf, Notaris, atau PPAT.'),
    ])


def bab_2():
    judul = cari('2.1 Kajian Riset Terkait')
    sisip_blok(judul, [
        ('p', 'Penelitian tentang prediksi keterlambatan administrasi banyak '
              'mengadopsi pendekatan dari domain kredit dan penagihan karena '
              'struktur masalahnya serupa: kelas minoritas yang biayanya jauh '
              'lebih besar daripada kelas mayoritas. Tabel 2.1 merangkum lima '
              'rujukan utama yang menjadi dasar perbandingan, sekaligus '
              'menunjukkan celah penelitian yang hendak diisi.'),
    ])

    isi_tabel(DOC.tables[2], [
        ['No', 'Peneliti & Tahun', 'Judul Penelitian', 'Metode / Algoritma',
         'Hasil & Metrik Kinerja', 'Kelemahan / Research Gap'],
        ['1', 'Lessmann et al. (2015) [2]',
         'Benchmarking state-of-the-art classification algorithms for credit '
         'scoring: An update of research',
         '41 algoritma, termasuk Random Forest, Gradient Boosting, dan SVM, '
         'pada 8 dataset kredit',
         'Metode ensemble pohon konsisten berada di peringkat teratas; rentang '
         'AUC sekitar 0,75 sampai 0,90',
         'Berhenti pada peringkat global; ambang keputusan dan biaya asimetris '
         'tidak dikalibrasi'],
        ['2', 'Saito & Rehmsmeier (2015) [3]',
         'The precision-recall plot is more informative than the ROC plot when '
         'evaluating binary classifiers on imbalanced datasets',
         'Analisis perbandingan kurva ROC dan kurva precision-recall pada data '
         'tidak seimbang',
         'PR-AUC lebih sensitif terhadap kelas minoritas; ROC-AUC dapat '
         'memberi kesan performa lebih baik',
         'Tidak membahas optimasi hiperparameter maupun pemilihan ambang '
         'operasional'],
        ['3', 'He & Garcia (2009) [4]',
         'Learning from imbalanced data',
         'Survei teknik sampling, cost-sensitive learning, dan ensemble untuk '
         'data tidak seimbang',
         'Mengonfirmasi akurasi tidak layak pada rasio kelas ekstrem; metrik '
         'kelas minoritas wajib dilaporkan',
         'Belum menyatukan HPO Bayesian dan kalibrasi ambang dalam satu '
         'pipeline yang dapat direproduksi'],
        ['4', 'Lipton et al. (2014) [6]',
         'Optimal thresholding of classifiers to maximize F1 measure',
         'Optimasi ambang secara analitis untuk memaksimalkan F1',
         'Ambang optimal berbeda dari 0,50 dan bergantung pada distribusi skor '
         'model',
         'Hanya membahas F1; belum mempertimbangkan F2, kapasitas alarm, dan '
         'validasi out-of-fold'],
        ['5', 'Akiba et al. (2019) [5]',
         'Optuna: A next-generation hyperparameter optimization framework',
         'Bayesian optimization dengan Tree-structured Parzen Estimator (TPE) '
         'dan pruning',
         'TPE mencapai kualitas setara grid/random search dengan biaya evaluasi '
         'jauh lebih rendah',
         'Tidak menyinggung domain administrasi maupun ambang keputusan yang '
         'biaya-sensitif'],
    ], lebar=[0.9, 2.5, 3.3, 2.6, 2.8, 2.5], font=8)

    p = cari('2.2 Paradigma Pembelajaran Mesin')
    sisip_blok(p, [
        ('p', 'Celah yang terlihat dari Tabel 2.1 bersifat konsisten: setiap '
              'penelitian menyumbang satu komponen, tetapi jarang menyatukan '
              'pipeline bebas kebocoran, optimasi Bayesian, dan kalibrasi ambang '
              'dalam satu alur yang dapat direproduksi. Penelitian ini mengisi '
              'celah tersebut pada domain administrasi notaris yang belum banyak '
              'diteliti, dengan penekanan pada pemisahan tegas antara data '
              'pemilihan ambang dan data pengujian.'),
    ])

    p = cari('[Jelaskan konsep teoretis algoritma pembelajaran mesin')
    ganti_blok(p, [
        ('p', 'Masalah dalam penelitian ini dirumuskan sebagai klasifikasi biner '
              'terarah (supervised binary classification). Untuk setiap berkas '
              'berkas i, model menerima vektor fitur x_i yang tersedia pada saat '
              'berkas masuk dan mempelajari fungsi f(x) yang memetakan berkas ke '
              'probabilitas keterlambatan p(y = 1 | x). Keputusan akhir baru '
              'dibentuk setelah probabilitas dibandingkan dengan ambang t, yaitu '
              'ŷ = 1 bila p(y = 1 | x) lebih besar atau sama dengan t. '
              'Pemisahan antara model probabilitas dan ambang keputusan ini '
              'penting karena keduanya dioptimasi dengan tujuan berbeda.'),
        ('p', 'Decision Tree dipilih sebagai model utama karena tiga alasan. '
              'Pertama, data hanya berisi 135 berkas latih dengan 26 contoh '
              'positif, sehingga model berkapasitas rendah lebih stabil daripada '
              'ensemble yang dalam. Kedua, pohon keputusan menghasilkan aturan '
              'yang dapat dibaca staf, misalnya kombinasi SLA, jumlah penghadap, '
              'dan antrean yang memicu risiko. Ketiga, kompleksitas pohon dapat '
              'dikendalikan langsung melalui kedalaman, jumlah minimum sampel per '
              'daun, dan cost-complexity pruning.'),
        ('p', 'Pohon dibangun dengan memilih pemisahan yang memaksimalkan '
              'penurunan impurity Gini. Untuk simpul dengan proporsi kelas p_k, '
              'impurity Gini didefinisikan sebagai Gini = 1 - jumlah p_k kuadrat. '
              'Setiap kandidat pemisahan dievaluasi dari penurunan impurity '
              'tertimbang, dan pemisahan dengan penurunan terbesar dipilih. '
              'Tanpa pembatasan, pohon akan tumbuh hingga menghafal data latih. '
              'Oleh karena itu digunakan prapemangkasan (max_depth, '
              'min_samples_leaf, min_samples_split) dan pascapemangkasan '
              'cost-complexity dengan parameter ccp_alpha.'),
        ('p', 'Cost-complexity pruning meminimalkan R_alpha(T) = R(T) + alpha '
              'dikali jumlah daun T, dengan R(T) sebagai error pelatihan. Nilai '
              'alpha yang lebih besar menghasilkan pohon yang lebih sederhana. '
              'Pada penelitian ini alpha tidak ditetapkan manual, tetapi '
              'dijadikan salah satu ruang pencarian Optuna. Dengan demikian, '
              'kompleksitas model dipilih berdasarkan bukti validasi silang, '
              'bukan preferensi penyusun.'),
        ('p', 'Random Forest, Gradient Boosting, dan Histogram Gradient Boosting '
              'dipakai sebagai pembanding ensemble. Random Forest membangun banyak '
              'pohon pada sampel bootstrap dan merata-ratakan probabilitasnya '
              'untuk menurunkan varians. Gradient Boosting menambahkan pohon '
              'secara berurutan untuk mengoreksi residual model sebelumnya, '
              'sedangkan Histogram Gradient Boosting mempercepat proses tersebut '
              'dengan binning fitur. Ketiganya memiliki kapasitas lebih besar, '
              'tetapi pada data kecil kapasitas tambahan dapat berubah menjadi '
              'overfitting. Karena itu perbandingan dilakukan secara empiris pada '
              'protokol yang sama, bukan diasumsikan dari literatur.'),
    ])

    p = cari('[Uraikan landasan teori teknik penanganan data mentah')
    ganti_blok(p, [
        ('p', 'Data mentah memiliki tiga persoalan utama: nilai hilang, tipe '
              'kategorikal, dan fitur waktu. Nilai hilang pada kolom numerik '
              'diimputasi dengan median karena median lebih tahan terhadap '
              'pencilan dibanding rata-rata. Kolom kategorikal diimputasi dengan '
              'nilai paling sering muncul. Seluruh proses imputasi ditempatkan '
              'di dalam pipeline dan hanya di-fit pada data latih setiap fold, '
              'sehingga statistik data uji tidak pernah merembes ke pelatihan.'),
        ('p', 'Kolom kategori akta memiliki 14 nilai, dengan PKR_PT sebagai '
              'kategori terbanyak (66 berkas), diikuti AJB_Saham (24) dan '
              'Waris_Wasiat (14). One-Hot Encoding dipakai karena kategori tidak '
              'memiliki urutan alami dan jumlahnya masih terkendali. Target '
              'encoding sengaja dihindari: pada data kecil, target encoding '
              'mudah membocorkan label ke dalam fitur bila tidak dihitung per '
              'fold, dan keuntungannya tidak sebanding dengan risikonya.'),
        ('p', 'Fitur waktu tidak diperlakukan sebagai angka linier. Bulan '
              'didekomposisi menjadi dua komponen siklik, yaitu sinus dan kosinus '
              'dari 2 pi bulan dibagi 12, agar Desember dan Januari berdekatan '
              'secara representasi. Hari masuk diubah menjadi kategori hari kerja. '
              'Fitur antrean berjalan dihitung sebagai jumlah berkas yang masih '
              'terbuka pada saat berkas baru masuk, dengan histori yang hanya '
              'diambil dari data latih. Aturan ini penting karena antrean yang '
              'dihitung dari seluruh dataset akan memuat informasi masa depan.'),
        ('p', 'Penyeimbangan kelas tidak dilakukan dengan Synthetic Minority '
              'Over-sampling Technique (SMOTE). Pada 169 baris, SMOTE berisiko '
              'membuat contoh sintetis yang tidak memiliki padanan administratif '
              'dan, bila ditempatkan sebelum pembagian data, menimbulkan '
              'kebocoran. Sebagai gantinya, bobot kelas (class_weight) '
              'dijadikan hyperparameter yang diuji Optuna. Keputusan ini menjaga '
              'agar data asli tidak diubah dan hasil tetap dapat diaudit.'),
    ])

    p = cari('[Tuliskan rumus matematis untuk Confusion Matrix')
    ganti_blok(p, [
        ('p', 'Evaluasi model tidak dapat dilakukan dengan satu angka. Confusion '
              'matrix pada ambang t menghasilkan empat sel: true positive (TP), '
              'true negative (TN), false positive (FP), dan false negative (FN). '
              'Dari sel tersebut diturunkan metrik berikut.'),
        ('rumus', 'Precision = TP / (TP + FP)'),
        ('rumus', 'Recall = TP / (TP + FN)'),
        ('rumus', 'F1 = 2 x Precision x Recall / (Precision + Recall)'),
        ('rumus', 'F_beta = (1 + beta^2) x Precision x Recall / '
                  '(beta^2 x Precision + Recall)'),
        ('rumus', 'ROC-AUC = luas daerah di bawah kurva TPR terhadap FPR'),
        ('rumus', 'PR-AUC = luas daerah di bawah kurva Precision terhadap Recall'),
        ('p', 'Precision mengukur ketepatan alarm: dari berkas yang ditandai '
              'berisiko, berapa bagian yang benar-benar terlambat. Recall '
              'mengukur cakupan: dari seluruh berkas yang terlambat, berapa '
              'bagian yang berhasil ditandai. F1 memberi bobot seimbang pada '
              'keduanya, sedangkan F2 memberi bobot lebih besar pada recall. '
              'Dalam konteks kantor notaris, F2 lebih relevan karena satu berkas '
              'terlambat yang tidak terdeteksi berdampak pada klien, bank, dan '
              'reputasi kantor, sementara satu alarm palsu hanya menambah satu '
              'pemeriksaan manual.'),
        ('p', 'ROC-AUC mengukur kemampuan model memeringkat contoh positif lebih '
              'tinggi daripada contoh negatif pada seluruh ambang. PR-AUC lebih '
              'informatif ketika kelas positif langka karena fokus pada kinerja '
              'kelas minoritas. Pada data ini proporsi positif 19,5 persen, '
              'sehingga kedua kurva dilaporkan berdampingan. Log-loss dipakai '
              'untuk menilai kualitas probabilitas: nilainya meningkat bila model '
              'memberi keyakinan tinggi pada prediksi yang salah.'),
        ('p', 'Accuracy paradox muncul ketika akurasi dipakai pada data tidak '
              'seimbang. Pada dataset ini, prediktor yang selalu menjawab "tepat '
              'waktu" memperoleh akurasi 136/169 = 80,5 persen, tetapi recall '
              '0 persen dan F1 kelas positif 0. Angka tersebut menunjukkan bahwa '
              'akurasi tinggi tidak identik dengan kegunaan operasional. Karena '
              'itu, laporan ini menempatkan Macro F1 sebagai objective optimasi '
              'dan F2 sebagai dasar pemilihan ambang.'),
    ])

    p = cari('[Jelaskan konsep dasar Bayesian Optimization')
    ganti_blok(p, [
        ('p', 'Optimasi hiperparameter pada data kecil tidak efisien bila '
              'dilakukan dengan grid search. Ruang kombinasi tujuh parameter '
              'Decision Tree sangat besar, sementara setiap evaluasi membutuhkan '
              'lima kali pelatihan. Bayesian optimization memanfaatkan hasil '
              'evaluasi sebelumnya untuk memilih kandidat berikutnya, sehingga '
              'anggaran evaluasi yang terbatas dapat diarahkan ke daerah yang '
              'paling menjanjikan.'),
        ('p', 'Optuna mengimplementasikan Tree-structured Parzen Estimator (TPE). '
              'Alih-alih memodelkan langsung fungsi objektif, TPE memodelkan dua '
              'distribusi kepadatan: l(x) untuk konfigurasi dengan nilai objektif '
              'baik dan g(x) untuk konfigurasi dengan nilai objektif buruk. '
              'Kandidat berikutnya dipilih dengan memaksimalkan rasio l(x)/g(x), '
              'yang berarti mencari konfigurasi yang lebih mungkin berasal dari '
              'kelompok performa baik daripada kelompok performa buruk. '
              'Pendekatan ini lebih efisien daripada random search karena '
              'memanfaatkan struktur ruang pencarian.'),
        ('p', 'Pada penelitian ini, study Optuna dijalankan dengan arah maximize, '
              'objective Macro F1 hasil Stratified 5-Fold Cross Validation pada '
              'data latih, sampler TPESampler dengan seed 42 dan 8 trial '
              'pemanasan, serta 30 trial total. Setiap trial mencatat '
              'konfigurasi, nilai per fold, dan status. Setelah study selesai, '
              'trial terbaik dilatih ulang pada seluruh data latih, lalu '
              'probabilitas out-of-fold dipakai untuk memilih ambang. Data uji '
              'baru disentuh pada tahap akhir.'),
    ])


def bab_3():
    p = cari('3.1 Kerangka Kerja Metodologi')
    sisip_blok(p, [
        ('p', 'Penelitian ini mengikuti kerangka CRISP-DM karena alurnya sesuai '
              'dengan siklus pekerjaan kantor: memahami proses bisnis, mengaudit '
              'data, menyiapkan fitur, membangun model, mengevaluasi, lalu '
              'merencanakan penerapan. Gambar 3.1 memetakan enam fase tersebut '
              'beserta keluaran yang dihasilkan pada setiap fase.'),
    ])

    p = cari('[TEMPELKAN GAMBAR 3.1')
    fmt(p, '', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, space_before=6,
        space_after=3)
    p.add_run().add_picture(str(GAMBAR / 'gambar_3_1_crispdm.png'),
                            width=Cm(14.4))
    sisip_blok(p, [
        ('cap', 'Gambar 3.1 Diagram alir metodologi penelitian berbasis CRISP-DM '
                'untuk prediksi keterlambatan akta.'),
        ('p', 'Fase business understanding menerjemahkan keluhan operasional '
              'menjadi target yang terukur, yaitu mendeteksi berkas berisiko '
              'sebelum tenggat. Fase data understanding menghasilkan audit 169 '
              'berkas, termasuk verifikasi duplikasi, rentang tanggal, dan '
              'distribusi kelas. Fase data preparation membentuk fitur antrean, '
              'indikator RUPS, dan encoding waktu dengan batas histori data '
              'latih. Fase modeling membandingkan baseline dan ensemble, lalu '
              'menjalankan Optuna. Fase evaluation memakai prediksi out-of-fold '
              'untuk memilih ambang dan mengunci data uji. Fase deployment '
              'direncanakan pada Bab IV dan Bab V melalui antarmuka Streamlit.'),
    ])

    p = cari('3.2 Karakteristik & Pemahaman Dataset')
    sisip_blok(p, [
        ('p', 'Dataset terdiri atas 169 berkas dengan 10 kolom mentah. Dua kolom '
              'turunan ditambahkan untuk keperluan audit, yaitu durasi_hari dan '
              'terlambat. Durasi_hari dipakai untuk membentuk label dan '
              'memvalidasi konstruk, tetapi tidak dimasukkan sebagai fitur karena '
              'baru diketahui setelah berkas selesai. Tabel 3.1 merangkum '
              'atribut, tipe data, makna, dan rentang nilainya.'),
    ])

    isi_tabel(DOC.tables[3], [
        ['No', 'Nama Atribut / Fitur', 'Tipe Data', 'Deskripsi Makna Fitur',
         'Statistik / Rentang Nilai'],
        ['1', 'tgl_masuk', 'Tanggal', 'Tanggal berkas diterima kantor; dasar '
         'pembentukan fitur hari dan bulan', '18 Apr 2024 - 2 Okt 2026'],
        ['2', 'tgl_selesai', 'Tanggal', 'Tanggal akta selesai; dipakai membentuk '
         'label, bukan fitur model', '29 Apr 2024 - 12 Okt 2026'],
        ['3', 'kategori_akta', 'Kategorikal (14 nilai)',
         'Jenis layanan akta yang menentukan kompleksitas pengerjaan',
         'PKR_PT 66; AJB_Saham 24; Waris_Wasiat 14; Kuasa 13'],
        ['4', 'jumlah_penghadap', 'Numerik (integer)',
         'Banyaknya pihak yang harus hadir dan menandatangani',
         'Min 1; maks 14; rata-rata 3,07'],
        ['5', 'sla_hari', 'Numerik (integer)',
         'Tenggat layanan yang dijanjikan untuk jenis akta tersebut',
         'Min 5; maks 40; median 14 hari'],
        ['6', 'tgl_rups', 'Tanggal (opsional)',
         'Tanggal RUPS; hanya terisi bila akta berkaitan dengan keputusan RUPS',
         '13 dari 169 berkas terisi'],
        ['7', 'durasi_hari', 'Numerik (turunan)',
         'Selisih tgl_selesai dan tgl_masuk; dasar label, TIDAK dipakai sebagai '
         'fitur', 'Min 2; maks 33; rata-rata 10,54'],
        ['8', 'antrean_berjalan', 'Numerik (turunan)',
         'Jumlah berkas terbuka saat berkas masuk; dihitung dari histori data '
         'latih', 'Min 0; maks 8; rata-rata 2,36'],
        ['9', 'ada_rups', 'Biner (turunan)',
         'Bernilai 1 bila RUPS sudah berlangsung saat berkas masuk',
         '0 atau 1'],
        ['10', 'bulan_sin, bulan_cos', 'Numerik (turunan)',
         'Encoding siklik bulan agar Desember dan Januari berdekatan',
         'Rentang -1 sampai 1'],
        ['11', 'hari_masuk', 'Kategorikal (5 nilai)',
         'Hari kerja berkas masuk', 'Senin sampai Jumat'],
        ['12', 'terlambat', 'Biner (label)',
         'Bernilai 1 bila durasi_hari lebih besar dari sla_hari',
         '33 positif (19,5 persen); 136 negatif'],
    ], lebar=[0.9, 2.6, 2.4, 5.1, 3.6], font=8)

    sisip_setelah_tabel(DOC.tables[3], [
        ('p', 'Komposisi kategori menunjukkan bahwa hampir separuh berkas adalah '
              'PKR_PT (66 berkas). Kategori ini umumnya melibatkan beberapa '
              'penghadap dan dokumen pendukung, sehingga waktu pengerjaannya '
              'lebih panjang. Sebaran SLA juga lebar, dari 5 hari untuk akta '
              'kuasa hingga 40 hari untuk akta tertentu. Perbedaan tenggat ini '
              'menjelaskan mengapa label harus dihitung relatif terhadap SLA '
              'masing-masing berkas, bukan memakai satu tenggat seragam.'),
        ('p', 'Tidak ditemukan duplikasi id_berkas. Seluruh 169 baris memiliki '
              'tanggal masuk dan tanggal selesai yang valid, sehingga tidak ada '
              'baris yang harus dibuang. Nilai hilang hanya muncul pada tgl_rups, '
              'yang memang bersifat opsional. Struktur data yang relatif bersih '
              'ini memungkinkan fokus penelitian diarahkan pada rekayasa fitur '
              'dan protokol evaluasi, bukan pada pembersihan data yang ekstensif.'),
    ])

    p = cari('[TEMPELKAN GAMBAR 3.2')
    fmt(p, '', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, space_before=6,
        space_after=3)
    p.add_run().add_picture(str(GAMBAR / 'gambar_3_2_eda.png'), width=Cm(14.4))
    sisip_blok(p, [
        ('cap', 'Gambar 3.2 (a) Distribusi kelas target dan (b) matriks korelasi '
                'Pearson antarfitur numerik.'),
        ('p', 'Gambar 3.2(a) menegaskan ketidakseimbangan kelas: 136 berkas tepat '
              'waktu berbanding 33 berkas terlambat. Rasio 4,1 banding 1 ini '
              'cukup untuk membuat model condong ke kelas mayoritas, tetapi tidak '
              'ekstrem sampai memerlukan generasi data sintetis. Konsekuensinya, '
              'metrik yang dipakai harus berfokus pada kelas minoritas, dan '
              'ambang keputusan perlu digeser dari nilai default.'),
        ('p', 'Gambar 3.2(b) menunjukkan tiga pola. Pertama, durasi_hari '
              'berkorelasi 0,52 dengan label; korelasi ini bukan temuan prediktif, '
              'melainkan validasi konstruk karena label memang dibentuk dari '
              'durasi. Fitur tersebut karena itu dikeluarkan dari model. Kedua, '
              'SLA dan durasi berkorelasi 0,66, yang wajar karena SLA lebih '
              'panjang diberikan pada akta yang memang memerlukan waktu lebih '
              'lama. Ketiga, antrean berjalan hanya berkorelasi 0,08 dengan label '
              'dan bulan 0,03, sehingga hubungan antrean dengan keterlambatan '
              'kemungkinan tidak linier. Temuan ini mendukung pemilihan model '
              'berbasis pohon yang mampu menangkap interaksi dan ambang lokal.'),
        ('p', 'Korelasi jumlah penghadap dengan label sebesar -0,04 juga tidak '
              'boleh dibaca sebagai "jumlah penghadap tidak penting". Pada data '
              'kecil, korelasi Pearson hanya menangkap hubungan linier dan mudah '
              'tertutup oleh variasi kategori akta. Pohon keputusan dapat memakai '
              'fitur ini bersama SLA dan antrean secara bersyarat, sehingga '
              'kontribusinya dinilai melalui importance model, bukan melalui '
              'korelasi tunggal.'),
    ])

    p = cari('[Tuliskan uraian pipeline pra-pemrosesan')
    ganti_blok(p, [
        ('p', 'Pipeline disusun sebagai satu objek yang menggabungkan transformer '
              'fitur, pra-pemrosesan kolom, dan model. Urutan pemrosesan adalah '
              'sebagai berikut.'),
        ('n', '1. Pemuatan data dan penetapan label. Durasi dihitung dari selisih '
              'tanggal, lalu label ditetapkan dengan aturan durasi lebih besar '
              'dari SLA. Tidak ada perubahan nilai, penghapusan baris, atau '
              'penyeimbangan ulang.'),
        ('n', '2. Pembentukan fitur pada tingkat baris. Kolom tanggal diubah '
              'menjadi hari masuk, bulan sinus, bulan kosinus, dan indikator '
              'RUPS. Kategori akta dipertahankan sebagai teks untuk di-encode '
              'pada tahap berikutnya.'),
        ('n', '3. Pembentukan fitur antrean. Untuk setiap berkas, antrean '
              'dihitung dari jumlah berkas pada histori yang tanggal masuknya '
              'lebih awal dan tanggal selesainya belum lewat. Histori diambil '
              'dari data latih tempat transformer di-fit, sehingga berkas uji '
              'tidak pernah "melihat" dirinya sendiri atau berkas lain di masa '
              'depan.'),
        ('n', '4. Imputasi. Median dipakai untuk kolom numerik dan nilai paling '
              'sering muncul untuk kolom kategorikal. Imputer di-fit hanya pada '
              'fold latih.'),
        ('n', '5. Encoding. One-Hot Encoding diterapkan pada kategori akta dan '
              'hari masuk dengan handle_unknown="ignore" agar kategori baru pada '
              'data uji tidak menimbulkan galat.'),
        ('n', '6. Pelatihan model. Decision Tree dilatih dengan parameter hasil '
              'Optuna. Seluruh langkah 1 sampai 5 berada di dalam pipeline, '
              'sehingga ketika validasi silang dijalankan, setiap fold memiliki '
              'imputer, encoder, dan histori antrean sendiri.'),
        ('p', 'Pemisahan tegas antara langkah yang boleh dan tidak boleh memakai '
              'data uji merupakan inti dari protokol bebas kebocoran. Pada '
              'penelitian ini, data uji hanya dipakai dua kali: sekali untuk '
              'memeriksa konsistensi artefak Tugas 05, dan sekali untuk evaluasi '
              'akhir setelah ambang dikunci. Data uji tidak pernah dipakai untuk '
              'memilih fitur, menyetel hiperparameter, atau memilih ambang.'),
        ('p', 'Konsekuensi lain dari protokol ini adalah tidak adanya SMOTE. '
              'Meskipun literatur sering menyarankan SMOTE untuk data tidak '
              'seimbang, penerapannya pada 135 baris latih dengan 26 positif '
              'berisiko menghasilkan contoh sintetis yang tidak realistis. '
              'Sebagai gantinya, bobot kelas diuji sebagai hyperparameter, dan '
              'sensitivitas model terhadap kelas minoritas diatur melalui ambang '
              'keputusan. Dengan demikian, data asli tetap utuh dan setiap '
              'perubahan dapat ditelusuri.'),
    ])

    p = cari('[Jelaskan skema pembagian data Train-Test Split')
    ganti_blok(p, [
        ('p', 'Data dibagi menjadi 135 berkas latih dan 34 berkas uji dengan '
              'proporsi 80:20, stratifikasi pada label, dan random_state 42. '
              'Hasilnya, data latih memuat 26 berkas terlambat dan data uji '
              'memuat 7 berkas terlambat. Pembagian ini sama dengan Tugas 04 '
              'sampai Tugas 06 sehingga perbandingan antar-tugas sah dilakukan.'),
        ('p', 'Pada data latih dijalankan Stratified 5-Fold Cross Validation '
              'dengan pengacakan dan seed 42. Stratifikasi menjaga proporsi kelas '
              'di setiap fold, sehingga tidak ada fold yang kehilangan seluruh '
              'contoh positif. Dengan 26 positif, setiap fold rata-rata memuat 5 '
              'sampel positif, cukup untuk menghitung F1 per fold meskipun '
              'variasinya masih lebar.'),
        ('p', 'Prediksi out-of-fold (OOF) dibentuk dengan cross_val_predict dan '
              'method="predict_proba". Setiap berkas latih menerima probabilitas '
              'dari model yang tidak pernah melihat berkas tersebut saat '
              'pelatihan. Probabilitas OOF inilah yang dipakai untuk menggambar '
              'kurva ambang dan memilih ambang, sehingga pemilihan tidak '
              'melibatkan data uji. Setelah ambang dipilih, model dilatih ulang '
              'pada seluruh 135 berkas latih dan diuji satu kali pada 34 berkas '
              'uji.'),
        ('p', 'Kestabilan hasil dilaporkan melalui rata-rata dan simpangan baku '
              'lima fold. Selain itu, interval kepercayaan bootstrap dipakai untuk '
              'menggambarkan ketidakpastian pada data uji yang kecil. Dengan 34 '
              'berkas, satu perubahan prediksi saja dapat menggeser F1 beberapa '
              'poin persen, sehingga angka tunggal tanpa interval berpotensi '
              'menyesatkan.'),
    ])

    p = cari('3.6 Perbandingan Model Baseline')
    sisip_blok(p, [
        ('p', 'Tabel 3.2 membandingkan lima algoritma pada pembagian data dan '
              'protokol pra-pemrosesan yang sama. Seluruh model dilatih dengan '
              'parameter default dan dievaluasi pada ambang 0,50 untuk melihat '
              'perilaku awal sebelum tuning. Kolom Macro F1 CV merupakan '
              'rata-rata lima fold pada data latih, sedangkan kolom lainnya '
              'merupakan hasil pada data uji.'),
    ])

    mb = {m['model']: m for m in HASIL['model_baseline']}
    urut = ['Logistic Regression (Baseline)', 'Decision Tree (Baseline)',
            'Random Forest (Ensemble)', 'Gradient Boosting (Ensemble)',
            'Histogram Gradient Boosting (Ensemble)']
    baris = [['Algoritma Model', 'Accuracy', 'Precision', 'Recall',
              'F1-Score (Macro)', 'ROC-AUC']]
    for nama in urut:
        m = mb[nama]
        t = m['test']
        baris.append([nama.replace(' (Baseline)', ' (Baseline)')
                      .replace(' (Ensemble)', ' (Ensemble)'),
                      f"{t['accuracy']:.4f}".replace('.', ','),
                      f"{t['precision']:.4f}".replace('.', ','),
                      f"{t['recall']:.4f}".replace('.', ','),
                      f"{t['macro_f1']:.4f}".replace('.', ','),
                      f"{t['roc_auc']:.4f}".replace('.', ',')])
    isi_tabel(DOC.tables[4], baris, lebar=[4.6, 2.0, 2.0, 1.9, 2.2, 1.9],
              font=9, tengah=(1, 2, 3, 4, 5))

    sisip_setelah_tabel(DOC.tables[4], [
        ('note', 'Catatan: Macro F1 CV untuk Logistic Regression 0,4612; Decision '
                 'Tree 0,4803; Random Forest 0,4278; Gradient Boosting 0,4168; '
                 'Histogram Gradient Boosting 0,4154. Seluruh nilai uji dihitung '
                 'pada ambang 0,50.'),
        ('p', 'Tiga temuan menonjol. Pertama, pada ambang 0,50 hampir semua model '
              'memperoleh recall 0,000; hanya Decision Tree yang menemukan satu '
              'dari tujuh berkas terlambat. Artinya, model dengan akurasi 61 '
              'sampai 79 persen sekalipun belum memberikan manfaat operasional '
              'bila dipakai pada ambang default. Inilah accuracy paradox dalam '
              'bentuk yang paling langsung.'),
        ('p', 'Kedua, model ensemble tidak otomatis lebih baik. Random Forest, '
              'Gradient Boosting, dan Histogram Gradient Boosting memperoleh '
              'Macro F1 CV 0,4278; 0,4168; dan 0,4154, lebih rendah daripada '
              'Decision Tree default 0,4803 dan Logistic Regression 0,4612. Pada '
              '135 baris latih, kapasitas tambahan ensemble berubah menjadi '
              'overfitting: model menghafal kombinasi kategori dan tanggal yang '
              'tidak berulang di data uji.'),
        ('p', 'Ketiga, Decision Tree memberikan keseimbangan terbaik antara '
              'Macro F1 uji (0,4440) dan kemudahan interpretasi. Karena itu '
              'keluarga Decision Tree dipilih untuk dioptimasi lebih lanjut, '
              'dengan catatan bahwa pemilihan ini didasarkan pada bukti empiris '
              'pada dataset ini, bukan klaim umum bahwa pohon selalu mengalahkan '
              'ensemble.'),
    ])

    p = cari('3.7 Optimasi Hiperparameter dengan Optuna')
    sisip_blok(p, [
        ('p', 'Optimasi dijalankan pada data latih dengan Stratified 5-Fold '
              'Cross Validation dan objective Macro F1. Ruang pencarian mencakup '
              'tujuh parameter: criterion (gini atau entropy), max_depth (2 '
              'sampai 12), min_samples_leaf (1 sampai 20), min_samples_split (2 '
              'sampai 30), ccp_alpha (0 sampai 0,01 pada skala log), class_weight '
              '(None atau balanced), dan max_features (None, sqrt, atau log2). '
              'Study memakai TPESampler dengan seed 42, 8 trial pemanasan, dan 30 '
              'trial total; seluruh 30 trial selesai tanpa kegagalan.'),
    ])

    isi_tabel(DOC.tables[5], [
        ['Kondisi Model', 'Konfigurasi Hiperparameter Utama', 'F1-Score',
         'ROC-AUC', 'Recall (Kelas 1)', 'Peningkatan (%)'],
        ['Default (Sebelum Tuning)',
         'max_depth=4; min_samples_leaf=15; min_samples_split=2; ccp_alpha=0; '
         'class_weight=None',
         '0,4467', '0,5240', '0,0000', 'Baseline (0%)'],
        ['Optuna Tuned (Trial #13)',
         'criterion=gini; max_depth=6; min_samples_leaf=3; '
         'min_samples_split=16; ccp_alpha=0,003536; max_features=log2; '
         'class_weight=None',
         '0,5532', '0,5535', '0,1600', '+23,8% (relatif)'],
    ], lebar=[2.8, 4.3, 1.8, 1.8, 1.9, 2.0], font=8.5, tengah=(2, 3, 4, 5))

    sisip_setelah_tabel(DOC.tables[5], [
        ('note', 'Catatan: F1-Score adalah Macro F1 rata-rata lima fold pada data '
                 'latih; ROC-AUC dan Recall juga rata-rata validasi silang pada '
                 'ambang 0,50. Peningkatan relatif dihitung dari Macro F1.'),
        ('p', 'Trial terbaik adalah trial nomor 13 dengan Macro F1 0,5532 dan '
              'simpangan baku 0,1182. Peningkatan relatif 23,8 persen terhadap '
              'konfigurasi default terutama berasal dari penurunan '
              'min_samples_leaf dari 15 menjadi 3 dan penambahan pascapemangkasan '
              'ccp_alpha 0,003536. Kombinasi ini memungkinkan pohon membentuk '
              'daun yang lebih spesifik, tetapi tetap membuang cabang yang '
              'kontribusinya tidak sebanding dengan kompleksitasnya.'),
        ('p', 'Analisis parameter importance menunjukkan min_samples_leaf '
              'menyumbang 0,354 dan ccp_alpha 0,297 dari total importance. '
              'Keduanya adalah parameter yang mengendalikan kompleksitas pohon, '
              'bukan parameter yang mengubah kriteria pemisahan. Temuan ini '
              'konsisten dengan karakteristik data kecil: yang menentukan '
              'kualitas bukan pemilihan gini versus entropy, melainkan seberapa '
              'besar pohon diizinkan tumbuh. Parameter criterion hanya '
              'menyumbang 0,008, sedangkan max_features 0,039.'),
        ('p', 'Meskipun rata-rata naik, simpangan baku antar-fold juga meningkat '
              'dari 0,0051 menjadi 0,1182. Kenaikan variansi ini wajar karena '
              'pohon yang lebih dalam lebih sensitif terhadap komposisi fold. '
              'Karena itu, angka 0,5532 tidak boleh dibaca sebagai jaminan '
              'generalisasi, melainkan sebagai titik tengah yang perlu diuji pada '
              'data uji dan dilengkapi interval kepercayaan.'),
    ])

    sisip_blok(cari('Meskipun rata-rata naik'), [
        ('img', GRAFIK / '04_optuna_history.png', 13.2),
        ('cap', 'Gambar 3.5 Riwayat 30 trial Optuna. Garis putus-putus menandai '
                'nilai terbaik (trial #13, Macro F1 0,5532); sumbu kanan '
                'menunjukkan akumulasi trial terbaik.'),
        ('p', 'Gambar 3.5 memperlihatkan bahwa perbaikan terbesar terjadi pada '
              'delapan trial pemanasan, lalu melandai setelah trial ke-15. Pola '
              'ini wajar untuk TPE: setelah distribusi l(x) dan g(x) terbentuk, '
              'sampler memusatkan pencarian pada daerah yang sudah baik. Karena '
              'kurva mendatar sebelum trial ke-30, penambahan trial besar '
              'kemungkinan tidak memberi peningkatan berarti pada dataset ini.'),
    ])

    p = cari('3.8 Kalibrasi Ambang Batas')
    sisip_blok(p, [
        ('p', 'Ambang dipilih dari probabilitas out-of-fold data latih, bukan dari '
              'data uji. Untuk setiap kandidat ambang dihitung TP, TN, FP, FN, '
              'precision, recall, F1, F2, dan beban alarm. Kriteria utama adalah '
              'F2 maksimum karena false negative lebih mahal; bila terjadi seri, '
              'dipilih precision lebih tinggi lalu ambang lebih besar agar alarm '
              'tidak berlebihan. Dari prosedur ini diperoleh ambang 0,05. Sebagai '
              'pembanding operasional ditetapkan guardrail 0,19, yaitu ambang '
              'terendah yang masih menahan beban alarm di bawah 50 persen pada '
              'data latih.'),
    ])

    isi_tabel(DOC.tables[6], [
        ['Threshold (Ambang)', 'Precision', 'Recall', 'F1-Score',
         'False Negative (Kasus)', 'Rasionalitas Bisnis / Operasional'],
        ['0,50 (default)', '0,000', '0,000', '0,000', '7',
         'Tidak ada alarm sama sekali; seluruh keterlambatan lolos. Tidak layak '
         'dipakai sebagai satu-satunya ambang.'],
        ['0,30', '0,182', '0,286', '0,222', '5',
         'Sensitivitas rendah; 11 alarm. Hanya menangkap dua dari tujuh kasus.'],
        ['0,25 (F1 OOF)', '0,143', '0,286', '0,190', '5',
         'F1 maksimum pada OOF, tetapi recall pada data uji justru turun; '
         'menunjukkan F1 kurang tepat untuk biaya asimetris.'],
        ['0,19 (guardrail)', '0,174', '0,571', '0,267', '3',
         '23 alarm (67,6 persen berkas); kompromi bila kapasitas pemeriksaan '
         'harian terbatas.'],
        ['0,05 (F2 OOF, terpilih)', '0,208', '0,714', '0,323', '2',
         '24 alarm (70,6 persen berkas); menangkap lima dari tujuh kasus. Sesuai '
         'prinsip meminimalkan false negative.'],
    ], lebar=[2.1, 1.5, 1.4, 1.4, 1.7, 6.5], font=8, tengah=(1, 2, 3, 4))

    sisip_setelah_tabel(DOC.tables[6], [
        ('note', 'Catatan: seluruh baris dihitung pada 34 berkas uji yang sama. '
                 'Ambang 0,05 dan 0,19 ditetapkan dari OOF data latih sebelum '
                 'data uji dievaluasi; baris 0,30 dan 0,25 disajikan sebagai '
                 'pembanding sensitivitas, bukan sebagai dasar pemilihan.'),
        ('p', 'Tabel 3.4 memperlihatkan trade-off yang tajam. Pada ambang 0,50 '
              'model tidak membunyikan alarm apa pun, sehingga recall 0,000 dan '
              'tujuh keterlambatan lolos. Pada ambang 0,05, model menandai 24 '
              'berkas, menemukan lima dari tujuh keterlambatan (recall 0,714), '
              'dengan 19 alarm palsu. Precision 0,208 terlihat rendah, tetapi '
              'harus dibaca dalam konteks: staf tidak diminta memeriksa seluruh '
              '169 berkas, melainkan 24 berkas yang diurutkan berdasarkan '
              'probabilitas. Pada ambang ini F2 mencapai 0,481, Macro F1 0,378, '
              'weighted F1 0,410, dan log-loss 1,155; nilai F2 yang lebih tinggi '
              'daripada F1 mencerminkan penekanan pada recall.'),
        ('p', 'Ambang 0,19 menawarkan kompromi bila kapasitas pemeriksaan hanya '
              'sekitar dua pertiga berkas. Dengan 23 alarm, model menemukan '
              'empat dari tujuh keterlambatan. Selisih satu temuan antara 0,19 '
              'dan 0,05 memang kecil, tetapi pada 34 berkas uji satu temuan setara '
              'dengan 14 poin persen recall. Karena itu, keputusan ambang tidak '
              'boleh hanya melihat satu angka; perlu mempertimbangkan kapasitas '
              'harian dan biaya satu pemeriksaan tambahan.'),
        ('p', 'Interval kepercayaan bootstrap pada ambang 0,05 menunjukkan F1 '
              '0,1875 sampai 0,4516 dan recall 0,4286 sampai 1,0000. Rentang yang '
              'lebar ini adalah konsekuensi langsung dari ukuran data uji 34 '
              'berkas. Laporan tetap menyajikan angka titik, tetapi '
              'menyertakan rentang agar pembaca tidak menyimpulkan presisi yang '
              'berlebihan.'),
    ])

    sisip_blok(cari('Interval kepercayaan bootstrap'), [
        ('img', GRAFIK / '03_threshold_tuning_oof.png', 13.2),
        ('cap', 'Gambar 3.6 Sensitivitas precision, recall, dan F2 terhadap '
                'ambang keputusan pada prediksi out-of-fold data latih. Titik '
                'terpilih 0,05 dan guardrail 0,19 ditandai.'),
        ('p', 'Gambar 3.6 menjelaskan dasar pemilihan ambang. Ketika ambang '
              'diturunkan dari 0,50 ke 0,05, recall naik tajam karena lebih '
              'banyak berkas melewati batas alarm, sedangkan precision turun '
              'perlahan. Kurva F2 mencapai puncak di sekitar 0,05, lebih rendah '
              'daripada puncak F1 yang berada di sekitar 0,25. Perbedaan posisi '
              'kedua puncak inilah yang membuat pilihan ambang bergantung pada '
              'fungsi biaya, bukan pada satu metrik tunggal.'),
        ('p', 'Grafik ini juga menunjukkan mengapa ambang 0,19 dipakai sebagai '
              'guardrail: pada titik tersebut kurva mulai mendatar, sehingga '
              'penurunan ambang lebih jauh menambah beban alarm tanpa kenaikan '
              'recall yang sebanding. Dengan demikian, keputusan operasional '
              'dapat dipertanggungjawabkan secara visual, bukan hanya melalui '
              'angka di tabel.'),
    ])

    p = cari('[TEMPELKAN GAMBAR 3.3')
    fmt(p, '', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, space_before=6,
        space_after=3)
    p.add_run().add_picture(str(GRAFIK / '02_roc_pr.png'), width=Cm(14.4))
    kursor = sisip_blok(p, [
        ('cap', 'Gambar 3.7 Kurva ROC (kiri) dan kurva precision-recall (kanan) '
                'model terbaik pada data uji, dengan penanda ambang 0,50; 0,19; '
                'dan ambang terpilih 0,05.'),
        ('p', 'Gambar 3.7 menunjukkan mengapa pemilihan ambang tidak dapat '
              'dilepaskan dari kurva. ROC-AUC 0,413 berada di bawah 0,5, yang '
              'berarti kemampuan peringkat model pada data uji ini lemah dan '
              'bahkan sedikit di bawah tebakan acak, dengan PR-AUC (average '
              'precision) 0,190. Sebaliknya, kurva '
              'precision-recall memperlihatkan bahwa pada ambang rendah model '
              'masih dapat menangkap sebagian besar kasus positif, dengan '
              'konsekuensi precision rendah. Kombinasi ini menjelaskan paradoks '
              'yang sering muncul di laporan: ROC-AUC rendah tidak otomatis '
              'berarti model tidak berguna untuk penyaringan awal, asalkan '
              'ambang dan biaya kesalahan dinyatakan eksplisit.'),
        ('p', 'Perlu ditegaskan bahwa ROC-AUC dan PR-AUC tidak berubah ketika '
              'ambang digeser. Yang berubah adalah titik operasi. Pada laporan '
              'ini, titik 0,50 dan 0,05 ditandai agar pembaca dapat melihat '
              'konsekuensi keputusan secara langsung, tanpa harus menebak dari '
              'tabel.'),
    ])

    p = kursor
    p2 = par_baru(p)
    fmt(p2, '', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, space_before=6,
        space_after=3)
    p2.add_run().add_picture(str(GRAFIK / '01_confusion_matrix_tuned.png'),
                             width=Cm(10.2))
    sisip_blok(p2, [
        ('cap', 'Gambar 3.8 Confusion matrix model terbaik pada ambang terpilih '
                '0,05 (TP 5, FN 2, FP 19, TN 8).'),
        ('p', 'Gambar 3.8 memperlihatkan komposisi kesalahan secara utuh. Dari 7 '
              'berkas terlambat, 5 berhasil ditandai dan 2 terlewat. Kedua false '
              'negative tersebut adalah BRK_0001 (Kuasa, selisih 5 hari) dan '
              'BRK_0075 (PKR_PT, selisih 4 hari). BRK_0001 memperoleh skor '
              '0,045, hanya sedikit di bawah ambang, sedangkan BRK_0075 '
              'memperoleh skor 0,000. Pola ini menunjukkan bahwa berkas dengan '
              'selisih keterlambatan kecil dan fitur yang mirip berkas tepat '
              'waktu merupakan kasus tersulit.'),
        ('p', 'Dari 19 false positive, 12 berasal dari kategori PKR_PT, diikuti '
              'PPJB 3 dan Waris_Wasiat 2. Kategori PKR_PT memiliki volume '
              'terbesar (66 berkas), sehingga wajar bila menyumbang alarm palsu '
              'terbanyak. Temuan ini memberi arah perbaikan pada Bab IV: '
              'menambahkan fitur beban kerja per kategori atau memisahkan model '
              'per jenis akta, bukan sekadar menaikkan ambang secara global.'),
    ])

    p = cari('3.9 Cetak Biru Deployment')
    sisip_blok(p, [
        ('p', 'Cetak biru deployment disusun agar hasil penelitian dapat '
              'dilanjutkan pada Bab IV dan Bab V menuju UAS. Arsitektur yang '
              'direncanakan terdiri atas lima komponen berikut.'),
        ('n', '1. Serialisasi model. Model terbaik dan seluruh pipeline '
              'pra-pemrosesan diekspor ke berkas .joblib beserta metadata versi '
              'pustaka, hash dataset, daftar fitur, dan ambang terpilih. Dengan '
              'cara ini, prediksi dapat direproduksi tanpa menjalankan ulang '
              'pelatihan.'),
        ('n', '2. Antarmuka pengguna. Aplikasi Streamlit menyediakan formulir '
              'untuk memasukkan kategori akta, tanggal masuk, jumlah penghadap, '
              'SLA, dan status RUPS. Sistem menghitung antrean berjalan dari '
              'snapshot histori terakhir, lalu menampilkan probabilitas '
              'keterlambatan dan rekomendasi prioritas.'),
        ('n', '3. Logika inferensi terkalibrasi. Ambang diterapkan sebagai '
              'parameter konfigurasi, bukan ditanam di dalam kode. Nilai default '
              '0,05 dipakai untuk mode "sensitivitas tinggi", sedangkan 0,19 '
              'dipakai untuk mode "kapasitas terbatas". Staf dapat melihat '
              'konsekuensi beban alarm sebelum mengubah mode.'),
        ('n', '4. Pemantauan dan pemeliharaan. Setiap prediksi dicatat bersama '
              'hasil aktualnya. Setiap bulan dihitung precision, recall, dan '
              'beban alarm; bila terjadi pergeseran distribusi (misalnya '
              'lonjakan kategori akta baru), model dilatih ulang dengan data '
              'terbaru dan ambang dihitung ulang dari OOF.'),
        ('n', '5. Tata kelola. Model diposisikan sebagai alat bantu penyaringan. '
              'Keputusan akhir tetap berada pada staf, Notaris, atau PPAT. '
              'Penjelasan alasan prediksi (fitur yang paling berpengaruh) '
              'ditampilkan agar keputusan dapat dipertanggungjawabkan dan tidak '
              'menjadi kotak hitam.'),
        ('p', 'Rencana pengujian pada tahap UAS mencakup tiga skenario. Skenario '
              'pertama adalah pengujian fungsional dengan data historis untuk '
              'memastikan antarmuka menghasilkan probabilitas yang sama dengan '
              'model di notebook. Skenario kedua adalah simulasi beban alarm '
              'harian pada ambang 0,05 dan 0,19 untuk mengukur waktu pemeriksaan '
              'tambahan. Skenario ketiga adalah uji penerimaan pengguna bersama '
              'staf kantor, dengan fokus pada kejelasan alasan prediksi dan '
              'kemudahan penyesuaian ambang.'),
    ])

    p = cari('Sebagai persiapan implementasi terapan')
    ganti_blok(p, [
        ('p', 'Prototipe antarmuka yang telah dibangun pada Tugas 05 menjadi '
              'titik awal deployment. Gambar 3.9 memperlihatkan tampilan '
              'prototipe ketika menerima masukan berkas dan menampilkan hasil '
              'prediksi beserta ambang yang berlaku. Pada tahap UAS, prototipe '
              'akan dihubungkan dengan model hasil Tugas 06 dan dilengkapi '
              'pencatatan hasil aktual untuk pemantauan.'),
        ('img', GRAFIK / '09_prototipe_tugas05.png', 12.4),
        ('cap', 'Gambar 3.9 Prototipe antarmuka Streamlit pada Tugas 05 yang '
                'menjadi dasar rencana deployment.'),
    ])


def daftar_pustaka():
    p = cari('Breiman, L. (2001)')
    refs = [
        '[1] L. Breiman, "Random forests," Machine Learning, vol. 45, no. 1, '
        'pp. 5-32, 2001, doi: 10.1023/A:1010933404324.',
        '[2] S. Lessmann, B. Baesens, H.-V. Seow, and L. C. Thomas, '
        '"Benchmarking state-of-the-art classification algorithms for credit '
        'scoring: An update of research," European Journal of Operational '
        'Research, vol. 247, no. 1, pp. 124-136, 2015, doi: '
        '10.1016/j.ejor.2015.05.030.',
        '[3] T. Saito and M. Rehmsmeier, "The precision-recall plot is more '
        'informative than the ROC plot when evaluating binary classifiers on '
        'imbalanced datasets," PLOS ONE, vol. 10, no. 3, Art. no. e0118432, '
        '2015, doi: 10.1371/journal.pone.0118432.',
        '[4] H. He and E. A. Garcia, "Learning from imbalanced data," IEEE '
        'Transactions on Knowledge and Data Engineering, vol. 21, no. 9, '
        'pp. 1263-1284, 2009, doi: 10.1109/TKDE.2008.239.',
        '[5] T. Akiba, S. Sano, T. Yanase, T. Ohta, and M. Koyama, "Optuna: A '
        'next-generation hyperparameter optimization framework," in Proceedings '
        'of the 25th ACM SIGKDD International Conference on Knowledge Discovery '
        '& Data Mining, 2019, pp. 2623-2631, doi: 10.1145/3292500.3330701.',
        '[6] Z. C. Lipton, C. Elkan, and B. Naryanaswamy, "Optimal thresholding '
        'of classifiers to maximize F1 measure," in Machine Learning and '
        'Knowledge Discovery in Databases (ECML PKDD 2014), LNCS 8725, 2014, '
        'pp. 225-239, doi: 10.1007/978-3-662-44851-9_15.',
        '[7] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting '
        'system," in Proceedings of the 22nd ACM SIGKDD International Conference '
        'on Knowledge Discovery and Data Mining, 2016, pp. 785-794, doi: '
        '10.1145/2939672.2939785.',
        '[8] F. Pedregosa et al., "Scikit-learn: Machine learning in Python," '
        'Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.',
        '[9] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting '
        'model predictions," in Advances in Neural Information Processing '
        'Systems, vol. 30, 2017, pp. 4765-4774.',
        '[10] C. Elkan, "The foundations of cost-sensitive learning," in '
        'Proceedings of the 17th International Joint Conference on Artificial '
        'Intelligence (IJCAI), 2001, pp. 973-978.',
        '[11] J. Gama, I. Zliobaite, A. Bifet, M. Pechenizkiy, and A. Bouchachia, '
        '"A survey on concept drift adaptation," ACM Computing Surveys, vol. 46, '
        'no. 4, pp. 1-37, 2014, doi: 10.1145/2523813.',
        '[12] Kantor Notaris & PPAT Aries Buwana, "Rekapitulasi berkas dan SLA '
        'layanan 2024-2026," dokumen internal, Jakarta Barat, 2026.',
    ]
    fmt(p, refs[0], align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=0, space_after=6,
        line=1.15)
    p.paragraph_format.left_indent = Cm(0.9)
    p.paragraph_format.first_line_indent = Cm(-0.9)
    sisip_blok(p, [('p', r) for r in refs[1:]])
    for par in p._p.getparent().iterchildren():
        pass
    # format semua paragraf referensi dengan hanging indent
    aktif = False
    for par in DOC.paragraphs:
        if par.text.strip().startswith('[1] L. Breiman'):
            aktif = True
        if aktif and par.text.strip().startswith('['):
            par.paragraph_format.left_indent = Cm(0.9)
            par.paragraph_format.first_line_indent = Cm(-0.9)
            par.paragraph_format.space_after = Pt(6)
            par.paragraph_format.line_spacing = 1.15


def lampiran():
    p = cari('LAMPIRAN 1: TAUTAN REPOSITORI')
    ganti_blok(p, [
        ('h', 'LAMPIRAN 1: TAUTAN REPOSITORI KODE DAN GOOGLE COLAB'),
        ('h', 'Repositori publik GitHub:'),
        ('link', 'https://github.com/rizqiProject/tugas06-pembelajaran-mesin-kelompok02'),
        ('p', 'Repositori memuat kode eksperimen Tugas 06, hasil Optuna, grafik, '
              'model .joblib, laporan Tugas 06, serta berkas penyusun proposal '
              'UTS. Tautan dapat dibuka tanpa login.'),
        ('h', 'Notebook Google Colab:'),
        ('link', 'https://colab.research.google.com/github/rizqiProject/'
                 'tugas06-pembelajaran-mesin-kelompok02/blob/main/'
                 'Jalankan_Tugas06_Colab.ipynb'),
        ('p', 'Notebook menyalin repositori, memasang dependensi, dan menjalankan '
              'ulang eksperimen 30 trial Optuna. Tautan telah diperiksa dapat '
              'dibuka tanpa login.'),
        ('h', 'LAMPIRAN 2: BERKAS MODEL DAN LINGKUNGAN EKSEKUSI'),
        ('b', 'model_tugas06_tuned.joblib - pipeline lengkap (fitur, imputer, '
              'encoder, pohon) hasil trial Optuna terbaik.'),
        ('b', 'model_tugas06_baseline.joblib - model default Tugas 04/05 sebagai '
              'pembanding before tuning.'),
        ('b', 'metadata_model.json - daftar fitur, ambang terpilih, hash dataset, '
              'dan versi pustaka.'),
        ('b', 'requirements_tugas_06.txt - numpy 2.5.4, pandas 3.1.1, '
              'scikit-learn 1.9.1, optuna 5.0.0, matplotlib 3.11.2, joblib 1.6.0, '
              'python-docx 1.2.0.'),
        ('h', 'LAMPIRAN 3: RINGKASAN LOG OPTUNA'),
        ('p', 'Study dijalankan dengan TPESampler(seed=42, n_startup_trials=8), '
              'arah maximize, dan 30 trial. Seluruh trial selesai dalam 8,31 '
              'detik. Trial terbaik nomor 13 menghasilkan Macro F1 0,5532 dengan '
              'konfigurasi gini, max_depth 6, min_samples_leaf 3, '
              'min_samples_split 16, ccp_alpha 0,003536, max_features log2, dan '
              'class_weight None. Riwayat lengkap tersedia pada '
              'riwayat_trial.csv di repositori.'),
        ('h', 'LAMPIRAN 4: PERNYATAAN INTEGRITAS DATA'),
        ('p', 'Dataset yang dipakai adalah rekapitulasi internal kantor dengan '
              'sidik digital SHA-256 berikut.'),
        ('rumus', '686aa269511d6eb26ad661ebfde499ffbfd64383de4e84e93ea54ab23905785b'),
        ('p', 'Tidak ada baris yang ditambahkan, dihapus, atau diubah nilainya. '
              'Label dihitung ulang secara deterministik dari tanggal dan SLA '
              'untuk memverifikasi konsistensi. Data uji 34 berkas sudah pernah '
              'dipakai pada Tugas 04 dan Tugas 05, sehingga bukan holdout yang '
              'sepenuhnya buta; keterbatasan ini dinyatakan terbuka pada Bab I.'),
        ('h', 'LAMPIRAN 5: LEMBAR KOMITMEN'),
        ('p', 'Lembar komitmen integritas akademik telah ditandatangani seluruh '
              'anggota kelompok dan disertakan pada bagian awal dokumen ini. '
              'Tanda tangan basah pada lembar persetujuan dosen dilengkapi pada '
              'saat pengumpulan.'),
    ])


# ---------------------------------------------------------------------------
# Penyusunan
# ---------------------------------------------------------------------------
DOC = Document(str(TEMPLATE))

# 1. Hapus kotak petunjuk
jumlah = hapus_tabel_petunjuk()

# 2. Cover
p = cari('PROPOSAL RISET REKAYASA MODEL MACHINE LEARNING:')
fmt(p, JUDUL_BARIS, size=15, bold=True,
    align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, space_before=6, space_after=6,
    line=1.2)
p = cari('DISUSUN OLEH: KELOMPOK [ XX ]')
fmt(p, 'DISUSUN OLEH: KELOMPOK 02', size=11, bold=True,
    align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)

t0 = DOC.tables[0]
isi_tabel(t0, [
    ['No', 'NIM', 'Nama Lengkap Mahasiswa', 'Peran Teknis dalam Tim'],
    ['1', '12250158', 'Muhammad Rizqi Saputra',
     'Ketua Tim; pipeline CRISP-DM, Optuna, evaluasi'],
    ['2', '12250162', 'Dian Nur Cahya',
     'EDA, pra-pemrosesan, dokumentasi'],
    ['3', '12250161', 'Dicky Handia',
     'Model baseline/ensemble, kalibrasi ambang, deployment'],
], lebar=[1.2, 3.0, 5.2, 5.2], font=10, tengah=(0, 1))

# 3. Lembar persetujuan
p = cari('Naskah Proposal Riset Rekayasa Model Machine Learning berjudul:')
fmt(p, 'Naskah Proposal Riset Rekayasa Model Machine Learning berjudul:\n'
       '"' + JUDUL + '"\n\n'
       'Telah disetujui, dievaluasi, dan disahkan sebagai salah satu komponen '
       'evaluasi Ujian Tengah Semester (UTS) Mata Kuliah Pembelajaran Mesin '
       '(S1 - 3 SKS), Kelas Gabungan KG.043.10.A pada Program Studi '
       'Informatika & Sains Data, Fakultas Teknologi Informasi, Universitas '
       'Nusa Mandiri.',
    size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=0, line=1.3)
p = cari('Jakarta, 13 November 2026')
fmt(p, 'Jakarta, 12 November 2026\nMenyetujui,\nDosen Pengampu Pembelajaran '
       'Mesin,\n\n\n\n\nDr. Irwansyah Saputra, M.Kom.\nNIP: 201909149',
    size=11, align=WD_ALIGN_PARAGRAPH.LEFT, indent=0, line=1.15)

# 4. Lembar komitmen
p = cari('Kami yang bertanda tangan di bawah ini, seluruh mahasiswa anggota')
fmt(p, 'Kami yang bertanda tangan di bawah ini, seluruh mahasiswa anggota '
       'Kelompok 02 menyatakan dengan penuh kesadaran dan tanggung jawab:',
    size=11, align=WD_ALIGN_PARAGRAPH.LEFT, indent=0, line=1.3)
sisip_blok(p, [
    ('n', '1. Naskah Proposal Riset Rekayasa Model Machine Learning ini adalah '
          'karya orisinal kelompok kami, disusun berdasarkan eksperimen mandiri, '
          'dan bebas dari unsur plagiarisme (similarity Turnitin maksimal 20%).'),
    ('n', '2. Seluruh data yang diolah dalam eksperimen bersumber dari dataset '
          'empiris yang sah (Kaggle/UCI/Instansi mitra) dan tidak memuat '
          'manipulasi atau fabrikasi data buatan.'),
    ('n', '3. Tautan repositori Google Colab / GitHub yang kami lampirkan memuat '
          'kode program orisinal dan dapat direproduksi secara mandiri '
          '(reproducible code).'),
    ('n', '4. Apabila di kemudian hari terbukti melanggar komitmen integritas '
          'ini, kami bersedia menerima sanksi akademik sesuai ketentuan '
          'Universitas Nusa Mandiri.'),
])

t1 = DOC.tables[1]
anggota = [('Muhammad Rizqi Saputra', '12250158'),
           ('Dian Nur Cahya', '12250162'),
           ('Dicky Handia', '12250161')]
for j, (nama, nim) in enumerate(anggota):
    sel = t1.cell(0, j)
    fmt(sel.paragraphs[0], f'{nama}\nNIM {nim}\n\n\n( .................... )',
        size=9, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, line=1.0)
# hapus kolom tanda tangan keempat yang tidak terpakai
grid = t1._tbl.tblGrid
kolom = grid.findall(qn('w:gridCol'))
if len(kolom) == 4:
    grid.remove(kolom[3])
    for baris in t1.rows:
        tc = baris.cells[3]._tc
        tc.getparent().remove(tc)
for baris in t1.rows:
    for sel in baris.cells:
        sel.width = Cm(4.7)

# 5. Isi bab
bab_1()
bab_2()
bab_3()
daftar_pustaka()
lampiran()

# 6. Nomor halaman
nomor_halaman_footer()

# 7. Daftar isi (nomor halaman diisi ulang setelah ekspor pertama)
TOC_ENTRIES = [
    ('LEMBAR PERSETUJUAN DOSEN PENGAMPU', '2'),
    ('LEMBAR KOMITMEN INTEGRITAS AKADEMIK', '3'),
    ('DAFTAR ISI', '4'),
    ('BAB I  PENDAHULUAN', '5'),
    ('   1.1 Latar Belakang Masalah Riil & Domain Konteks', '5'),
    ('   1.2 Identifikasi Masalah & Problem Statement ML', '7'),
    ('   1.3 Perumusan Masalah (Research Questions)', '8'),
    ('   1.4 Tujuan Penelitian & Rekayasa Model', '9'),
    ('   1.5 Manfaat Penelitian (Teoretis dan Terapan)', '10'),
    ('   1.6 Ruang Lingkup & Batasan Masalah', '10'),
    ('BAB II  TINJAUAN PUSTAKA & LANDASAN TEORETIS', '12'),
    ('   2.1 Kajian Riset Terkait (State-of-the-Art)', '12'),
    ('   2.2 Paradigma Pembelajaran Mesin & Pemilihan Model', '13'),
    ('   2.3 Teori Pra-Pemrosesan & Rekayasa Fitur', '14'),
    ('   2.4 Metrik Evaluasi Kinerja & Ambang Batas Klasifikasi', '15'),
    ('   2.5 Landasan Teori Optimasi Bayesian (Optuna TPE)', '17'),
    ('BAB III  METODOLOGI PENELITIAN & PIPELINE REKAYASA MODEL ML', '18'),
    ('   3.1 Kerangka Kerja Metodologi (CRISP-DM)', '18'),
    ('   3.2 Karakteristik & Pemahaman Dataset', '19'),
    ('   3.3 Exploratory Data Analysis (EDA) & Temuan Utama', '20'),
    ('   3.4 Pipeline Pra-Pemrosesan Data Bebas Kebocoran Data', '21'),
    ('   3.5 Skema Eksperimen & Validasi Silang (Stratified 5-Fold CV)', '22'),
    ('   3.6 Perbandingan Model Baseline vs Ensemble', '23'),
    ('   3.7 Optimasi Hiperparameter dengan Optuna (TPE)', '24'),
    ('   3.8 Kalibrasi Ambang Batas (Decision Threshold Tuning)', '25'),
    ('   3.9 Cetak Biru Deployment Menuju UAS', '27'),
    ('DAFTAR PUSTAKA', '29'),
    ('LAMPIRAN-LAMPIRAN', '30'),
]

HALAMAN = {}
if (BASE / 'halaman.json').exists():
    HALAMAN = json.loads((BASE / 'halaman.json').read_text())

p = cari('LEMBAR PERSETUJUAN DOSEN PENGAMPU')
fmt(p, '', indent=0, space_after=0, line=1.0)
for ts in list(p.paragraph_format.tab_stops):
    pass
p.paragraph_format.tab_stops.add_tab_stop(
    Cm(14.3), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
for i, (label, hal) in enumerate(TOC_ENTRIES):
    hal = str(HALAMAN.get(label, hal))
    r = p.add_run(label + '\t' + hal)
    r.font.name = TNR
    r.font.size = Pt(10.5)
    if label.startswith('BAB') or label in ('DAFTAR PUSTAKA',
                                            'LAMPIRAN-LAMPIRAN',
                                            'LEMBAR PERSETUJUAN DOSEN PENGAMPU',
                                            'LEMBAR KOMITMEN INTEGRITAS AKADEMIK',
                                            'DAFTAR ISI'):
        r.bold = True
    if i < len(TOC_ENTRIES) - 1:
        r.add_break()
p.paragraph_format.line_spacing = 1.25
p.paragraph_format.space_after = Pt(4)

# 7b. Rapikan pagination dan keterikatan caption
def rapikan():
    from docx.oxml.ns import qn as _qn
    # Lembar persetujuan mulai halaman baru tanpa paragraf break kosong
    for par in DOC.paragraphs:
        if par.text.strip().startswith('LEMBAR PERSETUJUAN PROPOSAL'):
            par.paragraph_format.page_break_before = True
            prev = par._p.getprevious()
            if prev is not None and prev.tag == _qn('w:p'):
                brs = prev.findall('.//' + _qn('w:br'))
                if brs and not ''.join(prev.itertext()).strip():
                    prev.getparent().remove(prev)
            break
    # Lembar komitmen mulai halaman baru
    for par in DOC.paragraphs:
        if par.text.strip().startswith('LEMBAR KOMITMEN INTEGRITAS'):
            par.paragraph_format.page_break_before = True
            par.paragraph_format.space_before = Pt(0)
            break
    # Caption menempel pada tabel/gambar
    for par in DOC.paragraphs:
        t = par.text.strip()
        if t.startswith('Tabel ') or t.startswith('Gambar '):
            par.paragraph_format.keep_with_next = True
            par.paragraph_format.space_before = Pt(6)
        if par._p.findall('.//' + _qn('w:drawing')):
            par.paragraph_format.keep_with_next = True
    # Rapatkan jarak sesudah judul bab
    for par in DOC.paragraphs:
        if re.match(r'^BAB (I|II|III)\b', par.text.strip()):
            nxt = par._p.getnext()
            for _ in range(2):
                if nxt is None or nxt.tag != _qn('w:p'):
                    break
                if ''.join(nxt.itertext()).strip() or nxt.findall(
                        './/' + _qn('w:drawing')):
                    break
                sesudah = nxt.getnext()
                nxt.getparent().remove(nxt)
                nxt = sesudah
    # Rapatkan paragraf kosong sesudah judul subbab
    for par in DOC.paragraphs:
        if re.match(r'^\d\.\d\s', par.text.strip()):
            nxt = par._p.getnext()
            if (nxt is not None and nxt.tag == _qn('w:p')
                    and not ''.join(nxt.itertext()).strip()
                    and not nxt.findall('.//' + _qn('w:drawing'))):
                nxt.getparent().remove(nxt)
    # Paragraf pertama sesudah tabel diberi jarak atas
    for tbl in DOC.tables:
        nxt = tbl._tbl.getnext()
        if nxt is not None and nxt.tag == _qn('w:p'):
            par = Paragraph(nxt, DOC)
            if par.text.strip():
                par.paragraph_format.space_before = Pt(8)


rapikan()

# 8. Metadata
DOC.core_properties.title = ('Proposal UTS Pembelajaran Mesin - Kelompok 02 - '
                             'Kantor Notaris & PPAT Aries Buwana')
DOC.core_properties.author = 'Kelompok 02'
DOC.core_properties.subject = ('Proposal riset rekayasa model machine learning '
                               'Bab I-III')
DOC.core_properties.keywords = ('Pembelajaran Mesin; Decision Tree; Optuna; '
                                'Threshold Tuning; Notaris PPAT; UTS')

DOC.save(str(OUT))
print(f'DOCX: {OUT}')
print(f'Kotak petunjuk dihapus: {jumlah}')
