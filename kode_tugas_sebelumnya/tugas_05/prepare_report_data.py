"""Siapkan gambar dan ringkasan dari hasil pengujian yang telah dieksekusi."""
from pathlib import Path
import json,xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
import joblib

ROOT=Path(__file__).resolve().parent;E=ROOT/'evidence';G=E/'figures';G.mkdir(exist_ok=True)
BLUE='#245A81';RED='#BD493F';TEAL='#245A63';GRAY='#596B76'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':10})

def save(fig,name):
    fig.savefig(G/name,dpi=190,bbox_inches='tight',facecolor='white');plt.close(fig)

fig,ax=plt.subplots(figsize=(10,4.6));ax.set_xlim(0,10);ax.set_ylim(0,5);ax.axis('off')
nodes=[(.25,3.35,2.25,1.1,'Form Streamlit\natau JSON POST /predict'),
       (3,3.35,2.3,1.1,'Schema Pydantic\nTipe, batas, tanggal'),
       (6,3.35,3.45,1.1,'model_final.joblib\nPipeline utuh dan ambang awal'),
       (6,1.15,3.45,1.2,'Fitur antrean dan waktu\nImputer + encoder → pohon'),
       (3,1.15,2.3,1.2,'Skor + ambang\nSHAP lokal\nPenanda review'),
       (.25,1.15,2.25,1.2,'Hasil untuk staf\nLabel dan skor\nUnduhan JSON')]
for x,y,w,h,t in nodes:
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.08',fc='#EEF3F6',ec='#B7CAD3',lw=1))
    ax.text(x+w/2,y+h/2,t,ha='center',va='center',color='#173D48',fontsize=10)
for a,b in [((2.6,3.9),(2.9,3.9)),((5.4,3.9),(5.9,3.9)),((7.7,3.25),(7.7,2.5)),((5.9,1.75),(5.4,1.75)),((2.9,1.75),(2.6,1.75))]:
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=14,color=GRAY,lw=1.4))
ax.text(5,.32,'Histori opsional masuk ke transformer per request; encoder dan pohon tetap.',ha='center',fontsize=10,color=GRAY)
save(fig,'01_architecture.png')

lat=pd.read_csv(E/'latency_all_requests.csv')
fig,axs=plt.subplots(1,2,figsize=(10.5,3.8),sharey=True)
for ax,(name,title,col) in zip(axs,[('service_with_shap','Layanan inferensi + SHAP',BLUE),('http_localhost_with_shap','HTTP localhost + SHAP',TEAL)]):
    v=lat.loc[lat.channel.eq(name),'ms'].to_numpy();ax.plot(np.arange(1,len(v)+1),v,color=col,lw=.9)
    ax.axhline(100,color=RED,ls='--',lw=1.1,label='Acuan 100 ms')
    ax.axhline(v.mean(),color=GRAY,ls=':',lw=1.1,label=f'Rata-rata {v.mean():.2f} ms')
    ax.set_title(title);ax.set_xlabel('Urutan permintaan (300)');ax.grid(alpha=.15);ax.spines[['top','right']].set_visible(False)
    ax.legend(fontsize=8,loc='upper left')
axs[0].set_ylabel('Waktu respons (ms)');fig.tight_layout();save(fig,'02_latency.png')

threshold=json.loads((E/'dynamic_threshold.json').read_text())
fig,ax=plt.subplots(figsize=(9.4,3.3))
xx=np.linspace(.01,.5,300);p=threshold[0]['score']
ax.step(xx,(p>=xx).astype(int),where='post',color=BLUE,lw=2)
ax.axvline(.11,color=TEAL,ls='--',label='Ambang awal 0,11')
ax.axvline(p,color=RED,ls=':',label=f'Skor tetap {p:.4f}')
ax.set_yticks([0,1],['Tidak terpicu alarm','Perlu pemeriksaan']);ax.set_xlabel('Ambang keputusan');ax.set_title('Keputusan BRK_0024 saat ambang diubah')
ax.grid(axis='x',alpha=.2);ax.spines[['top','right']].set_visible(False);ax.legend(loc='upper right',fontsize=9)
fig.tight_layout();save(fig,'03_threshold.png')

model=joblib.load(ROOT/'artifacts/model_final.joblib')
errors=json.loads((E/'error_cases.json').read_text())
for case in errors:
    exp=case['response']['explanation'];rows=exp['features'];phi=[x['shap'] for x in rows]
    fig,ax=plt.subplots(figsize=(9.2,3.2))
    ax.barh([x['label'] for x in rows],phi,color=[RED if x>0 else BLUE for x in phi],height=.6)
    ax.invert_yaxis();ax.axvline(0,color=GRAY,lw=.8);ax.spines[['top','right','left']].set_visible(False)
    ax.set_xlabel('Kontribusi SHAP pada skor keterlambatan')
    ax.set_title(f"{case['id_berkas']}: aktual {case['actual']}, skor {case['response']['model_score']:.5f}")
    ax.grid(axis='x',alpha=.15);fig.tight_layout();save(fig,f"error_{case['id_berkas']}.png")
    row={'id_berkas':case['id_berkas'],**case['raw']}
    frame=pd.DataFrame([row]);features=model.pipeline.named_steps['fitur'].transform(frame)
    encoded=model.pipeline.named_steps['prep'].transform(features);tree=model.pipeline.named_steps['model']
    leaf=int(tree.apply(encoded)[0]);case['leaf_id']=leaf;case['leaf_train_n']=int(tree.tree_.n_node_samples[leaf])
    case['leaf_class_distribution']=tree.tree_.value[leaf,0].tolist()
    case['path']=[]
    for node in tree.decision_path(encoded).indices:
        f=int(tree.tree_.feature[node])
        if f<0:continue
        value=float(encoded[0,f]);boundary=float(tree.tree_.threshold[node])
        case['path'].append({'feature':model.feature_names[f],'value':value,'operator':'<=' if value<=boundary else '>','boundary':boundary})
(E/'error_cases.json').write_text(json.dumps(errors,indent=2,ensure_ascii=False))
xml=ET.parse(E/'pytest_results.xml').getroot()
suites=xml.findall('testsuite') if xml.tag=='testsuites' else [xml]
summary={'tests':sum(int(s.attrib.get('tests',0)) for s in suites),'failures':sum(int(s.attrib.get('failures',0)) for s in suites),
         'errors':sum(int(s.attrib.get('errors',0)) for s in suites),'seconds':sum(float(s.attrib.get('time',0)) for s in suites)}
(E/'test_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({'tests':summary,'figures':len(list(G.glob('*.png'))),'cases':[{k:r[k] for k in ['id_berkas','leaf_train_n','leaf_class_distribution']} for r in errors]}))
