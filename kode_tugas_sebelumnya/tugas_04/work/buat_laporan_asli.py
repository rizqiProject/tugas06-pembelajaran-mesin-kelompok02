"""Susun laporan T04 di atas template resmi; seluruh angka dari hasil eksekusi."""
from pathlib import Path
import json
import math
import pandas as pd
import numpy as np
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
H=ROOT/'work/hasil_tugas04_asli'
S=json.loads((H/'ringkasan_hasil.json').read_text())
M=pd.DataFrame(S['metrics']); N=pd.DataFrame(S['nested'])
F=S['frozen']; L=S['local']; A=S['audit']
BEST=F['best_params']; T=F['threshold_oof']
PFI=pd.read_csv(H/'permutation_importance_100_ulangan.csv')
SH=pd.read_csv(H/'shap_global_semua_fitur.csv')
LC=pd.read_csv(H/'shap_kontribusi_kasus_lokal.csv')
DATA=pd.read_csv(H/'berkas_notaris_asli_dengan_fitur_tanggal.csv')
out=ROOT/'output';out.mkdir(exist_ok=True)
doc=Document(ROOT/'upload/Template_Tugas_04_Pembelajaran_Mesin.docx')
body=doc._element.body
for el in list(body):
    if el.tag!=qn('w:sectPr'): body.remove(el)
sec=doc.sections[0]
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Inches(.8)
sec.header_distance=Inches(.3);sec.footer_distance=Inches(.32)
for sty in doc.styles:
    if sty.type==1:
        sty.font.color.rgb=RGBColor(0,0,0)
        for b in list(sty._element.xpath('./w:pPr/w:pBdr')):
            b.getparent().remove(b)
normal=doc.styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(11)
normal.paragraph_format.line_spacing=1.13
normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.widow_control=True
for name,size in [('Title',14),('Heading 1',12),('Heading 2',11.3),('Heading 3',11)]:
    st=doc.styles[name];st.font.name='Times New Roman';st.font.size=Pt(size)
    st.font.color.rgb=RGBColor(0,0,0);st.font.bold=True
    st.paragraph_format.space_before=Pt(9 if name!='Title' else 0)
    st.paragraph_format.space_after=Pt(7)
    st.paragraph_format.keep_with_next=True
    st.paragraph_format.line_spacing=1.06
cp=doc.core_properties;cp.title='Tugas 04 Kelompok 02 Notaris PPAT'
cp.subject='Hyperparameter tuning dan explainability Decision Tree'
cp.author='Kelompok 02';cp.keywords='Pembelajaran Mesin; Decision Tree; SHAP; sumber asli'
footer=sec.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
rr=footer.add_run('Tugas 04 | Kelompok 02 | Notaris dan PPAT Aries Buwana                         Halaman ')
rr.font.size=Pt(8);rr.font.color.rgb=RGBColor(0,0,0)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)

def f(x,n=3):return f'{float(x):.{n}f}'.replace('.',',')
def pct(x,n=1):return f'{100*float(x):.{n}f}%'.replace('.',',')
def delta(a,b):return f'{100*(a-b):+.1f} pp'.replace('.',',')
def metric(model,part='Test'):
    return M[(M.model==model)&(M.partisi==part)].iloc[0]
BT=metric('Baseline v5');TT=metric('Tuned 0.50');OT=metric('Tuned OOF')
BR=metric('Baseline v5','Train');TR=metric('Tuned 0.50','Train')

def p(text='',bold=False,size=None,after=None):
    q=doc.add_paragraph()
    r=q.add_run(text);r.bold=bold
    if size:r.font.size=Pt(size)
    if after is not None:q.paragraph_format.space_after=Pt(after)
    return q
def heading(text,level=1):return doc.add_paragraph(text,style=f'Heading {level}')
def page(title,level=2):
    doc.add_page_break();heading(title,level)
def table(headers,rows,widths,font=9.7,align_cols=None):
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.autofit=False
    for j,w in enumerate(widths):t.columns[j].width=Inches(w)
    borders=OxmlElement('w:tblBorders')
    for k in ['top','left','bottom','right','insideH','insideV']:
        e=OxmlElement('w:'+k);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'5');e.set(qn('w:color'),'D9D9D9');borders.append(e)
    t._tbl.tblPr.append(borders)
    margins=OxmlElement('w:tblCellMar')
    for k,v in [('top',75),('bottom',75),('left',90),('right',90)]:
        e=OxmlElement('w:'+k);e.set(qn('w:w'),str(v));e.set(qn('w:type'),'dxa');margins.append(e)
    t._tbl.tblPr.append(margins)
    for j,h in enumerate(headers):t.rows[0].cells[j].text=str(h)
    for vals in rows:
        cells=t.add_row().cells
        for j,v in enumerate(vals):cells[j].text=str(v)
    for i,row in enumerate(t.rows):
        nr=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(nr)
        if i==0:
            rep=OxmlElement('w:tblHeader');row._tr.get_or_add_trPr().append(rep)
        for j,c in enumerate(row.cells):
            c.width=Inches(widths[j]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=c._tc.get_or_add_tcPr();shade=OxmlElement('w:shd')
            shade.set(qn('w:fill'),'233D70' if i==0 else ('F3F5F7' if i%2==0 else 'FFFFFF'))
            tcpr.append(shade)
            for q in c.paragraphs:
                q.paragraph_format.space_before=Pt(0);q.paragraph_format.space_after=Pt(0)
                q.paragraph_format.line_spacing=1.05
                q.paragraph_format.keep_with_next=False
                if align_cols and j in align_cols:q.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for r in q.runs:
                    r.font.name='Times New Roman';r.font.size=Pt(font)
                    r.font.bold=(i==0);r.font.color.rgb=RGBColor(255,255,255) if i==0 else RGBColor(0,0,0)
    p('',after=2).paragraph_format.line_spacing=.25
    return t
def fig(file,caption,width=6.85,max_height=None):
    from PIL import Image
    img=H/'grafik'/file
    iw,ih=Image.open(img).size
    if max_height:width=min(width,max_height*iw/ih)
    q=doc.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    q.paragraph_format.space_after=Pt(4);q.paragraph_format.keep_with_next=True
    run=q.add_run();run.add_picture(str(img),width=Inches(width))
    docpr=run._r.xpath('.//wp:docPr')
    if docpr:docpr[0].set('descr',caption)
    cap=p(caption,size=9,after=7);cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
    return cap
def code(text):
    q=doc.add_paragraph()
    q.paragraph_format.line_spacing=1.0;q.paragraph_format.space_after=Pt(7)
    for i,line in enumerate(text.strip('\n').splitlines()):
        r=q.add_run(('\n' if i else '')+line);r.font.name='Courier New';r.font.size=Pt(8.4)
    return q
def cv_summary(name,k):
    d=N[N.model==name][k]
    return f'{f(d.mean())} ± {f(d.std(ddof=1))}'
def nice(n):
    names={'jumlah_penghadap':'Jumlah penghadap','sla_hari':'SLA hari',
       'beban_7hari':'Beban 7 hari','jumlah_dokumen':'Jumlah dokumen',
       'dokumen_lengkap':'Dokumen lengkap saat masuk',
       'perlu_pengesahan_kemenkum':'Perlu pengesahan Kemenkum','perlu_pajak':'Perlu pajak',
       'ada_rups_awal':'RUPS tersedia saat masuk','bulan_sin':'Bulan sin','bulan_cos':'Bulan cos',
       'kategori_akta':'Kategori akta','hari_masuk':'Hari masuk','kanal_masuk':'Kanal masuk',
       'petugas':'Kode staf'}
    if n in names:return names[n]
    for prefix,word in [('kategori_akta_','Akta '),('hari_masuk_','Hari '),
        ('kanal_masuk_','Kanal '),('petugas_','Kode ')]:
        if n.startswith(prefix):return word+n[len(prefix):].replace('_',' ')
    return n.replace('_',' ')

# Seluruh isi berikut dihitung ulang pada baris sumber=asli dari CSV.
ntrain=int(BR['n']);ntest=int(BT['n']);npos=int(BT['positif'])
trainpos=int(BR['positif']);testneg=ntest-npos
global_values=pd.read_csv(H/'shap_semua_34_berkas.csv')
test_data=DATA.set_index('id_berkas').loc[global_values.id_berkas].reset_index()

def feature_values(name):
    if name in test_data.columns:return test_data[name].to_numpy(dtype=float)
    for raw_name in ['kategori_akta','hari_masuk','kanal_masuk','petugas']:
        pre=raw_name+'_'
        if name.startswith(pre):return test_data[raw_name].eq(name[len(pre):]).astype(float).to_numpy()
    raise KeyError(name)

def direction_note(name):
    vals=feature_values(name);phi=global_values[name].to_numpy()
    uniq=np.unique(vals)
    if len(uniq)<2:return 'Nilai fitur ini sama pada sampel uji; arah perbedaan nilainya tidak dapat dibandingkan.'
    if len(uniq)==2:lo,hi=uniq[0],uniq[-1]
    else:
        lo,hi=np.quantile(vals,[.25,.75])
        if np.isclose(lo,hi):lo,hi=uniq[0],uniq[-1]
    lv=float(phi[vals<=lo].mean());hv=float(phi[vals>=hi].mean())
    return (f'Pada nilai sampai {f(lo,2)}, rata-rata kontribusi SHAP adalah {f(lv,4)}; '
            f'pada nilai mulai {f(hi,2)}, rata-ratanya {f(hv,4)}.')

# Halaman 1
q=doc.add_paragraph('LAPORAN PENUGASAN MINGGU 04\nPEMBELAJARAN MESIN',style='Title')
q.alignment=WD_ALIGN_PARAGRAPH.CENTER
q=p('Hyperparameter Tuning, Feature Importance, dan Model Explainability',bold=True,size=11.2)
q.alignment=WD_ALIGN_PARAGRAPH.CENTER
q=p('Mata Kuliah Pembelajaran Mesin (S1, 3 SKS) | Semester Gasal 2026/2027\nDosen Pengampu Dr. Irwansyah Saputra, M.Kom. (NIP 201909149)',size=9.7)
q.alignment=WD_ALIGN_PARAGRAPH.CENTER
heading('A. IDENTITAS KELOMPOK & KONFIRMASI MODEL BASELINE TERBAIK')
table(['No','NIM Mahasiswa','Nama Mahasiswa & Peran Kerja Tim'],[
 ['1','12250158','Muhammad Rizqi Saputra\nKoordinator Tim, Dokumentator, dan QC'],
 ['2','12250162','Dian Nur Cahya\nLead Analis Data dan Pipeline Validation'],
 ['3','12250161','Dicky Handia\nLead Model Engineer, Tuning, dan Explainability']], [.35,1.05,5.5],10,align_cols=[0,1])
heading('Objek studi dan sumber data',2)
p('Objek penelitian kami adalah Kantor Notaris & PPAT Aries Buwana, Dipl.-Ing., SH, MKn, Jakarta Barat. Data berkas berasal dari rekap kantor dan tersimpan pada CSV v5. Analisis ini menggunakan 169 baris dengan kode sumber=asli. Nilai pengukuran dan label mengikuti CSV; fitur tambahan hanya berupa turunan tanggal.')
table(['Komponen','Konfirmasi'],[
 ['Target prediksi','terlambat: 0 = tepat waktu dan 1 = terlambat. Waktu prediksi ditetapkan pada penerimaan serta pemeriksaan awal berkas.'],
 ['Model terbaik Tugas 03','Decision Tree, max_depth=4, min_samples_leaf=5, class_weight=balanced, random_state=42. Test T03: F1 positif 0,267 dan AP 0,250.'],
 ['Dataset analisis Tugas 04','169 berkas sumber=asli; 35 terlambat dan 134 tepat waktu. Pembagian 135 train dan 34 test.'],
 ['Tujuan pengembangan','Tuning lima parameter, nested CV, threshold moving, permutation importance, dan penjelasan SHAP.']], [1.6,5.3],10)
p(f'Pada data uji, AP baseline {f(BT.ap)} berubah menjadi {f(TT.ap)} setelah tuning, dengan delta {delta(TT.ap,BT.ap)}. F1 positif pada ambang 0,50 berubah dari {f(BT.f1)} menjadi {f(TT.f1)}. Hasil ini menunjukkan perbaikan pada partisi uji saat ini, dengan keterbatasan hanya tujuh kasus terlambat. [1][2][3]',size=10.5)

# Halaman 2
page('A.1 Audit data dan tindak lanjut catatan dosen')
p('Pemilihan baris dilakukan menggunakan kondisi sumber == asli pada CSV yang diberikan kelompok. Kolom sumber dipakai untuk seleksi data dan tidak menjadi prediktor. Tidak ada perubahan label, penggantian nilai pengukuran, atau penambahan baris observasi. Daftar ID yang masuk train dan test disimpan agar setiap angka dapat diperiksa kembali.')
table(['Pemeriksaan','Hasil'],[
 ['Jumlah data analisis','169 baris; 35 terlambat (20,7%) dan 134 tepat waktu (79,3%).'],
 ['Duplikasi ID dan isi',f'{A["duplicate_payload"]} duplikasi isi setelah kolom identitas dibuang; tidak ada ID ganda.'],
 ['Konsistensi label',f'{A["label_discrepancies_calendar_days"]} perbedaan terhadap aturan hari kalender: durasi aktual melebihi SLA.'],
 ['Tanggal RUPS',f'{A["missing"]["tgl_rups"]} kosong; {A["future_rups_excluded"]} tanggal sesudah tanggal masuk tidak dipakai sebagai informasi awal.'],
 ['Versi Tugas 03 dibanding v5','Tugas 03 mencatat 33 terlambat dari 169 berkas; subset sumber=asli v5 memuat 35. Versi input tidak dianggap identik.']], [2,4.9],10)
p('Selisih jumlah positif sebesar dua dicatat sebagai perbedaan versi data; identitas baris yang berubah belum dapat ditentukan karena matriks input Tugas 03 tidak tersedia. Hasil historis Tugas 03 tetap dipertahankan sebagai rujukan. Delta tuning dihitung antara baseline yang dilatih ulang dan tuned pada 169 baris, fitur, dan partisi yang sama, sehingga pengaruh perubahan versi tidak tercampur dengan pengaruh tuning.')
table(['Catatan dosen Tugas 03','Tindak lanjut yang dapat diuji'],[
 ['Sampel kecil dan metrik tidak stabil','Nested 5-fold CV, simpangan baku antar-fold, bootstrap berpasangan, dan uji sensitivitas temporal.'],
 ['Tambahkan faktor eksternal','Gunakan perlu_pengesahan_kemenkum dan perlu_pajak yang sudah tersedia. Instansi tujuan tidak ditebak dari jenis akta.'],
 ['Tambahkan kelengkapan awal','Gunakan indikator dokumen_lengkap dan jumlah_dokumen yang tersedia. Jumlah item wajib dan item diterima belum tersedia untuk menghitung skor ceklis terperinci.'],
 ['TreeExplainer dan threshold moving','SHAP global dan lokal dihitung dengan pustaka asli. Ambang 0,25 diuji bersama 0,50 dan ambang OOF.']], [1.9,5],9.7)
p('Fitur biaya jasa, jumlah revisi, tanggal akta, dan tanggal selesai tidak menjadi prediktor karena belum tentu tersedia pada waktu penerimaan. Kolom identitas dan nomor urut juga dikeluarkan. Rincian seluruh fitur ada pada lampiran kamus data.',size=10.5)

# Halaman 3
page('B. DESAIN RUANG PENCARIAN HYPERPARAMETER & STRATEGI TUNING',1)
p('Kami mempertahankan Decision Tree dari Tugas 03 dan menala kompleksitasnya menggunakan GridSearchCV. Ruang pencarian disesuaikan dengan 135 data latih agar pohon dangkal maupun konfigurasi dengan dukungan daun lebih besar dapat dibandingkan. Objektif utama adalah Average Precision (AP), karena kelas terlambat merupakan minoritas dan kualitas peringkat risiko perlu diperiksa sebelum memilih ambang.')
gridvals={'max_depth':'1, 2, 3, 4, 5','min_samples_leaf':'2, 5, 10, 15',
 'min_samples_split':'2, 10','ccp_alpha':'0; 0,002; 0,010; 0,020','class_weight':'None, balanced'}
reasons={'max_depth':'Mengontrol panjang percabangan dan risiko menghafal data kecil.',
 'min_samples_leaf':'Menjaga jumlah dukungan data pada daun; nilai kecil juga diuji agar trade-off terlihat.',
 'min_samples_split':'Membatasi kapan simpul boleh dipecah. Beberapa kombinasi dapat setara bila syarat daun lebih ketat.',
 'ccp_alpha':'Menguji pruning atau pemangkasan cabang yang tidak memberi tambahan mutu yang cukup.',
 'class_weight':'Membandingkan pembobotan kelas dengan tanpa bobot, berdasarkan AP CV.'}
table(['Hyperparameter','Tipe','Nilai yang diuji','Nilai terpilih dan alasan'],[
 [k,'String' if k=='class_weight' else ('Float' if k=='ccp_alpha' else 'Integer'),v,
  str(BEST['model__'+k])+'\n'+reasons[k]] for k,v in gridvals.items()], [1.4,.6,1.55,3.35],9.7)
p('Jumlah kandidat adalah 5 × 4 × 2 × 4 × 2 = 320. Setiap kandidat dinilai dengan inner 5-fold Stratified CV. Pencarian final memerlukan 1.600 fit CV dan satu refit. Parameter terpilih adalah yang terbaik di antara kandidat yang diuji, bukan jaminan optimum di semua konfigurasi.')
table(['Partisi atau validasi','Pengaturan','Fungsi'],[
 ['Train',f'{ntrain} berkas; {trainpos} terlambat dan {ntrain-trainpos} tepat','Memilih parameter, transformasi, serta ambang.'],
 ['Test',f'{ntest} berkas; {npos} terlambat dan {testneg} tepat','Evaluasi setelah keputusan model dibekukan.'],
 ['Nested CV','Outer 5-fold dan inner 5-fold pada train','Mengukur prosedur seleksi pada validasi outer.'],
 ['Random state','42; stratified split 80:20','Memungkinkan pembagian yang sama dijalankan ulang.']], [1.2,2.6,3.1],9.8)

# Halaman 4
page('B.1 Pipeline dan potongan kode Python')
p('SimpleImputer dan One-Hot Encoding ditempatkan di dalam Pipeline. Setiap lipatan CV mempelajari imputasi dan kategori hanya dari lipatan latihnya. Decision Tree tidak memerlukan standardisasi skala. Penalaan memakai AP, sementara recall dan F1 kelas positif tetap diperiksa pada hasil akhir.')
code('''import pandas as pd
from sklearn.model_selection import GridSearchCV, train_test_split
from work.analisis_tugas04_asli import make_data, pipeline, FEATURES, cv5

raw = pd.read_csv("upload/berkas_notaris_ v5.csv")
raw = raw.loc[raw["sumber"].eq("asli")].reset_index(drop=True)
data = make_data(raw)  # Hanya turunan tanggal yang deterministik
X, y = data[FEATURES], data["terlambat"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42)

param_grid = {
    "model__max_depth": [1, 2, 3, 4, 5],
    "model__min_samples_leaf": [2, 5, 10, 15],
    "model__min_samples_split": [2, 10],
    "model__ccp_alpha": [0.0, 0.002, 0.01, 0.02],
    "model__class_weight": [None, "balanced"]
}
search = GridSearchCV(
    pipeline(), param_grid, cv=cv5(),
    scoring="average_precision", refit=True,
    return_train_score=True, n_jobs=2, error_score="raise")
search.fit(X_train, y_train)
best_model = search.best_estimator_
''')
heading('Waktu prediksi dan pencegahan kebocoran data',2)
p('Waktu prediksi ditetapkan setelah staf mencatat pemeriksaan awal berkas. Indikator RUPS hanya bernilai 1 bila tanggalnya sudah ada pada atau sebelum tanggal masuk. Hari serta koordinat bulan dihitung dari tanggal masuk. Target, tanggal selesai, durasi aktual, nomor urut, dan kode sumber tidak masuk ke matriks prediktor.')
p('Pada setiap outer fold, grid dan pemilihan ambang hanya memakai outer train. Model kemudian dievaluasi pada outer validation. Setelah seluruh prosedur tersebut selesai, pencarian final dilakukan pada seluruh train. Parameter serta ambang disimpan sebelum test dinilai. Permutation importance dan SHAP tidak digunakan untuk memilih ulang model pada test.')
p('Sebanyak 14 fitur mentah dipakai. Ketersediaan indikator kelengkapan, beban tujuh hari, kebutuhan eksternal, kanal, dan penugasan staf pada saat masuk merupakan definisi operasional model; pencatatannya perlu mengikuti waktu yang sama bila model diuji di kantor.',size=10.5)

# Halaman 5
page('C. EVALUASI KOMPARASI PERFORMA BASELINE TUGAS 03 VS TUNED TUGAS 04',1)
heading('C.1 Riwayat Tugas 03 dan perbandingan pada versi data saat ini',2)
p('Pada Tugas 03, Decision Tree dipilih dari Logistic Regression, Decision Tree, dan Random Forest. Riwayat berikut berasal dari laporan yang telah dinilai dosen. Hasil tersebut tidak disamakan dengan baseline yang dilatih ulang karena komposisi label serta fitur pada CSV v5 berbeda. [1][2]')
table(['Metrik historis Decision Tree','Train CV T03','Test T03'],[
 ['F1 positif','0,516','0,267'],['Precision dan recall positif','Tidak dilaporkan','0,250 dan 0,286'],
 ['AP dan ROC-AUC','Tidak dilaporkan','0,250 dan 0,476'],
 ['TP / FN / FP / TN','Tidak dilaporkan','2 / 5 / 6 / 21']], [3,1.6,2.3],9.9)
p('Tabel berikut memakai 169 baris sumber=asli dari v5. Kedua model memakai 14 fitur yang sama dan ID train-test yang sama. Ambang 0,50 dipertahankan agar delta di sini mengukur perubahan dari hyperparameter, bukan perubahan ambang.')
metrics_names={'accuracy':'Accuracy','precision':'Precision positif','recall':'Recall positif',
 'f1':'F1 positif','macro_f1':'Macro F1','ap':'Average Precision','roc_auc':'ROC-AUC'}
table(['Metrik','Baseline Train v5','Baseline Test v5','Tuned Train v5','Tuned Test dan delta'],[
 [lab,f(BR[k]),f(BT[k]),f(TR[k]),f(TT[k])+'\n'+delta(TT[k],BT[k])] for k,lab in metrics_names.items()],
 [1.45,1.1,1.1,1.1,2.15],10,align_cols=[1,2,3,4])
p('Baseline memakai konfigurasi T03: max_depth=4, min_samples_leaf=5, class_weight=balanced, min_samples_split=2, dan ccp_alpha=0. Delta adalah skor test tuned dikurangi baseline dalam poin persentase. Skor train merupakan hasil fit seluruh train, sedangkan skor CV dibahas tersendiri. F1 positif dan Macro F1 disajikan terpisah agar tidak tertukar dengan metrik macro pada Tugas 03.',size=10.3)
p(f'Pada ambang tetap, delta AP adalah {delta(TT.ap,BT.ap)}, F1 positif {delta(TT.f1,BT.f1)}, dan recall {delta(TT.recall,BT.recall)}. Peningkatan ini berlaku pada partisi uji saat ini; kestabilannya perlu dibaca bersama variasi CV dan jumlah positif uji yang kecil.')

# Halaman 6
page('C.2 Validasi silang dan diagnosis generalisasi')
table(['Prosedur','AP outer CV','F1 positif outer CV','Recall outer CV','Macro F1 outer CV'],[
 [lab,cv_summary(k,'ap'),cv_summary(k,'f1'),cv_summary(k,'recall'),cv_summary(k,'macro_f1')]
 for k,lab in [('baseline','Baseline 0,50'),('tuned_050','Tuned 0,50'),('tuned_threshold','Tuned dan ambang OOF')]],
 [1.65,1.3,1.3,1.3,1.35],9.5,align_cols=[1,2,3,4])
p('Skor CV adalah rata-rata lima outer validation dan simpangan baku sampel. Pada baris ambang OOF, setiap fold memakai ambang yang dipilih dari OOF outer train miliknya. Dengan demikian outer validation tidak ikut menentukan parameter atau ambang yang akan dinilainya. [8]')
table(['Fold','AP baseline','AP tuned','Ambang inner','F1 tuned dan ambang'],[
 [str(i),f(N[(N.fold==i)&(N.model=='baseline')].iloc[0].ap),
 f(N[(N.fold==i)&(N.model=='tuned_050')].iloc[0].ap),
 f(N[(N.fold==i)&(N.model=='tuned_threshold')].iloc[0].threshold,2),
 f(N[(N.fold==i)&(N.model=='tuned_threshold')].iloc[0].f1)] for i in range(1,6)],
 [.5,1.25,1.25,1.7,2.2],10,align_cols=[0,1,2,3,4])
p(f'AP inner CV tertinggi pada pencarian final adalah {f(F["best_inner_cv_ap"])}. Skor ini dipakai memilih kandidat sehingga dapat optimistis. AP outer CV prosedur tuned adalah {cv_summary("tuned_050","ap")}, dibanding baseline {cv_summary("baseline","ap")}. AP outer naik dari 0,364 ke 0,381, tetapi F1 outer pada 0,50 turun dari 0,339 ke 0,309. Kenaikan test tidak berarti semua ukuran generalisasi ikut membaik. Perbedaan antar-fold menunjukkan sensitivitas terhadap sampel.')
table(['Diagnosis pada ambang 0,50','Baseline v5','Tuned v5'],[
 ['F1 train dan test',f(BR.f1)+' dan '+f(BT.f1),f(TR.f1)+' dan '+f(TT.f1)],
 ['Gap F1 train dikurangi test',delta(BR.f1,BT.f1),delta(TR.f1,TT.f1)],
 ['AP train dan test',f(BR.ap)+' dan '+f(BT.ap),f(TR.ap)+' dan '+f(TT.ap)],
 ['Struktur pohon','Depth maksimum 4; leaf minimum 5',f'Depth aktual {L["model_depth"]}; {L["model_leaves"]} daun']],
 [2.75,2.05,2.1],10)
p(f'Gap F1 tuned masih {delta(TR.f1,TT.f1)} walaupun lebih kecil daripada baseline. Kedua pohon masih menunjukkan indikasi overfitting. Selisih kecil pada sebagian skor juga tidak otomatis berarti good fit; level skor, variasi fold, dan mutu prediksi kelas terlambat harus diperiksa bersama.')

# Halaman 7
page('C.3 Confusion matrix dan perubahan ambang prediksi')
fig('01_confusion_matrix.png',f'Gambar 1. Confusion matrix pada {ntest} test yang sama. Positif adalah Terlambat.',max_height=2.7)
table(['Model dan ambang','TP / FN','FP / TN','Precision','Recall','F1 positif','Alarm'],[
 [lab,f'{int(r.tp)} / {int(r.fn)}',f'{int(r.fp)} / {int(r.tn)}',f(r.precision),f(r.recall),f(r.f1),pct(r.alert_rate)]
 for n,lab in [('Baseline v5','Baseline 0,50'),('Tuned 0.50','Tuned 0,50'),('Tuned 0.25','Tuned 0,25'),('Tuned OOF',f'Tuned OOF {f(T,2)}')]
 for r in [metric(n)]], [1.55,.85,.85,.9,.8,.9,1.05],9.6,align_cols=[1,2,3,4,5,6])
p(f'Pada 0,50, model tuned menangkap {int(TT.tp)} dari {npos} kasus terlambat. Setelah ambang menjadi 0,25, jumlah tersebut menjadi {int(metric("Tuned 0.25").tp)}. Pada ambang OOF {f(T,2)}, model menangkap {int(OT.tp)} dan melewatkan {int(OT.fn)} kasus, dengan {int(OT.fp)} alarm palsu. Penurunan ambang menaikkan kepekaan sekaligus menambah pemeriksaan.')
p(f'Dari {int(OT.tp+OT.fp)} alarm pada ambang OOF, hanya {int(OT.tp)} yang benar terlambat. Proporsi alarm adalah {pct(OT.alert_rate)} dan precision {pct(OT.precision)}. Ambang ini dipilih dari train untuk tujuan penelitian. Karena 26 dari 34 berkas mendapat alarm, penggunaannya perlu diuji bersama kapasitas pemeriksaan staf; recall tinggi belum berarti aturan alarm sudah efisien.')
naive=pd.read_csv(H/'baseline_naif.csv')
table(['Pembanding sederhana','Accuracy','Recall','F1 positif','AP'],[
 [r.model,f(r.accuracy),f(r.recall),f(r.f1),f(r.ap)] for r in naive.itertuples()],
 [2.8,1,1,1.1,1],10,align_cols=[1,2,3,4])
p(f'Selalu menebak tepat waktu menghasilkan accuracy {pct(testneg/ntest)} dan tidak menangkap keterlambatan. Selalu menebak terlambat mencapai recall 1,000 sambil memberi {testneg} alarm palsu. Karena itu kami memeriksa precision, recall, F1, AP, dan jumlah alarm bersamaan.',size=10.5)

# Halaman 8
page('C.4 Kurva ROC PR dan ketidakpastian delta gain')
fig('02_kurva_roc_pr.png','Gambar 2. Kurva ROC serta Precision Recall dari skor model pada test.',max_height=3.25)
p(f'AP test berubah dari {f(BT.ap)} menjadi {f(TT.ap)}, sedangkan ROC-AUC berubah dari {f(BT.roc_auc)} menjadi {f(TT.roc_auc)}. AP memakai average_precision_score dan tidak sama dengan luas trapezoid PR. Prevalensi positif test sebesar {f(npos/ntest)} menjadi acuan AP peringkat tanpa informasi. [4][5]')
table(['Delta pada test yang sama','Rata-rata bootstrap','Interval persentil 95%'],[
 [lab,delta(c['mean'],0),f(c['low'],4)+' s.d. '+f(c['high'],4)]
 for key,lab in [('delta_ap_tuning','AP dari tuning'),('delta_f1_tuning','F1 dari tuning pada 0,50'),('delta_f1_total','F1 termasuk ambang OOF')]
 for c in [S['bootstrap'][key]]], [3.05,1.6,2.25],10)
p('Interval dihitung dari 2.000 bootstrap terstratifikasi dan berpasangan. Indeks berkas yang sama dipakai untuk kedua model pada setiap ulangan. Kolom interval memakai skala skor 0 sampai 1, sedangkan rata-rata memakai poin persentase. Interval bersyarat pada model yang sudah dilatih dan tidak mencakup seluruh variasi pemilihan model.')
p('Batas bawah interval delta AP menyentuh nol. Titik estimasi AP pada test membaik, tetapi sampel ini belum cukup untuk menyatakan bahwa keuntungan yang sama akan bertahan pada periode baru. Kesimpulan juga perlu memperhatikan outer CV yang memiliki variasi besar.')
p(f'Satu kasus positif yang berubah pada test menggeser recall sebesar {f(100/npos,1)} poin persentase. Oleh karena itu selisih satu atau dua prediksi perlu dijelaskan lewat jumlah TP, FN, dan FP, bukan hanya skor desimal.',size=10.5)

# Halaman 9
page('D. ANALISIS PERMUTATION FEATURE IMPORTANCE',1)
p('Permutation importance dihitung pada test melalui seluruh pipeline. Setiap kolom mentah diacak 100 kali, lalu AP setelah pengacakan dikurangkan dari AP awal. Penilaian per kolom mentah membuat kategori dengan banyak level tetap dinilai sebagai satu fitur, sehingga tidak bergantung pada Gini importance yang peka terhadap kardinalitas. [4]')
fig('03_permutation_importance.png','Gambar 3. Top 10 permutation importance. Galat menunjukkan ±1 simpangan baku pengacakan, bukan interval kepercayaan.',max_height=3.8)
table(['Peringkat dan fitur','Penurunan AP rata-rata','Simpangan baku'],[
 [f'{i+1}. {nice(r.fitur)}',f(r['mean'],4),f(r['sd'],4)] for i,(_,r) in enumerate(PFI.head(10).iterrows())],
 [4.05,1.55,1.3],9.6,align_cols=[1,2])
positive_count=int((PFI['mean']>1e-10).sum())
p(f'Terdapat {positive_count} fitur dengan mean PFI positif. Nilai mendekati nol menunjukkan tambahan mutu peringkat belum terlihat pada model serta test ini. Nilai negatif tetap dicatat pada tabel lengkap jika pengacakan memperbaiki AP. Peringkat fitur tidak menjadi bukti sebab keterlambatan.',size=10.3)

# Halaman 10
page('D.1 Interpretasi bisnis dan pemeriksaan kelompok fitur')
business={
 'beban_7hari':'Beban tujuh hari dapat mewakili jumlah pekerjaan yang perlu ditangani staf. Jika polanya stabil pada periode baru, kantor dapat memakai informasi beban untuk merencanakan pemeriksaan serta pembagian tugas. Nilai ini mengikuti kolom CSV dan tidak dihitung ulang sebagai jumlah seluruh antrean kantor dari sampel 169 berkas.',
 'jumlah_penghadap':'Jumlah penghadap dapat berkaitan dengan kebutuhan koordinasi, pemeriksaan identitas, dan penyelarasan dokumen. Hubungan model tidak berarti tambahan satu penghadap selalu menyebabkan keterlambatan.',
 'bulan_cos':'Bulan cos menyatakan posisi siklik bulan bersama bulan sin. Nilainya tidak menunjukkan urutan bulan yang makin besar. Pengaruhnya perlu dibaca bersama kalender pekerjaan dan belum membuktikan musim tertentu sebagai penyebab keterlambatan.',
 'bulan_sin':'Bulan sin adalah salah satu koordinat siklus tahunan. Interpretasi musim memerlukan pasangan cos dan kalender operasional, bukan nilai sin tunggal.',
 'dokumen_lengkap':'Indikator ini mencatat kelengkapan awal. Jika belum lengkap, staf dapat meminta item persyaratan yang kurang. Model yang tidak memakainya pada pohon final belum membuktikan bahwa pemeriksaan kelengkapan tidak penting.',
 'jumlah_dokumen':'Jumlah dokumen berbeda dari kelengkapan persyaratan. Interpretasi hitungan perlu mempertimbangkan jenis dan mutu dokumennya.',
 'perlu_pengesahan_kemenkum':'Indikator kebutuhan pengesahan memberi konteks jalur proses. Waktu tunggu aktual pada instansi belum tersedia, sehingga kontribusinya tidak langsung menunjukkan lamanya layanan eksternal.',
 'perlu_pajak':'Indikator kebutuhan pajak memberi konteks awal. Waktu pembayaran dan hasil pemeriksaan pajak tidak tercatat pada fitur awal ini.',
 'kategori_akta':'Kategori dapat merangkum kompleksitas dan pola kebutuhan layanan. Kontribusinya dapat berbagi informasi dengan SLA serta indikator eksternal.',
 'sla_hari':'SLA adalah batas toleransi waktu yang sudah ditetapkan sebelum prediksi. Karena juga dipakai membentuk target, perbedaan SLA harus ditafsirkan sebagai perbedaan definisi ketepatan waktu antar-berkas.',
 'petugas':'Kode staf dapat mencerminkan pembagian kasus. Ia tidak dipakai untuk menilai produktivitas individu tanpa mengendalikan perbedaan kompleksitas penugasan.',
 'kanal_masuk':'Kanal dapat berhubungan dengan pola penerimaan dan jenis berkas. Hubungan tersebut perlu dipisahkan dari kompleksitas kasus.',
 'hari_masuk':'Hari masuk memberi konteks jadwal penerimaan. Informasi jam dan kalender hari libur belum tersedia.',
 'ada_rups_awal':'Nilai nol dapat berarti belum ada informasi RUPS pada waktu masuk atau RUPS tidak relevan bagi akta tersebut.'}
for i,(_,r) in enumerate(PFI.head(3).iterrows(),1):
    heading(f'{i} {nice(r.fitur)}',3)
    p(f'Penurunan AP rata-rata {f(r["mean"],4)} dengan simpangan baku {f(r["sd"],4)}. '+business.get(r.fitur,'Interpretasi perlu mempertimbangkan waktu pencatatan dan konteks layanan.'))
gp=pd.read_csv(H/'permutation_importance_kelompok.csv')
table(['Fitur yang diacak bersama','Mean penurunan AP','Simpangan baku'],[
 [r.group,f(r.mean,4),f(r.sd,4)] for r in gp.itertuples()], [4.1,1.4,1.4],10,align_cols=[1,2])
p('Pengacakan bersama mempertahankan hubungan nilai di dalam kelompok pada baris yang dipindahkan. Hasilnya tidak harus sama dengan jumlah importance tunggal. Pemeriksaan ini membantu saat indikator kelengkapan, kebutuhan eksternal, atau koordinat bulan menyampaikan informasi yang saling berkaitan.')
table(['Ablasi pada CV train dengan parameter tetap','AP rata-rata','Simpangan baku'],[
 [r['skenario'],f(r['mean_ap']),f(r['sd_ap'])] for r in S['ablation']], [4.1,1.4,1.4],10,align_cols=[1,2])
p('Ablasi memakai train CV dan tidak digunakan memilih model ulang pada test. Pohon dipelajari kembali pada setiap fold, sehingga strukturnya dapat berbeda dari pohon final. PFI kelengkapan yang nol pada pohon final dapat muncul bersama perubahan AP CV setelah kelompok fitur dikeluarkan. Sampel evaluasi dan struktur pohon ablasi berbeda, sehingga keduanya merupakan bukti yang saling melengkapi.',size=10.3)

# Halaman 11
page('E. MODEL EXPLAINABILITY MENGGUNAKAN SHAP GLOBAL & LOKAL',1)
heading('E.1 Beeswarm global dan arah pengaruh fitur',2)
p(f'SHAP dihitung dengan shap {S["versions"]["shap"]}, TreeExplainer interventional, dan output probability untuk kelas terlambat. Background efektif adalah {L["background_n"]} baris dari kandidat train sebanyak {L["background_candidate_n"]}; test tidak menjadi background. Dari {L["features_encoded_n"]} fitur encoded, {L["active_shap_features_n"]} memiliki kontribusi tidak nol dan ditampilkan. [6][7]')
fig('04_shap_beeswarm.png',f'Gambar 4. SHAP beeswarm global pada {ntest} test; setiap titik mewakili satu berkas.',max_height=4.0)
p('Titik ke kanan menaikkan skor keterlambatan, sedangkan ke kiri menurunkannya. Merah berarti nilai fitur tinggi dan biru berarti rendah. Pada one-hot, nilai 1 berarti kategori hadir; warna tidak menunjukkan bahwa suatu kategori lebih tinggi atau lebih buruk daripada kategori lain.')
for r in SH[SH.mean_abs_shap>1e-9].head(3).itertuples():
    p(nice(r.fitur_encoded)+'. '+direction_note(r.fitur_encoded),size=10.3)
p('Perbandingan di atas menjelaskan arah skor pada sampel uji dan tidak membuktikan sebab akibat. SHAP tidak mengukur dampak intervensi atau kecepatan instansi, serta tidak mengubah skor pohon berbobot menjadi peluang yang telah terkalibrasi. Kontribusi numerik lengkap tersedia pada CSV pendamping.',size=10.3)

# Halaman 12
page('E.2 Waterfall pada satu berkas kritis')
table(['Identitas kasus','Hasil'],[
 ['ID berkas',L['id_berkas']+'; kode sumber '+L['source']],
 ['Posisi pada data',f'Urutan test {L["index_test_0_based"]+1}; baris data CSV asal {L["row_csv_1_based_header_excluded"]}, di luar header.'],
 ['Aturan pemilihan',L['selection_rule']],
 ['Aktual dan prediksi','Aktual terlambat; prediksi ambang 0,50 = '+str(L['pred_050'])+'; ambang OOF = '+str(L['pred_final'])],
 ['Nilai dasar dan skor akhir',f'E[f(x)]={f(L["base"],5)}; jumlah SHAP={f(L["sum_shap"],5)}; f(x)={f(L["p"],5)}']], [1.8,5.1],9.8)
fig('05_shap_waterfall.png',f'Gambar 5. SHAP waterfall {L["id_berkas"]}. Merah menaikkan skor dan biru menurunkannya.',max_height=4.4)
pos=LC[LC.shap>1e-8].sort_values('shap',ascending=False).head(2)
neg=LC[LC.shap< -1e-8].sort_values('shap').head(2)
pos_text=' dan '.join(f'{nice(r.fitur)}={f(r.nilai_encoded,2)} (+{f(r.shap,4)})' for r in pos.itertuples())
neg_text=' dan '.join(f'{nice(r.fitur)}={f(r.nilai_encoded,2)} ({f(r.shap,4)})' for r in neg.itertuples())
p(f'Pendorong skor terbesar pada kasus ini adalah {pos_text or "tidak ada kontribusi positif material"}. Kontribusi dibaca relatif terhadap nilai dasar model. Panah merah menjelaskan skor untuk kasus ini dan tidak menyatakan bahwa fitur tersebut selalu memperlambat seluruh berkas.')
p(f'Penekan skor terbesar adalah {neg_text or "tidak ada kontribusi negatif material"}. Seluruh kontribusi membentuk skor {f(L["p"],5)}, kemudian dibandingkan dengan ambang {f(T,2)}. Kasus dipilih untuk menunjukkan perubahan keputusan dari ambang; hasil lokal tersebut tidak dipakai menala model ulang.')

# Halaman 13
page('E.3 Kontribusi numerik dan jalur percabangan')
lv=L['features_raw']
p(f'Berkas {L["id_berkas"]} berkategori {lv["kategori_akta"].replace("_"," ")} dan mempunyai {int(lv["jumlah_penghadap"])} penghadap, SLA {int(lv["sla_hari"])} hari, beban tujuh hari {int(lv["beban_7hari"])} berkas, serta {int(lv["jumlah_dokumen"])} dokumen. Indikator dokumen lengkap bernilai {int(lv["dokumen_lengkap"])}. Semua nilai mengikuti baris CSV yang dianalisis.')
active_local=LC[LC.shap.abs()>1e-8].reindex(LC[LC.shap.abs()>1e-8].shap.abs().sort_values(ascending=False).index)
table(['Fitur','Nilai kasus','Kontribusi SHAP','Arah'],[
 [nice(r.fitur),f(r.nilai_encoded,3),('+' if r.shap>0 else '')+f(r.shap,5),'Naik' if r.shap>0 else 'Turun']
 for r in active_local.head(10).itertuples()], [3.65,1,1.35,.9],10,align_cols=[1,2,3])
p(f'Additivity diperiksa pada seluruh test dengan galat maksimum {L["shap_additivity_max_error"]:.2e}. Untuk kasus ini, nilai dasar {f(L["base"],6)} ditambah jumlah kontribusi {f(L["sum_shap"],6)} menghasilkan {f(L["p"],6)}. Nilai dasar berasal dari prediksi model pada background train dan bukan prevalensi aktual.')
heading('Percabangan yang benar-benar dilewati kasus',2)
table(['No','Fitur yang diperiksa','Nilai, operator, dan batas'],[
 [str(i+1),nice(r['fitur']),f'{f(r["nilai"],3)} {r["arah"]} {f(r["batas"],3)}']
 for i,r in enumerate(L['decision_path'])], [.5,4,2.4],10,align_cols=[0,2])
p('Setiap baris di atas adalah aturan yang dilewati sampel pada pohon final. Pada one-hot, nilai 0 berarti kategori tidak hadir. Jadi, Akta AJB Saham=0 pada kasus ini menjelaskan ketidakhadiran kategori AJB Saham, bukan berarti jenis aktanya AJB Saham. Batas koordinat bulan bukan tanggal kalender langsung. Aturan percabangan dan SHAP menggunakan perbandingan yang berbeda.')
p('Jika berkas ditandai berisiko, staf perlu memeriksa kelengkapan, memastikan kebutuhan pengesahan atau pajak, dan meninjau beban pekerjaan yang relevan. Keputusan layanan serta jadwal tetap ditinjau staf dan Notaris/PPAT. Atribusi kode staf tidak digunakan sebagai penilaian individu.')

# Halaman 14
page('E.4 Pemilihan ambang OOF dan beban pemeriksaan')
p('Ambang dipilih dari 0,10 sampai 0,75 dengan langkah 0,01 berdasarkan F2 maksimum pada prediksi OOF train. F2 memberi bobot lebih besar pada recall dibanding precision. Jika nilainya sama, aturan memilih precision lebih tinggi lalu ambang terbesar. Test tidak ikut memilih ambang. [5]')
fig('06_threshold_oof.png','Gambar 6. Pemilihan ambang dan proporsi alarm berdasarkan OOF train saja.',max_height=3.4)
code('''from sklearn.base import clone
from sklearn.model_selection import cross_val_predict
from work.analisis_tugas04_asli import choose_threshold, cv5

p_oof = cross_val_predict(
    clone(best_model), X_train, y_train, cv=cv5(),
    method="predict_proba", n_jobs=2)[:, 1]
threshold, tabel_oof = choose_threshold(y_train, p_oof)
# Simpan parameter dan threshold sebelum mengevaluasi X_test.
''')
p(f'Ambang terpilih adalah {f(T,2)}. Pada test, ambang ini menghasilkan {int(OT.tp+OT.fp)} alarm dari {ntest} berkas. Ambang 0,25 sesuai saran dosen tetap disajikan sebagai pembanding, bukan otomatis dianggap paling baik. AP serta ROC-AUC tetap sama untuk semua ambang tuned karena probabilitas dan peringkatnya tidak berubah.')
p('Kantor perlu menetapkan kemampuan pemeriksaan tambahan per hari dan prioritas biaya satu FN dibanding satu FP. Informasi biaya dan kapasitas tersebut belum tersedia sehingga tidak dipasang sebagai angka kantor. Evaluasi berikutnya dapat mengoptimalkan F2 dengan batas alarm, atau memakai fungsi biaya yang disepakati sebelum data periode baru diuji.')

# Halaman 15
page('E.5 Sensitivitas temporal dan langkah pengembangan berikutnya')
tm=S['temporal']
table(['Pemeriksaan temporal','Hasil'],[
 ['Tanggal pemisahan',tm['cutoff']],
 ['Train yang sudah selesai sebelum cutoff',str(tm['n_train'])+' berkas'],
 ['Dikeluarkan karena belum selesai saat cutoff',str(tm['n_purged'])+' berkas'],
 ['Test setelah cutoff',f'{tm["n"]} berkas; {tm["positif"]} terlambat'],
 ['AP, recall, dan F1',f(tm['ap'])+'; '+f(tm['recall'])+'; '+f(tm['f1'])],
 ['Proporsi alarm',pct(tm['alert_rate'])]], [3.75,3.15],10)
p('Uji temporal memakai konfigurasi dan ambang yang sudah dibekukan, lalu melatih ulang pada data sebelum cutoff. Berkas yang belum selesai saat cutoff dikeluarkan dari train agar label masa depan tidak masuk. Konfigurasi sebelumnya pernah dipilih pada random split korpus yang sama, sehingga uji ini merupakan pemeriksaan sensitivitas dan bukan validasi masa depan yang sepenuhnya independen.')
heading('Keterbatasan hasil saat ini',2)
p('Ukuran data masih 169 berkas dan test hanya memuat tujuh keterlambatan. Interval evaluasi lebar dan satu prediksi sangat memengaruhi recall. Tidak tersedia ID klien untuk memastikan pemisahan seluruh berkas milik klien yang sama. Makna SLA dalam hari kalender mengikuti konsistensi label CSV dan perlu diselaraskan dengan definisi operasional kantor.')
p('Waktu pencatatan indikator kelengkapan, beban tujuh hari, kebutuhan pengesahan, kebutuhan pajak, dan petugas harus tetap berada pada tahap awal. Jika indikator baru diisi setelah pekerjaan berjalan, model penerimaan perlu memakai catatan awal yang tersimpan, bukan nilai akhir yang telah diperbarui.')
heading('Pengukuran yang perlu dilengkapi',2)
p('Kelompok perlu menambahkan instansi tujuan yang dicatat langsung, jumlah item wajib, jumlah item diterima saat masuk, sebab pengembalian dokumen, serta waktu penyerahan dan hasil dari instansi. Identitas kategori instansi tidak disimpulkan hanya dari judul akta atau kebutuhan pajak. Peristiwa setelah penerimaan disimpan untuk analisis proses dan tidak otomatis menjadi fitur prediksi awal.')
p('Perbaikan AP dan F1 pada test saat ini mendukung pengembangan lebih lanjut, tetapi gap train-test serta variasi CV masih menunjukkan kebutuhan validasi. Model diposisikan sebagai prototipe untuk uji terawasi. Pengujian berikutnya memakai periode baru yang belum pernah masuk tuning, dengan kapasitas alarm dan kriteria keberhasilan ditetapkan terlebih dahulu.')

# Halaman 16
page('F. LEMBAR KOMITMEN & INTEGRITAS AKADEMIK KELOMPOK',1)
p('Pernyataan ini disediakan untuk ditinjau dan disahkan koordinator sebelum pengumpulan. Dataset analisis terdiri dari 169 baris berkode sumber=asli yang dipilih dari CSV kelompok. Seluruh nilai pengukuran dan label pada baris terpilih dipertahankan. Turunan tanggal dihitung secara deterministik dan tidak menambah catatan observasi.')
p('Metrik train, CV, dan test, seluruh pengacakan permutation importance, serta nilai SHAP dihitung melalui kode pendamping. Perbedaan komposisi label Tugas 03 dan v5 tetap dicatat. Angka yang belum menunjukkan perbaikan maupun keterbatasan model disajikan sesuai hasil eksekusi. Dataset tidak diubah untuk mengejar skor pengujian.')
p('Pengembangan kode dan naskah memakai bantuan AI. Kelompok perlu memeriksa hasil dan memahami metode sebelum menyatakan tanggung jawab akademik. Tanda tangan dan persetujuan koordinator tidak dibubuhkan secara otomatis.')
table(['Tanggal penyusunan','Koordinator tim','Pengesahan'],[
 ['22 Oktober 2026','Muhammad Rizqi Saputra\nNIM 12250158','Dibubuhkan koordinator setelah pemeriksaan laporan.']], [1.25,2.7,2.95],10)
heading('Referensi',2)
refs=[
 '[1] Kelompok 02. TUGAS 03 KELOMPOK 02 NOTARIS PPAT. 15 Oktober 2026, halaman 1 sampai 6.',
 '[2] Saputra, I. REKAP EVALUASI DAN FEEDBACK TUGAS 03. 16 Oktober 2026, bagian Kelompok 02 pada halaman 3 dan 4.',
 '[3] Saputra, I. Panduan Tugas 04 Pembelajaran Mesin dan Template Tugas 04 Pembelajaran Mesin. Semester Gasal 2026/2027. Dataset: berkas_notaris_ v5.csv, seleksi sumber=asli.',
 '[4] Scikit-learn. permutation_importance. https://scikit-learn.org/1.8/modules/generated/sklearn.inspection.permutation_importance.html',
 '[5] Scikit-learn. Tuning the decision threshold for class prediction. https://scikit-learn.org/1.8/modules/classification_threshold.html',
 '[6] SHAP. shap.TreeExplainer. https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html',
 '[7] SHAP. An introduction to explainable AI with Shapley values. https://shap.readthedocs.io/en/latest/example_notebooks/overviews/An%20introduction%20to%20explainable%20AI%20with%20Shapley%20values.html',
 '[8] Scikit-learn 1.8. Nested versus non-nested cross-validation. https://scikit-learn.org/1.8/auto_examples/model_selection/plot_nested_cross_validation_iris.html',
 'Dokumentasi daring diakses 22 Oktober 2026. Seluruh angka hasil berasal dari eksekusi pada baris CSV yang dipilih untuk analisis.'
]
for r in refs:p(r,size=9.5,after=5)

# Halaman 17
page('Lampiran 1 Reproduksi eksperimen dan pemetaan rubrik')
table(['Komponen rubrik','Bobot','Bukti dalam laporan'],[
 ['Desain hyperparameter dan strategi','25%','Lima parameter, 320 kandidat, pipeline, inner dan outer 5-fold CV, serta objective AP.'],
 ['Komparasi baseline dan tuned','25%','Riwayat T03, train/CV/test pada versi sekarang, delta, gap, confusion matrix, ROC/PR, dan bootstrap.'],
 ['Permutation feature importance','25%','Top 10 pada test, 100 pengacakan, interpretasi bisnis, pengacakan kelompok, serta ablasi pada train.'],
 ['Kedalaman interpretasi SHAP','25%','Beeswarm, waterfall, arah kontribusi, nilai dasar, penjumlahan SHAP, dan aturan pohon pada kasus kritis.']], [2.1,.55,4.25],9.7)
p('Pemetaan ini menunjukkan letak bukti untuk rubrik resmi dan tidak menetapkan nilai. Kelengkapan metode, kejelasan penjelasan, serta pengesahan laporan tetap dinilai oleh dosen.')
heading('Menjalankan ulang',2)
p('Paket pendamping berisi notebook Colab, skrip, dua model terlatih, CSV sumber, subset 169 baris, formulir fitur tambahan, daftar versi paket, hasil CV, ID partisi, prediksi test, dan grafik. Notebook disediakan untuk reproduksi; bukti eksekusi laporan adalah log skrip serta CSV hasil. Dari folder utama paket pada Python 3.12, jalankan:')
code('''python -m pip install -r requirements.txt
python work/analisis_tugas04_asli.py \\
    --csv "upload/berkas_notaris_ v5.csv" \\
    --out work/hasil_tugas04_asli --jobs 2
''')
p('Notebook menerapkan filter sumber=asli yang sama, sehingga tidak memerlukan penggantian label atau pengubahan CSV. Hasil seluruh 320 kandidat disimpan, dan konfigurasi final dicatat sebelum evaluasi test. File SHAP memuat semua fitur encoded, termasuk yang bernilai nol.')
heading('Identitas input dan lingkungan',2)
p('SHA256 input CSV',bold=True,size=10)
p(A['file_sha256'],size=8.5)
vers=S['versions']
table(['Komponen','Versi atau pengaturan'],[
 ['Python, NumPy, pandas',vers['python']+'; '+vers['numpy']+'; '+vers['pandas']],
 ['Scikit-learn, SciPy, SHAP',vers['scikit-learn']+'; '+vers['scipy']+'; '+vers['shap']],
 ['Seleksi dan seed','sumber=asli; random_state=42'],
 ['Audit utama','audit_data.json; partisi_dan_fold.csv; ringkasan_hasil.json']], [2,4.9],9.9)
p('Pengumpulan melalui LMS/EL-NUSA oleh koordinator paling lambat Kamis, 22 Oktober 2026 pukul 23:59:59 WIB. Nama PDF mengikuti TUGAS_04_KELOMPOK_02_NOTARIS_PPAT.pdf. [3]',size=10)

# Halaman 18
page('Lampiran 2 Kamus fitur dan waktu pencatatannya')
table(['Fitur input','Definisi dan asal','Ketersediaan saat prediksi'],[
 ['jumlah_penghadap','Jumlah penghadap yang dicatat pada CSV','Dicatat pada penerimaan.'],
 ['sla_hari','Batas hari penyelesaian pada CSV','Ditetapkan sebelum hasil diketahui.'],
 ['beban_7hari','Beban tujuh hari sesuai kolom CSV','Mewakili informasi beban awal.'],
 ['jumlah_dokumen','Jumlah dokumen pada CSV','Mengikuti catatan pemeriksaan awal.'],
 ['dokumen_lengkap','Indikator biner lengkap (1) atau belum lengkap (0)','Memerlukan nilai awal sebelum proses dilanjutkan.'],
 ['perlu_pengesahan_\nkemenkum','Indikator kebutuhan pengesahan pada CSV','Kebutuhan yang diketahui pada awal.'],
 ['perlu_pajak','Indikator kebutuhan pajak pada CSV','Kebutuhan yang diketahui pada awal.'],
 ['ada_rups_awal','1 bila tanggal RUPS tersedia dan tidak melewati tanggal masuk','Turunan deterministik dua tanggal.'],
 ['bulan_sin dan bulan_cos','Dua koordinat siklus bulan dari tanggal masuk','Dihitung dari waktu penerimaan.'],
 ['kategori_akta','Kategori layanan sesuai CSV','Dicatat saat masuk; tidak ditafsirkan sebagai kepastian instansi tujuan.'],
 ['hari_masuk','Nama hari dari tanggal masuk','Turunan kalender tanpa target.'],
 ['kanal_masuk','Kanal penerimaan pada CSV','Sudah diketahui saat berkas diterima.'],
 ['petugas','Kode petugas sesuai CSV','Penugasan awal harus sudah ditetapkan.']], [1.7,3.1,2.1],9.6)
p(f'Totalnya 14 fitur mentah karena sin dan cos dihitung sebagai dua fitur. Setelah encoding pada train, terdapat {L["features_encoded_n"]} kolom. Kategori baru pada test ditangani dengan handle_unknown=ignore tanpa mempelajari ulang encoder dari test.')
heading('Kolom audit dan pembentuk target',2)
p('id_berkas dan kode sumber dipakai untuk penelusuran serta pemilihan baris, sedangkan nomor urut dan nomor bulanan tidak menjadi prediktor. Tanggal selesai serta durasi aktual dipakai memeriksa target. Tanggal akta, jumlah revisi, dan biaya jasa dikeluarkan dari input karena waktu pencatatannya belum memastikan ketersediaan pada tahap awal.')
p('Rumus target yang konsisten dengan CSV adalah: status terlambat bernilai 1 ketika selisih hari kalender antara tanggal selesai dan tanggal masuk melebihi sla_hari. Pencatatan timestamp atau aturan hari kerja yang berbeda harus disepakati terlebih dahulu jika dataset diperbarui.')

# Lampiran tindak lanjut berfokus pada catatan resmi untuk Kelompok 02.
page('Lampiran 3 Tindak lanjut rekap dosen dan kelengkapan data')
p('Rekap Tugas 03 halaman 3 sampai 4 menyoroti sampel kecil, prediktor lemah, kebutuhan fitur eksternal serta kelengkapan awal, dan penggunaan TreeExplainer serta ambang 0,25. Matriks berikut menunjukkan bukti yang sudah dikerjakan pada 169 berkas. [2]')
table(['Catatan dosen','Bukti pada Tugas 04','Status dan tindakan berikutnya'],[
 ['Sampel 169; test hanya 7 positif','Outer dan inner 5-fold CV, variasi fold, bootstrap berpasangan, dan sensitivitas waktu.','Evaluasi diperluas. Ukuran sampel tetap 169; data periode baru masih diperlukan.'],
 ['Indikator instansi tujuan','Fitur perlu_pengesahan_kemenkum dan perlu_pajak dipakai tanpa mengubah nilai CSV.','Sebagian. BPN, AHU, KPP Pratama, dan Bapenda belum tercatat sebagai instansi tujuan aktual.'],
 ['Skor ceklis kelengkapan awal','Fitur dokumen_lengkap dan jumlah_dokumen, PFI kelompok, serta ablasi train CV.','Sebagian. Belum ada jumlah item wajib dan item valid awal untuk menghitung skor ceklis.'],
 ['SHAP TreeExplainer pada Decision Tree','Beeswarm global, waterfall berkas BRK_0273, additivity, dan jalur percabangan aktual.','Terpenuhi. Penjelasan mengacu pada skor model; bukan bukti sebab akibat.'],
 ['Threshold moving 0,50 ke 0,25','Recall test tuned naik dari 3/7 ke 4/7; FP berubah dari 11 ke 15.','Terpenuhi. Ambang 0,11 dari OOF menangkap 6/7 dengan FP 20; biaya pemeriksaan tetap dipertimbangkan.']], [1.55,2.55,2.8],9.5)
heading('Cara melengkapi dua kebutuhan data yang masih terbuka',2)
p('Formulir FORM_VERIFIKASI_FITUR_TAMBAHAN_169.csv memuat ID 169 berkas yang sama. Kolom tambahan sengaja belum diisi dan tidak masuk model saat ini. Petugas mengisi indikator tujuan BPN, AHU, KPP Pratama, Bapenda, atau instansi lain berdasarkan arsip. Beberapa instansi boleh terlibat pada satu berkas. Kebutuhan pajak saja tidak cukup untuk menyimpulkan kantor tujuan pajaknya.')
p('Untuk ceklis, catat jumlah item wajib menurut layanan, jumlah item yang sudah valid saat pemeriksaan awal, serta waktu pemeriksaannya. Skor dapat dihitung sebagai persentase item valid terhadap item wajib bila jumlah wajib lebih dari nol. Jumlah dokumen total tidak langsung menjadi skor kelengkapan karena item wajib antar-layanan dapat berbeda.')
p('Setiap pengisian mencantumkan sumber verifikasi dan pemeriksa. Setelah lengkap, data disimpan sebagai versi baru dan rancangan evaluasi ditetapkan sebelum test berikutnya dinilai. Tidak ada nilai instansi maupun skor ceklis yang diperkirakan untuk menaikkan hasil saat ini.')

page('Lampiran 4 Bukti pemilihan parameter dan kesinambungan Tugas 03')
grid=pd.read_csv(H/'hasil_gridsearch_320_kandidat.csv')
base_mask=(grid['param_model__max_depth'].eq(4)&grid['param_model__min_samples_leaf'].eq(5)&grid['param_model__min_samples_split'].eq(2)&grid['param_model__ccp_alpha'].eq(0)&grid['param_model__class_weight'].eq('balanced'))
base_grid=grid.loc[base_mask].iloc[0]
p(f'Pencarian final memakai lipatan train yang sama untuk setiap kandidat. AP CV konfigurasi baseline adalah {f(base_grid.mean_test_score,4)}; kandidat terpilih mencapai {f(F["best_inner_cv_ap"],4)}. Tabel merangkum lima baris teratas dari 320 kandidat. SD mengikuti keluaran GridSearchCV. Kandidat dipilih dari AP CV, bukan dari skor test.')
table(['Rank','Depth','Leaf min','Split min','ccp alpha','Bobot','AP CV dan SD'],[
 [int(r.rank_test_score),int(r.param_model__max_depth),int(r.param_model__min_samples_leaf),int(r.param_model__min_samples_split),f(r.param_model__ccp_alpha,3),str(r.param_model__class_weight),f(r.mean_test_score,4)+' ± '+f(r.std_test_score,4)]
 for r in grid.head(5).itertuples()], [.45,.55,.65,.65,.8,1.1,2.65],9.5,align_cols=[0,1,2,3,4,5,6])
p('Depth membatasi panjang aturan; leaf min adalah dukungan minimal per daun; split min adalah minimal data sebelum simpul dipecah. Pruning 0,002 membatasi cabang berdasarkan kompleksitas pohon; konfigurasinya terpilih melalui AP CV. Leaf minimum 2 terpilih secara empiris, tetapi dukungan sekecil ini tetap rentan pada variasi data. Selisih AP kandidat teratas yang kecil tidak diperlakukan sebagai bukti keunggulan permanen.')
heading('Hal yang dipertahankan dan hal yang berbeda',2)
table(['Komponen','Tugas 03','Tugas 04 pada CSV v5'],[
 ['Objek dan algoritma','Notaris dan PPAT Aries Buwana; Decision Tree.','Objek dan keluarga model dipertahankan.'],
 ['Data dan target','169 berkas; 33 terlambat; train 135 dengan 26 positif.','169 berkode asli; 35 terlambat; train 135 dengan 28 positif.'],
 ['Matriks fitur','18 kolom setelah encoding. Antrean berjalan dan ada_rups terdapat pada uraian T03.','14 fitur mentah; 36 setelah encoding. Beban 7 hari dan RUPS awal mengikuti definisi CSV v5.'],
 ['Perbandingan tuning','Hasil historis dicatat sebagaimana laporan T03.','Baseline ulang dan tuned memakai fitur, target, serta ID train-test yang sama.']], [1.1,2.9,2.9],9.5)
p('Antrean berjalan pada Tugas 03 tidak dianggap identik dengan beban tujuh hari. Indikator RUPS awal pada Tugas 04 hanya memakai tanggal yang tidak melampaui waktu masuk. Karena matriks mentah Tugas 03 tidak disertakan, eksperimen ini melanjutkan algoritma dan kasus yang sama, bukan mengklaim reproduksi persis atas semua angka Tugas 03.')
p('Peningkatan AP dan F1 test mendukung eksplorasi lanjutan, sementara penurunan F1 outer CV pada 0,50 serta gap train-test menunjukkan hasil belum stabil. Parameter, ambang, dan seed tidak diubah setelah test dibaca. Keputusan tersebut menjaga agar delta yang dilaporkan tetap dapat diperiksa ulang.')

for q in doc.paragraphs:
    if q.style.name.startswith('Heading') or q.style.name=='Title':
        for r in q.runs:r.font.color.rgb=RGBColor(0,0,0)
        pr=q._p.get_or_add_pPr()
        for el in list(pr.findall(qn('w:pBdr'))):pr.remove(el)
path=out/'TUGAS_04_KELOMPOK_02_NOTARIS_PPAT.docx'
doc.save(path)
print(path)
print('Paragraphs',len(doc.paragraphs),'tables',len(doc.tables),'figures',len(doc.inline_shapes))

