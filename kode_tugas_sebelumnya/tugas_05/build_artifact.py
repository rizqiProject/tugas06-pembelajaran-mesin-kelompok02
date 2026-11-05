"""Ekspor model Tugas 04 tanpa pelatihan ulang atau pemilihan parameter baru."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse,hashlib,importlib.metadata,json,platform,shutil
import joblib
import numpy as np
import pandas as pd
from inference import NotarisRiskModel

ROOT=Path(__file__).resolve().parent

def main(source_root):
    origin=Path(source_root);h=origin/'work/hasil_tugas04_kantor'
    (ROOT/'artifacts').mkdir(exist_ok=True);(ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'evidence').mkdir(exist_ok=True);(ROOT/'tests/fixtures').mkdir(parents=True,exist_ok=True)
    saved=joblib.load(h/'model_tuned_penelitian.joblib');pipe=saved['pipeline']
    raw=pd.read_csv(origin/'upload/berkas_notaris_terisi (2).csv')
    ids=pipe.named_steps['fitur'].id_hist_.tolist()
    train=raw.set_index('id_berkas',drop=False).loc[ids]
    encoded=pipe.named_steps['prep'].transform(pipe.named_steps['fitur'].transform(train))
    ix=np.random.default_rng(42).choice(len(train),size=min(200,len(train)),replace=False)
    categories=pipe.named_steps['prep'].named_transformers_['cat'].named_steps['onehot'].categories_[0].tolist()
    ref={'numeric_train_ranges':{k:[int(train[k].min()),int(train[k].max())] for k in ['jumlah_penghadap','sla_hari']},
         'categories':categories,'date_min':str(train.tgl_masuk.min()),'date_max':str(train.tgl_masuk.max()),
         'history_records':len(ids)}
    model=NotarisRiskModel(pipe,saved['threshold'],encoded[ix],pipe.named_steps['prep'].get_feature_names_out().tolist(),ref)
    path=ROOT/'artifacts/model_final.joblib';joblib.dump(model,path,compress=3)
    loaded=joblib.load(path)
    pred=pd.read_csv(h/'prediksi_test_34_berkas.csv')
    test=raw.set_index('id_berkas',drop=False).loc[pred.id_berkas]
    # Tanggal selesai berkas yang diprediksi tidak diperlukan endpoint.
    request_columns=['id_berkas','tgl_masuk','kategori_akta','jumlah_penghadap','sla_hari','tgl_rups']
    prob=loaded.predict_proba(test[request_columns])[:,1]
    error=float(np.max(np.abs(prob-pred.p_tuned.to_numpy())))
    roundtrip_error=float(np.max(np.abs(prob-model.predict_proba(test[request_columns])[:,1])))
    assert error<1e-14
    np.testing.assert_array_equal(loaded.predict(test[request_columns]),pred.pred_oof)
    frozen=json.loads((h/'konfigurasi_dibekukan_sebelum_test.json').read_text())
    versions={p:importlib.metadata.version(p) for p in ['numpy','pandas','scipy','scikit-learn','joblib','shap','numba','llvmlite','fastapi','pydantic','starlette','uvicorn','streamlit','httpx','pytest']}
    versions.update({'numpy':np.__version__,'pandas':pd.__version__})
    source_sha=hashlib.sha256((origin/'upload/berkas_notaris_terisi (2).csv').read_bytes()).hexdigest()
    metrik_t04=pd.read_csv(h/'metrik_train_test.csv')
    score_sets={name:metrik_t04[(metrik_t04.model.eq(name))&(metrik_t04.partisi.eq('Test'))].iloc[0].to_dict()
                for name in ['Tuned OOF','Tuned 0.50','Tuned 0.25']}
    meta={'model_version':'notaris-t04-export-1.0','training_date':'2026-10-22',
        'training_timestamp':None,'training_date_source':'Tanggal eksperimen dan laporan Tugas 04; jam fit tidak direkam.',
        'exported_at':datetime.now(ZoneInfo('Asia/Jakarta')).isoformat(),
        'training_repeated':False,'algorithm':'DecisionTreeClassifier','best_params':frozen['best_params'],
        'threshold_default':loaded.threshold,'threshold_source':'F2 maksimum dari OOF train Tugas 04',
        'threshold_runtime_range':[.01,.99],'n_source':169,'n_train':135,'n_test':34,'n_positive_test':7,
        'source_sha256':source_sha,'source_model_sha256':hashlib.sha256((h/'model_tuned_penelitian.joblib').read_bytes()).hexdigest(),
        'artifact_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'artifact_bytes':path.stat().st_size,
        'pipeline_steps':['FiturNotaris','ColumnTransformer (imputer dan OneHotEncoder)','DecisionTreeClassifier'],
        'request_columns':request_columns,'excluded_request_columns':['tgl_selesai','terlambat','durasi','selisih_sla'],
        'metrics_test':score_sets,'classification_reports_test':json.loads((h/'classification_report_test.json').read_text()),
        'versions':versions,'python':platform.python_version(),'reference_info':ref,
        'parity_test_max_abs_error':error,'serialization_roundtrip_error':roundtrip_error,'parity_test_predictions_identical':True,
        'feedback_parameter_note':'Rekap dosen menyebut depth=3, leaf=5; artefak dan tabel B T04 memuat depth=4, leaf=15. Ekspor mengikuti artefak T04 yang tervalidasi.',
        'queue_rule':'Masuk histori < tanggal input dan (selesai kosong atau selesai >= tanggal input). Histori baru masuk di hari yang sama tidak dihitung.',
        'default_history_limitation':'135 catatan latih; bukan inventaris antrean seluruh kantor. Snapshot pengguna dapat diberikan tanpa melatih ulang pohon.',
        'safe_use':'Prototipe lokal untuk penelitian, belum untuk prioritas otomatis; skor belum dikalibrasi.'}
    (ROOT/'artifacts/model_metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False))
    history=train[['id_berkas','tgl_masuk','tgl_selesai']].reset_index(drop=True)
    history.to_csv(ROOT/'data/history_train_reference.csv',index=False)
    raw.to_csv(ROOT/'data/berkas_notaris_169.csv',index=False)
    shutil.copy2(origin/'upload/berkas_notaris_terisi (2).csv',ROOT/'data/berkas_notaris_169.csv')
    pred.to_csv(ROOT/'data/prediksi_tugas04.csv',index=False)
    requests=[]
    for _,r in test[request_columns].iterrows():
        row=r.to_dict();row['tgl_rups']=None if pd.isna(row['tgl_rups']) else row['tgl_rups']
        row['jumlah_penghadap']=int(row['jumlah_penghadap']);row['sla_hari']=int(row['sla_hari'])
        requests.append({'record':row,'explain':True})
    (ROOT/'data/requests_test_34.json').write_text(json.dumps(requests,indent=2))
    for identifier in ['BRK_0024','BRK_0110','BRK_0075']:
        example=next(q for q in requests if q['record']['id_berkas']==identifier)
        (ROOT/'tests/fixtures'/f'{identifier}.json').write_text(json.dumps(example,indent=2))
    (ROOT/'evidence/serialization_check.json').write_text(json.dumps({'n':34,'max_abs_probability_error_vs_csv':error,'serialization_roundtrip_error':roundtrip_error,
        'labels_identical':True,'source_artifact_params':frozen['best_params'],'default_threshold':loaded.threshold},indent=2))
    print(json.dumps({'artifact_bytes':path.stat().st_size,'probability_parity_error':error,'threshold':loaded.threshold,'versions':versions}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-root',required=True);main(p.parse_args().source_root)
