"""Transformer fitur berkas notaris.

Disalin tanpa perubahan logika dari paket Tugas 05 Kelompok 02
(``fitur_notaris.py``). Transformer ini membentuk fitur antrean, indikator
RUPS, koordinat bulan, kategori akta, dan hari masuk. Histori antrean hanya
dipelajari dari data latih tempat transformer di-fit agar tidak membocorkan
label data uji ke dalam proses pelatihan.
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted

NUM = ['jumlah_penghadap', 'sla_hari', 'antrean_berjalan', 'ada_rups',
       'bulan_sin', 'bulan_cos']
CAT = ['kategori_akta', 'hari_masuk']
FEATURES = NUM + CAT
RAW = ['id_berkas', 'tgl_masuk', 'tgl_selesai', 'tgl_rups', 'kategori_akta',
       'jumlah_penghadap', 'sla_hari']


class FiturNotaris(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.masuk_hist_ = pd.to_datetime(X['tgl_masuk'], errors='raise').to_numpy()
        self.selesai_hist_ = pd.to_datetime(X['tgl_selesai'], errors='coerce').to_numpy()
        self.id_hist_ = X['id_berkas'].astype(str).to_numpy()
        return self

    def set_history(self, records):
        """Ganti snapshot histori tervalidasi tanpa melatih ulang model."""
        if not records:
            self.masuk_hist_ = np.array([], dtype='datetime64[ns]')
            self.selesai_hist_ = np.array([], dtype='datetime64[ns]')
            self.id_hist_ = np.array([], dtype=object)
            return self
        h = pd.DataFrame(records)
        self.masuk_hist_ = pd.to_datetime(h['tgl_masuk'], errors='raise').to_numpy()
        self.selesai_hist_ = pd.to_datetime(h['tgl_selesai'], errors='coerce').to_numpy()
        self.id_hist_ = h['id_berkas'].astype(str).to_numpy()
        return self

    def transform(self, X):
        check_is_fitted(self, 'masuk_hist_')
        masuk = pd.to_datetime(X['tgl_masuk'], errors='raise')
        rups = pd.to_datetime(X['tgl_rups'], errors='coerce')
        t = masuk.to_numpy()
        # Status pada awal hari: berkas yang selesai hari ini masih terbuka
        # pada awal hari. Tanggal selesai kosong berarti masih terbuka.
        antrean = ((self.masuk_hist_[:, None] < t[None, :]) &
                   (np.isnat(self.selesai_hist_[:, None]) |
                    (self.selesai_hist_[:, None] >= t[None, :]))).sum(axis=0)
        out = pd.DataFrame(index=X.index)
        out['jumlah_penghadap'] = X['jumlah_penghadap'].to_numpy()
        out['sla_hari'] = X['sla_hari'].to_numpy()
        out['antrean_berjalan'] = antrean
        out['ada_rups'] = (rups.notna() & (rups <= masuk)).astype(int).to_numpy()
        out['bulan_sin'] = np.sin(2 * np.pi * masuk.dt.month / 12).to_numpy()
        out['bulan_cos'] = np.cos(2 * np.pi * masuk.dt.month / 12).to_numpy()
        out['kategori_akta'] = X['kategori_akta'].to_numpy()
        out['hari_masuk'] = masuk.dt.dayofweek.map(dict(enumerate(
            ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']))).to_numpy()
        return out[FEATURES]

    def get_feature_names_out(self, input_features=None):
        return np.asarray(FEATURES, dtype=object)
