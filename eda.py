import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Membaca Data
df = pd.read_csv("data_kipk_cendekia_500.csv")

print("--- Informasi Umum Dataset ---")
print(df.info())
print("\n--- Jumlah Kelas Target ---")
print(df['Status_Kelayakan'].value_counts())

# 2. Membuat Visualisasi: Distribusi Status Kelayakan
plt.figure(figsize=(6, 4))
sns.countplot(data=df, x='Status_Kelayakan', palette='viridis')
plt.title('Distribusi Kelayakan KIP Kuliah Univ. Cendekia Abditama')
plt.xlabel('Status Kelayakan')
plt.ylabel('Jumlah Mahasiswa')
plt.show()

# 3. Membuat Visualisasi: Hubungan Nilai Rapor dan Kelayakan
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x='Status_Kelayakan', y='Nilai_Rapor', palette='Set2')
plt.title('Perbandingan Nilai Rapor Berdasarkan Status Kelayakan')
plt.show()

# 4. Membuat Visualisasi: Hubungan Penghasilan Orang Tua dan Kelayakan
plt.figure(figsize=(8, 5))
sns.boxplot(data=df, x='Status_Kelayakan', y='Penghasilan_Ortu', palette='Set3')
plt.title('Perbandingan Penghasilan Orang Tua Berdasarkan Status Kelayakan')
plt.show()