"""Periksa kesesuaian data, model tersimpan, dan angka laporan tanpa tuning ulang."""
from pathlib import Path
import hashlib
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from analisis_tugas04_asli import make_data, FEATURES

ROOT=Path(__file__).resolve().parents[1]
H=ROOT/'work/hasil_tugas04_asli'
raw_all=pd.read_csv(ROOT/'upload/berkas_notaris_ v5.csv')
raw=raw_all.loc[raw_all.sumber.eq('asli')].reset_index(drop=True)
saved=pd.read_csv(H/'berkas_notaris_asli_dengan_fitur_tanggal.csv')
assert len(raw)==169 and raw.terlambat.sum()==35
for col in raw.columns:
    pd.testing.assert_series_equal(raw[col],saved[col])
z=make_data(raw).set_index('id_berkas')
part=pd.read_csv(H/'partisi_dan_fold.csv')
tr=part.loc[part.partisi.eq('train'),'id_berkas']
te=part.loc[part.partisi.eq('test'),'id_berkas']
assert len(tr)==135 and len(te)==34 and not set(tr)&set(te)
assert set(tr)|set(te)==set(z.index)
preds=pd.read_csv(H/'prediksi_test_34_berkas.csv').set_index('id_berkas')
assert set(preds.index)==set(te)
y=z.loc[preds.index,'terlambat'].to_numpy()
metrics=pd.read_csv(H/'metrik_train_test.csv')
b=joblib.load(H/'model_baseline.joblib')
t=joblib.load(H/'model_tuned_penelitian.joblib')
for obj,key in [(b,'p_baseline'),(t,'p_tuned')]:
    assert obj['features']==FEATURES
    p=obj['pipeline'].predict_proba(z.loc[preds.index,FEATURES])[:,1]
    np.testing.assert_allclose(p,preds[key],rtol=0,atol=1e-14)
for name,col,threshold in [('Baseline v5','p_baseline',.5),('Tuned 0.50','p_tuned',.5),('Tuned 0.25','p_tuned',.25),('Tuned OOF','p_tuned',t['threshold'])]:
    p=preds[col].to_numpy();positive=p>=threshold
    tp=int(((y==1)&positive).sum());fn=int(((y==1)&~positive).sum())
    fp=int(((y==0)&positive).sum());tn=int(((y==0)&~positive).sum())
    m=metrics.loc[metrics.model.eq(name)&metrics.partisi.eq('Test')].iloc[0]
    assert [tp,fn,fp,tn]==[m.tp,m.fn,m.fp,m.tn]
    assert np.isclose(2*tp/(2*tp+fp+fn),m.f1)
    assert np.isclose(average_precision_score(y,p),m.ap)
subset=ROOT/'work/data_final_asli/berkas_notaris_asli_169.csv'
if subset.exists():
    reread=pd.read_csv(subset)
    for col in raw.columns:pd.testing.assert_series_equal(raw[col],reread[col])
form=ROOT/'work/data_final_asli/FORM_VERIFIKASI_FITUR_TAMBAHAN_169.csv'
if form.exists():
    f=pd.read_csv(form)
    assert f.id_berkas.tolist()==raw.id_berkas.tolist()
    assert f.drop(columns='id_berkas').isna().all().all()
proof={'n_asli':169,'train':135,'test':34,'positive_train':28,'positive_test':7,
    'input_values_unchanged':True,'holdout_probabilities_match_saved_results':True,
    'test_train_ids_disjoint':True,'confusion_counts_f1_and_ap_match_saved_metrics':True,
    'raw_input_sha256':hashlib.sha256((ROOT/'upload/berkas_notaris_ v5.csv').read_bytes()).hexdigest(),
    'subset_csv_sha256':hashlib.sha256(subset.read_bytes()).hexdigest(),
    'new_predictors_generated_randomly':False,'form_fields_not_used_in_current_model':True,
    'original_t03_raw_matrix_provided':False}
(H/'verifikasi_konsistensi_final.json').write_text(json.dumps(proof,indent=2))
print('LULUS: 169 nilai data asli, partisi, probabilitas, confusion matrix, F1, AP, dan formulir kosong konsisten.')
