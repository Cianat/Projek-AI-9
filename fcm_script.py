import pandas as pd
import numpy as np
import skfuzzy.cluster as fuzz
from sklearn.preprocessing import MinMaxScaler
import os

def read_data_file(file_path):
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
                    print(f"Mencoba membaca Excel dengan header di baris ke-{header_row_index + 1} (indeks {header_row_index})...")
                    temp_df = pd.read_excel(file_path, header=header_row_index)
                    
                    temp_df.columns = temp_df.columns.map(lambda x: x.strip() if isinstance(x, str) else x)
                    current_cols = temp_df.columns.tolist()
                    print(f"  Kolom terdeteksi pada percobaan ini: {current_cols}")

                    is_likely_header = not all(str(col).startswith('Unnamed:') for col in current_cols) and \
                                       sum(expected_col in current_cols for expected_col in expected_cols_subset) >= 5 

                    if is_likely_header:
                        df = temp_df
                        print(f"  BERHASIL! Header kemungkinan ditemukan di baris ke-{header_row_index + 1}.")
                        header_found = True
                        break 
                    else:
                        print(f"  Header di baris ke-{header_row_index + 1} sepertinya bukan header yang dicari.")

                except Exception as read_err:
                    print(f"  Gagal membaca dengan header di baris ke-{header_row_index + 1}: {read_err}")
            
            if not header_found:
                print("Tidak dapat menemukan header yang sesuai secara otomatis setelah mencoba beberapa baris.")
                print("Mencoba membaca secara default (Pandas menebak header)...")
                df = pd.read_excel(file_path) 
                if df is not None:
                     df.columns = df.columns.map(lambda x: x.strip() if isinstance(x, str) else x)

        else:
            raise ValueError(f"Format file tidak didukung: {file_extension}. Gunakan .csv atau .xlsx")

        if df is None:
            raise ValueError("Gagal membaca file atau file kosong.")

        print("\nKolom terdeteksi setelah semua proses pembacaan:")
        print(df.columns.tolist())
        return df

    except FileNotFoundError:
        print(f"Error: File tidak ditemukan di path '{file_path}'")
        return None
    except Exception as e:
        print(f"Terjadi error yang tidak terduga saat membaca file: {e}")
        return None

def calculate_fcm_clusters(df, random_seed=42): 
    try:
        np.random.seed(random_seed)
        print(f"\nMenggunakan random seed: {random_seed} untuk konsistensi hasil FCM.")

        feature_columns = [
            'Rata-rata Suhu (°C)', 'Rata-rata Curah Hujan (mm)', 
            'Rata-rata Lama Penyinaran Matahari (jam)', 'Rata-rata pH', 
            'Rata-rata Kelembapan Tanah', 'Rata-rata Ketinggian Tanah'
        ]
        id_columns = ['No', 'Nama Tanaman']
        all_needed_columns = id_columns + feature_columns
        
        missing_cols = [col for col in all_needed_columns if col not in df.columns]
        if missing_cols:
            print(f"\nKolom yang ada di DataFrame sebelum clustering: {df.columns.tolist()}")
            raise ValueError(f"KESALAHAN: Kolom berikut tidak ditemukan di file setelah dibaca: {missing_cols}. Pastikan nama kolom di file Excel Anda sesuai dan header terbaca dengan benar.")

        data_for_clustering = df[feature_columns].copy()
        original_data_selected = df[all_needed_columns].copy()

        for col in feature_columns:
            data_for_clustering[col] = pd.to_numeric(data_for_clustering[col], errors='coerce')
        
        if data_for_clustering.isnull().any().any():
            print("Menangani nilai NaN yang ditemukan setelah konversi numerik:")
            for col in feature_columns:
                if data_for_clustering[col].isnull().any():
                    mean_val = data_for_clustering[col].mean()
                    if pd.isnull(mean_val): 
                        print(f"  PERINGATAN: Kolom '{col}' seluruhnya NaN atau tidak dapat dihitung rata-ratanya. Mengisi nilai NaN di kolom ini dengan 0.")
                        data_for_clustering[col] = data_for_clustering[col].fillna(0)
                    else:
                        print(f"  Nilai NaN di kolom '{col}' diisi dengan rata-rata: {mean_val:.2f}")
                        data_for_clustering[col] = data_for_clustering[col].fillna(mean_val)
        
        if data_for_clustering.isnull().any().any():
            nan_cols_after_fill = data_for_clustering.columns[data_for_clustering.isnull().any()].tolist()
            raise ValueError(f"Masih ada nilai NaN di data setelah proses pengisian pada kolom: {nan_cols_after_fill}. Proses imputasi gagal. Periksa data sumber Anda.")

        scaler = MinMaxScaler()
        if not np.issubdtype(data_for_clustering.values.dtype, np.number) and not data_for_clustering.empty:
            all_numeric = True
            for col in data_for_clustering.columns:
                try:
                    pd.to_numeric(data_for_clustering[col])
                except ValueError:
                    all_numeric = False
                    print(f"Kolom '{col}' tidak dapat dikonversi menjadi numerik sepenuhnya.")
                    break
            if not all_numeric:
                raise ValueError("Data untuk clustering mengandung nilai non-numerik yang tidak dapat dinormalisasi.")
        
        if data_for_clustering.empty:
            raise ValueError("Data untuk clustering kosong setelah diproses.")
            
        normalized_data = scaler.fit_transform(data_for_clustering)

        n_clusters = 3
        m = 2.0  
        error = 0.001  
        maxiter = 100  

        data_transposed = normalized_data.T

        if data_transposed.shape[1] < n_clusters:
            raise ValueError(f"Jumlah sampel data ({data_transposed.shape[1]}) lebih sedikit dari jumlah cluster yang diminta ({n_clusters}). Tidak dapat melanjutkan FCM.")

        cntr, u, u0, d, jm, p, fpc = fuzz.cmeans(
            data_transposed, n_clusters, m, error=error, maxiter=maxiter, init=None, seed=random_seed
        )

        cluster_membership = np.argmax(u, axis=0)

        results_df = original_data_selected.copy()
        
        for i in range(n_clusters):
            results_df[f'Membership_Cluster_{i+1}'] = u[i, :]
        results_df['Assigned_Cluster'] = cluster_membership + 1

        original_scale_centers = scaler.inverse_transform(cntr)
        centers_df = pd.DataFrame(original_scale_centers, columns=feature_columns)
        
        print("\nPusat Cluster (dalam skala asli):")
        print(centers_df)
        print(f"\nKoefisien Partisi Fuzzy (FPC): {fpc:.4f}")
        print(f"(Semakin dekat FPC ke 1, semakin baik pemisahan clusternya)")
        print(f"Jumlah iterasi: {p}")

        return results_df, centers_df

    except ValueError as ve:
        print(f"ValueError dalam proses clustering: {ve}")
        return None, None
    except Exception as e:
        print(f"Terjadi error yang tidak terduga saat clustering: {e}")
        import traceback
        traceback.print_exc() 
        return None, None

file_path = 'Dataset.xlsx'
dataframe = read_data_file(file_path)

if dataframe is not None:
    required_cols_for_clustering = [
        'No', 'Nama Tanaman', 'Rata-rata Suhu (°C)', 'Rata-rata Curah Hujan (mm)', 
        'Rata-rata Lama Penyinaran Matahari (jam)', 'Rata-rata pH', 
        'Rata-rata Kelembapan Tanah', 'Rata-rata Ketinggian Tanah'
    ]
    if all(col in dataframe.columns for col in required_cols_for_clustering):
        print("\nMemulai proses clustering dengan nama kolom baru...")
        results_df, cluster_centers_df = calculate_fcm_clusters(dataframe, random_seed=42) 
        if results_df is not None:
            print("\n--- Hasil Clustering FCM ---")
            pd.set_option('display.max_columns', None) 
            pd.set_option('display.width', 1200) 
            print(results_df)
    else:
        print(f"\nGAGAL melanjutkan ke clustering karena kolom yang dibutuhkan tidak lengkap setelah pembacaan file.")
        print(f"  Kolom yang dibutuhkan: {required_cols_for_clustering}")
        print(f"  Kolom yang terdeteksi di file (setelah semua upaya baca): {dataframe.columns.tolist()}")
        print("\nSARAN: ")
        print("1. Pastikan file Excel Anda ('Dataset.xlsx') memiliki nama kolom yang persis seperti yang didefinisikan (misalnya, 'Rata-rata Suhu (°C)', 'No', dll.) dan berisi data numerik.")
        print("2. Periksa kembali output 'Mencoba membaca Excel dengan header di baris ke-X...' untuk memastikan header terbaca dengan benar.")
        print("3. Jika kolom-kolom fitur memang kosong atau datanya tidak valid, skrip ini akan mencoba mengisi nilai yang hilang dengan 0 (untuk kolom yang seluruhnya NaN) atau rata-rata (untuk NaN individual) dan memberikan peringatan.")
