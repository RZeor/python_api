# Spatial Clustering Python API

Flask API wrapper untuk clustering_script.py dan convert_shapefile_to_geojson.py

## Deploy ke Railway

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

### Langkah 2: Deploy di Railway
1. Buka https://railway.app
2. Login dengan GitHub
3. Klik "New Project"
4. Pilih "Deploy from GitHub repo"
5. Pilih repository Anda
6. Railway akan auto-detect dan deploy

### Langkah 3: Dapatkan URL
Setelah deploy selesai, Railway akan memberikan URL seperti:
`https://your-app.railway.app`

## API Endpoints

### 1. Clustering
```
POST /api/clustering
Content-Type: multipart/form-data

Parameters:
- file: CSV/Excel file
- linkage: ward (default), complete, average
- metric: euclidean (default), manhattan, cosine
- n_clusters: 3 (default)

Response:
{
  "success": true,
  "message": "Clustering completed successfully",
  "data": { ... }
}
```

### 2. Convert Shapefile
```
POST /api/convert-shapefile
Content-Type: multipart/form-data

Parameters:
- cluster_results: cluster_results.json file
- shapefile_path: path to shapefile (optional)

Response:
{
  "success": true,
  "message": "GeoJSON created successfully"
}
```

### 3. Get Results
```
GET /api/results

Response:
{
  "success": true,
  "data": { ... }
}
```

### 4. Get GeoJSON
```
GET /api/geojson

Response:
{ GeoJSON data }
```

### 5. Health Check
```
GET /health

Response:
{
  "status": "healthy",
  "service": "Spatial Clustering API"
}
```

## Test Locally

```bash
pip install -r requirements.txt
python app.py
```

Server akan jalan di http://localhost:5000

## Cara Pakai dari PHP

Setelah deploy, update PHP Anda untuk memanggil Railway API:

```php
$api_url = 'https://your-app.railway.app/api/clustering';

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $api_url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$post_fields = [
    'file' => new CURLFile($file_path),
    'linkage' => 'ward',
    'metric' => 'euclidean',
    'n_clusters' => 3
];

curl_setopt($ch, CURLOPT_POSTFIELDS, $post_fields);
$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);
```
