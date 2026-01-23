import sys
import json
import pandas as pd
import geopandas as gpd

def main():
    if len(sys.argv) != 4:
        print("Usage: python convert_shapefile_to_geojson.py <shapefile_path> <cluster_json> <output_geojson>")
        sys.exit(1)
    
    shapefile_path = sys.argv[1]
    cluster_json_path = sys.argv[2]
    output_geojson = sys.argv[3]
    
    try:
        # Load shapefile
        print("Loading shapefile...")
        gdf_kelurahan = gpd.read_file(shapefile_path)
        
        # Load clustering results
        print("Loading cluster results...")
        with open(cluster_json_path, 'r', encoding='utf-8') as f:
            cluster_data = json.load(f)
        
        # Convert to DataFrame
        df_cluster = pd.DataFrame(cluster_data['data'])
        
        # Standarisasi nama kolom kelurahan di shapefile
        # Coba berbagai kemungkinan nama kolom
        kelurahan_col = None
        for col in ['WADMKD', 'NAMOBJ', 'DESA', 'KELURAHAN', 'NAME']:
            if col in gdf_kelurahan.columns:
                kelurahan_col = col
                break
        
        if kelurahan_col is None:
            print("Available columns in shapefile:", gdf_kelurahan.columns.tolist())
            raise ValueError("Could not find kelurahan name column in shapefile")
        
        print(f"Using column: {kelurahan_col}")
        
        # Standarisasi nama kelurahan
        gdf_kelurahan['kelurahan_std'] = gdf_kelurahan[kelurahan_col].str.strip().str.lower()
        df_cluster['kelurahan_std'] = df_cluster['Kelurahan'].str.strip().str.lower()
        
        # Merge shapefile dengan data clustering
        merge_cols = ['kelurahan_std', 'Cluster', 'Kategori_Potensi', 'Total_Penjualan', 'Top_3_Brands', 'Toko_Didatangi', 'Toko_Membeli']
        
        # Add Sale_Total if exists
        if 'Sale_Total' in df_cluster.columns:
            merge_cols.append('Sale_Total')
        
        gdf_merged = gdf_kelurahan.merge(
            df_cluster[merge_cols],
            on='kelurahan_std',
            how='left'
        )
        
        print(f"Total features: {len(gdf_merged)}")
        print(f"Matched with cluster data: {gdf_merged['Cluster'].notna().sum()}")
        
        # Convert to WGS84 (EPSG:4326) for web mapping
        if gdf_merged.crs is not None and gdf_merged.crs != 'EPSG:4326':
            gdf_merged = gdf_merged.to_crs('EPSG:4326')
        
        # Clean up columns for GeoJSON
        gdf_merged['Cluster'] = gdf_merged['Cluster'].fillna(-1).astype(int)
        gdf_merged['Total_Penjualan'] = gdf_merged['Total_Penjualan'].fillna(0).astype(float)
        gdf_merged['Toko_Didatangi'] = gdf_merged['Toko_Didatangi'].fillna(0).astype(int)
        gdf_merged['Toko_Membeli'] = gdf_merged['Toko_Membeli'].fillna(0).astype(int)
        
        # Handle Sale_Total if exists
        if 'Sale_Total' in gdf_merged.columns:
            gdf_merged['Sale_Total'] = gdf_merged['Sale_Total'].fillna(0).astype(float)
        
        # Convert Top_3_Brands list to string
        if 'Top_3_Brands' in gdf_merged.columns:
            gdf_merged['Top_3_Brands'] = gdf_merged['Top_3_Brands'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else ''
            )
        
        # Select columns to include in GeoJSON
        columns_to_keep = [kelurahan_col, 'Cluster', 'Kategori_Potensi', 'Total_Penjualan', 'Toko_Didatangi', 'Toko_Membeli', 'Top_3_Brands', 'geometry']
        
        # Add Sale_Total if exists
        if 'Sale_Total' in gdf_merged.columns:
            columns_to_keep.insert(4, 'Sale_Total')
        
        columns_to_keep = [col for col in columns_to_keep if col in gdf_merged.columns]
        gdf_output = gdf_merged[columns_to_keep]
        
        # Save to GeoJSON
        print(f"Saving to {output_geojson}...")
        gdf_output.to_file(output_geojson, driver='GeoJSON')
        
        print("GeoJSON created successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
