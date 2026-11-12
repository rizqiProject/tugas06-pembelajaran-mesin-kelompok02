# Tugas 06 Pembelajaran Mesin — Kelompok 02

**Objek:** Kantor Notaris & PPAT Aries Buwana, Jakarta Barat  
**Mata kuliah:** Pembelajaran Mesin (KG.043.10.A) — Semester Gasal 2026/2027  
**Anggota:** Muhammad Rizqi Saputra (12250158), Dian Nur Cahya (12250162), Dicky Handia (12250161)

Repositori ini memuat laporan Tugas 06, proposal UTS, kode eksperimen, hasil,
grafik, dan model.

## Proposal UTS

- [Proposal UTS PDF](proposal_uts/PROPOSAL_UTS_ML_KELOMPOK_02_NOTARIS_PPAT.pdf)
- [Proposal UTS Word](proposal_uts/PROPOSAL_UTS_ML_KELOMPOK_02_NOTARIS_PPAT.docx)
- [README proposal dan cara membangun ulang](proposal_uts/README_UTS.md)
- [Checklist unggah UTS](CHECKLIST_UNGGAH_UTS.md)

## Laporan Tugas 06

- [Laporan PDF](laporan_tugas_06/TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.pdf)
- [Laporan Word](laporan_tugas_06/TUGAS_06_KELOMPOK_02_NOTARIS_PPAT.docx)
- [README lengkap dan cara menjalankan ulang](README_TUGAS_06.md)
- [Checklist kesesuaian template dan arahan dosen](CEK_KESESUAIAN_TEMPLATE_TUGAS_06.md)

## Hasil utama

| Komponen | Hasil |
|---|---|
| Dataset | 169 berkas; 33 terlambat |
| Split | 135 train / 34 test |
| Model | Decision Tree hasil Optuna |
| Threshold | 0,05 (F2 maksimum OOF train) |
| Test @0,05 | TP 5, FN 2, FP 19, TN 8 |
| Precision / Recall / F1 | 0,208 / 0,714 / 0,323 |
| F2 / Macro F1 | 0,481 / 0,378 |
| ROC-AUC / PR-AUC | 0,413 / 0,190 |
| Optuna | 30 trial TPE; trial terbaik #13; CV Macro F1 0,5532 |

## Isi repositori

```text
laporan_tugas_06/       laporan Word/PDF dan skrip penyusun
eksperimen_tugas_06/    skrip eksperimen, hasil, grafik, model .joblib
data/                   dataset sumber
referensi/              panduan, template, slide, cheatsheet
kode_tugas_sebelumnya/  paket Tugas 04 dan Tugas 05
```

## Menjalankan ulang

```bash
cd eksperimen_tugas_06
python eksperimen_tugas06.py --trials 30

cd ../laporan_tugas_06
python buat_laporan.py
```

Detail lingkungan dan langkah lengkap ada di [README_TUGAS_06.md](README_TUGAS_06.md).

## Catatan

Model diposisikan sebagai alat bantu penyaringan, bukan pengganti keputusan staf atau Notaris/PPAT. Data uji 34 berkas sudah pernah dipakai pada Tugas 04–05, sehingga bukan holdout yang sepenuhnya buta.
