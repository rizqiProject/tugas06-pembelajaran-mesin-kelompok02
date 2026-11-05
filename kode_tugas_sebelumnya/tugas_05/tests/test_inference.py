from pathlib import Path
import json,sys
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from api import app
from schemas import PredictRequest
from service import InferenceService

@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:yield c

@pytest.fixture
def payload():return json.loads((ROOT/'tests/fixtures/BRK_0024.json').read_text())

def test_reference_case_and_shap(client,payload):
    r=client.post('/predict',json=payload);assert r.status_code==200
    b=r.json();assert b['model_score']==.1875 and b['prediction']==1 and b['threshold_used']==.11
    assert b['queue_at_entry']==1 and b['explanation']['additivity_error']<1e-6

@pytest.mark.parametrize('threshold,label',[(.11,1),(.25,0),(.1875,1),(.187501,0),(.5,0)])
def test_dynamic_threshold(client,payload,threshold,label):
    payload['threshold']=threshold;b=client.post('/predict',json=payload).json()
    assert b['model_score']==.1875 and b['prediction']==label

@pytest.mark.parametrize('case',[
    'empty','missing_numeric','numeric_string','negative_count','bool_count','too_large_count',
    'zero_sla','huge_sla','invalid_date','empty_category','extra_completion','bad_threshold',
    'threshold_string','duplicate_history','history_bad_order'])
def test_invalid_input_is_422(client,payload,case):
    if case=='empty':payload={}
    elif case=='missing_numeric':del payload['record']['jumlah_penghadap']
    elif case=='numeric_string':payload['record']['jumlah_penghadap']='dua'
    elif case=='negative_count':payload['record']['jumlah_penghadap']=-1
    elif case=='bool_count':payload['record']['jumlah_penghadap']=True
    elif case=='too_large_count':payload['record']['jumlah_penghadap']=101
    elif case=='zero_sla':payload['record']['sla_hari']=0
    elif case=='huge_sla':payload['record']['sla_hari']=366
    elif case=='invalid_date':payload['record']['tgl_masuk']='2026-02-30'
    elif case=='empty_category':payload['record']['kategori_akta']='   '
    elif case=='extra_completion':payload['record']['tgl_selesai']='2026-10-30'
    elif case=='bad_threshold':payload['threshold']=1.1
    elif case=='threshold_string':payload['threshold']='0.11'
    elif case=='duplicate_history':payload['history']=[{'id_berkas':'H1','tgl_masuk':'2024-09-01','tgl_selesai':None}]*2
    elif case=='history_bad_order':payload['history']=[{'id_berkas':'H1','tgl_masuk':'2024-09-20','tgl_selesai':'2024-09-01'}]
    r=client.post('/predict',json=payload);assert r.status_code==422
    assert 'detail' in r.json() and client.get('/health').status_code==200

def test_unknown_category_warns(client,payload):
    payload['record']['kategori_akta']='Layanan_Baru_Tidak_Dilatih'
    b=client.post('/predict',json=payload).json()
    assert any('Kategori' in x for x in b['warnings']) and b['review_required']

def test_future_rups_is_ignored(client,payload):
    payload['record']['tgl_rups']='2024-09-20'
    b=client.post('/predict',json=payload).json()
    assert b['derived_features']['ada_rups']==0 and b['warnings'] and b['model_score']==.1875

def test_history_open_cases_and_no_shared_mutation(client,payload):
    baseline=client.post('/predict',json=payload).json()
    payload['history']=[
      {'id_berkas':'H_OPEN','tgl_masuk':'2024-09-01','tgl_selesai':None},
      {'id_berkas':'H_TODAY','tgl_masuk':'2024-09-01','tgl_selesai':'2024-09-17'},
      {'id_berkas':'H_CLOSED','tgl_masuk':'2024-09-01','tgl_selesai':'2024-09-16'},
      {'id_berkas':'H_SAME_DAY','tgl_masuk':'2024-09-17','tgl_selesai':None},
      {'id_berkas':'H_FUTURE','tgl_masuk':'2024-09-18','tgl_selesai':None}]
    b=client.post('/predict',json=payload).json();assert b['queue_at_entry']==2
    del payload['history']
    after=client.post('/predict',json=payload).json()
    assert after['queue_at_entry']==baseline['queue_at_entry']==1

def test_empty_history_is_zero(client,payload):
    payload['history']=[]
    assert client.post('/predict',json=payload).json()['queue_at_entry']==0

def test_all_34_predictions_match_t04(client):
    reference=pd.read_csv(ROOT/'data/prediksi_tugas04.csv')
    requests=json.loads((ROOT/'data/requests_test_34.json').read_text())
    probs=[];labels=[]
    for p in requests:
        r=client.post('/predict',json=p);assert r.status_code==200
        probs.append(r.json()['model_score']);labels.append(r.json()['prediction'])
    np.testing.assert_allclose(probs,reference.p_tuned,rtol=0,atol=1e-14)
    np.testing.assert_array_equal(labels,reference.pred_oof)

def test_streamlit_form_and_prediction():
    from streamlit.testing.v1 import AppTest
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    assert not at.exception
    at.button[0].click().run()
    assert not at.exception
    assert at.session_state['result']['model_score']==.1875
    at.slider[0].set_value(.25)
    at.button[0].click().run()
    assert at.session_state['result']['threshold_used']==.25
    assert at.session_state['result']['prediction']==0
