"""Logika inferensi bersama untuk Streamlit dan FastAPI."""
from pathlib import Path
from threading import Lock
import time
import json
import joblib
import numpy as np
import pandas as pd
import shap
from schemas import PredictRequest

ROOT=Path(__file__).resolve().parent

def nice(name):
    labels={'jumlah_penghadap':'Jumlah penghadap','sla_hari':'SLA hari',
            'antrean_berjalan':'Antrean awal hari','ada_rups':'RUPS tersedia saat masuk',
            'bulan_sin':'Bulan sin','bulan_cos':'Bulan cos'}
    return labels.get(name,name.replace('kategori_akta_','Akta = ').replace('hari_masuk_','Hari = ').replace('_',' '))

class InferenceService:
    def __init__(self,path=None):
        self.model=joblib.load(path or ROOT/'artifacts/model_final.joblib')
        self.metadata=json.loads((ROOT/'artifacts/model_metadata.json').read_text())
        self.explainer=shap.TreeExplainer(self.model.pipeline.named_steps['model'],
            data=self.model.background,feature_perturbation='interventional',model_output='probability')
        self.explainer_lock=Lock()

    def predict(self,request:PredictRequest):
        started=time.perf_counter_ns()
        row=request.record.model_dump(mode='json')
        raw=pd.DataFrame([row])
        history=None if request.history is None else [h.model_dump(mode='json') for h in request.history]
        pipe=self.model.working_pipeline(history)
        engineered=pipe.named_steps['fitur'].transform(raw)
        encoded=pipe.named_steps['prep'].transform(engineered)
        prob=float(pipe.named_steps['model'].predict_proba(encoded)[0,1])
        threshold=self.model.threshold if request.threshold is None else float(request.threshold)
        pred=int(prob>=threshold)
        warnings=[];ood=[]
        ranges=self.model.reference_info['numeric_train_ranges']
        for column in ['jumlah_penghadap','sla_hari']:
            lo,hi=ranges[column]
            if not lo<=row[column]<=hi:ood.append(f'{column} di luar rentang train {lo}-{hi}')
        if row['kategori_akta'] not in self.model.reference_info['categories']:
            ood.append('Kategori belum terdapat pada encoder train')
        if not self.model.reference_info['date_min']<=row['tgl_masuk']<=self.model.reference_info['date_max']:
            ood.append('Tanggal masuk di luar periode train')
        if row['tgl_rups'] is not None and row['tgl_rups']>row['tgl_masuk']:
            warnings.append('Tanggal RUPS sesudah penerimaan tidak dipakai sebagai informasi awal.')
        warnings.extend(ood)
        near=abs(prob-threshold)<=.02
        reasons=[]
        if pred:reasons.append('Skor mencapai ambang pemeriksaan')
        if near:reasons.append('Skor berdekatan dengan ambang, dalam jarak 0,02')
        if ood:reasons.append('Masukan berbeda dari cakupan data latih')
        explanation=None
        if request.explain:
            with self.explainer_lock:
                exp=self.explainer(encoded,check_additivity=True)
            if exp.values.ndim==3:
                phi=exp.values[0,:,1];base=float(exp.base_values[0,1])
            else:phi=exp.values[0];base=float(np.ravel(exp.base_values)[0])
            order=np.argsort(-np.abs(phi))
            explanation={'base_value':base,'sum_shap':float(phi.sum()),
                'reconstructed_probability':float(base+phi.sum()),
                'additivity_error':float(abs(base+phi.sum()-prob)),
                'features':[{'feature':self.model.feature_names[i],
                    'label':nice(self.model.feature_names[i]),'value':float(encoded[0,i]),
                    'shap':float(phi[i])} for i in order if abs(phi[i])>1e-10]}
        result={'id_berkas':row['id_berkas'],'prediction':pred,
            'label':'Perlu pemeriksaan staf' if pred else 'Tidak terpicu alarm',
            'model_score':prob,'threshold_used':threshold,'default_threshold':self.model.threshold,
            'probability_calibrated':False,'review_required':bool(pred or near or ood),
            'review_reasons':reasons,'warnings':warnings,
            'history_source':'snapshot train Tugas 04' if history is None else 'snapshot yang diberikan pengguna',
            'history_records':len(pipe.named_steps['fitur'].id_hist_),
            'queue_at_entry':int(engineered.iloc[0].antrean_berjalan),
            'derived_features':{k:(float(v) if isinstance(v,(np.floating,float)) else int(v) if isinstance(v,(np.integer,int)) else str(v))
                                for k,v in engineered.iloc[0].items()},
            'explanation':explanation,'model_version':self.metadata['model_version']}
        result['processing_ms']=(time.perf_counter_ns()-started)/1e6
        return result
