import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. Membaca Data
# Pastikan file CSV berada di folder yang sama dengan file Python ini
df = pd.read_csv("data_kipk_cendekia_500.csv")

# 2. Pra-pemrosesan Data (Encoding)
le = LabelEncoder()
# Mengubah teks menjadi angka otomatis (Hanya untuk Status_Rumah)
df['Status_Rumah'] = le.fit_transform(df['Status_Rumah'])

# [REVISI]: Memilih fitur (X) secara spesifik alih-alih menggunakan df.drop()
# Ini memastikan AI hanya fokus pada parameter ekonomi & nilai akademik
fitur = ['Penghasilan_Ortu', 'Tanggungan', 'Daya_Listrik', 'Status_Rumah', 'Nilai_Rapor']
X = df[fitur]
y = df['Status_Kelayakan']

# 3. Membagi Data (80% Training, 20% Testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. MELATIH ALGORITMA
# Kita panggil algoritma Random Forest dengan 100 pohon (n_estimators=100)
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Baris di bawah ini adalah proses "Training" atau latihannya
model.fit(X_train, y_train)
print("Model berhasil dilatih!")

# 5. Evaluasi (Ujian)
# Menyuruh model menebak soal ujian (X_test)
y_pred = model.predict(X_test)

# Menghitung nilainya dengan membandingkan tebakan (y_pred) dengan kunci jawaban (y_test)
akurasi = accuracy_score(y_test, y_pred)
print(f"\nAkurasi Model: {akurasi * 100:.2f}%")
print("\nDetail Laporan Klasifikasi:")
print(classification_report(y_test, y_pred))