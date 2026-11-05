"""Kontrak masukan untuk form dan endpoint yang sama."""
from datetime import date
from typing import Annotated
import math
from pydantic import BaseModel,ConfigDict,Field,StrictInt,field_validator,model_validator

class ItemSchema(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    id_berkas:str=Field(min_length=1,max_length=64,pattern=r'^[A-Za-z0-9_-]+$')
    tgl_masuk:date
    kategori_akta:str=Field(min_length=1,max_length=80)
    jumlah_penghadap:Annotated[StrictInt,Field(ge=1,le=100)]
    sla_hari:Annotated[StrictInt,Field(ge=1,le=365)]
    tgl_rups:date|None=None

    @field_validator('kategori_akta')
    @classmethod
    def clean_category(cls,v):
        v=v.strip()
        if not v:raise ValueError('Kategori tidak boleh kosong.')
        return v

    @field_validator('tgl_masuk','tgl_rups',mode='before')
    @classmethod
    def date_only(cls,v):
        if v is None:return None
        if isinstance(v,date):return v
        if not isinstance(v,str):raise ValueError('Tanggal harus teks YYYY-MM-DD.')
        return date.fromisoformat(v)

    @field_validator('tgl_masuk','tgl_rups')
    @classmethod
    def year_range(cls,v):
        if v is not None and not 2000<=v.year<=2100:raise ValueError('Tahun di luar batas teknis prototipe 2000-2100.')
        return v

class HistoryItem(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id_berkas:str=Field(min_length=1,max_length=64,pattern=r'^[A-Za-z0-9_-]+$')
    tgl_masuk:date
    tgl_selesai:date|None=None

    @model_validator(mode='after')
    def dates_valid(self):
        if self.tgl_selesai is not None and self.tgl_selesai<self.tgl_masuk:
            raise ValueError('Tanggal selesai histori tidak boleh mendahului tanggal masuk.')
        return self

class PredictRequest(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    record:ItemSchema
    threshold:Annotated[float,Field(strict=True,ge=.01,le=.99)]|None=None
    history:list[HistoryItem]|None=Field(default=None,max_length=5000)
    explain:bool=True

    @model_validator(mode='after')
    def unique_history(self):
        if self.history is not None:
            ids=[r.id_berkas for r in self.history]
            if len(ids)!=len(set(ids)):raise ValueError('ID pada histori tidak boleh ganda.')
        return self
