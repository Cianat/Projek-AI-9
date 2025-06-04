from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import numpy as np
import skfuzzy.cluster as fuzz
from sklearn.preprocessing import MinMaxScaler
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

def calculate_recommendation(input_data):
    try:
        # Read the dataset
        file_path = 'Dataset.xlsx'
        df = pd.read_excel(file_path)
        
        # Define feature columns
        feature_columns = [
            'Rata-rata Suhu (°C)', 'Rata-rata Curah Hujan (mm)', 
            'Rata-rata Lama Penyinaran Matahari (jam)', 'Rata-rata pH', 
            'Rata-rata Kelembapan Tanah', 'Rata-rata Ketinggian Tanah'
        ]
        
        # Prepare data for clustering
        data_for_clustering = df[feature_columns].copy()
        
        # Normalize data
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(data_for_clustering)
        
        # Normalize input data using the same scaler
        input_normalized = scaler.transform([input_data])
        
        # FCM parameters
        n_clusters = 3
        m = 2.0
        error = 0.001
        maxiter = 100
        
        # Run FCM
        cntr, u, _, _, _, _, _ = fuzz.cmeans(
            normalized_data.T, n_clusters, m, error=error, maxiter=maxiter, init=None, seed=42
        )
        
        # Find the closest cluster for input data
        distances = np.zeros((input_normalized.shape[0], cntr.shape[0]))
        for i, center in enumerate(cntr):
            distances[:, i] = np.linalg.norm(input_normalized - center, axis=1)
        
        closest_cluster = int(np.argmin(distances[0])) + 1  # Convert np.int64 to Python int
        
        # Get plants from the same cluster
        cluster_membership = np.argmax(u, axis=0)
        cluster_plants = df[cluster_membership == (closest_cluster - 1)]
        
        # Return top 5 recommended plants
        recommendations = cluster_plants['Nama Tanaman'].head(5).tolist()
        return recommendations, closest_cluster
        
    except Exception as e:
        print(f"Error in calculation: {str(e)}")
        return [], 0

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Get form data
        input_values = [
            float(request.form['suhu']),
            float(request.form['curah_hujan']),
            float(request.form['penyinaran']),
            float(request.form['ph']),
            float(request.form['kelembapan']),
            float(request.form['ketinggian'])
        ]
        
        recommendations, cluster = calculate_recommendation(input_values)
        
        if recommendations:
            return render_template('index.html', 
                                recommendations=recommendations, 
                                cluster=cluster,
                                input_values={
                                    'suhu': input_values[0],
                                    'curah_hujan': input_values[1],
                                    'penyinaran': input_values[2],
                                    'ph': input_values[3],
                                    'kelembapan': input_values[4],
                                    'ketinggian': input_values[5]
                                })
        else:
            flash('Tidak dapat menghasilkan rekomendasi. Silakan cek input Anda.', 'error')
            return redirect(url_for('home'))
            
    except ValueError as ve:
        flash('Mohon isi semua field dengan angka yang valid.', 'error')
        return redirect(url_for('home'))
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True) 