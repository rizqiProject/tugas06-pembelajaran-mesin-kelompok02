# PANDUAN MEMBUAT AKUN GITHUB DAN MEMPUBLIKASIKAN REPOSITORI

Panduan ini untuk Kelompok 02 Tugas 06. Pilih **Jalur A** jika Anda tidak terbiasa
dengan terminal. Jalur B dan C adalah alternatif.

> **Penting:** jangan unggah folder `.venv`. Folder itu berisi pustaka Python
> berukuran besar dan sudah dikecualikan oleh `.gitignore`. Yang diunggah cukup
> kode, data, hasil, laporan, dan README.

## Jalur A — VS Code (paling mudah, direkomendasikan)

### A.1 Buat akun GitHub

1. Buka **https://github.com/signup** di Chrome/Safari.
2. Isi:
   - **Email** aktif (email pribadi atau kampus).
   - **Password** minimal 8 karakter.
   - **Username** unik, misalnya `rizqi-t06` atau `kelompok02-unm`.
3. Klik **Create account**.
4. Buka email, cari kode verifikasi dari GitHub, lalu masukkan kodenya.
5. Jika muncul pertanyaan pengaturan (personalization), pilih **Skip personalization**
   atau jawab seadanya. Akun tetap bisa dipakai.

### A.2 Buka proyek di VS Code

1. Buka aplikasi **Visual Studio Code**.
2. Klik **File → Open Folder…**
3. Pilih folder:
   `/Users/admin/PEMBELAJARAN_MESIN_KELOMPOK_02`
4. Tunggu sampai daftar file muncul di panel kiri.

### A.3 Publikasikan ke GitHub

1. Klik ikon **Source Control** di panel kiri (ikon seperti ranting/pohon,
   biasanya di bawah ikon pencarian).
2. Klik tombol **Publish to GitHub**.
   - Jika yang muncul **Publish Branch**, klik itu.
3. VS Code akan membuka browser dan meminta login GitHub.
4. Klik **Sign in with GitHub**, masukkan email/username dan password.
5. Klik **Authorize** jika diminta.
6. Kembali ke VS Code. Pilih:
   - **Publish to GitHub public repository** (agar tautan bisa dibuka dosen).
   - Nama repo: `tugas06-pembelajaran-mesin-kelompok02`
7. Klik **Publish** dan tunggu proses unggah selesai.
8. Setelah selesai, buka browser ke:
   `https://github.com/USERNAME/tugas06-pembelajaran-mesin-kelompok02`
   Ganti `USERNAME` dengan username GitHub Anda.

### A.4 Kirim tautan ke saya

Kirim tautan repo, contoh:

`https://github.com/rizqi-t06/tugas06-pembelajaran-mesin-kelompok02`

Saya akan memasukkan tautan itu ke Lampiran laporan dan membuat ulang DOCX/PDF.

---

## Jalur B — GitHub web + terminal

Gunakan ini jika tombol Publish to GitHub tidak muncul.

### B.1 Buat repositori kosong

1. Login ke GitHub.
2. Klik **+** di kanan atas → **New repository**.
3. Isi:
   - **Repository name:** `tugas06-pembelajaran-mesin-kelompok02`
   - **Visibility:** **Public**
   - **Jangan** centang "Add a README file", "Add .gitignore", atau "Choose a license".
4. Klik **Create repository**.
5. Salin alamat repo, misalnya:
   `https://github.com/USERNAME/tugas06-pembelajaran-mesin-kelompok02.git`

### B.2 Buat token akses (sekali saja)

1. Buka **https://github.com/settings/tokens**
2. Klik **Generate new token → Generate new token (classic)**.
3. Isi **Note:** `Tugas 06 Kelompok 02`.
4. Pilih **Expiration:** 7 days (atau 30 days).
5. Centang scope **repo**.
6. Klik **Generate token**.
7. Salin token (mulai `ghp_...`). Token ini hanya muncul sekali.

### B.3 Jalankan perintah

Buka **Terminal** di VS Code (**Terminal → New Terminal**), lalu jalankan:

```bash
cd /Users/admin/PEMBELAJARAN_MESIN_KELOMPOK_02
git remote add origin https://github.com/USERNAME/tugas06-pembelajaran-mesin-kelompok02.git
git branch -M main
git push -u origin main
```

Saat diminta:

- **Username:** username GitHub Anda.
- **Password:** tempel token `ghp_...` (bukan password akun).

Jika muncul error `remote origin already exists`, jalankan:

```bash
git remote set-url origin https://github.com/USERNAME/tugas06-pembelajaran-mesin-kelompok02.git
git push -u origin main
```

Jika `git branch -M main` error karena Git lama, jalankan:

```bash
git checkout -b main
git push -u origin main
```

---

## Jalur C — GitHub Desktop

1. Unduh **GitHub Desktop** dari **https://desktop.github.com**.
2. Install, lalu buka dan klik **Sign in to GitHub.com**.
3. Pilih **File → Add local repository…**
4. Pilih folder `/Users/admin/PEMBELAJARAN_MESIN_KELOMPOK_02`.
5. Klik **Publish repository**.
6. **Hilangkan centang** "Keep this code private".
7. Klik **Publish repository**.

---

## Membuat tautan Colab (opsional, nilai tambah)

Colab memerlukan akun Google. Notebook sudah disiapkan di
`Jalankan_Tugas06_Colab.ipynb`.

1. Buka **https://colab.research.google.com** dan login dengan akun Google.
2. Klik **File → Open notebook → GitHub**.
3. Tempel URL repo GitHub Anda, lalu pilih
   `Jalankan_Tugas06_Colab.ipynb`.
4. Di sel pertama, ganti `REPO_URL` dengan URL repo Anda.
5. Klik **Runtime → Run all**.
6. Klik **Share** (kanan atas) → **Anyone with the link** → **Viewer**.
7. Salin tautan dan kirim ke saya.

Tautan Colab langsung juga bisa dibuat dengan pola:

```text
https://colab.research.google.com/github/USERNAME/REPO/blob/main/Jalankan_Tugas06_Colab.ipynb
```

Catatan: PDF tidak bisa diekspor dari Colab karena memerlukan Microsoft Word.
DOCX bisa dihasilkan dan diunduh dari Colab; PDF final tetap memakai berkas yang
sudah ada di repo.

---

## Checklist setelah publikasi

- [ ] Repo bisa dibuka di jendela **Incognito** (tidak login) → berarti publik.
- [ ] `README_TUGAS_06.md` tampil di halaman depan repo.
- [ ] Folder `laporan_tugas_06/` berisi DOCX dan PDF.
- [ ] Folder `eksperimen_tugas_06/hasil/grafik/` berisi 8 grafik + 1 tangkapan layar.
- [ ] Folder `eksperimen_tugas_06/hasil/model/` berisi `.joblib`.
- [ ] Tautan repo dikirim ke saya untuk dimasukkan ke Lampiran laporan.

## Jika gagal

Kirimkan ke saya:

1. Tulisan error yang muncul (screenshot atau teks).
2. Username GitHub Anda.
3. Nama repo yang dibuat.

Saya bantu telusuri langkah yang macet.
