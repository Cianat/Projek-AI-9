import pandas as pd
import numpy as np
import skfuzzy.cluster as fuzz
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import cdist # Untuk menghitung jarak Euclidean
import os
import traceback

# =============================================================================
# BAGIAN 1: FUNGSI-FUNGSI DARI SCRIPT ASLI (fcm_script.py)
# Fungsi-fungsi ini disalin langsung untuk membaca data dan melakukan clustering.
# =============================================================================

def read_data_file(file_path):
    """
    Membaca data dari file .csv atau .xlsx secara otomatis,
    dengan penanganan header yang lebih baik dan debugging untuk .xlsx.
    """
    _, file_extension = os.path.splitext(file_path)
    df = None
    expected_cols_subset = [
        'No', 'Nama Tanaman', 'Rata-rata Suhu (°C)', 'Rata-rata Curah Hujan (mm)', 
        'Rata-rata Lama Penyinaran Matahari (jam)', 'Rata-rata pH', 
        'Rata-rata Kelembapan Tanah', 'Rata-rata Ketinggian Tanah'
    ]

    try:
        if file_extension.lower() == '.csv':
            print("Membaca file CSV...")
            df = pd.read_csv(file_path, on_bad_lines='skip')
        elif file_extension.lower() == '.xlsx':
            print("Membaca file Excel (.xlsx)...")
            possible_header_rows = list(range(10)) 
            header_found = False
            for header_row_index in possible_header_rows:
                try:
                    temp_df = pd.read_excel(file_path, header=header_row_index)
                    temp_df.columns = temp_df.columns.map(lambda x: x.strip() if isinstance(x, str) else x)
                    current_cols = temp_df.columns.tolist()
                    is_likely_header = not all(str(col).startswith('Unnamed:') for col in current_cols) and \
                                       sum(expected_col in current_cols for expected_col in expected_cols_subset) >= 5

                    if is_likely_header:
                        df = temp_df
                        print(f"  BERHASIL! Header ditemukan di baris ke-{header_row_index + 1}.")
                        header_found = True
                        break 
                except Exception:
                    continue
            
            if not header_found:
                print("Tidak dapat menemukan header yang sesuai secara otomatis. Membaca secara default...")
                df = pd.read_excel(file_path) 
                if df is not None:
                    df.columns = df.columns.map(lambda x: x.strip() if isinstance(x, str) else x)
        else:
            raise ValueError(f"Format file tidak didukung: {file_extension}. Gunakan .csv atau .xlsx")

        if df is None:
            raise ValueError("Gagal membaca file atau file kosong.")

        return df

    except FileNotFoundError:
        print(f"Error: File tidak ditemukan di path '{file_path}'")
        return None
    except Exception as e:
        print(f"Terjadi error yang tidak terduga saat membaca file: {e}")
        return None

def calculate_fcm_clusters(df):
    """
    Melakukan clustering FCM pada data tanaman dari DataFrame yang sudah dibaca.
    """
    try:
        feature_columns = [
            'Rata-rata Suhu (°C)', 'Rata-rata Curah Hujan (mm)', 
            'Rata-rata Lama Penyinaran Matahari (jam)', 'Rata-rata pH', 
            'Rata-rata Kelembapan Tanah', 'Rata-rata Ketinggian Tanah'
        ]
        id_columns = ['No', 'Nama Tanaman']
        all_needed_columns = id_columns + feature_columns
        
        missing_cols = [col for col in all_needed_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"KESALAHAN: Kolom berikut tidak ditemukan: {missing_cols}.")

        data_for_clustering = df[feature_columns].copy()
        original_data_selected = df[all_needed_columns].copy()

        for col in feature_columns:
            data_for_clustering[col] = pd.to_numeric(data_for_clustering[col], errors='coerce')
        
        if data_for_clustering.isnull().any().any():
            print("Menangani nilai NaN yang ditemukan...")
            for col in feature_columns:
                if data_for_clustering[col].isnull().any():
                    mean_val = data_for_clustering[col].mean()
                    data_for_clustering[col] = data_for_clustering[col].fillna(mean_val)
        
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(data_for_clustering)

        n_clusters = 3
        m = 2.0
        error = 0.001
        maxiter = 100
        data_transposed = normalized_data.T

        if data_transposed.shape[1] < n_clusters:
            raise ValueError(f"Jumlah sampel data ({data_transposed.shape[1]}) lebih sedikit dari jumlah cluster ({n_clusters}).")

        cntr, u, _, _, _, _, fpc = fuzz.cmeans(
            data_transposed, n_clusters, m, error=error, maxiter=maxiter, init=None
        )

        cluster_membership = np.argmax(u, axis=0)
        results_df = original_data_selected.copy()
        results_df['Assigned_Cluster'] = cluster_membership + 1

        original_scale_centers = scaler.inverse_transform(cntr)
        centers_df = pd.DataFrame(original_scale_centers, columns=feature_columns)
        
        print(f"\nKoefisien Partisi Fuzzy (FPC): {fpc:.4f} (Semakin dekat ke 1, semakin baik)")
        return results_df, centers_df

    except Exception as e:
        print(f"Terjadi error saat clustering: {e}")
        traceback.print_exc()
        return None, None

# =============================================================================
# BAGIAN 2: FUNGSI BARU UNTUK SISTEM REKOMENDASI
# =============================================================================

def get_user_input(feature_columns):
    """
    Meminta pengguna untuk memasukkan data kondisi lingkungan dan memvalidasinya.
    Mengembalikan DataFrame pandas dengan data dari pengguna.
    """
    print("\n" + "="*40)
    print(" SILAKAN MASUKKAN KONDISI LAHAN ANDA ".center(40, "="))
    print("="*40)
    user_data = {}
    for col in feature_columns:
        while True:
            try:
                # Membersihkan nama kolom untuk tampilan input yang lebih baik
                prompt_message = col.replace('Rata-rata', '').replace('()', '').strip()
                value = float(input(f"Masukkan {prompt_message}: "))
                user_data[col] = value
                break
            except ValueError:
                print("Input tidak valid! Harap masukkan dalam bentuk angka.")
    return pd.DataFrame([user_data])

def find_best_cluster(user_input_df, centers_df):
    """
    Menemukan cluster terdekat dengan input pengguna menggunakan Jarak Euclidean.
    Mengembalikan indeks dari cluster terbaik (dimulai dari 0).
    """
    # Menghitung jarak Euclidean dari input pengguna ke setiap pusat cluster
    distances = cdist(user_input_df.values, centers_df.values, 'euclidean')
    # Mencari indeks cluster dengan jarak minimum
    best_cluster_index = np.argmin(distances)
    return best_cluster_index

def recommend_plants(best_cluster_index, results_df):
    """
    Memberikan rekomendasi tanaman dari cluster yang paling cocok.
    """
    # Nomor cluster di 'Assigned_Cluster' adalah 1-based (1, 2, 3, ...)
    best_cluster_number = best_cluster_index + 1
    
    print("\n" + "="*40)
    print(" HASIL REKOMENDASI ".center(40, "="))
    print("="*40)
    print(f"✅ Kondisi Anda paling cocok dengan karakteristik Cluster {best_cluster_number}.")
    
    # Filter hasil untuk mendapatkan tanaman yang termasuk dalam cluster terbaik
    recommended_plants_df = results_df[results_df['Assigned_Cluster'] == best_cluster_number]
    
    if recommended_plants_df.empty:
        print("Tidak ada tanaman yang ditemukan untuk cluster ini.")
    else:
        print("\n🌱 Tanaman yang cocok untuk ditanam di lokasi Anda adalah:")
        # Cetak daftar nama tanaman
        for plant_name in recommended_plants_df['Nama Tanaman']:
            print(f"   - {plant_name}")

# =============================================================================
# BAGIAN 3: FUNGSI UTAMA UNTUK MENJALANKAN PROGRAM
# =============================================================================

def main():
    """
    Fungsi utama untuk menjalankan sistem rekomendasi tanaman.
    """
    # --- Langkah 1: Jalankan clustering FCM awal untuk membangun model ---
    file_path = 'Dataset.xlsx' 
    print(f"Membaca dan memproses data dari '{file_path}' untuk membangun model cluster...")
    
    dataframe = read_data_file(file_path)
    
    if dataframe is None:
        print("\nProgram tidak dapat melanjutkan karena gagal membaca file data.")
        return

    results_df, cluster_centers_df = calculate_fcm_clusters(dataframe)

    if results_df is None or cluster_centers_df is None:
        print("\nProgram tidak dapat melanjutkan karena proses clustering gagal.")
        return
    
    print("\n--- Model Cluster Berhasil Dibuat ---")
    print("Pusat cluster (centroid) yang digunakan untuk acuan rekomendasi:")
    print(cluster_centers_df.round(2))

    # Ekstrak nama kolom fitur yang digunakan untuk clustering
    feature_columns = cluster_centers_df.columns.tolist()

    # --- Langkah 2: Loop interaktif untuk rekomendasi kepada pengguna ---
    while True:
        user_input_df = get_user_input(feature_columns)
        
        best_cluster_index = find_best_cluster(user_input_df, cluster_centers_df)
        
        recommend_plants(best_cluster_index, results_df)
        
        # Tanya pengguna apakah ingin mencoba lagi
        another_go = input("\nApakah Anda ingin mencoba dengan data lain? (y/n): ").lower()
        if another_go != 'y':
            print("\nTerima kasih telah menggunakan sistem rekomendasi. Sampai jumpa! 👋")
            break

if __name__ == "__main__":
    main()