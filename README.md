# Sistem Rekomendasi Tanaman Berbasis Fuzzy Logic

Aplikasi ini merupakan sistem pendukung keputusan untuk memilih jenis tanaman yang sesuai berdasarkan karakteristik tanah menggunakan metode Fuzzy Logic.

## Fitur

- Input parameter tanah (suhu, curah hujan, penyinaran matahari, pH, ketinggian, dan kelembapan)
- Analisis kesesuaian menggunakan Fuzzy Logic
- Tampilan GUI yang user-friendly
- Hasil berupa rekomendasi tanaman beserta persentase kesesuaiannya

## Instalasi

1. Pastikan Python 3.7+ sudah terinstall di sistem Anda
2. Clone repository ini
3. Install dependencies yang diperlukan:
```bash
pip install -r requirements.txt
```

## Penggunaan

1. Jalankan program dengan perintah:
```bash
python main.py
```

2. Masukkan nilai parameter tanah yang akan dianalisis:
   - Suhu (°C)
   - Curah Hujan (mm)
   - Penyinaran Matahari (jam)
   - pH Tanah
   - Ketinggian Tanah (mdpl)
   - Kelembapan Tanah (%)

3. Klik tombol "Analisis" untuk melihat hasil rekomendasi

## Dataset

Program ini menggunakan dataset tanaman yang mencakup 10 jenis tanaman dengan karakteristik ideal masing-masing:
- Kedelai
- Kentang
- Kacang Tanah
- Kacang Hijau
- Bayam
- Sawi
- Cabai
- Tomat
- Bawang Merah
- Kacang Panjang

## Metode Fuzzy Logic

Sistem menggunakan metode Fuzzy Logic dengan:
- 6 variabel input (suhu, curah hujan, penyinaran, pH, ketinggian, kelembapan)
- Fungsi keanggotaan triangular
- Pembobotan berdasarkan tingkat kepentingan parameter
- Defuzzifikasi menggunakan weighted average 