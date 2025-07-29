from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from fpdf import FPDF
from datetime import datetime
import os
import logging
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'supersecretkey' # Ganti dengan kunci rahasia yang lebih kuat di produksi
app.config['UPLOAD_FOLDER'] = 'static'

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Harga default
DEFAULT_PRICES = {
    "TENDA POLOS 4X6": 300000,
    "TENDA SEMI 4X6": 400000,
    "TENDA BALON 4X6": 600000,
    "TENDA SKAK 4X6": 750000,
    "TENDA LAMPION 4X6": 800000,
    "TENDA LAPIS 4X6": 850000,
    "TENDA POLOS 6X6": 400000,
    "TENDA SEMI 6X6": 900000,
    "TENDA LAMPION 6X6": 1200000,
    "TENDA BALON 6X6": 1200000,
    "TENDA SKAK 6X6": 1000000,
    "TENDA LAPIS 6X6": 950000,
    "KURSI BIASA": 3500,
    "KURSI COVER": 6000,
    "MEJA BIASA": 50000,
    "MEJA BULAT": 55000,
    "MEJA + GUBUKAN": 100000,
    "PIRING": 75000,
    "MANGKOK BAKSO": 75000,
    "MANGKOK SOTO": 75000,
    "PANGGUNG 4 X 4": 700000,
    "PANGGUNG 4 X 6": 1000000,
    "PANGGUNG 6 X 6": 1100000,
    "PANGGUNG 6 X 8": 1600000,
    "BLOWER BIASA": 300000,
    "BLOWER AIR": 350000,
    "TIRAI 6 METER": 150000,
    "KARPET 1 METER": 10000
}

class PDF(FPDF):
    def header(self):
        # Pastikan file logo.png ada di folder 'static'
        # dan path-nya benar relatif terhadap lokasi di mana app.py dijalankan
        try:
            self.image('static/logo.png', 10, 8, 50)
        except RuntimeError as e:
            logger.error(f"Error loading image 'static/logo.png': {e}. Ensure the file exists and is accessible.")
            # Anda bisa menambahkan teks placeholder atau hanya melewati jika gambar gagal dimuat
            # self.set_font('Arial', 'B', 10)
            # self.cell(0, 10, 'Logo Not Found', 0, 0, 'L')

        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'INVOICE TRISKA KENCANA', 0, 1, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C')

def generate_pdf(customer_data, items):
    pdf = PDF()
    pdf.add_page()

    # Informasi pelanggan
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Tanggal: {customer_data['tanggal']}", 0, 1)
    pdf.cell(0, 10, f"Nama: {customer_data['nama']}", 0, 1)
    pdf.cell(0, 10, f"Alamat: {customer_data['alamat']}", 0, 1)
    pdf.cell(0, 10, f"Telepon: {customer_data['telp']}", 0, 1)
    pdf.ln(10)

    # Tabel barang
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(10, 10, 'No', 1, 0, 'C')
    pdf.cell(80, 10, 'Nama Barang', 1, 0, 'C')
    pdf.cell(30, 10, 'Jumlah', 1, 0, 'C')
    pdf.cell(30, 10, 'Harga', 1, 0, 'C')
    pdf.cell(30, 10, 'Total', 1, 1, 'C')

    pdf.set_font('Arial', '', 12)
    total = 0
    for i, item in enumerate(items, 1):
        pdf.cell(10, 10, str(i), 1, 0, 'C')
        # Menyesuaikan lebar sel untuk Nama Barang agar tidak terpotong
        pdf.cell(80, 10, item['name'], 1, 0, 'L') # Menggunakan 'L' untuk rata kiri
        pdf.cell(30, 10, str(item['quantity']), 1, 0, 'C')
        pdf.cell(30, 10, f"Rp {item['price']:,}", 1, 0, 'R')
        pdf.cell(30, 10, f"Rp {item['total']:,}", 1, 1, 'R')
        total += item['total']

    # Total keseluruhan
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(150, 10, 'TOTAL', 1, 0, 'R')
    pdf.cell(30, 10, f"Rp {total:,}", 1, 1, 'R')

    return pdf.output(dest='S').encode('latin-1')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            nama = request.form.get('nama', '').strip()
            if not nama:
                flash('Nama pelanggan harus diisi', 'error')
                return redirect(url_for('index'))

            customer_data = {
                'nama': nama,
                'alamat': request.form.get('alamat', '-').strip(),
                'telp': request.form.get('telp', '-').strip(),
                'tanggal': request.form.get('tanggal', datetime.now().strftime('%Y-%m-%d')) # Format tanggal untuk input HTML
            }

            item_names = request.form.getlist('item[]')
            quantities = request.form.getlist('quantity[]')
            prices = request.form.getlist('price[]')

            items = []
            for i in range(len(item_names)):
                # Memastikan semua bagian item ada dan tidak kosong
                if item_names[i] and quantities[i] and prices[i]:
                    try:
                        quantity = int(quantities[i])
                        price = int(prices[i])
                        total = quantity * price
                        items.append({
                            'name': item_names[i],
                            'quantity': quantity,
                            'price': price,
                            'total': total
                        })
                    except ValueError:
                        flash('Jumlah atau harga harus berupa angka', 'error')
                        return redirect(url_for('index'))

            if not items:
                flash('Minimal harus ada 1 barang', 'error')
                return redirect(url_for('index'))

            pdf_bytes = generate_pdf(customer_data, items)

            # --- PERUBAHAN UTAMA DI SINI ---
            # Mengirim PDF agar ditampilkan secara inline (di browser)
            response = send_file(
                BytesIO(pdf_bytes),
                as_attachment=False, # UBAH: False agar ditampilkan di browser
                mimetype='application/pdf',
                # download_name tidak lagi relevan jika as_attachment=False
            )
            # HAPUS: response.headers['Content-Disposition'] tidak diperlukan untuk tampilan inline
            return response

        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('index'))

    return render_template('index.html',
                           default_prices=DEFAULT_PRICES,
                           today=datetime.now().strftime('%Y-%m-%d'))

if __name__ == '__main__':
    # Pastikan mode debug hanya untuk pengembangan, nonaktifkan di produksi
    app.run(debug=True, port=4000)
