"""Objek inferensi yang menyimpan pipeline, ambang, dan background SHAP."""
from __future__ import annotations
from copy import copy,deepcopy
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

@dataclass
class NotarisRiskModel:
    pipeline:Pipeline
    threshold:float
    background:np.ndarray
    feature_names:list
    reference_info:dict

    def working_pipeline(self,history=None):
        if history is None:return self.pipeline
        # Fitur histori terpisah untuk tiap request; estimator dan encoder tidak di-fit.
        transformer=deepcopy(self.pipeline.named_steps['fitur'])
        transformer.set_history(history)
        return Pipeline([('fitur',transformer),('prep',self.pipeline.named_steps['prep']),
                         ('model',self.pipeline.named_steps['model'])])

    def predict_proba(self,raw,history=None):
        return self.working_pipeline(history).predict_proba(raw)

    def predict(self,raw,threshold=None,history=None):
        t=self.threshold if threshold is None else float(threshold)
        if not np.isfinite(t) or not .01<=t<=.99:raise ValueError('Ambang harus 0,01 sampai 0,99.')
        return (self.predict_proba(raw,history)[:,1]>=t).astype(int)
