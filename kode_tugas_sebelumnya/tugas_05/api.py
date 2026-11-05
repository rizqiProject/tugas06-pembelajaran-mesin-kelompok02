from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from schemas import PredictRequest
from service import InferenceService

@asynccontextmanager
async def lifespan(app):
    app.state.service=InferenceService()
    yield

app=FastAPI(title='Inferensi Berkas Notaris dan PPAT',version='1.0.0',lifespan=lifespan,
            description='Prototipe penelitian. Skor belum dikalibrasi; keputusan layanan tetap melalui staf.')

@app.exception_handler(RequestValidationError)
async def validation_error(request:Request,exc:RequestValidationError):
    # Pesan terstruktur tanpa stack trace maupun nilai masukan sensitif.
    errors=[{'field':'.'.join(str(p) for p in e['loc']),'message':e['msg'],'type':e['type']} for e in exc.errors()]
    return JSONResponse(status_code=422,content={'detail':errors,'message':'Masukan perlu diperbaiki.'})

@app.get('/health')
def health():return {'status':'ok','model_version':app.state.service.metadata['model_version']}

@app.post('/predict')
def predict(body:PredictRequest):return app.state.service.predict(body)
