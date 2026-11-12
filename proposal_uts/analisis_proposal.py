#!/usr/bin/env python3
"""Analisis pendukung Proposal UTS Kelompok 02.

Menghasilkan angka dan gambar yang dipakai di Bab III proposal:
- statistik deskriptif fitur,
- matriks korelasi dan distribusi kelas,
- perbandingan model baseline vs ensemble (default parameters),
- sensitivitas ambang batas pada data uji,
- diagram CRISP-DM.

Seluruh angka berasal dari dataset Tugas 05/06 yang sama (169 berkas) dan
pembagian train/test yang sama (seed 42).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (GradientBoostingClassifier,
                              HistGradientBoostingClassifier,
                              RandomForestClassifier)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score,
                             confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import (StratifiedKFold, cross_validate,
                                     train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

BASE = Path(__file__).resolve().parent
PROYEK = BASE.parent
HASIL = BASE / 'hasil'
GAMBAR = BASE / 'gambar'
for p in (HASIL, GAMBAR):
    p.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PROYEK / 'eksperimen_tugas_06'))
from fitur_notaris import CAT, FEATURES, NUM, FiturNotaris  # noqa: E402

SEED = 42
DATA = PROYEK / 'data' / 'berkas_notaris_terisi (2).csv'
BIRU = '#245a81'
MERAH = '#bd493f'
ABU = '#697684'
HIJAU = '#2f7d5c'
ORANGE = '#c47a24'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.titleweight': 'bold',
    'axes.labelsize': 9,
    'figure.dpi': 200,
})


def metrik(y, p, t):
    pred = (np.asarray(p) >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        'threshold': float(t), 'tp': int(tp), 'tn': int(tn),
        'fp': int(fp), 'fn': int(fn),
        'accuracy': float(accuracy_score(y, pred)),
        'precision': float(precision_score(y, pred, zero_division=0)),
        'recall': float(recall_score(y, pred, zero_division=0)),
        'f1': float(f1_score(y, pred, zero_division=0)),
        'macro_f1': float(f1_score(y, pred, average='macro', zero_division=0)),
        'roc_auc': float(roc_auc_score(y, p)),
        'average_precision': float(average_precision_score(y, p)),
        'alarm': int(pred.sum()),
        'alert_rate': float(pred.mean()),
    }


def siapkan_data():
    raw = pd.read_csv(DATA)
    masuk = pd.to_datetime(raw['tgl_masuk'])
    selesai = pd.to_datetime(raw['tgl_selesai'])
    raw['durasi_hari'] = (selesai - masuk).dt.days
    raw['terlambat'] = (raw['durasi_hari'] > raw['sla_hari']).astype(int)
    y = raw['terlambat'].to_numpy()
    X = raw.drop(columns=['terlambat'])
    return raw, X, y


def prep_numerik():
    return ColumnTransformer([
        ('num', Pipeline([
            ('impute', SimpleImputer(strategy='median')),
            ('scale', StandardScaler()),
        ]), NUM),
        ('cat', Pipeline([
            ('impute', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore',
                                     sparse_output=False)),
        ]), CAT),
    ], remainder='drop')


def prep_pohon():
    return ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), NUM),
        ('cat', Pipeline([
            ('impute', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore',
                                     sparse_output=False)),
        ]), CAT),
    ], remainder='drop')


def evaluasi_model(nama, model, prep, X_train, X_test, y_train, y_test, cv):
    pipe = Pipeline([('fitur', FiturNotaris()), ('prep', prep),
                     ('model', model)])
    skor = cross_validate(pipe, X_train, y_train, cv=cv,
                          scoring=['f1_macro', 'roc_auc', 'average_precision'],
                          n_jobs=1)
    pipe.fit(X_train, y_train)
    p = pipe.predict_proba(X_test)[:, 1]
    m = metrik(y_test, p, 0.50)
    return {
        'model': nama,
        'cv_macro_f1': float(np.mean(skor['test_f1_macro'])),
        'cv_macro_f1_std': float(np.std(skor['test_f1_macro'])),
        'cv_roc_auc': float(np.mean(skor['test_roc_auc'])),
        'cv_pr_auc': float(np.mean(skor['test_average_precision'])),
        'test': m,
        'probabilitas_test': p.tolist(),
    }


def gambar_eda(raw):
    fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.5),
                           gridspec_kw={'width_ratios': [1, 1.35]})
    kelas = raw['terlambat'].value_counts().sort_index()
    batang = ax[0].bar(['Tepat waktu\n(0)', 'Terlambat\n(1)'], kelas.values,
                       color=[BIRU, MERAH], width=0.55)
    for b, v in zip(batang, kelas.values):
        ax[0].text(b.get_x() + b.get_width() / 2, v + 2, f'{v}',
                   ha='center', fontweight='bold')
        ax[0].text(b.get_x() + b.get_width() / 2, v / 2,
                   f'{v / len(raw) * 100:.1f}%', ha='center',
                   color='white', fontweight='bold')
    ax[0].set_ylim(0, 165)
    ax[0].set_ylabel('Jumlah berkas')
    ax[0].set_title('(a) Distribusi kelas target')
    ax[0].spines[['top', 'right']].set_visible(False)
    ax[0].grid(axis='y', alpha=0.2)
    ax[0].set_axisbelow(True)

    kolom = ['jumlah_penghadap', 'sla_hari', 'durasi_hari', 'bulan_akta',
             'antrean_berjalan', 'terlambat']
    kerja = pd.DataFrame({
        'jumlah_penghadap': raw['jumlah_penghadap'],
        'sla_hari': raw['sla_hari'],
        'durasi_hari': raw['durasi_hari'],
        'bulan_akta': pd.to_datetime(raw['tgl_masuk']).dt.month,
        'antrean_berjalan': 0,
        'terlambat': raw['terlambat'],
    })
    masuk = pd.to_datetime(raw['tgl_masuk']).to_numpy()
    selesai = pd.to_datetime(raw['tgl_selesai']).to_numpy()
    kerja['antrean_berjalan'] = [
        int(((masuk < t) & (selesai >= t)).sum()) for t in masuk
    ]
    kor = kerja[kolom].corr()
    im = ax[1].imshow(kor, cmap='RdBu_r', vmin=-1, vmax=1)
    ax[1].set_xticks(range(len(kolom)))
    ax[1].set_xticklabels(['Penghadap', 'SLA', 'Durasi', 'Bulan',
                           'Antrean', 'Terlambat'], rotation=35, ha='right')
    ax[1].set_yticks(range(len(kolom)))
    ax[1].set_yticklabels(['Penghadap', 'SLA', 'Durasi', 'Bulan',
                           'Antrean', 'Terlambat'])
    for i in range(len(kolom)):
        for j in range(len(kolom)):
            v = kor.iloc[i, j]
            ax[1].text(j, i, f'{v:.2f}', ha='center', va='center',
                       fontsize=7.5,
                       color='white' if abs(v) > 0.55 else '#222222')
    ax[1].set_title('(b) Korelasi Pearson antarfitur numerik')
    fig.colorbar(im, ax=ax[1], fraction=0.046, pad=0.04, label='Koefisien r')
    fig.tight_layout()
    fig.savefig(GAMBAR / 'gambar_3_2_eda.png', bbox_inches='tight',
                facecolor='white')
    plt.close(fig)
    return kor.round(3).to_dict()


def gambar_crispdm():
    fig, ax = plt.subplots(figsize=(9.4, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.4)
    ax.axis('off')
    tahap = [
        ('1. Business\nUnderstanding', 'Konteks kantor\nnotaris & PPAT', BIRU),
        ('2. Data\nUnderstanding', 'Audit 169 berkas,\nEDA, label SLA', '#3d6f8e'),
        ('3. Data\nPreparation', 'Fitur antrean, RUPS,\nsiklus bulan, encoding', '#5d8aa8'),
        ('4. Modeling', 'Baseline vs ensemble,\nOptuna TPE 30 trial', HIJAU),
        ('5. Evaluation', 'OOF threshold,\nROC/PR, uji terkunci', ORANGE),
        ('6. Deployment', 'Streamlit, .joblib,\nmonitoring drift', MERAH),
    ]
    lebar, tinggi, jarak = 1.46, 1.05, 0.10
    x0, y0 = 0.35, 2.35
    for i, (judul, isi, warna) in enumerate(tahap):
        x = x0 + i * (lebar + jarak)
        kotak = FancyBboxPatch((x, y0), lebar, tinggi,
                               boxstyle='round,pad=0.03,rounding_size=0.12',
                               linewidth=1.1, edgecolor=warna,
                               facecolor=warna + '14')
        ax.add_patch(kotak)
        ax.text(x + lebar / 2, y0 + tinggi - 0.22, judul, ha='center',
                va='center', fontsize=8.2, fontweight='bold', color=warna)
        ax.text(x + lebar / 2, y0 + 0.33, isi, ha='center', va='center',
                fontsize=6.2, color='#333333')
        if i < len(tahap) - 1:
            ax.add_patch(FancyArrowPatch(
                (x + lebar, y0 + tinggi / 2),
                (x + lebar + jarak, y0 + tinggi / 2),
                arrowstyle='-|>', mutation_scale=9, linewidth=1.0,
                color=ABU))
    # panah melengkung evaluasi -> modeling
    ax.add_patch(FancyArrowPatch((7.9, y0), (5.1, y0),
                                 connectionstyle='arc3,rad=-0.28',
                                 arrowstyle='-|>', mutation_scale=10,
                                 linewidth=1.1, color=ORANGE, linestyle='--'))
    ax.text(6.5, 1.05, 'Iterasi perbaikan model\n(bila metrik belum stabil)',
            ha='center', fontsize=7.4, color=ORANGE, style='italic')
    ax.text(5.0, 4.65, 'Kerangka CRISP-DM Penelitian Kelompok 02',
            ha='center', fontsize=10.5, fontweight='bold', color='#1f2933')
    ax.text(5.0, 4.28, 'Kantor Notaris & PPAT Aries Buwana — 169 berkas, '
            'target keterlambatan akta', ha='center', fontsize=8,
            color=ABU)
    ax.text(0.35, 0.35, 'Batas evaluasi: threshold dipilih dari OOF train; '
            'data uji 34 berkas hanya dipakai sekali untuk laporan akhir.',
            fontsize=7.2, color=ABU, style='italic')
    fig.savefig(GAMBAR / 'gambar_3_1_crispdm.png', bbox_inches='tight',
                facecolor='white')
    plt.close(fig)


def main():
    raw, X, y = siapkan_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=SEED)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    model_def = [
        ('Logistic Regression (Baseline)', LogisticRegression(
            max_iter=2000, random_state=SEED), prep_numerik()),
        ('Decision Tree (Baseline)', DecisionTreeClassifier(
            random_state=SEED), prep_pohon()),
        ('Random Forest (Ensemble)', RandomForestClassifier(
            n_estimators=300, random_state=SEED, n_jobs=-1), prep_pohon()),
        ('Gradient Boosting (Ensemble)', GradientBoostingClassifier(
            random_state=SEED), prep_pohon()),
        ('Histogram Gradient Boosting (Ensemble)',
         HistGradientBoostingClassifier(random_state=SEED), prep_pohon()),
    ]
    hasil_model = []
    for nama, model, prep in model_def:
        hasil_model.append(evaluasi_model(
            nama, model, prep, X_train, X_test, y_train, y_test, cv))
        print(f"{nama}: CV macro F1 {hasil_model[-1]['cv_macro_f1']:.4f} | "
              f"test macro F1 {hasil_model[-1]['test']['macro_f1']:.4f}")

    tuned = pd.read_csv(PROYEK / 'eksperimen_tugas_06/hasil/data/'
                        'prediksi_test_34.csv')
    p_tuned = tuned['p_tuned'].to_numpy()
    y_test_urut = tuned['aktual'].to_numpy()
    ambang = [0.50, 0.40, 0.35, 0.30, 0.25, 0.19, 0.05]
    tabel_ambang = [metrik(y_test_urut, p_tuned, t) for t in ambang]

    kor = gambar_eda(raw)
    gambar_crispdm()

    fitur = []
    for kol in ['jumlah_penghadap', 'sla_hari', 'durasi_hari']:
        fitur.append({
            'nama': kol, 'tipe': 'Numerik (integer)',
            'min': float(raw[kol].min()), 'max': float(raw[kol].max()),
            'mean': float(raw[kol].mean()),
            'median': float(raw[kol].median()),
        })
    for kol in ['kategori_akta', 'hari_masuk']:
        if kol == 'kategori_akta':
            fitur.append({'nama': kol, 'tipe': 'Kategorikal (nominal)',
                          'n_unik': int(raw[kol].nunique()),
                          'modus': raw[kol].mode().iloc[0]})
        else:
            hari = pd.to_datetime(raw['tgl_masuk']).dt.day_name()
            fitur.append({'nama': 'hari_masuk', 'tipe': 'Kategorikal (nominal)',
                          'n_unik': int(hari.nunique()),
                          'modus': hari.mode().iloc[0]})

    ringkas = {
        'dataset': {
            'n': int(len(raw)), 'positif': int(y.sum()),
            'proporsi_positif': float(y.mean()),
            'n_train': int(len(X_train)), 'n_test': int(len(X_test)),
            'positif_train': int(y_train.sum()),
            'positif_test': int(y_test.sum()),
            'durasi_min': int(raw['durasi_hari'].min()),
            'durasi_max': int(raw['durasi_hari'].max()),
            'durasi_mean': float(raw['durasi_hari'].mean()),
            'sla_min': int(raw['sla_hari'].min()),
            'sla_max': int(raw['sla_hari'].max()),
            'kategori_unik': int(raw['kategori_akta'].nunique()),
            'penghadap_mean': float(raw['jumlah_penghadap'].mean()),
            'korelasi': kor,
        },
        'model_baseline': [
            {k: v for k, v in m.items() if k != 'probabilitas_test'}
            for m in hasil_model
        ],
        'ambang_test': tabel_ambang,
    }
    (HASIL / 'analisis_proposal.json').write_text(
        json.dumps(ringkas, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Selesai. Hasil:', HASIL / 'analisis_proposal.json')


if __name__ == '__main__':
    main()
