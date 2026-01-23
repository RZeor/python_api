# Spatial Clustering Python API

Flask API untuk clustering analysis (tanpa geopandas - peta menggunakan marker point)

## Deploy ke Render.com

### Langkah 1: Push ke GitHub
```bash
cd python
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Langkah 2: Deploy di Render
1. Buka https://render.com
2. Login dengan GitHub
3. Klik "New +" → "Web Service"
4. Connect repository Anda
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --timeout 300`
   - **Plan:** Free
6. Deploy

### Langkah 3: Dapatkan URL
Setelah deploy: `https://your-app.onrender.com`

## API Endpoints

### 1. Clustering
```
POST /api/clustering

Parameters (multipart/form-data):
- file: CSV/Excel file
- linkage: ward|complete|average (default: ward)
- metric: euclidean|manhattan|cosine (default: euclidean)
- n_clusters: number (default: 3)

Response:
{
  "success": true,
  "data": { cluster results }
}
```

### 2. Get Results
```
GET /api/results

Response:
{
  "success": true,
  "data": { cluster results }
}
```

### 3. Health Check
```
GET /health
```

## Dependencies (Ringan - Tanpa Geopandas)
- Flask
- pandas
- scikit-learn
- numpy
- scipy

**Total size: ~200MB** (vs 800MB dengan geopandas)
