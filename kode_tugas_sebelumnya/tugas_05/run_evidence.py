"""Jalankan server dan klien pengujian dalam proses kerja yang sama."""
from pathlib import Path
import json,os,subprocess,sys,time
import httpx
ROOT=Path(__file__).resolve().parent

def main(browser_pythonpath=None,reuse_evaluation=False):
    logs=[];processes=[]
    try:
        commands=[('api_server.log',[sys.executable,'-m','uvicorn','api:app','--host','127.0.0.1','--port','8005']),
                  ('streamlit_server.log',[sys.executable,'-m','streamlit','run','app.py','--server.address','127.0.0.1','--server.port','8505','--global.developmentMode','false'])]
        for name,cmd in commands:
            f=(ROOT/'evidence'/name).open('w');logs.append(f)
            processes.append(subprocess.Popen(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,env=os.environ.copy()))
        with httpx.Client(timeout=2,trust_env=False) as client:
            for url in ['http://127.0.0.1:8005/health','http://127.0.0.1:8505/_stcore/health']:
                for _ in range(100):
                    try:
                        if client.get(url).status_code==200:break
                    except httpx.HTTPError:pass
                    if any(p.poll() is not None for p in processes):raise RuntimeError('Server berhenti; periksa log.')
                    time.sleep(.2)
                else:raise RuntimeError('Server tidak siap dalam batas waktu.')
        if reuse_evaluation:
            scenarios=json.loads((ROOT/'evidence/scenarios.json').read_text())
            scenarios[2]['request']['record']['tgl_masuk']='2024-09-17'
            with httpx.Client(timeout=10,trust_env=False) as c:
                for q in scenarios:
                    response=c.post('http://127.0.0.1:8005/predict',json=q['request']);response.raise_for_status()
                    q['http_status']=response.status_code;q['response']=response.json()
            assert scenarios[2]['response']['model_score']==scenarios[2]['request']['threshold']
            (ROOT/'evidence/scenarios.json').write_text(json.dumps(scenarios,indent=2,ensure_ascii=False))
        else:
            with (ROOT/'evidence/evaluation_execution.log').open('w') as f:
                subprocess.run([sys.executable,'evaluate.py'],cwd=ROOT,check=True,stdout=f,stderr=subprocess.STDOUT)
        print('Evaluasi HTTP dan benchmark selesai.',flush=True)
        env=os.environ.copy()
        if browser_pythonpath:env['PYTHONPATH']=browser_pythonpath
        with (ROOT/'evidence/ui_capture_execution.log').open('w') as f:
            subprocess.run([sys.executable,'capture_ui.py'],cwd=ROOT,check=True,stdout=f,stderr=subprocess.STDOUT,env=env)
        print('Tangkapan layar aplikasi selesai.',flush=True)
        fixture=json.loads((ROOT/'tests/fixtures/BRK_0024.json').read_text())
        fixture['record']['jumlah_penghadap']='dua'
        (ROOT/'tests/fixtures/invalid_numeric.json').write_text(json.dumps(fixture,indent=2))
        for stem,file in [('valid','BRK_0024.json'),('invalid','invalid_numeric.json')]:
            cmd=['curl','--noproxy','*','--silent','--show-error','--dump-header',f'evidence/curl_{stem}_headers.txt',
                 '--request','POST','http://127.0.0.1:8005/predict','--header','Content-Type: application/json',
                 '--data-binary',f'@tests/fixtures/{file}','--output',f'evidence/curl_{stem}_response.json']
            subprocess.run(cmd,cwd=ROOT,check=True)
        print('cURL 200 dan 422 tersimpan.',flush=True)
    finally:
        for p in processes:
            p.terminate()
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        for f in logs:f.close()

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--browser-pythonpath');p.add_argument('--reuse-evaluation',action='store_true')
    args=p.parse_args();main(args.browser_pythonpath,args.reuse_evaluation)
