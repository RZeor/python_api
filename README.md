# Spatial Clustering Python API

Flask API untuk analisis hierarchical clustering dari file CSV atau Excel. Proyek ini tidak memakai geopandas; hasil visualisasi dibuat sebagai dendrogram, bukan peta.

## Fitur

- Upload data CSV atau Excel untuk clustering.
- Parameter clustering bisa diatur lewat request.
- Hasil analisis disimpan ke JSON dan bisa diambil kembali lewat endpoint hasil.
- Mendukung output statistik cluster, label kategori potensi, dan dendrogram.

## Struktur Input Data

Script akan mencoba membaca kolom berikut jika tersedia:

- `Sale_Total`
- `Toko_Didatangi`
- `Toko_Membeli`
- `Latitude`
- `Longitude`
- Kolom brand seperti `SSB`, `KSN`, `SBS`, `Spc 16`, `SE12`, `SE16`, `BCK`, `LS 12`, `LS 16`, `TRN B`, `Spirit`, `RVL 16`, `LSFB 12`, `RVL M 12`

Kolom `Kecamatan` akan diubah menjadi `Kelurahan` jika ditemukan. Kolom `call` dan `effcall` juga akan dinormalisasi menjadi `Toko_Didatangi` dan `Toko_Membeli`.

## Instalasi

Pastikan menggunakan Python 3.11.13 atau yang kompatibel dengan project ini.

```bash
pip install -r requirements.txt
```

## Menjalankan Lokal

```bash
python app.py
```

Server akan berjalan di `http://127.0.0.1:5000` atau port dari environment variable `PORT`.

## API Endpoints

### Root

```http
GET /
```

Mengembalikan informasi service dan daftar endpoint yang tersedia.

### Clustering

```http
POST /api/clustering
```

Gunakan `multipart/form-data` dengan field berikut:

- `file` - file CSV atau Excel
- `linkage` - `ward`, `complete`, `average`, atau `single` untuk script clustering
- `metric` - `euclidean`, `manhattan`, atau `cosine`
- `n_clusters` - jumlah cluster, default `3`

Contoh response sukses:

```json
{
  "success": true,
  "message": "Clustering completed successfully",
  "data": {
    "silhouette_score": 0.0,
    "davies_bouldin_index": 0.0,
    "calinski_harabasz_index": 0.0
  }
}
```

### Ambil Hasil Terakhir

```http
GET /api/results
```

Mengambil hasil clustering terakhir yang tersimpan di `results/cluster_results.json`.

### Health Check

```http
GET /health
```

Mengembalikan status service.

## Output File

Setelah proses clustering berhasil, aplikasi akan menyimpan:

- `results/cluster_results.json`
- `results/dendrogram.png`

## Deploy ke Railway

Project ini sudah cocok untuk deployment di Railway.

### Langkah

1. Push project ke GitHub.
2. Buka https://railway.app dan login dengan akun GitHub.
3. Klik **New Project** lalu pilih deploy dari GitHub repository.
4. Hubungkan repository project ini.
5. Gunakan konfigurasi berikut:
  - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
  - **Start Command:** `gunicorn app:app --timeout 300 --workers 1 --bind 0.0.0.0:$PORT`
6. Deploy service.

Jika kamu memakai Railway dengan konfigurasi file, buat `railway.json` atau set command tersebut langsung di dashboard Railway.

## Requirements

- Flask
- Flask-CORS
- pandas
- scikit-learn
- numpy
- scipy
- matplotlib
- openpyxl
- xlrd
- gunicorn

## Catatan

- API ini mengandalkan proses clustering via subprocess pada `clustering_script.py`.
- Jika file input tidak memiliki semua kolom yang dibutuhkan, script akan mencoba mengisi nilai default untuk beberapa kolom, tetapi sebagian perhitungan tetap bisa gagal jika struktur data terlalu berbeda.
