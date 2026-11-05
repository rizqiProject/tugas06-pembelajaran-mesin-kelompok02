"""Bukti pengujian nyata: skenario, API, latensi, dan kesalahan holdout T04."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse,copy,json,os,platform,time
import numpy as np
import pandas as pd
import httpx
from sklearn.metrics import confusion_matrix,precision_score,recall_score,f1_score,accuracy_score,average_precision_score
from schemas import PredictRequest
from service import InferenceService

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'evidence'

def dump(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')

def stats(v):
    a=np.asarray(v)
    return {'n':len(a),'mean_ms':float(a.mean()),'median_ms':float(np.median(a)),
            'p95_ms':float(np.percentile(a,95)),'max_ms':float(a.max()),'min_ms':float(a.min()),
            'mean_below_100_ms':bool(a.mean()<100)}

def main(url):
    OUT.mkdir(exist_ok=True)
    started=time.perf_counter_ns();s=InferenceService();init_ms=(time.perf_counter_ns()-started)/1e6
    requests=json.loads((ROOT/'data/requests_test_34.json').read_text())
    reference=pd.read_csv(ROOT/'data/prediksi_tugas04.csv')
    raw=pd.read_csv(ROOT/'data/berkas_notaris_169.csv').set_index('id_berkas')
    # Angka skenario adalah input uji perangkat lunak; tidak menambah observasi kantor.
    scenarios=[
      {'name':'Kasus normal pada skenario baru','kind':'software_fixture','request':{'record':{'id_berkas':'UJI_NORMAL_001','tgl_masuk':'2026-10-29','kategori_akta':'PKR_PT','jumlah_penghadap':2,'sla_hari':14,'tgl_rups':None},'explain':True}},
      {'name':'Skor lebih tinggi pada skenario baru','kind':'software_fixture','request':{'record':{'id_berkas':'UJI_RISIKO_001','tgl_masuk':'2026-12-01','kategori_akta':'PKR_PT','jumlah_penghadap':8,'sla_hari':10,'tgl_rups':None},'explain':True}},
      {'name':'Tepat pada ambang keputusan','kind':'software_fixture','request':{'record':{'id_berkas':'UJI_AMBANG_001','tgl_masuk':'2024-09-17','kategori_akta':'AJB_Saham','jumlah_penghadap':2,'sla_hari':10,'tgl_rups':None},'threshold':.1875,'explain':True}}]
    all_results=[];errors=[];rows=[]
    with httpx.Client(base_url=url,timeout=30,trust_env=False) as client:
        assert client.get('/health').status_code==200
        for q in scenarios:
            r=client.post('/predict',json=q['request']);assert r.status_code==200
            q['http_status']=r.status_code;q['response']=r.json()
        assert scenarios[2]['response']['model_score']==scenarios[2]['request']['threshold']
        dump('scenarios.json',scenarios)
        for req in requests:
            r=client.post('/predict',json=req);assert r.status_code==200
            response=r.json();all_results.append(response)
            identifier=req['record']['id_berkas'];actual=int(reference.loc[reference.id_berkas.eq(identifier),'terlambat'].iloc[0])
            rows.append({'id_berkas':identifier,'actual':actual,'score':response['model_score'],'prediction':response['prediction'],
                         'error_type':'FP' if response['prediction']==1 and actual==0 else 'FN' if response['prediction']==0 and actual==1 else 'TP' if actual else 'TN',
                         'queue':response['queue_at_entry'],'shap_error':response['explanation']['additivity_error']})
            if identifier in ['BRK_0110','BRK_0075','BRK_0168']:
                observation=raw.loc[identifier].to_dict()
                observation={k:(None if pd.isna(v) else int(v) if isinstance(v,np.integer) else v) for k,v in observation.items()}
                duration=int((pd.Timestamp(observation['tgl_selesai'])-pd.Timestamp(observation['tgl_masuk'])).days)
                errors.append({'id_berkas':identifier,'actual':actual,'duration_days':duration,'raw':observation,'response':response})
        table=pd.DataFrame(rows);table.to_csv(OUT/'holdout_replay_34.csv',index=False)
        np.testing.assert_allclose(table.score,reference.p_tuned,rtol=0,atol=1e-14)
        np.testing.assert_array_equal(table.prediction,reference.pred_oof)
        cm=confusion_matrix(table.actual,table.prediction,labels=[0,1]).ravel()
        dump('holdout_replay_summary.json',{'n':34,'tn':int(cm[0]),'fp':int(cm[1]),'fn':int(cm[2]),'tp':int(cm[3]),
            'accuracy':accuracy_score(table.actual,table.prediction),'precision':precision_score(table.actual,table.prediction),
            'recall':recall_score(table.actual,table.prediction),'f1':f1_score(table.actual,table.prediction),
            'ap':average_precision_score(table.actual,table.score),'max_shap_additivity_error':float(table.shap_error.max()),
            'max_abs_difference_t04_csv':float(np.max(np.abs(table.score-reference.p_tuned))),
            'purpose':'Uji regresi implementasi pada holdout lama, bukan estimasi performa pada data baru.'})
        dump('error_cases.json',errors)
        dump('replay_responses_34.json',all_results)
        base=json.loads((ROOT/'tests/fixtures/BRK_0024.json').read_text())
        threshold_rows=[]
        for t in [.01,.11,.1875,.187501,.25,.50,.99]:
            q=copy.deepcopy(base);q['threshold']=t;b=client.post('/predict',json=q).json()
            threshold_rows.append({'threshold':t,'score':b['model_score'],'prediction':b['prediction'],'queue':b['queue_at_entry']})
        dump('dynamic_threshold.json',threshold_rows)
        # Histori perangkat lunak dengan kasus masih terbuka, selesai hari yang sama,
        # sudah tertutup, masuk hari yang sama, serta baru masuk setelah waktu prediksi.
        hist=[{'id_berkas':'UJI_H_OPEN','tgl_masuk':'2024-09-01','tgl_selesai':None},
              {'id_berkas':'UJI_H_TODAY','tgl_masuk':'2024-09-01','tgl_selesai':'2024-09-17'},
              {'id_berkas':'UJI_H_CLOSED','tgl_masuk':'2024-09-01','tgl_selesai':'2024-09-16'},
              {'id_berkas':'UJI_H_SAME','tgl_masuk':'2024-09-17','tgl_selesai':None},
              {'id_berkas':'UJI_H_FUTURE','tgl_masuk':'2024-09-18','tgl_selesai':None}]
        q=copy.deepcopy(base);q['history']=hist
        history_result=client.post('/predict',json=q).json()
        assert history_result['queue_at_entry']==2
        original=client.post('/predict',json=base).json();assert original['queue_at_entry']==1
        dump('history_test.json',{'fixture_is_observed_office_data':False,'history':hist,
            'response':history_result,'default_queue_after_custom_request':original['queue_at_entry']})
        mutations=[
          ('Body kosong',{},422),
          ('Kolom wajib hilang',{'record':{k:v for k,v in base['record'].items() if k!='jumlah_penghadap'}},422),
          ('String pada numerik',{'record':dict(base['record'],jumlah_penghadap='dua')},422),
          ('Jumlah penghadap negatif',{'record':dict(base['record'],jumlah_penghadap=-1)},422),
          ('Jumlah melebihi batas teknis',{'record':dict(base['record'],jumlah_penghadap=101)},422),
          ('SLA nol',{'record':dict(base['record'],sla_hari=0)},422),
          ('Tanggal tidak valid',{'record':dict(base['record'],tgl_masuk='2026-02-30')},422),
          ('Tanggal selesai berkas baru disisipkan',{'record':dict(base['record'],tgl_selesai='2026-12-01')},422),
          ('Ambang di luar rentang',dict(base,threshold=1.1),422),
          ('Kategori belum dilatih',{'record':dict(base['record'],kategori_akta='Layanan_Baru')},200),
          ('RUPS setelah penerimaan',{'record':dict(base['record'],tgl_rups='2024-09-20')},200),
          ('Nilai valid di luar rentang train',{'record':dict(base['record'],jumlah_penghadap=100,sla_hari=365)},200),
          ('Histori kosong',dict(base,history=[]),200)]
        edge=[]
        for name,q,expected in mutations:
            r=client.post('/predict',json=q);b=r.json()
            edge.append({'name':name,'expected_status':expected,'actual_status':r.status_code,'passed':r.status_code==expected,
                         'warnings':b.get('warnings',[]),'response':b})
            assert r.status_code==expected,name
        dump('edge_cases.json',edge)
        # 100 indeks sampel berulang dari 34 holdout; tiga putaran, koneksi digunakan ulang.
        rng=np.random.default_rng(20261029);sample_idx=rng.choice(len(requests),size=100,replace=True)
        samples=[requests[int(i)] for i in sample_idx]
        for q in samples[:10]:client.post('/predict',json=q).raise_for_status()
        local=[];network=[];processing=[];timing_rows=[]
        typed=[PredictRequest.model_validate(q) for q in samples]
        for repeat in range(3):
            for i,q in enumerate(typed):
                t=time.perf_counter_ns();s.predict(q);ms=(time.perf_counter_ns()-t)/1e6
                local.append(ms);timing_rows.append({'channel':'service_with_shap','repeat':repeat+1,'sample':i+1,'ms':ms})
        for repeat in range(3):
            for i,q in enumerate(samples):
                t=time.perf_counter_ns();r=client.post('/predict',json=q);ms=(time.perf_counter_ns()-t)/1e6
                r.raise_for_status();network.append(ms);processing.append(r.json()['processing_ms'])
                timing_rows.append({'channel':'http_localhost_with_shap','repeat':repeat+1,'sample':i+1,'ms':ms})
        pd.DataFrame(timing_rows).to_csv(OUT/'latency_all_requests.csv',index=False)
        cpu_quota=Path('/sys/fs/cgroup/cpu.max')
        benchmark={'measured_at':datetime.now(ZoneInfo('Asia/Jakarta')).isoformat(),'samples_per_round':100,'rounds':3,
            'request_count_per_channel':300,'warmup_requests':10,'unique_sample_records':len(set(sample_idx.tolist())),
            'sample_source':'34 holdout Tugas 04, dipilih ulang dengan replacement; bukan 100 observasi kantor baru',
            'seed':20261029,'service_with_shap':stats(local),'http_localhost_with_shap':stats(network),
            'server_reported_processing':stats(processing),'service_initialization_in_imported_process_ms':init_ms,
            'host':{'os':platform.system(),'machine':platform.machine(),'python':platform.python_version(),
                    'visible_cpu_count':os.cpu_count(),'cgroup_cpu_max':cpu_quota.read_text().strip() if cpu_quota.exists() else None},
            'limitations':'Single worker, permintaan berurutan, localhost, koneksi dipakai ulang; waktu UI dan jaringan luar tidak termasuk.'}
        dump('benchmark.json',benchmark)
    print(json.dumps({'benchmark':benchmark,'scenarios':[{'name':q['name'],'score':q['response']['model_score'],'label':q['response']['prediction']} for q in scenarios],
        'edge_cases_passed':sum(q['passed'] for q in edge)},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base-url',default='http://127.0.0.1:8005');main(p.parse_args().base_url)
