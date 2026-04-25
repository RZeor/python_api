import sys
import json
import pandas as pd
import numpy as np
import argparse
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Spatial Clustering Analysis')
    parser.add_argument('data_file', help='Path to data file (CSV or Excel)')
    parser.add_argument('output_file', help='Path to output JSON file')
    parser.add_argument('--linkage', default='complete', choices=['ward', 'complete', 'average', 'single'],
                        help='Linkage method for hierarchical clustering')
    parser.add_argument('--metric', default='euclidean', choices=['euclidean', 'manhattan', 'cosine'],
                        help='Distance metric')
    parser.add_argument('--n_clusters', type=int, default=3, help='Number of clusters')
    
    args = parser.parse_args()
    
    data_file = args.data_file
    output_file = args.output_file
    linkage_method = args.linkage
    metric = args.metric
    n_clusters = args.n_clusters
    
    try:
        # Load data - support CSV and Excel formats
        if data_file.endswith('.csv'):
            # Try to auto-detect delimiter
            try:
                # First try with comma
                df = pd.read_csv(data_file, delimiter=',')
                # If only 1-2 columns, try semicolon
                if len(df.columns) <= 2:
                    df = pd.read_csv(data_file, delimiter=';')
            except:
                # Fallback to default pandas detection
                df = pd.read_csv(data_file)
        elif data_file.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(data_file)
        else:
            raise ValueError(f"Unsupported file format: {data_file}")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Rename Kecamatan to Kelurahan if exists
        if 'Kecamatan' in df.columns:
            df.rename(columns={'Kecamatan': 'Kelurahan'}, inplace=True)
        
        # Clean Longitude column if has extra semicolons
        if 'Longitude;;' in df.columns:
            df.rename(columns={'Longitude;;': 'Longitude'}, inplace=True)
        if 'Longitude' in df.columns:
            if df['Longitude'].dtype == object:
                df['Longitude'] = df['Longitude'].astype(str).str.replace(';', '').astype(float)
        
        # Find Latitude and Longitude columns (case-insensitive search)
        lat_col = None
        lon_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'latitude' in col_lower or 'lat' == col_lower:
                lat_col = col
            if 'longitude' in col_lower or 'lon' == col_lower or 'long' == col_lower:
                lon_col = col
        
        # Rename to standard names if found
        if lat_col and lat_col != 'Latitude':
            df.rename(columns={lat_col: 'Latitude'}, inplace=True)
        if lon_col and lon_col != 'Longitude':
            df.rename(columns={lon_col: 'Longitude'}, inplace=True)
        
        # Add default coordinates if not exist
        if 'Latitude' not in df.columns:
            print("Warning: Latitude column not found, using default value 0")
            df['Latitude'] = 0
        if 'Longitude' not in df.columns:
            print("Warning: Longitude column not found, using default value 0")
            df['Longitude'] = 0
        
        # Define brand columns
        brand_columns = [
            'SSB', 'KSN', 'SBS', 'Spc 16', 'SE12', 'SE16', 
            'BCK', 'LS 12', 'LS 16', 'TRN B', 'Spirit', 
            'RVL 16', 'LSFB 12', 'RVL M 12', 
        ]
        
        # Filter existing columns
        existing_brand_columns = [col for col in brand_columns if col in df.columns]
        
        # HITUNG TOTAL PENJUALAN dari semua jenis rokok
        df['Total_Penjualan'] = df[existing_brand_columns].sum(axis=1)
        df['Rasio_Barang_Terjual'] = df['Total_Penjualan'] / df['Toko_Membeli']
        df['Rasio_Toko_Membeli'] = df['Toko_Membeli'] / df['Toko_Didatangi']
        df['rata_rata_nilai_transaksi'] = df['Sale_Total'] / df['Toko_Membeli'] if df['Toko_Membeli'].sum() > 0 else 0
        
        # Add Toko columns if they don't exist
        if 'Toko_Didatangi' not in df.columns:
            df['Toko_Didatangi'] = 0
        if 'Toko_Membeli' not in df.columns:
            df['Toko_Membeli'] = 0
        if 'Sale_Total' not in df.columns:
            df['Sale_Total'] = 0
        
        # PILIH KOLOM UNTUK CLUSTERING: Sale_Total, Rasio_Barang_Terjual, Rasio_Toko_Membeli, Total_Penjualan, rata_rata_nilai_transaksi, Latitude, Longitude
        clustering_columns = ['Sale_Total', 'Rasio_Barang_Terjual', 'Rasio_Toko_Membeli', 'Total_Penjualan', 'rata_rata_nilai_transaksi', 'Latitude', 'Longitude']
        
        # Validate clustering columns exist
        missing_cols = [col for col in clustering_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}. Available columns: {list(df.columns)}")
        
        # Extract features for clustering
        features = df[clustering_columns].copy()
        
        # Handle missing values
        features = features.fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(features)
        
        # Hierarchical Clustering with custom parameters
        hac = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric=metric,
            linkage=linkage_method
        )
        
        df['Cluster'] = hac.fit_predict(X_scaled)
        
        # Generate and save dendrogram
        try:
            # Get kelurahan names for labels
            kelurahan_labels = df['Kelurahan'].tolist() if 'Kelurahan' in df.columns else [f'K{i}' for i in range(len(df))]
            
            # Create dendrogram using scipy linkage function
            Z = linkage(X_scaled, method=linkage_method, metric=metric)
            
            # Create figure
            plt.figure(figsize=(20, 10))
            plt.title(f'Dendrogram Hierarchical Clustering\nMethod: {linkage_method.upper()}, Metric: {metric.upper()}, Clusters: {n_clusters}', 
                     fontsize=16, fontweight='bold', pad=20)
            
            # Plot dendrogram with kelurahan names
            dendrogram(
                Z,
                labels=kelurahan_labels,
                truncate_mode='lastp',  # Show only last p merged clusters
                p=30,  # Show last 30 merges
                leaf_rotation=90,
                leaf_font_size=8,
                show_contracted=True,
                color_threshold=None,
                above_threshold_color='#0066cc'
            )
            
            plt.xlabel('Nama Kelurahan / Cluster Size', fontsize=12, fontweight='bold')
            plt.ylabel('Distance', fontsize=12, fontweight='bold')
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            # Save dendrogram image
            dendrogram_path = os.path.join(os.path.dirname(output_file), 'dendrogram.png')
            plt.savefig(dendrogram_path, dpi=120, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"Dendrogram saved to: {dendrogram_path}")
        except Exception as e:
            print(f"Warning: Could not generate dendrogram: {str(e)}", file=sys.stderr)
        
        # Calculate cluster statistics for sorting
        cluster_stats = []
        for i in range(n_clusters):
            cluster_data = df[df['Cluster'] == i]
            avg_sale = cluster_data['Sale_Total'].mean()
            avg_penjualan = cluster_data['Total_Penjualan'].mean()
            avg_toko_did = cluster_data['Toko_Didatangi'].mean()
            avg_toko_beli = cluster_data['Toko_Membeli'].mean()
            
            # Calculate overall score (weighted average)
            overall_score = (avg_sale * 0.4 + avg_penjualan * 0.4 + 
                           avg_toko_beli * 0.1 + avg_toko_did * 0.1)
            
            cluster_stats.append({
                'cluster_id': i,
                'count': len(cluster_data),
                'avg_sale_total': float(avg_sale),
                'avg_total_penjualan': float(avg_penjualan),
                'avg_toko_didatangi': float(avg_toko_did),
                'avg_toko_membeli': float(avg_toko_beli),
                'overall_score': float(overall_score)
            })
        
        # Sort clusters by overall score (descending)
        cluster_stats.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Map cluster to categories (dynamically based on n_clusters)
        # Default names based on ranking
        if n_clusters == 3:
            cluster_map = {
                cluster_stats[0]['cluster_id']: "Potensi Tinggi",
                cluster_stats[1]['cluster_id']: "Potensi Sedang",
                cluster_stats[2]['cluster_id']: "Potensi Rendah"
            }
        elif n_clusters == 2:
            cluster_map = {
                cluster_stats[0]['cluster_id']: "Potensi Tinggi",
                cluster_stats[1]['cluster_id']: "Potensi Rendah"
            }
        elif n_clusters == 4:
            cluster_map = {
                cluster_stats[0]['cluster_id']: "Potensi Sangat Tinggi",
                cluster_stats[1]['cluster_id']: "Potensi Tinggi",
                cluster_stats[2]['cluster_id']: "Potensi Sedang",
                cluster_stats[3]['cluster_id']: "Potensi Rendah"
            }
        elif n_clusters == 5:
            cluster_map = {
                cluster_stats[0]['cluster_id']: "Potensi Sangat Tinggi",
                cluster_stats[1]['cluster_id']: "Potensi Tinggi",
                cluster_stats[2]['cluster_id']: "Potensi Sedang",
                cluster_stats[3]['cluster_id']: "Potensi Rendah",
                cluster_stats[4]['cluster_id']: "Potensi Sangat Rendah"
            }
        else:
            # Generic mapping for other numbers
            cluster_map = {cluster_stats[i]['cluster_id']: f"Cluster Rank {i+1}" for i in range(n_clusters)}
        
        df['Kategori_Potensi'] = df['Cluster'].map(cluster_map)
        
        # Calculate silhouette score
        silhouette_avg = silhouette_score(X_scaled, df['Cluster'])
        
        # Get top 3 brands per kelurahan
        def get_top_brands(row, n=3):
            brand_sales = {brand: float(row.get(brand, 0)) for brand in existing_brand_columns}
            sorted_brands = sorted(brand_sales.items(), key=lambda x: x[1], reverse=True)
            return [brand for brand, _ in sorted_brands[:n]]
        
        df['Top_3_Brands'] = df.apply(lambda row: get_top_brands(row), axis=1)
        
        # Prepare output data
        output_data = df.to_dict('records')
        
        # Clean NaN values for JSON serialization
        for record in output_data:
            for key, value in record.items():
                # Handle list/array values (skip check for lists)
                if isinstance(value, list):
                    continue
                # Handle numpy arrays
                elif isinstance(value, np.ndarray):
                    continue
                # Handle scalar values that might be NaN
                elif value is None or (isinstance(value, float) and np.isnan(value)):
                    record[key] = None
                # Handle numpy numbers
                elif isinstance(value, (np.integer, np.floating)):
                    record[key] = float(value)
        
        # Create result object
        result = {
            'success': True,
            'silhouette_score': float(silhouette_avg),
            'num_clusters': n_clusters,
            'linkage': linkage_method,
            'metric': metric,
            'total_kelurahan': len(df),
            'brand_columns': existing_brand_columns,
            'cluster_stats': cluster_stats,
            'cluster_map': {str(k): v for k, v in cluster_map.items()},
            'data': output_data
        }
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"Clustering completed successfully.")
        print(f"Parameters: {n_clusters} clusters, {linkage_method} linkage, {metric} metric")
        print(f"Silhouette Score: {silhouette_avg:.3f}")
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
