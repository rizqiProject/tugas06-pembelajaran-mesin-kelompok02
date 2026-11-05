#!/usr/bin/env python3
"""Menyusun laporan Tugas 06 dari hasil eksperimen yang benar-benar dijalankan."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
EKS = BASE / 'eksperimen_tugas_06' / 'hasil'
FIG = EKS / 'grafik'
TEMPLATE = BASE / 'referensi' / 'Template_Tugas_06_Pembelajaran_Mesin.docx'

sys.path.insert(0, str(OUT))
from laporan_lib import Laporan  # noqa: E402


def baca_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    D = {
        'ringkas': baca_json(EKS / 'data/ringkasan_eksekusi.json'),
        'met': baca_json(EKS / 'data/metrik_test_terpilih.json'),
        'rep': baca_json(EKS / 'data/classification_report_test_tuned.json'),
        'rep_base': baca_json(EKS / 'data/classification_report_test_baseline.json'),
        'th_test': pd.read_csv(EKS / 'data/threshold_test_tuned.csv'),
        'th_oof': pd.read_csv(EKS / 'data/threshold_oof_tuned.csv'),
        'ba': pd.read_csv(EKS / 'data/perbandingan_before_after_test.csv'),
        'cv': baca_json(EKS / 'data/cv_before_after.json'),
        'opt': baca_json(EKS / 'optuna/informasi_study.json'),
        'trials': pd.read_csv(EKS / 'optuna/riwayat_trial.csv'),
        'fp': pd.read_csv(EKS / 'data/analisis_false_positive.csv'),
        'fn': pd.read_csv(EKS / 'data/analisis_false_negative.csv'),
        'naif': pd.read_csv(EKS / 'data/baseline_naif_test.csv'),
        'boot': baca_json(EKS / 'data/bootstrap_interval_tuned.json'),
        'hist': baca_json(EKS / 'data/validasi_historis_tugas05.json'),
        'audit': baca_json(EKS / 'data/audit_dataset.json'),
        'split': baca_json(EKS / 'data/ringkasan_split.json'),
        'sel': baca_json(EKS / 'data/threshold_terpilih.json'),
        'fig': FIG,
        'out': OUT,
    }

    lap = Laporan(TEMPLATE)

    from bagian_a_b import tulis as tulis_ab
    from bagian_c_d import tulis as tulis_cd
    from bagian_e import tulis as tulis_e
    from bagian_f_lampiran import tulis as tulis_f

    tulis_ab(lap, D)
    tulis_cd(lap, D)
    tulis_e(lap, D)
    tulis_f(lap, D)

    tujuan = OUT / 'TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.docx'
    lap.simpan(tujuan)
    print('DOCX:', tujuan)


if __name__ == '__main__':
    main()
