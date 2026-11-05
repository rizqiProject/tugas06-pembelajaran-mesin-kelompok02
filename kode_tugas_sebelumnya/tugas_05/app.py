"""Antarmuka staf untuk mencoba model Tugas 04 yang telah diserialisasi."""
from datetime import date
from pathlib import Path
import io,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import streamlit as st
from pydantic import ValidationError
from schemas import PredictRequest,HistoryItem
from service import InferenceService

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='Tinjau Berkas | Aries Buwana',page_icon='📁',layout='wide')
st.markdown('''<style>
.block-container{max-width:1180px;padding-top:1.6rem;padding-bottom:2rem}
h1{font-size:2.1rem!important;letter-spacing:-.04em;color:#173d48}
h2{font-size:1.18rem!important;color:#173d48}
div[data-testid="stMetric"]{border:1px solid #dce6e8;border-radius:12px;padding:14px;background:#fff}
div[data-testid="stForm"]{border-radius:15px;border-color:#dce6e8;background:white}
div[data-testid="stCaptionContainer"]{color:#546871}
.office{font-size:12px;text-transform:uppercase;letter-spacing:.14em;color:#537b83;margin-bottom:5px}
</style>''',unsafe_allow_html=True)

@st.cache_resource
def load_service():return InferenceService()

service=load_service()
st.markdown('<div class="office">Kantor Notaris & PPAT Aries Buwana</div>',unsafe_allow_html=True)
st.title('Tinjau risiko keterlambatan berkas')
st.write('Masukkan data saat berkas diterima. Hasil membantu pemeriksaan staf dan tidak menetapkan kepastian waktu penyelesaian.')
st.caption('Prototipe penelitian Kelompok 02 · Model dari Tugas 04 · Ambang awal 11%')

presets={
 'Berkas BRK_0024 dari rekap kantor':json.loads((ROOT/'tests/fixtures/BRK_0024.json').read_text())['record'],
 'Skenario uji layanan baru':{'id_berkas':'UJI_BARU_001','tgl_masuk':'2026-10-29','kategori_akta':'PKR_PT','jumlah_penghadap':2,'sla_hari':14,'tgl_rups':None},
 'Skenario uji skor lebih tinggi':{'id_berkas':'UJI_RISIKO_001','tgl_masuk':'2026-12-01','kategori_akta':'PKR_PT','jumlah_penghadap':8,'sla_hari':10,'tgl_rups':None}}
selected=st.selectbox('Isi contoh untuk mencoba aplikasi',list(presets),key='preset')
if st.session_state.get('applied_preset')!=selected:
    r=presets[selected]
    st.session_state.update({'record_id':r['id_berkas'],'entry':date.fromisoformat(r['tgl_masuk']),
        'category':r['kategori_akta'],'people':r['jumlah_penghadap'],'sla':r['sla_hari'],
        'has_rups':r['tgl_rups'] is not None,'rups':date.fromisoformat(r['tgl_rups']) if r['tgl_rups'] else date.fromisoformat(r['tgl_masuk']),
        'applied_preset':selected})
    st.session_state.pop('result',None)

with st.expander('Sumber histori antrean',expanded=False):
    st.write('Histori awal berisi 135 catatan train. Hitungan ini terbatas pada snapshot tersebut, belum seluruh antrean kantor.')
    uploaded=st.file_uploader('Ganti dengan snapshot histori CSV',type=['csv'],key='history_csv',
        help='Kolom: id_berkas, tgl_masuk, tgl_selesai. Tanggal selesai boleh kosong jika masih terbuka.')
    st.caption('Mengganti histori memperbarui hitungan antrean. Pohon dan encoder tetap memakai model Tugas 04.')

left,right=st.columns([1.05,1],gap='large')
with left:
    st.subheader('Data penerimaan')
    with st.form('input_berkas'):
        st.text_input('ID berkas',key='record_id')
        st.date_input('Tanggal masuk',key='entry',min_value=date(2000,1,1),max_value=date(2100,12,31))
        st.selectbox('Kategori akta',service.model.reference_info['categories'],key='category',format_func=lambda s:s.replace('_',' '))
        a,b=st.columns(2)
        a.number_input('Jumlah penghadap',min_value=1,max_value=100,step=1,key='people')
        b.number_input('SLA (hari kalender)',min_value=1,max_value=365,step=1,key='sla')
        st.checkbox('Tanggal RUPS tercatat',key='has_rups')
        st.date_input('Tanggal RUPS (opsional)',key='rups',min_value=date(2000,1,1),max_value=date(2100,12,31))
        st.slider('Ambang pemeriksaan',min_value=.01,max_value=.99,value=.11,step=.01,format='%.2f',key='threshold',
            help='Contoh 0,11 berarti alarm aktif jika skor model setidaknya 11%. Ambang lebih rendah menambah alarm.')
        submitted=st.form_submit_button('Periksa risiko',type='primary',width='stretch')
    if submitted:
        try:
            history=None
            if uploaded is not None:
                h=pd.read_csv(io.BytesIO(uploaded.getvalue()))
                needed=['id_berkas','tgl_masuk','tgl_selesai']
                if not set(needed).issubset(h.columns):raise ValueError('CSV histori harus memuat tiga kolom yang disebutkan.')
                history=h[needed].replace({np.nan:None}).to_dict('records')
            payload={'record':{'id_berkas':st.session_state.record_id,'tgl_masuk':st.session_state.entry.isoformat(),
                'kategori_akta':st.session_state.category,'jumlah_penghadap':int(st.session_state.people),
                'sla_hari':int(st.session_state.sla),'tgl_rups':st.session_state.rups.isoformat() if st.session_state.has_rups else None},
                'threshold':float(st.session_state.threshold),'history':history,'explain':True}
            req=PredictRequest.model_validate(payload)
            st.session_state['result']=service.predict(req)
            st.session_state['request_used']=req.model_dump(mode='json')
            st.session_state['staff_reviewed']=False
        except (ValidationError,ValueError) as e:
            st.session_state.pop('result',None)
            st.error('Masukan belum dapat diproses. Periksa ID, tanggal, angka, dan format histori.')
            with st.expander('Rincian masukan yang perlu diperbaiki'):st.text(str(e))

with right:
    st.subheader('Hasil pemeriksaan')
    result=st.session_state.get('result')
    if result is None:
        st.info('Hasil akan muncul setelah Anda menekan Periksa risiko.')
        st.write('Tanggal selesai berkas baru tidak diminta. Antrean, hari masuk, dan fitur waktu dihitung otomatis dari data penerimaan serta histori.')
    else:
        if result['prediction']:st.warning(result['label'])
        else:st.success(result['label'])
        x,y=st.columns(2)
        x.metric('Skor risiko model',f"{result['model_score']*100:.2f}%")
        y.metric('Ambang pemeriksaan',f"{result['threshold_used']*100:.2f}%")
        st.caption('Skor belum dikalibrasi sebagai peluang nyata. Pemeriksaan berkas tetap dilakukan staf.')
        st.write(f"**Antrean awal hari:** {result['queue_at_entry']} berkas dari {result['history_records']} catatan histori.")
        if result['warnings']:
            for warning in result['warnings']:st.info(warning)
        explanation=result['explanation']
        if explanation:
            st.markdown('**Fitur yang membentuk skor**')
            rows=explanation['features'];labels=[r['label'] for r in rows];values=[r['shap'] for r in rows]
            fig,ax=plt.subplots(figsize=(5.4,2.3),dpi=140)
            ax.barh(labels,values,color=['#bd493f' if v>0 else '#245a81' for v in values],height=.6)
            ax.axvline(0,color='#aab7bd',lw=.8);ax.invert_yaxis();ax.spines[['top','right','left']].set_visible(False)
            ax.tick_params(axis='y',length=0,labelsize=9);ax.tick_params(axis='x',labelsize=8)
            ax.set_xlabel('Kontribusi SHAP pada skor',fontsize=8);fig.tight_layout()
            st.pyplot(fig,width='stretch');plt.close(fig)
            st.caption(f"Nilai dasar {explanation['base_value']:.5f} + kontribusi {explanation['sum_shap']:+.5f} = skor {result['model_score']:.5f}. Merah menaikkan, biru menurunkan skor.")
        reviewed=st.checkbox('Saya sudah memeriksa hasil bersama kondisi berkas',key='staff_reviewed')
        record={'request':st.session_state['request_used'],'result':result,'staff_review_acknowledged':reviewed}
        st.download_button('Unduh hasil pemeriksaan',json.dumps(record,indent=2,ensure_ascii=False),
            file_name=f"hasil_{result['id_berkas']}.json",mime='application/json',width='stretch')
        with st.expander('Detail hasil dan fitur yang dihitung'):
            st.json({'features':result['derived_features'],'review_reasons':result['review_reasons'],
                     'processing_ms':round(result['processing_ms'],3),'model_version':result['model_version']})

st.divider()
st.caption('Data penelitian: 169 berkas. Pengujian Tugas 04 pada 34 berkas masih menunjukkan banyak alarm palsu. Prototipe digunakan untuk uji terawasi.')
