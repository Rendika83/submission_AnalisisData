
# E-Commerce Public Dataset Dashboard ✨

Proyek ini merupakan hasil analisis data dan pengembangan dashboard interaktif menggunakan **E-Commerce Public Dataset** untuk menganalisis performa pendapatan (*revenue*) kategori produk, evaluasi keterlambatan pengiriman logistik antar negara bagian (*customer state*), serta segmentasi pelanggan menggunakan metode *RFM Analysis* dan *Manual Grouping*.

## Struktur Direktori

- `dashboard/` : Berisi kode aplikasi Streamlit (`dashboard.py`) dan dataset utama hasil pembersihan (`main_data.csv`).
- `data/` : Berisi berkas dataset mentah (*raw data*) dari E-Commerce Public Dataset.
- `notebook.ipynb` : Berkas Jupyter Notebook yang memuat seluruh tahapan analisis data (*Data Wrangling, EDA, Visualization, RFM Analysis, Conclusion*).
- `requirements.txt` : Daftar pustaka (*library*) Python yang dibutuhkan untuk menjalankan proyek.
- `url.txt` : Tautan menuju dashboard yang telah di-*deploy* pada Streamlit Community Cloud.

## Setup Environment - Anaconda

Jika Anda menggunakan Anaconda atau Miniconda, jalankan perintah berikut pada Anaconda Prompt:

```bash
conda create --name main-ds python=3.10
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal (venv / pipenv)

Jika Anda menggunakan Terminal bawaan OS, Command Prompt, atau PowerShell tanpa Anaconda, jalankan perintah berikut pada direktori utama proyek:

```bash
python -m venv env
```

Aktifkan *virtual environment*:

- **Windows:**

```bash
.\env\Scripts\activate
```

- **macOS/Linux:**

```bash
source env/bin/activate
```

Kemudian instal seluruh dependensi (*library*) yang dibutuhkan:

```bash
pip install -r requirements.txt
```

## Run Streamlit App

Pastikan terminal Anda berada pada **direktori utama proyek** (sejajar dengan berkas `README.md` dan `notebook.ipynb`), lalu jalankan perintah berikut:

```bash
streamlit run dashboard/dashboard.py
```

Atau jika Anda menjalankan dari dalam folder `dashboard`:

```bash
cd dashboard
streamlit run dashboard.py
```
