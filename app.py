from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# --- BAGIAN 1: FUNGSI KEANGGOTAAN (SUDAH AKURAT) ---

def suhu_membership(x):
    if x <= 20:
        rendah = 1.0
    elif 20 < x < 25:
        rendah = (25 - x) / (25 - 20)
    else:
        rendah = 0.0
    if 20 < x <= 22.5:
        sedang = (x - 20) / (22.5 - 20)
    elif 22.5 < x < 25:
        sedang = (25 - x) / (25 - 22.5)
    else:
        sedang = 0.0
    if x <= 20:
        tinggi = 0.0
    elif 20 < x < 25:
        tinggi = (x - 20) / (25 - 20)
    else:
        tinggi = 1.0
    return {'Rendah': rendah, 'Sedang': sedang, 'Tinggi': tinggi}

def curah_hujan_membership(x):
    if x <= 500:
        rendah = 1.0
    elif 500 < x < 1000:
        rendah = (1000 - x) / (1000 - 500)
    else:
        rendah = 0.0
    if 500 < x <= 750:
        sedang = (x - 500) / (750 - 500)
    elif 750 < x < 1000:
        sedang = (1000 - x) / (1000 - 750)
    else:
        sedang = 0.0
    if x <= 500:
        tinggi = 0.0
    elif 500 < x < 1000:
        tinggi = (x - 500) / (1000 - 500)
    else:
        tinggi = 1.0
    return {'Rendah': rendah, 'Sedang': sedang, 'Tinggi': tinggi}
    
def penyinaran_membership(x):
    if x <= 5:
        rendah = 1.0
    elif 5 < x < 8:
        rendah = (8 - x) / (8 - 5)
    else:
        rendah = 0.0
    if 5 < x <= 6.5:
        sedang = (x - 5) / (6.5 - 5)
    elif 6.5 < x < 8:
        sedang = (8 - x) / (8 - 6.5)
    else:
        sedang = 0.0
    if x <= 5:
        tinggi = 0.0
    elif 5 < x < 8:
        tinggi = (x - 5) / (8 - 5)
    else:
        tinggi = 1.0
    return {'Rendah': rendah, 'Sedang': sedang, 'Tinggi': tinggi}

def ph_membership(x):
    if x <= 5.5:
        asam = 1.0
    elif 5.5 < x < 7:
        asam = (7 - x) / (7 - 5.5)
    else:
        asam = 0.0
    if 5.5 < x <= 6.25:
        netral = (x - 5.5) / (6.25 - 5.5)
    elif 6.25 < x < 7:
        netral = (7 - x) / (7 - 6.25)
    else:
        netral = 0.0
    if x <= 5.5:
        basa = 0.0
    elif 5.5 < x < 7:
        basa = (x - 5.5) / (7 - 5.5)
    else:
        basa = 1.0
    return {'Asam': asam, 'Netral': netral, 'Basa': basa}

def kelembapan_membership(x):
    if x <= 30:
        rendah = 1.0
    elif 30 < x < 50:
        rendah = (50 - x) / (50 - 30)
    else:
        rendah = 0.0
    if 30 < x <= 50:
        sedang = (x - 30) / (50 - 30)
    elif 50 < x < 70:
        sedang = (70 - x) / (70 - 50)
    else:
        sedang = 0.0
    if x <= 50:
        tinggi = 0.0
    elif 50 < x < 70:
        tinggi = (x - 50) / (70 - 50)
    else:
        tinggi = 1.0
    return {'Rendah': rendah, 'Sedang': sedang, 'Tinggi': tinggi}

def ketinggian_membership(x):
    if x <= 200:
        rendah = 1.0
    elif 200 < x < 450:
        rendah = (450 - x) / (450 - 200)
    else:
        rendah = 0.0
    if 200 < x <= 450:
        sedang = (x - 200) / (450 - 200)
    elif 450 < x < 700:
        sedang = (700 - x) / (700 - 450)
    else:
        sedang = 0.0
    if x <= 450:
        tinggi = 0.0
    elif 450 < x < 700:
        tinggi = (x - 450) / (700 - 450)
    else:
        tinggi = 1.0
    return {'Rendah': rendah, 'Sedang': sedang, 'Tinggi': tinggi}


# --- BAGIAN 2: IMPLEMENTASI ATURAN FUZZY (81 ATURAN FINAL) ---

def evaluate_rules(inputs):
    print("\n" + "="*50)
    print("MEMULAI PROSES DEBUGGING ATURAN FUZZY (81 ATURAN FINAL)")
    print("="*50)

    # Fuzzifikasi
    suhu = suhu_membership(inputs['suhu'])
    hujan = curah_hujan_membership(inputs['curah_hujan'])
    sinar = penyinaran_membership(inputs['penyinaran'])
    ph = ph_membership(inputs['ph'])
    lembab = kelembapan_membership(inputs['kelembapan'])
    tinggi = ketinggian_membership(inputs['ketinggian'])

    print("\n[LANGKAH 1: HASIL FUZZIFIKASI INPUT]")
    print(f"  Suhu ({inputs['suhu']}): {suhu}")
    print(f"  Curah Hujan ({inputs['curah_hujan']}): {hujan}")
    print(f"  Penyinaran ({inputs['penyinaran']}): {sinar}")
    print(f"  pH ({inputs['ph']}): {ph}")
    print(f"  Kelembapan ({inputs['kelembapan']}): {lembab}")
    print(f"  Ketinggian ({inputs['ketinggian']}): {tinggi}")
    
    # Hitung kekuatan setiap aturan sesuai 81 aturan baru
    r = {}
    # Suhu Rendah
    r[1]  = min(suhu['Rendah'], hujan['Rendah'], tinggi['Rendah'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[2]  = min(suhu['Rendah'], hujan['Rendah'], tinggi['Rendah'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[3]  = min(suhu['Rendah'], hujan['Rendah'], tinggi['Rendah'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[4]  = min(suhu['Rendah'], hujan['Rendah'], tinggi['Sedang'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[5]  = min(suhu['Rendah'], hujan['Rendah'], tinggi['Sedang'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[6]  = min(suhu['Rendah'], hujan['Rendah'], tinggi['Sedang'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[7]  = min(suhu['Rendah'], hujan['Rendah'], tinggi['Tinggi'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[8]  = min(suhu['Rendah'], hujan['Rendah'], tinggi['Tinggi'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[9]  = min(suhu['Rendah'], hujan['Rendah'], tinggi['Tinggi'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[10] = min(suhu['Rendah'], hujan['Sedang'], tinggi['Rendah'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[11] = min(suhu['Rendah'], hujan['Sedang'], tinggi['Rendah'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[12] = min(suhu['Rendah'], hujan['Sedang'], tinggi['Rendah'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[13] = min(suhu['Rendah'], hujan['Sedang'], tinggi['Sedang'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[14] = min(suhu['Rendah'], hujan['Sedang'], tinggi['Sedang'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[15] = min(suhu['Rendah'], hujan['Sedang'], tinggi['Sedang'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[16] = min(suhu['Rendah'], hujan['Sedang'], tinggi['Tinggi'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[17] = min(suhu['Rendah'], hujan['Sedang'], tinggi['Tinggi'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[18] = min(suhu['Rendah'], hujan['Sedang'], tinggi['Tinggi'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[19] = min(suhu['Rendah'], hujan['Tinggi'], tinggi['Rendah'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[20] = min(suhu['Rendah'], hujan['Tinggi'], tinggi['Rendah'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[21] = min(suhu['Rendah'], hujan['Tinggi'], tinggi['Rendah'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[22] = min(suhu['Rendah'], hujan['Tinggi'], tinggi['Sedang'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[23] = min(suhu['Rendah'], hujan['Tinggi'], tinggi['Sedang'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[24] = min(suhu['Rendah'], hujan['Tinggi'], tinggi['Sedang'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[25] = min(suhu['Rendah'], hujan['Tinggi'], tinggi['Tinggi'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[26] = min(suhu['Rendah'], hujan['Tinggi'], tinggi['Tinggi'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[27] = min(suhu['Rendah'], hujan['Tinggi'], tinggi['Tinggi'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    # Suhu Sedang
    r[28] = min(suhu['Sedang'], hujan['Rendah'], tinggi['Rendah'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[29] = min(suhu['Sedang'], hujan['Rendah'], tinggi['Rendah'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[30] = min(suhu['Sedang'], hujan['Rendah'], tinggi['Rendah'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[31] = min(suhu['Sedang'], hujan['Rendah'], tinggi['Sedang'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[32] = min(suhu['Sedang'], hujan['Rendah'], tinggi['Sedang'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[33] = min(suhu['Sedang'], hujan['Rendah'], tinggi['Sedang'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[34] = min(suhu['Sedang'], hujan['Rendah'], tinggi['Tinggi'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[35] = min(suhu['Sedang'], hujan['Rendah'], tinggi['Tinggi'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[36] = min(suhu['Sedang'], hujan['Rendah'], tinggi['Tinggi'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[37] = min(suhu['Sedang'], hujan['Sedang'], tinggi['Rendah'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[38] = min(suhu['Sedang'], hujan['Sedang'], tinggi['Rendah'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[39] = min(suhu['Sedang'], hujan['Sedang'], tinggi['Rendah'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[40] = min(suhu['Sedang'], hujan['Sedang'], tinggi['Sedang'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[41] = min(suhu['Sedang'], hujan['Sedang'], tinggi['Sedang'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[42] = min(suhu['Sedang'], hujan['Sedang'], tinggi['Sedang'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[43] = min(suhu['Sedang'], hujan['Sedang'], tinggi['Tinggi'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[44] = min(suhu['Sedang'], hujan['Sedang'], tinggi['Tinggi'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[45] = min(suhu['Sedang'], hujan['Sedang'], tinggi['Tinggi'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[46] = min(suhu['Sedang'], hujan['Tinggi'], tinggi['Rendah'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[47] = min(suhu['Sedang'], hujan['Tinggi'], tinggi['Rendah'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[48] = min(suhu['Sedang'], hujan['Tinggi'], tinggi['Rendah'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[49] = min(suhu['Sedang'], hujan['Tinggi'], tinggi['Sedang'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[50] = min(suhu['Sedang'], hujan['Tinggi'], tinggi['Sedang'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[51] = min(suhu['Sedang'], hujan['Tinggi'], tinggi['Sedang'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[52] = min(suhu['Sedang'], hujan['Tinggi'], tinggi['Tinggi'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[53] = min(suhu['Sedang'], hujan['Tinggi'], tinggi['Tinggi'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[54] = min(suhu['Sedang'], hujan['Tinggi'], tinggi['Tinggi'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    # Suhu Tinggi
    r[55] = min(suhu['Tinggi'], hujan['Rendah'], tinggi['Rendah'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[56] = min(suhu['Tinggi'], hujan['Rendah'], tinggi['Rendah'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[57] = min(suhu['Tinggi'], hujan['Rendah'], tinggi['Rendah'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[58] = min(suhu['Tinggi'], hujan['Rendah'], tinggi['Sedang'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[59] = min(suhu['Tinggi'], hujan['Rendah'], tinggi['Sedang'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[60] = min(suhu['Tinggi'], hujan['Rendah'], tinggi['Sedang'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[61] = min(suhu['Tinggi'], hujan['Rendah'], tinggi['Tinggi'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[62] = min(suhu['Tinggi'], hujan['Rendah'], tinggi['Tinggi'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[63] = min(suhu['Tinggi'], hujan['Rendah'], tinggi['Tinggi'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[64] = min(suhu['Tinggi'], hujan['Sedang'], tinggi['Rendah'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[65] = min(suhu['Tinggi'], hujan['Sedang'], tinggi['Rendah'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[66] = min(suhu['Tinggi'], hujan['Sedang'], tinggi['Rendah'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[67] = min(suhu['Tinggi'], hujan['Sedang'], tinggi['Sedang'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[68] = min(suhu['Tinggi'], hujan['Sedang'], tinggi['Sedang'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[69] = min(suhu['Tinggi'], hujan['Sedang'], tinggi['Sedang'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[70] = min(suhu['Tinggi'], hujan['Sedang'], tinggi['Tinggi'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[71] = min(suhu['Tinggi'], hujan['Sedang'], tinggi['Tinggi'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[72] = min(suhu['Tinggi'], hujan['Sedang'], tinggi['Tinggi'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[73] = min(suhu['Tinggi'], hujan['Tinggi'], tinggi['Rendah'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[74] = min(suhu['Tinggi'], hujan['Tinggi'], tinggi['Rendah'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[75] = min(suhu['Tinggi'], hujan['Tinggi'], tinggi['Rendah'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[76] = min(suhu['Tinggi'], hujan['Tinggi'], tinggi['Sedang'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[77] = min(suhu['Tinggi'], hujan['Tinggi'], tinggi['Sedang'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[78] = min(suhu['Tinggi'], hujan['Tinggi'], tinggi['Sedang'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    r[79] = min(suhu['Tinggi'], hujan['Tinggi'], tinggi['Tinggi'], sinar['Rendah'], ph['Netral'], lembab['Sedang'])
    r[80] = min(suhu['Tinggi'], hujan['Tinggi'], tinggi['Tinggi'], sinar['Sedang'], ph['Netral'], lembab['Sedang'])
    r[81] = min(suhu['Tinggi'], hujan['Tinggi'], tinggi['Tinggi'], sinar['Tinggi'], ph['Netral'], lembab['Sedang'])
    # Aturan R4 (pH Basa) dan aturan lain yang mungkin menggunakan pH Asam/Basa atau Kelembaban selain Sedang, belum ditambahkan ke daftar ini
    # Jika ada aturan dengan pH atau Kelembaban berbeda, tambahkan di sini

    print("\n[LANGKAH 2: KEKUATAN SETIAP ATURAN (R1-R81)]")
    for i in range(1, 82):
        print(f"  Kekuatan Aturan R{i}: {r.get(i, 'N/A')}") # Dihapus .4f untuk menghindari error jika N/A

    # Agregasi aturan ke kelompok sesuai 81 aturan baru
    kelompok_strength = {1: 0, 2: 0, 3: 0}
    kelompok_strength[1] = max(r[30], r[33], r[39], r[42], r[56], r[57], r[58], r[59], r[60], r[61], r[62], r[63], r[65], r[66], r[67], r[68], r[69], r[70], r[71], r[72], r[77], r[78], r[79], r[80], r[81])
    kelompok_strength[2] = max(r[7], r[8], r[9], r[16], r[17], r[18], r[25], r[26], r[27])
    # Aturan R3 dan R4 belum dimasukkan ke kelompok manapun karena ada keraguan dari daftar sebelumnya. Sesuai daftar baru:
    # R3 -> Kelompok 3
    # R4 -> (tidak ada di daftar 81, tapi dari daftar lama itu Kelompok 2)
    # Mari asumsikan daftar 81 adalah yang paling benar.
    kelompok_strength[3] = max(r[1], r[2], r[3], r[5], r[6], r[10], r[11], r[12], r[13], r[14], r[15], r[19], r[20], r[21], r[22], r[23], r[24], r[28], r[29], r[31], r[32], r[34], r[35], r[36], r[37], r[38], r[40], r[41], r[43], r[44], r[45], r[46], r[47], r[48], r[49], r[50], r[51], r[52], r[53], r[54], r[55], r[64], r[73], r[74], r[75], r[76])
    # Aturan R4 dari daftar lama (pH Basa) tidak ada di daftar 81 ini. Jika ingin ditambahkan, bisa ditaruh di kelompok 2
    # kelompok_strength[2] = max(kelompok_strength[2], r[...]) 

    print("\n[LANGKAH 3: KEKUATAN AKHIR SETIAP KELOMPOK]")
    print(f"  Kekuatan Kelompok 1: {kelompok_strength[1]:.4f}")
    print(f"  Kekuatan Kelompok 2: {kelompok_strength[2]:.4f}")
    print(f"  Kekuatan Kelompok 3: {kelompok_strength[3]:.4f}")

    # Defuzzifikasi
    if max(kelompok_strength.values()) == 0:
        print("\n--> KESIMPULAN: Semua kekuatan kelompok bernilai 0. Tidak ada aturan yang cocok.")
        print("="*50 + "\n")
        return None 
        
    best_cluster = max(kelompok_strength, key=kelompok_strength.get)
    print(f"\n--> KESIMPULAN: Kelompok terbaik adalah Kelompok {best_cluster} dengan kekuatan {kelompok_strength[best_cluster]:.4f}")
    print("="*50 + "\n")
    return best_cluster


# --- BAGIAN 3: REKOMENDASI (TETAP SAMA) ---
def get_plant_recommendations(cluster):
    plant_mapping = {
        1: ['Kacang Tanah', 'Kacang Hijau', 'Jagung', 'Cabai', 'Bawang Merah'],
        2: ['Kentang', 'Sawi', 'Selada', 'Daun Bawang', 'Lobak', 'Wortel', 'Kubis'],
        3: ['Kedelai', 'Bayam', 'Tomat', 'Kacang Panjang', 'Mentimun', 'Terong', 'Kangkung', 'Labu']
    }
    return plant_mapping.get(cluster, [])


# --- ROUTING APLIKASI FLASK (TETAP SAMA) ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        input_values = {
            'suhu': float(request.form['suhu']),
            'curah_hujan': float(request.form['curah_hujan']),
            'penyinaran': float(request.form['penyinaran']),
            'ph': float(request.form['ph']),
            'kelembapan': float(request.form['kelembapan']),
            'ketinggian': float(request.form['ketinggian'])
        }
        cluster = evaluate_rules(input_values)
        if cluster:
            recommendations = get_plant_recommendations(cluster)
            return render_template('index.html', 
                                recommendations=recommendations, 
                                cluster=cluster,
                                input_values=input_values)
        else:
            flash('Tidak ada rekomendasi yang cocok berdasarkan aturan yang ada. Silakan coba dengan nilai input yang berbeda.', 'error')
            return redirect(url_for('home'))
    except ValueError:
        flash('Mohon isi semua field dengan angka yang valid.', 'error')
        return redirect(url_for('home'))
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
