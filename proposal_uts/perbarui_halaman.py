#!/usr/bin/env python3
"""Menghitung nomor halaman setiap judul dari PDF proposal.

Hasil disimpan ke halaman.json. Skrip penyusun proposal membaca berkas ini
pada proses build berikutnya, sehingga daftar isi konsisten dengan PDF.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pypdf

BASE = Path(__file__).resolve().parent
PDF = BASE / 'PROPOSAL_UTS_ML_KELOMPOK_02_NOTARIS_PPAT.pdf'

PETA = {
    'LEMBAR PERSETUJUAN DOSEN PENGAMPU': 'LEMBAR PERSETUJUAN PROPOSAL RISET',
    'LEMBAR KOMITMEN INTEGRITAS AKADEMIK': 'LEMBAR KOMITMEN INTEGRITAS AKADEMIK',
    'DAFTAR ISI': 'DAFTAR ISI',
    'BAB I  PENDAHULUAN': 'BAB I PENDAHULUAN',
    '   1.1 Latar Belakang Masalah Riil & Domain Konteks':
        '1.1 Latar Belakang Masalah Riil',
    '   1.2 Identifikasi Masalah & Problem Statement ML':
        '1.2 Identifikasi Masalah',
    '   1.3 Perumusan Masalah (Research Questions)': '1.3 Perumusan Masalah',
    '   1.4 Tujuan Penelitian & Rekayasa Model': '1.4 Tujuan Penelitian',
    '   1.5 Manfaat Penelitian (Teoretis dan Terapan)': '1.5 Manfaat Penelitian',
    '   1.6 Ruang Lingkup & Batasan Masalah': '1.6 Ruang Lingkup',
    'BAB II  TINJAUAN PUSTAKA & LANDASAN TEORETIS': 'BAB II TINJAUAN PUSTAKA',
    '   2.1 Kajian Riset Terkait (State-of-the-Art)': '2.1 Kajian Riset Terkait',
    '   2.2 Paradigma Pembelajaran Mesin & Pemilihan Model':
        '2.2 Paradigma Pembelajaran Mesin',
    '   2.3 Teori Pra-Pemrosesan & Rekayasa Fitur': '2.3 Teori Pra-Pemrosesan',
    '   2.4 Metrik Evaluasi Kinerja & Ambang Batas Klasifikasi':
        '2.4 Metrik Evaluasi Kinerja',
    '   2.5 Landasan Teori Optimasi Bayesian (Optuna TPE)':
        '2.5 Landasan Teori Optimasi',
    'BAB III  METODOLOGI PENELITIAN & PIPELINE REKAYASA MODEL ML':
        'BAB III METODOLOGI PENELITIAN',
    '   3.1 Kerangka Kerja Metodologi (CRISP-DM)': '3.1 Kerangka Kerja Metodologi',
    '   3.2 Karakteristik & Pemahaman Dataset': '3.2 Karakteristik & Pemahaman Dataset',
    '   3.3 Exploratory Data Analysis (EDA) & Temuan Utama':
        '3.3 Exploratory Data Analysis',
    '   3.4 Pipeline Pra-Pemrosesan Data Bebas Kebocoran Data':
        '3.4 Pipeline Pra-Pemrosesan',
    '   3.5 Skema Eksperimen & Validasi Silang (Stratified 5-Fold CV)':
        '3.5 Skema Eksperimen',
    '   3.6 Perbandingan Model Baseline vs Ensemble':
        '3.6 Perbandingan Model Baseline',
    '   3.7 Optimasi Hiperparameter dengan Optuna (TPE)':
        '3.7 Optimasi Hiperparameter',
    '   3.8 Kalibrasi Ambang Batas (Decision Threshold Tuning)':
        '3.8 Kalibrasi Ambang Batas',
    '   3.9 Cetak Biru Deployment Menuju UAS': '3.9 Cetak Biru Deployment',
    'DAFTAR PUSTAKA': 'DAFTAR PUSTAKA',
    'LAMPIRAN-LAMPIRAN': 'LAMPIRAN-LAMPIRAN',
}


def main():
    r = pypdf.PdfReader(PDF)
    teks = [re.sub(r'\s+', ' ', (p.extract_text() or '')) for p in r.pages]
    toc = None
    for i, t in enumerate(teks, 1):
        if 'DAFTAR ISI' in t and 'BAB I PENDAHULUAN' in t:
            toc = i
            break
    hasil = {}
    for label, frasa in PETA.items():
        frasa = re.sub(r'\s+', ' ', frasa)
        if label == 'DAFTAR ISI':
            hasil[label] = toc
            continue
        hasil[label] = None
        for i, t in enumerate(teks, 1):
            if i == toc:
                continue
            if frasa in t:
                hasil[label] = i
                break
    (BASE / 'halaman.json').write_text(
        json.dumps(hasil, ensure_ascii=False, indent=1), encoding='utf-8')
    kosong = [k for k, v in hasil.items() if not v]
    print(f'TOC halaman {toc}; {len(hasil)} entri; kosong: {kosong}')
    for k, v in hasil.items():
        print(f'{v}\t{k.strip()}')


if __name__ == '__main__':
    main()
