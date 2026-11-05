"""Laporan Tugas 05 dari artefak, pengujian HTTP, dan tangkapan aplikasi nyata."""
from pathlib import Path
import json
from PIL import Image
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent;E=ROOT/'evidence';G=E/'figures';SS=E/'screenshots'
def read(name):return json.loads((E/name).read_text())
META=json.loads((ROOT/'artifacts/model_metadata.json').read_text())
BENCH=read('benchmark.json');TEST=read('test_summary.json');PARITY=read('serialization_check.json')
REPLAY=read('holdout_replay_summary.json');SCENARIOS=read('scenarios.json');EDGES=read('edge_cases.json')
ERRORS={r['id_berkas']:r for r in read('error_cases.json')};THRESHOLD=read('dynamic_threshold.json')
HISTORY=read('history_test.json');CURL=read('curl_valid_response.json');INVALID=read('curl_invalid_response.json')
reports=ROOT/'reports';reports.mkdir(exist_ok=True)
doc=Document(ROOT/'source_documents/Template_Tugas_05_Pembelajaran_Mesin.docx')
for el in list(doc._element.body):
    if el.tag!=qn('w:sectPr'):doc._element.body.remove(el)
sec=doc.sections[0]
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Inches(1)
sec.header_distance=Inches(.35);sec.footer_distance=Inches(.35)
for style in doc.styles:
    if style.type==1:
        style.font.name='Arial';style.font.color.rgb=RGBColor(0,0,0)
        for border in list(style._element.xpath('./w:pPr/w:pBdr')):border.getparent().remove(border)
normal=doc.styles['Normal'];normal.font.size=Pt(10.5)
normal.paragraph_format.line_spacing=1.1;normal.paragraph_format.space_after=Pt(6)
normal.paragraph_format.widow_control=True
for name,size in [('Title',14),('Heading 1',11.5),('Heading 2',11),('Heading 3',10.5)]:
    s=doc.styles[name];s.font.name='Arial';s.font.size=Pt(size);s.font.bold=True
    s.paragraph_format.keep_with_next=True;s.paragraph_format.space_before=Pt(8);s.paragraph_format.space_after=Pt(7)
    s.paragraph_format.line_spacing=1.05
doc.core_properties.title='Tugas 05 Kelompok 02 Notaris dan PPAT'
doc.core_properties.author='Kelompok 02'
doc.core_properties.subject='Serialisasi pipeline, Streamlit, FastAPI, dan pengujian inferensi'
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=footer.add_run('Pembelajaran Mesin | Tugas 05 | Kelompok 02                     Halaman ');r.font.size=Pt(8)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)

def f(v,n=3):
    x=float(v)
    if abs(x)<.5*10**(-n):x=0.
    return f'{x:.{n}f}'.replace('.',',')
def pct(v,n=2):return f(float(v)*100,n)+'%'
def p(text='',bold=False,size=None,after=6):
    q=doc.add_paragraph();r=q.add_run(text);r.bold=bold
    if size:r.font.size=Pt(size)
    q.paragraph_format.space_after=Pt(after);return q
def h(text,level=1):return doc.add_paragraph(text,style=f'Heading {level}')
def page(text,level=2):doc.add_page_break();h(text,level)
def table(headers,rows,widths,font=9.3,centers=()):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for j,w in enumerate(widths):t.columns[j].width=Inches(w)
    borders=OxmlElement('w:tblBorders')
    for key in ['top','left','bottom','right','insideH','insideV']:
        x=OxmlElement('w:'+key);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'5');x.set(qn('w:color'),'D9D9D9');borders.append(x)
    t._tbl.tblPr.append(borders)
    margins=OxmlElement('w:tblCellMar')
    for key,val in [('top',85),('bottom',85),('left',85),('right',85)]:
        x=OxmlElement('w:'+key);x.set(qn('w:w'),str(val));x.set(qn('w:type'),'dxa');margins.append(x)
    t._tbl.tblPr.append(margins)
    for j,name in enumerate(headers):t.rows[0].cells[j].text=str(name)
    for row in rows:
        cells=t.add_row().cells
        for j,value in enumerate(row):cells[j].text=str(value)
    for i,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr();trpr.append(OxmlElement('w:cantSplit'))
        if i==0:trpr.append(OxmlElement('w:tblHeader'))
        for j,cell in enumerate(row.cells):
            cell.width=Inches(widths[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            fill=OxmlElement('w:shd');fill.set(qn('w:fill'),'233D70' if i==0 else ('F2F5F7' if i%2==0 else 'FFFFFF'))
            cell._tc.get_or_add_tcPr().append(fill)
            for q in cell.paragraphs:
                q.paragraph_format.space_after=Pt(0);q.paragraph_format.space_before=Pt(0);q.paragraph_format.line_spacing=1.05
                q.paragraph_format.keep_with_next=False
                if j in centers:q.alignment=WD_ALIGN_PARAGRAPH.CENTER
                for r in q.runs:
                    r.font.name='Arial';r.font.size=Pt(font);r.bold=i==0
                    r.font.color.rgb=RGBColor(255,255,255) if i==0 else RGBColor(0,0,0)
    p('',after=2).paragraph_format.line_spacing=.3
    return t
def code(text):
    q=doc.add_paragraph();q.paragraph_format.line_spacing=1.0;q.paragraph_format.space_after=Pt(7)
    for i,line in enumerate(text.strip('\n').splitlines()):
        r=q.add_run(('\n' if i else '')+line);r.font.name='Courier New';r.font.size=Pt(8)
    return q
def figure(path,caption,max_height=4,width=6.5):
    path=Path(path);iw,ih=Image.open(path).size;width=min(width,max_height*iw/ih)
    q=doc.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER;q.paragraph_format.keep_with_next=True
    q.paragraph_format.space_after=Pt(4)
    r=q.add_run();r.add_picture(str(path),width=Inches(width))
    r._r.xpath('.//wp:docPr')[0].set('descr',caption)
    q=p(caption,size=9,after=7);q.alignment=WD_ALIGN_PARAGRAPH.CENTER

# 1 A
q=doc.add_paragraph('LAPORAN PENUGASAN MINGGU 05\nPEMBELAJARAN MESIN',style='Title');q.alignment=WD_ALIGN_PARAGRAPH.CENTER
q=p('Serialisasi Model Terbaik dan Prototipe Inferensi Berkas Notaris',bold=True,size=11);q.alignment=WD_ALIGN_PARAGRAPH.CENTER
q=p('Semester Gasal 2026/2027 | S1, 3 SKS\nDr. Irwansyah Saputra, M.Kom. | NIP 201909149',size=9.5);q.alignment=WD_ALIGN_PARAGRAPH.CENTER
h('A. IDENTITAS KELOMPOK DAN MODEL FINAL TERBAIK')
table(['No','NIM','Nama dan peran'],[
 ['1','12250158','Muhammad Rizqi Saputra\nKoordinator, dokumentasi, dan quality control'],
 ['2','12250162','Dian Nur Cahya\nSerialisasi model dan validasi pipeline'],
 ['3','12250161','Dicky Handia\nInferensi, API, dan prototipe antarmuka']], [.35,1.05,5.1],9.7,centers=[0,1])
p('Kami melanjutkan penelitian keterlambatan berkas pada Kantor Notaris & PPAT Aries Buwana, Jakarta Barat. Pada tugas ini, model Tugas 04 dikemas agar dapat menerima masukan dari form dan API. Fokus pekerjaan adalah menjaga kesamaan prediksi, menghitung fitur secara otomatis, dan menangani masukan yang tidak valid tanpa menghentikan layanan.')
table(['Komponen','Konfirmasi'],[
 ['Data dan target','169 berkas; 33 terlambat dan 136 tepat waktu. Target = 1 bila durasi hari kalender melebihi SLA. Train 135; test 34 dengan 7 positif.'],
 ['Model yang diekspor','DecisionTreeClassifier; max_depth=4; min_samples_leaf=15; min_samples_split=2; ccp_alpha=0; class_weight=None.'],
 ['Keputusan awal','Ambang 0,11 dari OOF train Tugas 04. Skor setidaknya ambang menghasilkan label perlu pemeriksaan staf.'],
 ['Hasil test pada ambang 0,11',f'AP {f(REPLAY["ap"])}; precision {f(REPLAY["precision"])}; recall {f(REPLAY["recall"])}; F1 positif {f(REPLAY["f1"])}. TP 4, FN 3, FP 18, TN 9.']], [1.5,5],9.4)
p('Pipeline yang dimuat ulang mempertahankan seluruh label test. Aplikasi dan API berjalan sebagai prototipe lokal; keterbatasan prediksi Tugas 04 tetap berlaku. [1][2]',size=10)

# 2 B
page('B. ARSITEKTUR SERIALISASI MODEL DAN INFERENCE PIPELINE',1)
figure(G/'01_architecture.png','Gambar 1. Alur implementasi yang dipakai bersama oleh form dan API.',max_height=3.05)
table(['Komponen deployment','Implementasi'],[
 ['Artefak model',f'model_final.joblib; {str(META["artifact_bytes"])} byte ({f(META["artifact_bytes"]/1024,2)} KiB), kompresi joblib tingkat 3.'],
 ['Isi objek inferensi','Pipeline fitur, imputer, encoder, Decision Tree, ambang 0,11, background SHAP, dan keterangan data referensi.'],
 ['Antarmuka dan API','Streamlit pada app.py; FastAPI pada api.py; schema bersama pada schemas.py. Keduanya memanggil service.py.'],
 ['Penggunaan memori','Model dan TreeExplainer dimuat saat layanan dimulai; Streamlit memakai st.cache_resource. Model tidak dimuat ulang pada setiap klik.'],
 ['Latensi HTTP terukur',f'Rata-rata {f(BENCH["http_localhost_with_shap"]["mean_ms"],2)} ms pada 300 permintaan lokal, termasuk SHAP.']], [1.6,4.9],9.6)
p('Histori train tersimpan bersama transformer antrean. Jika pengguna memberi snapshot histori lain, layanan membuat transformer per request dan tetap memakai encoder serta pohon yang sama. Dengan demikian pergantian histori tidak mengubah model global atau hasil request lain. [4][7]')

# 3 B schema
page('B.1 Kontrak masukan dan fitur yang dihitung otomatis')
table(['Masukan mentah','Aturan pada prototipe','Fungsi'],[
 ['id_berkas','Teks 1-64 karakter: huruf, angka, garis bawah, atau tanda hubung.','Penelusuran hasil; tidak menjadi prediktor.'],
 ['tgl_masuk','Tanggal YYYY-MM-DD; tahun 2000-2100.','Menghitung hari dan koordinat bulan.'],
 ['kategori_akta','Teks tidak kosong, maksimal 80 karakter.','Kategori layanan; kategori baru memicu peringatan.'],
 ['jumlah_penghadap','Integer 1-100; string dan boolean ditolak.','Masukan numerik.'],
 ['sla_hari','Integer 1-365; string dan nilai nol ditolak.','Batas hari kalender pada rekap.'],
 ['tgl_rups','Opsional. Jika sesudah tanggal masuk, tidak dianggap tersedia saat awal.','Indikator RUPS awal.'],
 ['threshold','Opsional; angka 0,01-0,99. Nilai awal 0,11.','Mengubah keputusan tanpa mengubah skor.'],
 ['history','Opsional; maksimal 5.000 catatan dengan ID unik.','Snapshot antrean pengganti.']], [1.5,2.9,2.1],9.5)
p('Batas 100 penghadap, 365 hari, dan tahun 2000-2100 merupakan batas teknis masukan prototipe. Angka tersebut tidak dinyatakan sebagai ketentuan layanan kantor. Nilai yang masih sah secara teknis tetapi berada di luar rentang train tetap menghasilkan peringatan agar staf memeriksanya. [5][6]')
h('Waktu ketersediaan informasi',2)
p('Tanggal selesai berkas yang sedang diprediksi tidak diminta dan ditolak bila disisipkan ke body record. Transformer menghasilkan jumlah penghadap, SLA, antrean berjalan, indikator RUPS, bulan sin/cos, kategori akta, dan hari masuk. Imputasi dan encoding menggunakan objek hasil fit train, tanpa fit ulang pada request.')
p('Antrean adalah catatan histori yang masuk sebelum hari penerimaan dan belum selesai sebelum awal hari itu. Berkas yang selesai pada hari tersebut masih dihitung terbuka pada awal hari. Tanggal selesai histori boleh kosong untuk berkas yang masih terbuka; berkas baru pada hari yang sama belum masuk hitungan.')

# 4 B serialization code
page('B.2 Penyimpanan model dan kesamaan hasil setelah pemuatan')
code('''import json
from pathlib import Path
import joblib
import pandas as pd
from schemas import PredictRequest
from service import InferenceService

# Contoh round-trip dari artefak yang sudah dilatih pada Tugas 04.
bundle = joblib.load("artifacts/model_final.joblib")
joblib.dump(bundle, "artifacts/model_roundtrip.joblib", compress=3)
loaded = joblib.load("artifacts/model_roundtrip.joblib")
payload = json.loads(Path("tests/fixtures/BRK_0024.json").read_text())
X_raw = pd.DataFrame([payload["record"]])
score = loaded.predict_proba(X_raw)[:, 1]
label = loaded.predict(X_raw)  # memakai threshold awal 0.11

# Form dan API memakai service yang sama, tanpa fit ulang.
request = PredictRequest.model_validate(payload)
result = InferenceService().predict(request)
''')
table(['Pemeriksaan','Hasil'],[
 ['Jumlah berkas pada uji regresi','34 berkas test yang sama dengan Tugas 04.'],
 ['Selisih skor sebelum dan setelah serialisasi',f'{PARITY["serialization_roundtrip_error"]:.1e} (nol).'],
 ['Selisih terhadap angka pada CSV Tugas 04',f'Maksimum {PARITY["max_abs_probability_error_vs_csv"]:.2e}; dalam toleransi 1e-14.'],
 ['Label pada ambang 0,11','34 dari 34 identik; TP 4, FN 3, FP 18, TN 9.'],
 ['Metadata','Tanggal pelatihan 22 Oktober 2026; tanggal ekspor, parameter, threshold, metrik, versi pustaka, serta SHA256 disimpan di model_metadata.json.']], [2.6,3.9],9.6)
p('Tidak ada pelatihan ulang pada Tugas 05. Tanggal pelatihan mengikuti eksperimen Tugas 04; jam fit tidak dicatat sehingga tidak ditambahkan sebagai fakta baru. SHA256 artefak diverifikasi bersama metadata saat pemeriksaan paket. Berkas joblib berasal dari eksperimen kelompok dan modul transformer disertakan agar dapat diimpor saat load. [4]')
h('Rekonsiliasi parameter pada dokumen',2)
p('Rekap dosen menyebut max_depth=3 dan min_samples_leaf=5. Tabel parameter pada laporan Tugas 04 yang dikumpulkan serta artefak terlatih memuat max_depth=4 dan min_samples_leaf=15. Implementasi ini mengikuti artefak yang menghasilkan skor Tugas 04, dan kesamaan hasilnya dibuktikan pada 34 test. Catatan ini menjaga agar versi model yang diperiksa tetap jelas. [1][2]',size=10)

# 5 C input
page('C. PENGEMBANGAN ANTARMUKA APLIKASI WEB INTERAKTIF',1)
figure(SS/'ui_form.png','Gambar 2. Form Streamlit yang dijalankan pada pengujian.',max_height=5.6)
p('Staf memilih contoh yang tersedia atau mengisi ID berkas, tanggal penerimaan, kategori layanan, jumlah penghadap, serta SLA. Tanggal RUPS diaktifkan jika memang tercatat. Form memakai istilah penerimaan berkas dan tidak meminta tanggal selesai berkas baru. Staf kemudian menekan Periksa risiko untuk menjalankan validasi serta inferensi.')
p('Histori awal berisi 135 catatan train. Melalui bagian Sumber histori antrean, staf dapat memuat CSV histori yang sesuai untuk percobaan. Aplikasi menerangkan bahwa hitungan snapshot belum mewakili seluruh antrean kantor. Ambang pemeriksaan disediakan agar sensitivitas alarm dapat dicoba tanpa melatih ulang pohon.')

# 6 C result
page('C.1 Hasil prediksi dan penjelasan bagi staf')
figure(SS/'ui_result.png','Gambar 3. Hasil berkas BRK_0024 pada ambang awal 0,11.',max_height=5.65)
p('Untuk BRK_0024, skor model 18,75% melampaui ambang 11%, sehingga labelnya perlu pemeriksaan staf. Antrean yang terbaca adalah satu berkas dari histori referensi. Skor ini belum dikalibrasi menjadi peluang nyata; label rendah juga tidak menjamin suatu berkas akan selesai tepat waktu.')
p('Empat kontribusi SHAP ditampilkan dengan arah yang sama seperti hasil numerik: merah menaikkan skor dan biru menurunkannya. Nilai dasar '+f(CURL['explanation']['base_value'],5)+' ditambah kontribusi '+f(CURL['explanation']['sum_shap'],5)+' membentuk skor '+f(CURL['model_score'],5)+'. Pengguna dapat mencatat konfirmasi pemeriksaan dan mengunduh hasil JSON beserta threshold serta versi model. [8]')

# 7 C API
page('C.2 Endpoint FastAPI dan bukti pengujian cURL')
p('Endpoint POST /predict menerima record, threshold opsional, histori opsional, serta pilihan explain. Pydantic memeriksa body sebelum service dipanggil. Tanggal selesai berkas baru tidak menjadi bagian schema. Contoh berikut dijalankan terhadap server lokal yang aktif. [5][6]')
code('''curl -X POST http://127.0.0.1:8005/predict \\
  -H "Content-Type: application/json" \\
  --data-binary @tests/fixtures/BRK_0024.json
''')
code('''{
  "record": {
    "id_berkas": "BRK_0024", "tgl_masuk": "2024-09-17",
    "kategori_akta": "AJB_Saham", "jumlah_penghadap": 2,
    "sla_hari": 10, "tgl_rups": null
  },
  "threshold": 0.11,
  "explain": true
}
''')
table(['Respons yang direkam','Nilai'],[
 ['HTTP','200 OK'],['model_score; threshold_used',f'{f(CURL["model_score"],5)}; {f(CURL["threshold_used"],2)}'],
 ['prediction; label',f'{CURL["prediction"]}; {CURL["label"]}'],['queue_at_entry; history_records',f'{CURL["queue_at_entry"]}; {CURL["history_records"]}'],
 ['Kesamaan SHAP dengan skor',f'Galat {CURL["explanation"]["additivity_error"]:.2e}.']], [2.8,3.7],9.7)
p('Uji kedua mengubah jumlah_penghadap menjadi teks dua. Respons cURL adalah HTTP 422 dengan penunjuk field body.record.jumlah_penghadap. Layanan tetap aktif; masukan tidak diteruskan ke model. Header serta body respons asli tersimpan pada evidence/curl_valid_* dan evidence/curl_invalid_*.')
code('''{"message": "Masukan perlu diperbaiki.",
 "detail": [{"field": "body.record.jumlah_penghadap",
             "type": "int_type", "message": "Input should be a valid integer"}]}
''')

# 8 C dynamic threshold
page('C.3 Ambang dinamis tanpa mengubah skor model')
figure(G/'03_threshold.png','Gambar 4. Perubahan keputusan pada skor BRK_0024 yang tetap.',max_height=2.7)
table(['Threshold','Skor model','Kelas hasil keputusan'],[[f(r['threshold'],6),f(r['score'],6),'Perlu pemeriksaan' if r['prediction'] else 'Tidak terpicu alarm'] for r in THRESHOLD], [1.2,1.6,3.7],9.6,centers=[0,1])
p('Aturan yang digunakan adalah skor ≥ threshold. Pada threshold 0,187500, berkas masih memicu alarm; pada 0,187501, alarm tidak terpicu. Pengujian ini memeriksa batas keputusan secara tepat, bukan memilih threshold baru berdasarkan hasil test.')
p('Ambang awal tetap 0,11 dari OOF train Tugas 04. Pada holdout lama, ambang ini menghasilkan 22 alarm, termasuk 18 alarm palsu. Ambang 0,25 menghasilkan 9 alarm tetapi tidak menangkap tujuh keterlambatan. Pilihan ambang perlu dibaca bersama beban pemeriksaan dan risiko kasus terlewat; kapasitas staf serta biaya kesalahan belum diukur. [1][2]')

# 9 C historical queue
page('C.4 Pengujian antrean harian dan isolasi histori')
p('Transformer antrean menyimpan histori referensi di dalam objek serial. Body API dapat membawa snapshot histori lain yang sudah dicatat. Histori tersebut digunakan pada transformer per request, sehingga dua pengguna tidak saling mengganti antrean referensi model.')
table(['Catatan uji perangkat lunak','Tanggal masuk','Tanggal selesai','Masuk antrean 17 Sep 2024'],[
 ['UJI_H_OPEN','1 Sep 2024','Masih terbuka','Ya'],['UJI_H_TODAY','1 Sep 2024','17 Sep 2024','Ya, masih terbuka pada awal hari'],
 ['UJI_H_CLOSED','1 Sep 2024','16 Sep 2024','Tidak'],['UJI_H_SAME','17 Sep 2024','Masih terbuka','Tidak, masuk pada hari yang sama'],
 ['UJI_H_FUTURE','18 Sep 2024','Masih terbuka','Tidak, masuk setelah waktu prediksi']], [1.65,1.1,1.2,2.55],9.4)
p('Pada skenario tersebut, antrean hasil perhitungan adalah '+str(HISTORY['response']['queue_at_entry'])+' berkas. Setelah request selesai, panggilan berikutnya tanpa histori tambahan kembali menghasilkan antrean referensi '+str(HISTORY['default_queue_after_custom_request'])+' berkas untuk BRK_0024. Hasil ini membuktikan bahwa snapshot tambahan tidak mengubah state global.')
code('''# t adalah tanggal penerimaan yang sedang diprediksi.
open_at_entry = (history_entry < t) & (
    history_finish_is_missing | (history_finish >= t))
queue = open_at_entry.sum()
''')
p('Lima catatan berawalan UJI adalah fixture untuk memeriksa program dan tidak ditambahkan ke 169 observasi kantor. Jika digunakan dengan data operasional, isi snapshot harus berasal dari catatan penerimaan serta penyelesaian yang benar-benar tersedia.')
p('Skor BRK_0024 tidak berubah ketika antrean fixture menjadi dua. Pohon final Tugas 04 tidak memakai fitur antrean pada percabangan. Perhitungan antrean yang benar merupakan kewajiban pipeline, sedangkan pengaruhnya terhadap prediksi tetap ditentukan pohon yang telah dilatih.')

# 10 D scenarios
page('D. PENGUJIAN SKENARIO MASUKAN BARU',1)
p('Tiga skenario berikut digunakan untuk menguji perilaku program. ID UJI menandai input buatan untuk pengujian perangkat lunak. Skenario ini tidak dinyatakan sebagai hasil survei baru dan tidak dipakai menilai ulang akurasi model.')
rows=[]
for i,q in enumerate(SCENARIOS):
    r=q['request']['record'];b=q['response'];t=b['threshold_used']
    interpretation=['Tidak memicu alarm; tanggal melampaui periode train sehingga peninjauan tetap ditandai.',
                    'Memicu pemeriksaan pada ambang 0,11; skor bukan kepastian keterlambatan.',
                    'Skor tepat sama dengan ambang; aturan ≥ menghasilkan alarm.'][i]
    rows.append([q['name'],f'{r["id_berkas"]}\n{r["tgl_masuk"]}; {r["kategori_akta"]}\n{r["jumlah_penghadap"]} penghadap; SLA {r["sla_hari"]}',
                 f'Skor {pct(b["model_score"])}\nAmbang {pct(t)}\n{b["label"]}',interpretation])
table(['Skenario','Nilai fitur input','Hasil aktual program','Kesesuaian dan batas pembacaan'],rows,[1.25,1.85,1.5,1.9],9.3)
p('Kasus normal menghasilkan skor '+pct(SCENARIOS[0]['response']['model_score'])+' dan kasus skor lebih tinggi '+pct(SCENARIOS[1]['response']['model_score'])+'. Perbedaannya mengikuti pola yang dipelajari pohon, terutama kalender dan kategori tertentu. Jumlah penghadap delapan pada skenario kedua tidak dijadikan bukti bahwa banyak penghadap menyebabkan keterlambatan.')
p('Skenario ambang menggunakan pola masukan BRK_0024 dengan ID pengujian tersendiri agar batas 0,1875 dapat diperiksa. Hal ini merupakan uji fungsional, bukan sampel independen untuk mengklaim generalisasi. Pada semua skenario, label keputusan dan skor berhasil dikembalikan melalui HTTP 200.')
h('Hubungan dengan pengujian data kantor',2)
p('Uji regresi terhadap 34 berkas test lama dilakukan terpisah. Label aktual pada data kantor tetap berasal dari selisih tanggal selesai dan tanggal masuk terhadap SLA. Kesalahan prediksi dari test lama dibahas pada Bagian E; label aktual tidak dilekatkan pada tiga skenario buatan di atas.')

# 11 D edges
page('D.1 Ketahanan terhadap masukan kosong dan tidak wajar')
def behavior(r):
    if r['actual_status']==422:return 'Ditolak terstruktur; model tidak dipanggil.'
    if 'Kategori' in r['name']:return 'Diproses; encoder mengabaikan kategori baru, disertai peringatan.'
    if 'RUPS' in r['name']:return 'Diproses; indikator RUPS awal = 0 dan peringatan tampil.'
    if 'Nilai valid' in r['name']:return 'Diproses; ditandai di luar cakupan train.'
    return 'Diproses; antrean = 0.'
table(['Skenario edge case','HTTP yang diharapkan','HTTP aktual','Perilaku'],[[r['name'],r['expected_status'],r['actual_status'],behavior(r)] for r in EDGES], [2.05,.8,.75,2.9],9.15,centers=[1,2])
p(f'{sum(r["passed"] for r in EDGES)} dari {len(EDGES)} skenario sesuai dengan respons yang ditetapkan. Respons 422 memuat nama field yang perlu diperbaiki tanpa menampilkan stack trace. Endpoint health tetap dapat diakses setelah masukan tidak valid.')
p('Masukan di luar rentang train dibedakan dari masukan yang tidak sah. Contohnya, 100 penghadap dan SLA 365 masih berada dalam batas teknis, tetapi berbeda jauh dari rentang yang dipelajari model. Hasilnya diberi penanda review, sehingga skor tidak langsung diperlakukan sebagai dasar keputusan layanan.')

# 12 D latency
page('D.2 Pengukuran latensi inferensi dan respons API')
figure(G/'02_latency.png','Gambar 5. Seluruh waktu pengukuran pada dua jalur pengujian.',max_height=2.7)
table(['Jalur pengukuran','Rerata ms','Median ms','P95 ms','Maksimum ms'],[
 [label,*[f(BENCH[key][metric],2) for metric in ['mean_ms','median_ms','p95_ms','max_ms']]]
 for key,label in [('service_with_shap','Service + SHAP'),('http_localhost_with_shap','HTTP lokal + SHAP')]], [2.2,1.05,1.05,1.05,1.15],9.4,centers=[1,2,3,4])
p('Seratus indeks masukan diambil ulang dari 34 holdout dengan seed 20261029. Daftar yang sama dijalankan tiga putaran pada tiap jalur, setelah sepuluh request pemanasan. Dengan demikian terdapat 300 pengukuran service dan 300 pengukuran HTTP. Seluruh 34 ID terwakili; ini tidak berarti tersedia 100 pengamatan kantor baru.')
p('Rata-rata HTTP '+f(BENCH['http_localhost_with_shap']['mean_ms'],2)+' ms memenuhi sasaran rerata di bawah 100 ms. Maksimum HTTP adalah '+f(BENCH['http_localhost_with_shap']['max_ms'],2)+' ms. Jalur service mencatat maksimum '+f(BENCH['service_with_shap']['max_ms'],2)+' ms, sedikit melampaui acuan. Variasi tersebut tetap dilaporkan; hasil lokal ini tidak menjamin batas waktu setiap permintaan pada komputer atau jaringan lain.')
table(['Kondisi pengujian','Keterangan'],[
 ['Lingkungan','Linux x86_64; Python '+BENCH['host']['python']+'; kuota CPU cgroup 8 vCPU.'],
 ['Skema beban','Satu worker; permintaan berurutan; koneksi HTTP digunakan ulang; localhost.'],
 ['Yang termasuk','Validasi HTTP, pembentukan fitur, prediksi, SHAP, dan pengembalian JSON pada jalur HTTP.'],
 ['Yang tidak termasuk','Waktu memuat halaman browser, jaringan internet kantor, dan pelatihan model.']], [1.5,5],9.4)

# 13 D verification
page('D.3 Hasil pengujian otomatis dan reproduksi')
table(['Pemeriksaan','Bukti yang tersimpan','Hasil'],[
 ['Unit dan integrasi','pytest_results.xml; pytest_execution.log',f'{TEST["tests"]} pengujian lolos; {TEST["failures"]} failure; {TEST["errors"]} error.'],
 ['Uji form Streamlit','AppTest dan capture_metadata.json','Skor BRK_0024 0,1875; ambang 0,25 mengubah kelas menjadi 0.'],
 ['Masukan ID kosong pada UI','ui_validation.png','Pesan perbaikan muncul; hasil lama tidak dipertahankan sebagai hasil valid.'],
 ['Uji regresi 34 test','holdout_replay_34.csv','Semua label sama dengan Tugas 04.'],
 ['Penjumlahan SHAP', 'holdout_replay_summary.json',f'Galat maksimum {REPLAY["max_shap_additivity_error"]:.2e}, di bawah 1e-6.'],
 ['Respons HTTP nyata','curl_valid_*; curl_invalid_*','HTTP 200 dan 422 direkam dari server yang dijalankan.']], [1.7,2.2,2.6],9.4)
code('''python -m pytest tests/test_inference.py -q
python run_evidence.py
''')
p('AppTest menjalankan form serta perubahan widget secara terprogram. Tangkapan layar diperoleh dari browser Chromium yang membuka Streamlit aktif, kemudian menekan tombol dan mengubah ambang. Bukti visual tersebut melengkapi uji otomatis, sehingga gambar dalam laporan menunjukkan aplikasi yang benar-benar berjalan. [7]')
h('Makna kesamaan hasil',2)
p('Uji regresi mengonfirmasi bahwa pemindahan model ke aplikasi tidak mengubah prediksi pada test lama. AP tetap '+f(REPLAY['ap'])+', recall '+f(REPLAY['recall'])+', dan F1 positif '+f(REPLAY['f1'])+' pada ambang 0,11. Hasil ini menguji konsistensi implementasi, bukan membuktikan peningkatan mutu model pada periode baru.')
p('Seluruh request pengujian, respons, log, dan metadata disimpan dalam paket. Waktu pengukuran dapat berubah ketika dijalankan pada komputer lain. Versi pustaka dikunci untuk mengurangi perbedaan pemuatan model. [4]')

# 14 E FP
page('E. ERROR ANALYSIS DAN FAILURE MODE TAXONOMY',1)
fp=ERRORS['BRK_0110'];b=fp['response'];r=fp['raw']
h('E.1 False positive pada BRK_0110',2)
table(['Informasi kasus','Nilai'],[
 ['Masukan','Pendirian PT; masuk 30 Desember 2025; 4 penghadap; SLA 14 hari.'],
 ['Aktual',f'Selesai 9 Januari 2026; durasi {fp["duration_days"]} hari. Target 0 atau tepat waktu.'],
 ['Prediksi',f'Skor {pct(b["model_score"])} ≥ ambang 11%; kelas 1. Hasil merupakan false positive.'],
 ['Daun pohon',f'{fp["leaf_train_n"]} data latih; proporsi kelas positif {f(b["model_score"],5)}.']], [1.45,5.05],9.5)
figure(G/'error_BRK_0110.png','Gambar 6. Kontribusi fitur pada satu alarm palsu.',max_height=2.55)
p('Berkas melewati percabangan bulan cos > 0,683 dan indikator PKR PT ≤ 0,5. Daun tersebut berisi 17 contoh train, dengan tujuh positif, sehingga skornya 7/17 atau 0,41176. Pada ambang rendah 0,11, skor ini menimbulkan alarm meskipun berkas sebenarnya selesai sebelum SLA.')
p('Atribusi menunjukkan model bergantung pada kalender dan kategori tertentu. Catatan instansi tujuan, kelengkapan awal, serta perkembangan proses tidak tersedia sebagai prediktor. Ketiadaan informasi itu merupakan hipotesis keterbatasan fitur; analisis ini tidak menetapkan penyebab lapangan dari alarm palsu. Dampak praktisnya adalah tambahan pemeriksaan staf, bukan perubahan hasil aktual berkas.')

# 15 E FN
page('E.2 False negative dan keterlambatan yang tidak terpicu')
fn=ERRORS['BRK_0075'];z=ERRORS['BRK_0168'];b=fn['response']
table(['Informasi kasus','Nilai'],[
 ['BRK_0075','PKR PT; masuk Kamis, 14 Agustus 2025; 3 penghadap; SLA 14 hari.'],
 ['Aktual',f'Selesai 1 September 2025; durasi {fn["duration_days"]} hari. Target 1 atau terlambat.'],
 ['Prediksi',f'Skor {pct(b["model_score"])} < ambang 11%; kelas 0. Hasil merupakan false negative.'],
 ['Daun pohon',f'{fn["leaf_train_n"]} data latih; satu positif. Skor 1/22 atau 0,04545.']], [1.45,5.05],9.5)
figure(G/'error_BRK_0075.png','Gambar 7. Atribusi pada satu keterlambatan yang terlewat.',max_height=2.5)
p('Berkas masuk ke cabang bulan cos ≤ 0,683 dan hari Kamis > 0,5. Mayoritas contoh train pada daun itu tepat waktu. Nilai dasar SHAP turun hingga skor 0,04545, padahal target aktualnya terlambat. Pola hari penerimaan pada sampel kecil belum dapat menjelaskan seluruh variasi pengurusan.')
p('BRK_0168 juga terlambat, tetapi memperoleh skor nol pada daun berisi 17 contoh train yang semuanya kelas 0. Mengubah ambang di rentang positif tidak dapat memunculkan alarm bagi skor nol. Kasus ini menunjukkan bahwa pengaturan threshold saja belum menyelesaikan keterbatasan model.')
p('Label tidak terpicu alarm tidak diperlakukan sebagai persetujuan otomatis. Staf tetap memeriksa kondisi berkas dan tanggal target, termasuk kasus dengan skor rendah. Hasil prediksi serta konfirmasi pemeriksaan dapat disimpan agar peninjauan berikutnya memiliki jejak yang jelas.')

# 16 E taxonomy
page('E.3 Taksonomi kegagalan dan mitigasi pada prototipe')
table(['Jenis kegagalan','Bukti atau pemicu','Mitigasi yang diterapkan'],[
 ['Kualitas masukan','Kolom wajib kosong, numerik berupa string, tanggal tidak sah.','Schema menolak dengan 422; UI menampilkan pesan perbaikan.'],
 ['Di luar cakupan train','Kategori baru, nilai di luar rentang train, atau tanggal di luar periode train.','Peringatan dan review_required; tidak dianggap sebagai prediksi terverifikasi.'],
 ['Ambang keputusan','Skor dekat threshold atau banyak alarm pada threshold rendah.','Ambang dapat diatur per request; jarak 0,02 dari ambang memicu penanda review.'],
 ['Cakupan histori antrean','Histori referensi hanya 135 train; bukan seluruh antrean kantor.','Sumber dan jumlah histori ditampilkan; snapshot tambahan diisolasi per request.'],
 ['Keterbatasan pola model','FP BRK_0110, FN BRK_0075 dan BRK_0168; dominasi kalender.','Model tetap prototipe; pemeriksaan staf tidak digantikan skor.'],
 ['Informasi proses belum tersedia','Instansi tujuan dan skor ceklis awal tidak tercatat pada sumber.','Tidak dibuat nilai perkiraan; diperlukan catatan awal dan validasi pada periode baru.']], [1.3,2.4,2.8],9.3)
p('Penanda review diprioritaskan saat alarm aktif, skor dekat ambang, atau input berada di luar cakupan train. Penanda ini tidak mendeteksi semua kesalahan, termasuk false negative berprobabilitas rendah. Karena itu alur kerja tetap menempatkan pemeriksaan staf sebagai bagian yang terpisah dari keputusan model.')
p('Checkbox pemeriksaan pada aplikasi mencatat apakah pengguna mengakui telah meninjau hasil. Berkas unduhan menyimpan nilai konfirmasi tersebut bersama input, threshold, skor, dan versi model. Keberadaan unduhan tanpa konfirmasi tidak diartikan sebagai bukti bahwa pemeriksaan telah dilakukan.')
p('Uji sebelum penggunaan yang lebih luas perlu memakai periode baru, histori kantor yang lengkap, kapasitas pemeriksaan, dan definisi kerugian false positive serta false negative. Login peran, penyimpanan audit terpusat, dan pemantauan perubahan data belum menjadi layanan produksi dalam prototipe lokal ini.')

# 17 F
page('F. LEMBAR KOMITMEN DAN INTEGRITAS AKADEMIK TIM',1)
p('Kami menyusun prototipe berdasarkan pipeline terpilih Tugas 04 dan mempertahankan 169 catatan sumber. Tidak ada perubahan label atau penambahan catatan survei untuk memperbaiki skor. Kasus berawalan UJI merupakan fixture pengujian perangkat lunak dan dibedakan dari data kantor.')
p('Hasil serialisasi, pengujian API, latensi, tangkapan aplikasi, serta analisis kesalahan diperoleh melalui eksekusi kode yang disertakan. Pembuatan kode dan penyuntingan laporan memakai bantuan AI. Kelompok bertanggung jawab memeriksa isi, memahami metode, dan mengesahkan laporan sebelum pengumpulan.')
t=table(['Tempat dan tanggal','Koordinator tim','Tanda tangan'],[['Jakarta,\n29 Oktober 2026','Muhammad Rizqi Saputra\nNIM 12250158','\n\n\nMuhammad Rizqi Saputra']], [1.5,2.4,2.6],9.6)
h('Referensi',2)
refs=[
 '[1] Kelompok 02. Tugas 04 Pembelajaran Mesin. Kantor Notaris & PPAT Aries Buwana. 22 Oktober 2026, 17 halaman.',
 '[2] Saputra, I. Rekap Evaluasi dan Feedback Tugas 04. 23 Oktober 2026. Bagian Kelompok 02 halaman 4-5 dan instruksi Tugas 05 halaman 13-14.',
 '[3] Saputra, I. Template Tugas 05 Pembelajaran Mesin. Semester Gasal 2026/2027.',
 '[4] Scikit-learn 1.8. Model persistence. https://scikit-learn.org/1.8/model_persistence.html',
 '[5] FastAPI. Request Body. https://fastapi.tiangolo.com/tutorial/body/',
 '[6] Pydantic. Strict Mode. https://docs.pydantic.dev/latest/concepts/strict_mode/',
 '[7] Streamlit. st.cache_resource dan App testing. https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource ; https://docs.streamlit.io/develop/concepts/app-testing',
 '[8] SHAP. TreeExplainer. https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html',
 'Dokumentasi daring diakses 29 Oktober 2026. Data sumber: berkas_notaris_terisi (2).csv, 169 baris.'
]
for r in refs:p(r,size=8.9,after=5)

# 18 appendix
page('Lampiran Bukti kelengkapan dan cara menjalankan')
table(['Ketentuan Tugas 05','Bukti dalam paket','Status'],[
 ['Pipeline serial terpadu','artifacts/model_final.joblib; inference.py; fitur_notaris.py','Tersedia dan diuji.'],
 ['Metadata model','artifacts/model_metadata.json','Tanggal, parameter, ambang, metrik, versi, hash.'],
 ['Antarmuka interaktif dan SHAP','app.py; screenshots/ui_form.png dan ui_result.png','Dijalankan dan direkam.'],
 ['API POST /predict dan schema','api.py; schemas.py; bukti cURL','HTTP 200 dan 422 diuji.'],
 ['Ambang dinamis dan antrean','dynamic_threshold.json; history_test.json','Batas tepat dan isolasi state diuji.'],
 ['100 masukan berulang dan edge cases','benchmark.json; latency_all_requests.csv; edge_cases.json','100 indeks × 3 putaran; 13 skenario edge.'],
 ['Analisis kegagalan','error_cases.json; holdout_replay_34.csv','FP dan FN dari data test lama.']], [1.65,3.2,1.65],9.2)
h('Menjalankan prototipe dari folder utama paket',2)
code('''python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port 8505

# Terminal lain, dengan lingkungan yang sama:
python -m uvicorn api:app --host 127.0.0.1 --port 8005
''')
p('Buka http://localhost:8505 untuk form dan http://localhost:8005/docs untuk dokumentasi endpoint. Model sudah disertakan; menjalankan prototipe tidak memerlukan pengulangan GridSearchCV. Petunjuk pengujian serta susunan bukti dijelaskan pada README.md.')
p('Pengumpulan sesuai instruksi Minggu 05 memuat PDF laporan dan ZIP kode, artefak model, serta pengujian. Nama PDF: TUGAS_05_KELOMPOK_02_NOTARIS_PPAT.pdf. Unggah melalui LMS EL-NUSA dan cadangkan ke Google Drive penugasan kelompok, paling lambat Kamis, 29 Oktober 2026 pukul 23:59:59 WIB. Pengesahan Bagian F diisi koordinator. [2]')

path=reports/'TUGAS_05_KELOMPOK_02_NOTARIS_PPAT.docx';doc.save(path)
print(json.dumps({'docx':str(path),'paragraphs':len(doc.paragraphs),'tables':len(doc.tables),'figures':len(doc.inline_shapes)}))
