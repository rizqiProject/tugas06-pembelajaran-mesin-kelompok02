#!/usr/bin/env python3
"""Eksperimen Tugas 06 Kelompok 02 - Kantor Notaris & PPAT Aries Buwana.

Alur:
1. Memuat dan mengaudit dataset 169 berkas.
2. Memvalidasi ulang pembagian 135 train / 34 test dan hasil historis Tugas 05.
3. Menjalankan Optuna (TPE) + Stratified 5-Fold CV pada train.
4. Membandingkan model before tuning dan after tuning.
5. Membuat prediksi OOF train, memilih threshold dari OOF, lalu mengunci
   threshold sebelum mengevaluasi test.
6. Menyimpan seluruh tabel, gambar, model, dan log bukti eksekusi.

Jalankan dari folder eksperimen_tugas_06:
    ../.venv/bin/python eksperimen_tugas06.py --trials 30
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import platform
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings('ignore')

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, average_precision_score,
                             classification_report, confusion_matrix,
                             f1_score, fbeta_score, log_loss,
                             precision_recall_curve, precision_score,
                             recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import (StratifiedKFold, cross_val_predict,
                                     cross_validate, train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

import optuna
from optuna.samplers import TPESampler

from fitur_notaris import CAT, FEATURES, NUM, FiturNotaris

SEED = 42
BASE = Path(__file__).resolve().parent
HASIL = BASE / 'hasil'
GRAFIK = HASIL / 'grafik'
OPTUNA_DIR = HASIL / 'optuna'
MODEL_DIR = HASIL / 'model'
LOG_DIR = HASIL / 'log'
DATA = BASE.parent / 'data' / 'berkas_notaris_terisi (2).csv'
HISTORIS = BASE.parent / 'kode_tugas_sebelumnya' / 'tugas_05' / 'artifacts' / 'model_final.joblib'

# Parameter Tugas 04/05 yang dijadikan pembanding "before tuning".
BASELINE_PARAMS = {
    'max_depth': 4,
    'min_samples_leaf': 15,
    'min_samples_split': 2,
    'ccp_alpha': 0.0,
    'class_weight': None,
}

BLUE = '#245a81'
RED = '#bd493f'
GRAY = '#697684'
GREEN = '#2f7d5c'
ORANGE = '#c47a24'


def siapkan_folder():
    for p in (HASIL, HASIL / 'data', GRAFIK, OPTUNA_DIR, MODEL_DIR, LOG_DIR):
        p.mkdir(parents=True, exist_ok=True)


def siapkan_log():
    logger = logging.getLogger('tugas06')
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    fh = logging.FileHandler(LOG_DIR / 'eksekusi.log', mode='w', encoding='utf-8')
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def tulis_json(nama, obj):
    def default(x):
        if hasattr(x, 'item'):
            return x.item()
        if isinstance(x, (np.ndarray,)):
            return x.tolist()
        return str(x)
    (HASIL / nama).write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, default=default),
        encoding='utf-8')


def hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def muat_data(logger):
    raw = pd.read_csv(DATA)
    logger.info('Dataset dimuat: %s baris, %s kolom', len(raw), raw.shape[1])
    if len(raw) != 169:
        raise ValueError(f'Dataset harus 169 baris, ditemukan {len(raw)}')
    if raw['id_berkas'].duplicated().any():
        raise ValueError('Terdapat id_berkas duplikat')

    masuk = pd.to_datetime(raw['tgl_masuk'], errors='raise')
    selesai = pd.to_datetime(raw['tgl_selesai'], errors='raise')
    durasi = (selesai - masuk).dt.days
    y = (durasi > raw['sla_hari']).astype(int)
    raw = raw.copy()
    raw['durasi_hari'] = durasi
    raw['terlambat'] = y

    audit = {
        'file': str(DATA),
        'sha256': hash_file(DATA),
        'n_baris': int(len(raw)),
        'n_kolom': int(raw.shape[1]),
        'positif_terlambat': int(y.sum()),
        'negatif_tepat_waktu': int((1 - y).sum()),
        'proporsi_positif': float(y.mean()),
        'duplikat_id': int(raw['id_berkas'].duplicated().sum()),
        'tanggal_rups_terisi': int(raw['tgl_rups'].notna().sum()),
        'tanggal_rups_setelah_masuk': int(
            (pd.to_datetime(raw['tgl_rups'], errors='coerce') > masuk).sum()),
        'durasi_min': int(durasi.min()),
        'durasi_maks': int(durasi.max()),
        'sla_min': int(raw['sla_hari'].min()),
        'sla_maks': int(raw['sla_hari'].max()),
        'kategori_akta': sorted(raw['kategori_akta'].unique().tolist()),
        'rumus_label': 'terlambat = 1 jika (tgl_selesai - tgl_masuk) hari > sla_hari',
    }
    tulis_json('data/audit_dataset.json', audit)
    logger.info('Label: %s terlambat, %s tepat waktu', audit['positif_terlambat'],
                audit['negatif_tepat_waktu'])
    return raw, y


def buat_pipeline(params):
    prep = ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), NUM),
        ('cat', Pipeline([
            ('impute', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
        ]), CAT),
    ], remainder='drop', verbose_feature_names_out=False)
    model = DecisionTreeClassifier(random_state=SEED, **params)
    return Pipeline([('fitur', FiturNotaris()), ('prep', prep), ('model', model)])


def metrik(y, p, threshold):
    y = np.asarray(y).astype(int)
    pred = (np.asarray(p) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        'n': int(len(y)),
        'positif': int(y.sum()),
        'threshold': float(threshold),
        'tp': int(tp), 'tn': int(tn), 'fp': int(fp), 'fn': int(fn),
        'accuracy': float(accuracy_score(y, pred)),
        'precision': float(precision_score(y, pred, zero_division=0)),
        'recall': float(recall_score(y, pred, zero_division=0)),
        'f1': float(f1_score(y, pred, zero_division=0)),
        'f2': float(fbeta_score(y, pred, beta=2, zero_division=0)),
        'macro_f1': float(f1_score(y, pred, average='macro', zero_division=0)),
        'weighted_f1': float(f1_score(y, pred, average='weighted', zero_division=0)),
        'roc_auc': float(roc_auc_score(y, p)),
        'average_precision': float(average_precision_score(y, p)),
        'log_loss': float(log_loss(y, np.clip(p, 1e-9, 1 - 1e-9))),
        'alert_rate': float(pred.mean()),
        'alarm': int(pred.sum()),
    }


def tabel_threshold(y, p, low=0.01, high=0.99, step=0.01):
    rows = []
    for t in np.round(np.arange(low, high + 1e-9, step), 2):
        m = metrik(y, p, float(t))
        rows.append({k: m[k] for k in [
            'threshold', 'tp', 'tn', 'fp', 'fn', 'precision', 'recall',
            'f1', 'f2', 'alert_rate', 'alarm']})
    return pd.DataFrame(rows)


def pilih_threshold(tabel, kolom='f2'):
    """Pilih threshold dari OOF train.

    Utama: nilai metrik tertinggi. Seri: precision lebih tinggi, lalu
    threshold lebih besar agar alarm tidak berlebihan.
    """
    urut = tabel.sort_values([kolom, 'precision', 'threshold'],
                             ascending=[False, False, False])
    baris = urut.iloc[0]
    return float(baris['threshold']), baris.to_dict()


def simpan_grafik(path):
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close('all')


def rapikan_sumbu(ax, grid_axis='y'):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis=grid_axis, alpha=0.18)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------
# 1. Validasi historis Tugas 05
# ---------------------------------------------------------------------------
def validasi_historis(X_train, X_test, y_train, y_test, logger):
    hasil = {
        'sumber_artefak': str(HISTORIS),
        'sha256_artefak': hash_file(HISTORIS),
        'catatan': 'Artefak Tugas 05 dimuat hanya untuk memeriksa konsistensi, '
                   'bukan untuk tuning Tugas 06.',
    }
    try:
        # Modul inference/schemas Tugas 05 diperlukan saat unpickle artefak.
        sys.path.insert(0, str(HISTORIS.parents[1]))
        bundle = joblib.load(HISTORIS)
        p = bundle.predict_proba(X_test)[:, 1]
        pred = (p >= 0.11).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()
        hasil.update({
            'status': 'berhasil dimuat',
            'threshold_historis': 0.11,
            'tp': int(tp), 'fn': int(fn), 'fp': int(fp), 'tn': int(tn),
            'precision': float(precision_score(y_test, pred, zero_division=0)),
            'recall': float(recall_score(y_test, pred, zero_division=0)),
            'f1': float(f1_score(y_test, pred, zero_division=0)),
            'cocok_dengan_laporan_tugas05': bool(
                (tp, fn, fp, tn) == (4, 3, 18, 9)),
        })
    except Exception as exc:  # pragma: no cover - dicatat bila artefak gagal
        hasil.update({'status': 'gagal dimuat', 'error': repr(exc)})
    tulis_json('data/validasi_historis_tugas05.json', hasil)
    logger.info('Validasi historis T05: %s', hasil)
    return hasil


# ---------------------------------------------------------------------------
# 2. Optuna
# ---------------------------------------------------------------------------
def jalankan_optuna(X_train, y_train, n_trials, logger):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    def objective(trial):
        params = {
            'criterion': trial.suggest_categorical('criterion', ['gini', 'entropy']),
            'max_depth': trial.suggest_int('max_depth', 2, 10),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 2, 30),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 40),
            'ccp_alpha': trial.suggest_float('ccp_alpha', 0.0, 0.02),
            'class_weight': trial.suggest_categorical(
                'class_weight', ['none', 'balanced']),
            'max_features': trial.suggest_categorical(
                'max_features', ['none', 'sqrt', 'log2']),
        }
        if params['class_weight'] == 'none':
            params['class_weight'] = None
        if params['max_features'] == 'none':
            params['max_features'] = None
        pipe = buat_pipeline(params)
        skor = cross_validate(pipe, X_train, y_train, cv=cv,
                              scoring='f1_macro', n_jobs=1,
                              error_score='raise')['test_score']
        return float(skor.mean())

    sampler = TPESampler(seed=SEED, n_startup_trials=8)
    study = optuna.create_study(direction='maximize', sampler=sampler,
                                study_name='notaris_t06')
    logger.info('Optuna dimulai: %s trials, TPE, Stratified 5-Fold', n_trials)
    mulai = time.time()
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
    durasi = time.time() - mulai

    trials = study.trials_dataframe(attrs=(
        'number', 'state', 'value', 'params', 'duration', 'datetime_start',
        'datetime_complete'))
    trials.to_csv(OPTUNA_DIR / 'riwayat_trial.csv', index=False)

    best = dict(study.best_params)
    if best.get('class_weight') == 'none':
        best['class_weight'] = None
    if best.get('max_features') == 'none':
        best['max_features'] = None

    info = {
        'n_trials': int(n_trials),
        'n_selesai': int(sum(t.state.name == 'COMPLETE' for t in study.trials)),
        'arah': 'maximize',
        'objektif': 'macro F1 (Stratified 5-Fold CV pada train)',
        'sampler': 'TPESampler(seed=42, n_startup_trials=8)',
        'best_value_cv_macro_f1': float(study.best_value),
        'best_trial': int(study.best_trial.number),
        'best_params': best,
        'durasi_detik': float(durasi),
        'seed': SEED,
    }
    tulis_json('optuna/informasi_study.json', info)

    # Riwayat optimasi: nilai per trial dan best-so-far.
    nilai = trials['value'].astype(float).to_numpy()
    nomor = trials['number'].to_numpy()
    best_so_far = np.maximum.accumulate(nilai)
    plt.figure(figsize=(8.6, 4.4))
    plt.scatter(nomor, nilai, s=28, color=BLUE, alpha=0.75,
                label='Macro F1 per trial')
    plt.step(nomor, best_so_far, where='post', color=RED, lw=2,
             label='Nilai terbaik kumulatif')
    plt.axhline(info['best_value_cv_macro_f1'], color=GRAY, ls=':', lw=1)
    plt.xlabel('Nomor trial')
    plt.ylabel('Macro F1 (rata-rata 5-fold)')
    plt.title('Riwayat optimasi Optuna (TPE)')
    plt.legend(fontsize=8)
    rapikan_sumbu(plt.gca())
    simpan_grafik(GRAFIK / '04_optuna_history.png')

    # Kepentingan parameter.
    try:
        importance = optuna.importance.get_param_importances(study)
        imp = pd.DataFrame({'parameter': list(importance.keys()),
                            'importance': list(importance.values())})
        imp.to_csv(OPTUNA_DIR / 'kepentingan_parameter.csv', index=False)
        imp = imp.sort_values('importance')
        plt.figure(figsize=(8.2, 4.2))
        plt.barh(imp['parameter'], imp['importance'], color=BLUE)
        plt.xlabel('Kepentingan relatif')
        plt.title('Kepentingan hiperparameter pada studi Optuna')
        rapikan_sumbu(plt.gca(), 'x')
        simpan_grafik(GRAFIK / '05_optuna_importance.png')
        info['parameter_importance'] = dict(importance)
        tulis_json('optuna/informasi_study.json', info)
    except Exception as exc:
        logger.warning('Kepentingan parameter tidak dapat dihitung: %s', exc)

    logger.info('Optuna selesai dalam %.1f detik. Best CV Macro F1=%.4f',
                durasi, study.best_value)
    logger.info('Best params: %s', best)
    return best, info, trials


# ---------------------------------------------------------------------------
# 3. Cross-validation before vs after
# ---------------------------------------------------------------------------
SKOR_CV = {
    'macro_f1': 'f1_macro',
    'f1_positif': 'f1',
    'precision': 'precision',
    'recall': 'recall',
    'average_precision': 'average_precision',
    'roc_auc': 'roc_auc',
    'log_loss': 'neg_log_loss',
}


def ringkas_cv(pipe, X, y, cv):
    res = cross_validate(pipe, X, y, cv=cv, scoring=SKOR_CV, n_jobs=1,
                         error_score='raise', return_train_score=False)
    out = {}
    for nama in SKOR_CV:
        vals = res[f'test_{nama}']
        if nama == 'log_loss':
            vals = -vals
        out[nama] = {
            'mean': float(np.mean(vals)),
            'std': float(np.std(vals, ddof=1)),
            'per_fold': [float(v) for v in vals],
        }
    return out


# ---------------------------------------------------------------------------
# 4. Evaluasi test dan analisis kesalahan
# ---------------------------------------------------------------------------
def bootstrap_ci(y, p, threshold, n=2000, seed=20261105):
    rng = np.random.default_rng(seed)
    y = np.asarray(y)
    idx_pos = np.flatnonzero(y == 1)
    idx_neg = np.flatnonzero(y == 0)
    nilai = {'f1': [], 'recall': [], 'precision': [], 'f2': [],
             'average_precision': [], 'roc_auc': []}
    for _ in range(n):
        ix = np.concatenate([
            rng.choice(idx_pos, len(idx_pos), replace=True),
            rng.choice(idx_neg, len(idx_neg), replace=True),
        ])
        yy, pp = y[ix], np.asarray(p)[ix]
        pred = (pp >= threshold).astype(int)
        nilai['f1'].append(f1_score(yy, pred, zero_division=0))
        nilai['recall'].append(recall_score(yy, pred, zero_division=0))
        nilai['precision'].append(precision_score(yy, pred, zero_division=0))
        nilai['f2'].append(fbeta_score(yy, pred, beta=2, zero_division=0))
        nilai['average_precision'].append(average_precision_score(yy, pp))
        nilai['roc_auc'].append(roc_auc_score(yy, pp))
    return {k: {'mean': float(np.mean(v)),
                'low': float(np.quantile(v, 0.025)),
                'high': float(np.quantile(v, 0.975))}
            for k, v in nilai.items()}


def tabel_prediksi_test(raw, X_test, y_test, p_base, p_tuned, t_base, t_tuned):
    df = X_test[['id_berkas', 'tgl_masuk', 'tgl_selesai', 'kategori_akta',
                 'jumlah_penghadap', 'sla_hari']].copy()
    df['durasi_hari'] = raw.loc[X_test.index, 'durasi_hari'].to_numpy()
    df['aktual'] = np.asarray(y_test)
    df['p_baseline'] = np.asarray(p_base)
    df['p_tuned'] = np.asarray(p_tuned)
    df['pred_baseline_050'] = (df['p_baseline'] >= 0.5).astype(int)
    df['pred_tuned_050'] = (df['p_tuned'] >= 0.5).astype(int)
    df['pred_baseline_oof'] = (df['p_baseline'] >= t_base).astype(int)
    df['pred_tuned_oof'] = (df['p_tuned'] >= t_tuned).astype(int)
    df['selisih_hari'] = df['durasi_hari'] - df['sla_hari']
    df['jenis_kesalahan_tuned'] = np.select(
        [(df.aktual == 1) & (df.pred_tuned_oof == 1),
         (df.aktual == 1) & (df.pred_tuned_oof == 0),
         (df.aktual == 0) & (df.pred_tuned_oof == 1)],
        ['TP', 'FN', 'FP'], default='TN')
    df = df.sort_values(['aktual', 'p_tuned'], ascending=[False, False])
    df.to_csv(HASIL / 'data/prediksi_test_34.csv', index=False)
    return df


def analisis_kesalahan(df, logger):
    fp = df[df.jenis_kesalahan_tuned == 'FP'].copy()
    fn = df[df.jenis_kesalahan_tuned == 'FN'].copy()
    fp.to_csv(HASIL / 'data/analisis_false_positive.csv', index=False)
    fn.to_csv(HASIL / 'data/analisis_false_negative.csv', index=False)
    ringkas = {
        'n_fp': int(len(fp)),
        'n_fn': int(len(fn)),
        'fp_ids': fp['id_berkas'].tolist(),
        'fn_ids': fn['id_berkas'].tolist(),
        'fp_skor_min': float(fp['p_tuned'].min()) if len(fp) else None,
        'fp_skor_maks': float(fp['p_tuned'].max()) if len(fp) else None,
        'fn_skor_min': float(fn['p_tuned'].min()) if len(fn) else None,
        'fn_skor_maks': float(fn['p_tuned'].max()) if len(fn) else None,
        'fn_dengan_skor_nol': int((fn['p_tuned'] == 0).sum()),
        'fp_kategori': fp['kategori_akta'].value_counts().to_dict(),
        'fn_kategori': fn['kategori_akta'].value_counts().to_dict(),
    }
    tulis_json('data/ringkasan_analisis_kesalahan.json', ringkas)
    logger.info('Analisis kesalahan: %s FP, %s FN', len(fp), len(fn))
    return fp, fn, ringkas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=30)
    args = parser.parse_args()

    siapkan_folder()
    logger = siapkan_log()
    mulai = datetime.now()
    logger.info('=== EKSPERIMEN TUGAS 06 DIMULAI ===')
    logger.info('Python %s | numpy %s | pandas %s | scikit-learn %s | optuna %s',
                platform.python_version(), np.__version__, pd.__version__,
                sklearn.__version__, optuna.__version__)

    raw, y = muat_data(logger)
    # Kolom target dan turunannya tidak boleh masuk matriks prediktor.
    X = raw.drop(columns=['terlambat', 'durasi_hari'])
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=SEED)
    logger.info('Split: train %s (%s positif), test %s (%s positif)',
                len(y_train), int(y_train.sum()), len(y_test), int(y_test.sum()))

    split = raw[['id_berkas', 'tgl_masuk', 'terlambat']].copy()
    split['partisi'] = np.where(split.index.isin(X_train.index), 'train', 'test')
    cv_tmp = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    split['fold'] = 0
    for k, (_, va) in enumerate(cv_tmp.split(X_train, y_train), 1):
        split.loc[X_train.iloc[va].index, 'fold'] = k
    split.to_csv(HASIL / 'data/split_train_test_fold.csv', index=False)
    tulis_json('data/ringkasan_split.json', {
        'n_train': int(len(y_train)), 'positif_train': int(y_train.sum()),
        'n_test': int(len(y_test)), 'positif_test': int(y_test.sum()),
        'test_size': 0.2, 'stratify': True, 'random_state': SEED,
        'test_ids': X_test['id_berkas'].tolist(),
    })

    hist = validasi_historis(X_train, X_test, y_train, y_test, logger)

    # --- Optuna ---------------------------------------------------------
    best_params, info_optuna, trials = jalankan_optuna(
        X_train, y_train, args.trials, logger)

    # --- Model ----------------------------------------------------------
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    pipe_base = buat_pipeline(BASELINE_PARAMS)
    pipe_tuned = buat_pipeline(best_params)

    cv_base = ringkas_cv(pipe_base, X_train, y_train, cv)
    cv_tuned = ringkas_cv(pipe_tuned, X_train, y_train, cv)
    tulis_json('data/cv_before_after.json', {
        'baseline': cv_base, 'tuned': cv_tuned,
        'baseline_params': BASELINE_PARAMS, 'tuned_params': best_params,
    })

    baris_cv = []
    for nama, cvr in [('Before Tuning', cv_base), ('After Tuning', cv_tuned)]:
        for met, v in cvr.items():
            baris_cv.append({'model': nama, 'metrik': met,
                             'mean': v['mean'], 'std': v['std'],
                             'per_fold': json.dumps(v['per_fold'])})
    pd.DataFrame(baris_cv).to_csv(HASIL / 'data/cv_before_after.csv', index=False)

    # OOF pada train (dipakai memilih threshold).
    p_oof_base = cross_val_predict(pipe_base, X_train, y_train, cv=cv,
                                   method='predict_proba', n_jobs=1)[:, 1]
    p_oof_tuned = cross_val_predict(pipe_tuned, X_train, y_train, cv=cv,
                                    method='predict_proba', n_jobs=1)[:, 1]
    pd.DataFrame({
        'id_berkas': X_train['id_berkas'].to_numpy(),
        'aktual': y_train.to_numpy(),
        'p_oof_baseline': p_oof_base,
        'p_oof_tuned': p_oof_tuned,
    }).to_csv(HASIL / 'data/oof_train.csv', index=False)

    tab_oof_base = tabel_threshold(y_train, p_oof_base)
    tab_oof_tuned = tabel_threshold(y_train, p_oof_tuned)
    tab_oof_base.to_csv(HASIL / 'data/threshold_oof_baseline.csv', index=False)
    tab_oof_tuned.to_csv(HASIL / 'data/threshold_oof_tuned.csv', index=False)

    t_f2_base, baris_f2_base = pilih_threshold(tab_oof_base, 'f2')
    t_f1_base, baris_f1_base = pilih_threshold(tab_oof_base, 'f1')
    t_f2_tuned, baris_f2_tuned = pilih_threshold(tab_oof_tuned, 'f2')
    t_f1_tuned, baris_f1_tuned = pilih_threshold(tab_oof_tuned, 'f1')

    # Titik operasional dengan batas beban alarm 50% pada OOF train. Batas ini
    # adalah skenario perencanaan kapasitas, bukan angka kapasitas kantor.
    kandidat_guard = tab_oof_tuned[tab_oof_tuned['alert_rate'] <= 0.50]
    t_guard, baris_guard = pilih_threshold(kandidat_guard, 'f2')

    # Ambang alternatif tetap, ditetapkan sebelum melihat test.
    alternatif = 0.25 if t_f2_tuned != 0.25 else 0.35
    daftar_threshold = sorted({0.50, t_f2_tuned, t_f1_tuned, t_guard,
                               alternatif}, reverse=True)
    if len({round(v, 4) for v in daftar_threshold}) < 3:
        daftar_threshold = sorted(set(daftar_threshold + [0.35, 0.25]),
                                  reverse=True)
    tulis_json('data/threshold_terpilih.json', {
        'metode_pemilihan': 'F2 maksimum pada prediksi OOF train; seri memilih '
                            'precision lebih tinggi lalu threshold lebih besar',
        'metrik_utama': 'F2',
        'alasan': 'False negative (berkas terlambat tidak terdeteksi) dinilai '
                  'lebih mahal daripada pemeriksaan tambahan akibat false positive.',
        'threshold_f2_baseline': t_f2_base,
        'threshold_f1_baseline': t_f1_base,
        'threshold_f2_tuned': t_f2_tuned,
        'threshold_f1_tuned': t_f1_tuned,
        'threshold_operasional_guard': t_guard,
        'guardrail': 'Beban alarm OOF <= 50%; skenario kapasitas, bukan klaim '
                     'kapasitas aktual kantor.',
        'threshold_0_50': 0.50,
        'threshold_alternatif': alternatif,
        'daftar_threshold_diuji': daftar_threshold,
        'test_tidak_dipakai_memilih': True,
        'baris_oof_f2_tuned': baris_f2_tuned,
        'baris_oof_f1_tuned': baris_f1_tuned,
        'baris_oof_guard': baris_guard,
    })

    # Fit final pada seluruh train.
    pipe_base.fit(X_train, y_train)
    pipe_tuned.fit(X_train, y_train)
    p_test_base = pipe_base.predict_proba(X_test)[:, 1]
    p_test_tuned = pipe_tuned.predict_proba(X_test)[:, 1]

    df_test = tabel_prediksi_test(raw, X_test, y_test, p_test_base, p_test_tuned,
                                  t_f2_base, t_f2_tuned)

    # Tabel threshold model tuned pada test (semua angka setelah threshold dikunci).
    baris_th = []
    for t in daftar_threshold:
        m = metrik(y_test, p_test_tuned, t)
        if t == 0.50:
            label = 'Default 0,50'
        elif t == t_f2_tuned:
            label = 'Optimal F2 OOF'
        elif t == t_guard:
            label = 'Operasional (alarm <=50%)'
        elif t == t_f1_tuned:
            label = 'Optimal F1 OOF'
        else:
            label = 'Alternatif sensitif'
        m['label'] = label
        baris_th.append(m)
    tab_test_tuned = pd.DataFrame(baris_th)
    tab_test_tuned.to_csv(HASIL / 'data/threshold_test_tuned.csv', index=False)

    # Before vs after pada threshold yang sama dan pada threshold OOF masing-masing.
    baris_ba = []
    konfigurasi = [
        ('Before Tuning', '0,50', p_test_base, t_f2_base, 0.50),
        ('After Tuning', '0,50', p_test_tuned, t_f2_tuned, 0.50),
        ('Before Tuning', 'OOF F2', p_test_base, t_f2_base, t_f2_base),
        ('After Tuning', 'OOF F2', p_test_tuned, t_f2_tuned, t_f2_tuned),
        ('Before Tuning', 'OOF F1', p_test_base, t_f2_base, t_f1_base),
        ('After Tuning', 'OOF F1', p_test_tuned, t_f2_tuned, t_f1_tuned),
        ('After Tuning', 'Operasional (alarm <=50%)', p_test_tuned,
         t_f2_tuned, t_guard),
    ]
    for model, label, p, _, t in konfigurasi:
        m = metrik(y_test, p, t)
        m.update({'model': model, 'skenario_threshold': label})
        baris_ba.append(m)
    tab_ba = pd.DataFrame(baris_ba)
    tab_ba.to_csv(HASIL / 'data/perbandingan_before_after_test.csv', index=False)

    # Tabel utama eval test tuned pada threshold terpilih.
    m_utama = metrik(y_test, p_test_tuned, t_f2_tuned)
    tulis_json('data/metrik_test_terpilih.json', m_utama)

    rep = classification_report(
        y_test, (p_test_tuned >= t_f2_tuned).astype(int),
        labels=[0, 1], target_names=['Tepat Waktu', 'Terlambat'],
        output_dict=True, zero_division=0)
    tulis_json('data/classification_report_test_tuned.json', rep)

    rep_base = classification_report(
        y_test, (p_test_base >= t_f2_base).astype(int),
        labels=[0, 1], target_names=['Tepat Waktu', 'Terlambat'],
        output_dict=True, zero_division=0)
    tulis_json('data/classification_report_test_baseline.json', rep_base)

    # Bootstrap interval.
    boot = bootstrap_ci(y_test, p_test_tuned, t_f2_tuned)
    tulis_json('data/bootstrap_interval_tuned.json', boot)

    # Pembanding naif untuk membongkar paradoks akurasi.
    naif = []
    for nama, pred in [('Selalu tepat waktu', np.zeros(len(y_test), dtype=int)),
                       ('Selalu terlambat', np.ones(len(y_test), dtype=int))]:
        tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()
        naif.append({
            'model': nama,
            'accuracy': float(accuracy_score(y_test, pred)),
            'precision': float(precision_score(y_test, pred, zero_division=0)),
            'recall': float(recall_score(y_test, pred, zero_division=0)),
            'f1': float(f1_score(y_test, pred, zero_division=0)),
            'tp': int(tp), 'fn': int(fn), 'fp': int(fp), 'tn': int(tn),
        })
    pd.DataFrame(naif).to_csv(HASIL / 'data/baseline_naif_test.csv', index=False)

    # Error analysis.
    fp, fn, ringkas_error = analisis_kesalahan(df_test, logger)

    # --- Simpan model ---------------------------------------------------
    metadata = {
        'kelompok': '02',
        'objek': 'Kantor Notaris & PPAT Aries Buwana',
        'mata_kuliah': 'Pembelajaran Mesin',
        'kelas': 'KG.043.10.A',
        'semester': 'Gasal 2026/2027',
        'tanggal_eksperimen': mulai.isoformat(),
        'algoritma': 'DecisionTreeClassifier',
        'baseline_params': BASELINE_PARAMS,
        'tuned_params': best_params,
        'threshold_baseline_oof_f2': t_f2_base,
        'threshold_tuned_oof_f2': t_f2_tuned,
        'threshold_tuned_oof_f1': t_f1_tuned,
        'threshold_operasional_guard': t_guard,
        'threshold_dipakai_test': t_f2_tuned,
        'n_train': int(len(y_train)), 'positif_train': int(y_train.sum()),
        'n_test': int(len(y_test)), 'positif_test': int(y_test.sum()),
        'fitur': FEATURES,
        'kolom_input': ['id_berkas', 'tgl_masuk', 'tgl_selesai', 'tgl_rups',
                        'kategori_akta', 'jumlah_penghadap', 'sla_hari'],
        'sha256_dataset': hash_file(DATA),
        'versi': {
            'python': platform.python_version(),
            'numpy': np.__version__,
            'pandas': pd.__version__,
            'scikit-learn': sklearn.__version__,
            'optuna': optuna.__version__,
        },
    }
    joblib.dump({'pipeline': pipe_tuned, 'threshold': t_f2_tuned,
                 'params': best_params, 'metadata': metadata},
                MODEL_DIR / 'model_tugas06_tuned.joblib', compress=3)
    joblib.dump({'pipeline': pipe_base, 'threshold': t_f2_base,
                 'params': BASELINE_PARAMS, 'metadata': metadata},
                MODEL_DIR / 'model_tugas06_baseline.joblib', compress=3)
    tulis_json('model/metadata_model.json', metadata)

    # Prediksi ulang setelah pemuatan untuk memeriksa kesamaan.
    load = joblib.load(MODEL_DIR / 'model_tugas06_tuned.joblib')
    p_load = load['pipeline'].predict_proba(X_test)[:, 1]
    paritas = {
        'max_abs_error': float(np.max(np.abs(p_load - p_test_tuned))),
        'prediksi_identik': bool(np.array_equal(
            p_load >= t_f2_tuned, p_test_tuned >= t_f2_tuned)),
    }
    tulis_json('model/uji_paritas.joblib.json', paritas)

    # --- Grafik ---------------------------------------------------------
    # 1. Confusion matrix tuned pada threshold terpilih.
    cm = confusion_matrix(y_test, p_test_tuned >= t_f2_tuned, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(5.4, 4.4))
    im = ax.imshow(cm, cmap='Blues')
    label_cm = [['TN', 'FP'], ['FN', 'TP']]
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f'{label_cm[i][j]}\n{cm[i, j]}', ha='center',
                    va='center', fontsize=15,
                    color='white' if cm[i, j] > cm.max() / 2 else '#13283b')
    ax.set(xticks=[0, 1], yticks=[0, 1],
           xticklabels=['Tepat Waktu', 'Terlambat'],
           yticklabels=['Tepat Waktu', 'Terlambat'],
           xlabel='Prediksi', ylabel='Aktual',
           title=f'Confusion Matrix After Tuning\nambang {t_f2_tuned:.2f}')
    ax.grid(False)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    simpan_grafik(GRAFIK / '01_confusion_matrix_tuned.png')

    # 2. ROC dan PR.
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.3))
    for nama, p, warna in [('Before Tuning', p_test_base, GRAY),
                           ('After Tuning', p_test_tuned, BLUE)]:
        fpr, tpr, _ = roc_curve(y_test, p)
        pr, rc, _ = precision_recall_curve(y_test, p)
        axes[0].plot(fpr, tpr, color=warna, lw=2,
                     label=f'{nama} (AUC {roc_auc_score(y_test, p):.3f})')
        axes[1].step(rc, pr, where='post', color=warna, lw=2,
                     label=f'{nama} (AP {average_precision_score(y_test, p):.3f})')
    axes[0].plot([0, 1], [0, 1], '--', color='#a0a8b0', lw=1)
    axes[1].axhline(y_test.mean(), ls='--', color='#a0a8b0',
                    label=f'Prevalensi {y_test.mean():.3f}')
    # Tandai threshold pada kurva PR/ROC model tuned.
    for t, gaya in [(0.50, ':'), (t_f2_tuned, '--'), (t_f1_tuned, '-.')]:
        pred = (p_test_tuned >= t).astype(int)
        tn, fp_, fn_, tp_ = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()
        tpr_ = tp_ / (tp_ + fn_) if (tp_ + fn_) else 0
        fpr_ = fp_ / (fp_ + tn) if (fp_ + tn) else 0
        prec_ = tp_ / (tp_ + fp_) if (tp_ + fp_) else 1
        rec_ = tpr_
        axes[0].scatter([fpr_], [tpr_], s=38, color=RED, zorder=5)
        axes[1].scatter([rec_], [prec_], s=38, color=RED, zorder=5)
        axes[0].annotate(f'{t:.2f}', (fpr_, tpr_), textcoords='offset points',
                         xytext=(6, 4), fontsize=7, color=RED)
        axes[1].annotate(f'{t:.2f}', (rec_, prec_), textcoords='offset points',
                         xytext=(6, 4), fontsize=7, color=RED)
    for ax in axes:
        ax.set(xlim=(0, 1), ylim=(0, 1.03))
        ax.legend(fontsize=7.5, loc='lower left')
        rapikan_sumbu(ax, 'both')
    axes[0].set(xlabel='False Positive Rate', ylabel='True Positive Rate',
                title=f'ROC pada {len(y_test)} berkas uji')
    axes[1].set(xlabel='Recall (Terlambat)', ylabel='Precision (Terlambat)',
                title='Precision-Recall pada data uji')
    fig.tight_layout()
    simpan_grafik(GRAFIK / '02_roc_pr.png')

    # 3. Threshold tuning dari OOF.
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.1))
    for kolom, label, warna in [('precision', 'Precision', RED),
                                ('recall', 'Recall', BLUE),
                                ('f1', 'F1', GRAY),
                                ('f2', 'F2', GREEN)]:
        axes[0].plot(tab_oof_tuned['threshold'], tab_oof_tuned[kolom],
                     label=label, color=warna, lw=2)
    axes[0].axvline(0.5, color='#333333', ls=':', lw=1.2, label='Default 0,50')
    axes[0].axvline(t_f2_tuned, color=RED, ls='--', lw=1.2,
                    label=f'F2 OOF {t_f2_tuned:.2f}')
    axes[0].set(xlabel='Ambang keputusan', ylabel='Skor pada OOF train',
                ylim=(0, 1.03), title='Pemilihan ambang dari OOF train')
    axes[0].legend(fontsize=7.5)
    rapikan_sumbu(axes[0])
    axes[1].plot(tab_oof_tuned['threshold'], tab_oof_tuned['alert_rate'],
                 color=BLUE, lw=2)
    axes[1].axvline(0.5, color='#333333', ls=':', lw=1.2)
    axes[1].axvline(t_f2_tuned, color=RED, ls='--', lw=1.2)
    axes[1].set(xlabel='Ambang keputusan', ylabel='Proporsi alarm',
                ylim=(0, 1.03), title='Beban alarm pada OOF train')
    rapikan_sumbu(axes[1])
    fig.tight_layout()
    simpan_grafik(GRAFIK / '03_threshold_tuning_oof.png')

    # 6. CV before vs after.
    metrik_plot = [('macro_f1', 'Macro F1'), ('f1_positif', 'F1 positif'),
                   ('recall', 'Recall'), ('precision', 'Precision'),
                   ('average_precision', 'PR-AUC (AP)'), ('roc_auc', 'ROC-AUC')]
    x = np.arange(len(metrik_plot))
    lebar = 0.36
    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    for offset, (nama, cvr, warna) in [(-lebar / 2, ('Before', cv_base, GRAY)),
                                       (lebar / 2, ('After', cv_tuned, BLUE))]:
        vals = [cvr[k]['mean'] for k, _ in metrik_plot]
        errs = [cvr[k]['std'] for k, _ in metrik_plot]
        ax.bar(x + offset, vals, lebar, yerr=errs, capsize=3, color=warna,
               label=nama, alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels([l for _, l in metrik_plot])
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('Skor rata-rata 5-fold')
    ax.set_title('Perbandingan Stratified 5-Fold CV: Before vs After Tuning')
    ax.legend()
    rapikan_sumbu(ax)
    fig.tight_layout()
    simpan_grafik(GRAFIK / '06_cv_before_after.png')

    # 7. Confusion matrix perbandingan.
    fig, axes = plt.subplots(2, 2, figsize=(8.6, 7.4))
    kombinasi = [
        ('Before Tuning @ 0,50', p_test_base, 0.50),
        ('After Tuning @ 0,50', p_test_tuned, 0.50),
        (f'Before Tuning @ {t_f2_base:.2f}', p_test_base, t_f2_base),
        (f'After Tuning @ {t_f2_tuned:.2f}', p_test_tuned, t_f2_tuned),
    ]
    for ax, (judul, p, t) in zip(axes.ravel(), kombinasi):
        cmx = confusion_matrix(y_test, p >= t, labels=[0, 1])
        ax.imshow(cmx, cmap='Blues', vmin=0, vmax=len(y_test))
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cmx[i, j]), ha='center', va='center',
                        fontsize=14,
                        color='white' if cmx[i, j] > cmx.max() / 2 else '#13283b')
        ax.set(xticks=[0, 1], yticks=[0, 1],
               xticklabels=['Tepat', 'Terlambat'],
               yticklabels=['Tepat', 'Terlambat'],
               xlabel='Prediksi', ylabel='Aktual', title=judul)
        ax.grid(False)
    fig.tight_layout()
    simpan_grafik(GRAFIK / '07_confusion_compare.png')

    # 8. Sebaran skor test menurut kelas aktual.
    fig, ax = plt.subplots(figsize=(9.2, 3.7))
    rng = np.random.default_rng(7)
    for kelas, warna, label in [(0, GRAY, 'Tepat waktu'), (1, RED, 'Terlambat')]:
        mask = np.asarray(y_test) == kelas
        ax.scatter(np.asarray(p_test_tuned)[mask],
                   rng.normal(kelas, 0.045, mask.sum()),
                   s=34, color=warna, alpha=0.8, label=label)
    for t, gaya, label in [(0.50, ':', '0,50'), (t_f2_tuned, '--', f'F2 {t_f2_tuned:.2f}')]:
        ax.axvline(t, color='#333333', ls=gaya, lw=1.3, label=f'Ambang {label}')
    ax.set(xlim=(-0.02, 1.02), xlabel='Skor After Tuning',
           title='Sebaran skor model After Tuning pada 34 berkas uji')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Tepat waktu', 'Terlambat'])
    ax.legend(fontsize=8, loc='upper right')
    rapikan_sumbu(ax, 'x')
    fig.tight_layout()
    simpan_grafik(GRAFIK / '08_test_scores.png')

    # --- Ringkasan ------------------------------------------------------
    ringkasan = {
        'waktu_mulai': mulai.isoformat(),
        'waktu_selesai': datetime.now().isoformat(),
        'durasi_total_detik': float((datetime.now() - mulai).total_seconds()),
        'dataset': {'n': 169, 'positif': int(y.sum()),
                    'train': int(len(y_train)), 'test': int(len(y_test))},
        'validasi_historis_t05': hist,
        'optuna': info_optuna,
        'cv_baseline': cv_base,
        'cv_tuned': cv_tuned,
        'threshold_f2_baseline': t_f2_base,
        'threshold_f2_tuned': t_f2_tuned,
        'threshold_f1_tuned': t_f1_tuned,
        'threshold_operasional_guard': t_guard,
        'metrik_test_tuned_terpilih': m_utama,
        'bootstrap': boot,
        'analisis_kesalahan': ringkas_error,
        'uji_paritas_model': paritas,
    }
    tulis_json('data/ringkasan_eksekusi.json', ringkasan)

    env = {
        'python': platform.python_version(),
        'platform': platform.platform(),
        'numpy': np.__version__, 'pandas': pd.__version__,
        'scikit-learn': sklearn.__version__, 'optuna': optuna.__version__,
        'matplotlib': matplotlib.__version__, 'joblib': joblib.__version__,
        'seed': SEED,
    }
    tulis_json('log/environment.json', env)

    logger.info('=== SELESAI ===')
    logger.info('Threshold F2 OOF baseline=%.2f, tuned=%.2f', t_f2_base, t_f2_tuned)
    logger.info('Test tuned @%.2f: TP=%s FN=%s FP=%s TN=%s | P=%.3f R=%.3f F1=%.3f AP=%.3f AUC=%.3f',
                t_f2_tuned, m_utama['tp'], m_utama['fn'], m_utama['fp'],
                m_utama['tn'], m_utama['precision'], m_utama['recall'],
                m_utama['f1'], m_utama['average_precision'], m_utama['roc_auc'])
    print(json.dumps({
        'threshold_tuned': t_f2_tuned,
        'test_metrics': m_utama,
        'best_params': best_params,
        'best_cv_macro_f1': info_optuna['best_value_cv_macro_f1'],
    }, indent=2, default=str))


if __name__ == '__main__':
    main()
