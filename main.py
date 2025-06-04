import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import pandas as pd

class PlantRecommendationSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Rekomendasi Tanaman")
        self.root.geometry("800x600")
        
        # Membaca data dari file Excel
        try:
            df = pd.read_excel('Dataset.xlsx')
            self.plants_data = {}
            for _, row in df.iterrows():
                self.plants_data[row['Nama Tanaman']] = {
                    'suhu': float(row['Suhu (°C)']),
                    'curah_hujan': float(row['Curah Hujan (mm)']),
                    'penyinaran': float(row['Lama Penyinaran Matahari (jam)']),
                    'ph': float(row['pH']),
                    'ketinggian': float(row['Ketinggian Tanah (mdpl)']),
                    'kelembapan': float(row['Kelembapan Tanah'])
                }
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca file Excel: {str(e)}")
            self.root.destroy()
            return
        
        self.setup_fuzzy_system()
        self.create_gui()
        
    def setup_fuzzy_system(self):
        # Input variables
        self.suhu = ctrl.Antecedent(np.arange(15, 31, 1), 'suhu')
        self.curah_hujan = ctrl.Antecedent(np.arange(0, 1501, 1), 'curah_hujan')
        self.penyinaran = ctrl.Antecedent(np.arange(0, 13, 1), 'penyinaran')
        self.ph = ctrl.Antecedent(np.arange(5, 8, 0.1), 'ph')
        self.ketinggian = ctrl.Antecedent(np.arange(0, 2001, 1), 'ketinggian')
        self.kelembapan = ctrl.Antecedent(np.arange(0, 101, 1), 'kelembapan')
        
        # Output variable
        self.kesesuaian = ctrl.Consequent(np.arange(0, 101, 1), 'kesesuaian')
        
        # Membership functions for input variables
        self.suhu['rendah'] = fuzz.trimf(self.suhu.universe, [15, 15, 20])
        self.suhu['sedang'] = fuzz.trimf(self.suhu.universe, [20, 22.5, 25])
        self.suhu['tinggi'] = fuzz.trimf(self.suhu.universe, [25, 30, 30])
        
        self.curah_hujan['rendah'] = fuzz.trimf(self.curah_hujan.universe, [0, 0, 500])
        self.curah_hujan['sedang'] = fuzz.trimf(self.curah_hujan.universe, [500, 750, 1000])
        self.curah_hujan['tinggi'] = fuzz.trimf(self.curah_hujan.universe, [1000, 1500, 1500])
        
        self.penyinaran['rendah'] = fuzz.trimf(self.penyinaran.universe, [0, 0, 5])
        self.penyinaran['sedang'] = fuzz.trimf(self.penyinaran.universe, [5, 6.5, 8])
        self.penyinaran['tinggi'] = fuzz.trimf(self.penyinaran.universe, [8, 12, 12])
        
        self.ph['asam'] = fuzz.trimf(self.ph.universe, [5, 5, 5.5])
        self.ph['netral'] = fuzz.trimf(self.ph.universe, [5.5, 6.25, 7])
        self.ph['basa'] = fuzz.trimf(self.ph.universe, [7, 7.5, 7.5])
        
        self.ketinggian['rendah'] = fuzz.trimf(self.ketinggian.universe, [0, 0, 500])
        self.ketinggian['sedang'] = fuzz.trimf(self.ketinggian.universe, [500, 750, 1000])
        self.ketinggian['tinggi'] = fuzz.trimf(self.ketinggian.universe, [1000, 1500, 1500])
        self.ketinggian['sangat_tinggi'] = fuzz.trimf(self.ketinggian.universe, [1500, 2000, 2000])
        
        self.kelembapan['rendah'] = fuzz.trimf(self.kelembapan.universe, [0, 15, 30])
        self.kelembapan['sedang'] = fuzz.trimf(self.kelembapan.universe, [30, 45, 60])
        self.kelembapan['tinggi'] = fuzz.trimf(self.kelembapan.universe, [60, 70, 80])
        self.kelembapan['sangat_tinggi'] = fuzz.trimf(self.kelembapan.universe, [80, 90, 100])
        
        # Membership functions for output variable
        self.kesesuaian['tidak_sesuai'] = fuzz.trimf(self.kesesuaian.universe, [0, 0, 50])
        self.kesesuaian['cukup_sesuai'] = fuzz.trimf(self.kesesuaian.universe, [30, 50, 70])
        self.kesesuaian['sangat_sesuai'] = fuzz.trimf(self.kesesuaian.universe, [50, 100, 100])
        
    def create_gui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input fields
        ttk.Label(main_frame, text="Suhu (°C):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.suhu_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.suhu_var).grid(row=0, column=1, pady=5)
        
        ttk.Label(main_frame, text="Curah Hujan (mm):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.curah_hujan_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.curah_hujan_var).grid(row=1, column=1, pady=5)
        
        ttk.Label(main_frame, text="Penyinaran Matahari (jam):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.penyinaran_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.penyinaran_var).grid(row=2, column=1, pady=5)
        
        ttk.Label(main_frame, text="pH Tanah:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.ph_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.ph_var).grid(row=3, column=1, pady=5)
        
        ttk.Label(main_frame, text="Ketinggian Tanah (mdpl):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.ketinggian_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.ketinggian_var).grid(row=4, column=1, pady=5)
        
        ttk.Label(main_frame, text="Kelembapan Tanah (%):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.kelembapan_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.kelembapan_var).grid(row=5, column=1, pady=5)
        
        # Button
        ttk.Button(main_frame, text="Analisis", command=self.analyze).grid(row=6, column=0, columnspan=2, pady=20)
        
        # Result area
        self.result_text = tk.Text(main_frame, height=10, width=50)
        self.result_text.grid(row=7, column=0, columnspan=2, pady=10)
        
    def analyze(self):
        try:
            # Get input values
            suhu_val = float(self.suhu_var.get())
            curah_hujan_val = float(self.curah_hujan_var.get())
            penyinaran_val = float(self.penyinaran_var.get())
            ph_val = float(self.ph_var.get())
            ketinggian_val = float(self.ketinggian_var.get())
            kelembapan_val = float(self.kelembapan_var.get())
            
            # Calculate suitability for each plant
            results = {}
            
            # Print cluster information
            print("\nInformasi Tanaman per Cluster:")
            for plant, criteria in self.plants_data.items():
                score = self.calculate_suitability(
                    suhu_val, curah_hujan_val, penyinaran_val,
                    ph_val, ketinggian_val, kelembapan_val,
                    criteria
                )
                results[plant] = score
                print(f"Tanaman: {plant}")
                print(f"Kriteria: {criteria}")
                print("------------------------")
            
            # Sort results
            sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
            
            # Display results
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Rekomendasi Tanaman:\n\n")
            
            for plant, score in sorted_results.items():
                self.result_text.insert(tk.END, f"{plant}: {score:.2f}%\n")
                
        except ValueError:
            messagebox.showerror("Error", "Mohon masukkan nilai numerik yang valid untuk semua field")
            
    def calculate_suitability(self, suhu, curah_hujan, penyinaran, ph, ketinggian, kelembapan, criteria):
        # Simple weighted scoring
        suhu_score = 100 - min(abs(suhu - criteria['suhu']) * 10, 100)
        curah_hujan_score = 100 - min(abs(curah_hujan - criteria['curah_hujan']) / 10, 100)
        penyinaran_score = 100 - min(abs(penyinaran - criteria['penyinaran']) * 15, 100)
        ph_score = 100 - min(abs(ph - criteria['ph']) * 50, 100)
        ketinggian_score = 100 - min(abs(ketinggian - criteria['ketinggian']) / 10, 100)
        kelembapan_score = 100 - min(abs(kelembapan - criteria['kelembapan']), 100)
        
        # Weighted average
        weights = [0.2, 0.2, 0.15, 0.15, 0.15, 0.15]
        total_score = (
            suhu_score * weights[0] +
            curah_hujan_score * weights[1] +
            penyinaran_score * weights[2] +
            ph_score * weights[3] +
            ketinggian_score * weights[4] +
            kelembapan_score * weights[5]
        )
        
        return total_score

if __name__ == "__main__":
    root = tk.Tk()
    app = PlantRecommendationSystem(root)
    root.mainloop() 