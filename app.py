import os
import numpy as np
from PIL import Image
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

# Load model
model = load_model('Tenun Tarutung-Tenun-93.99.h5')
print('Model loaded. Check http://127.0.0.1:5000/')

# Label kelas prediksi
labels = {
    0: 'Bintang Maratur', 1: 'Bintik Toraja', 2: 'Bukan Tenun', 3: 'Harungguan', 4: 'Iccor Moror', 5: 'Maulana', 6: 'Maulana Pull', 7: 'Piala Kosong', 8: 'Piala Pull', 9: 'Polos-polos', 10: 'Pucca Bunga', 11: 'Sadum', 12: 'Semi Tumtuman', 13: 'Sibolang Rasta', 14: 'Tumtuman'
}

# Label kelas dan kegunaan prediksi
kegunaan_labels = {
    'Bintang Maratur': 'Bintang Maratur memiliki motif yang menyerupai bintang, tersusun secara simetris di tengah kain dan diapit oleh garis-garis zigzag di kedua sisinya. Kain ini memiliki makna sebagai perantara ucapan suka cita atau berita gembira yang diberikan kepada orang-orang yang mendapat berkat atau rezeki, misalnya pada acara mambosuri atau tujuh bulanan.',
    'Bintik Toraja': 'Bintik Toraja memiliki motif yang cenderung geometris, terdiri dari bentuk-bentuk segi empat, segitiga, dan lingkaran yang saling tumpang tindih. Kain ini memiliki tekstur yang sedikit kasar atau timbul pada bagian motif. Kain ini digunakan sebagai selendang yang dililitkan di bahu dan juga dijadikan sebagai rok untuk memberikan sentuhan elegan dalam berbagai acara, seperti pesta, pernikahan, dan upacara adat.',
    'Harungguan': 'Harungguan memiliki motif garis-garis horizontal berwarna-warni yang disusun secara berulang. Garis-garis ini memiliki variasi warna yang cukup banyak dan disusun secara sejajar serta rapat, menciptakan kesan yang dinamis dan berlapis. Makna dari harungguan adalah kumpulan bersatu. Kain harungguan ini biasanya digunakan pada acara adat istiadat Batak dan dikenakan oleh wanita Batak.',
    'Iccor Moror': 'Iccor Moror memiliki motif yang terdiri dari garis-garis vertikal berwarna-warni yang membentang dari atas ke bawah kain. Garis-garis vertikal disusun secara paralel dan berulang, menciptakan kesan yang dinamis dan berlapis. Variasi warna pada setiap garis membuat tampilan kain menjadi lebih menarik. Kain songket ini biasanya dipakai dalam upacara adat oleh pengantin wanita atau disebut sebagai hasuhuton.',
    'Maulana': 'Maulana memiliki motif yang terdiri dari garis-garis horizontal tipis yang diselingi oleh pola-pola kecil berbentuk kotak atau belah ketupat yang disusun secara berulang dan teratur. Pola-pola kecil ini memiliki warna yang kontras dengan warna dasar kain. Kain ini digunakan sebagai selendang oleh para ibu dan dikenakan dalam acara adat ketika kehadirannya hanya sekadar meramaikan.',
    'Maulana Pull': 'Maulana Pull memiliki motif yang cenderung abstrak, terdiri dari bentuk-bentuk tidak beraturan yang saling tumpang tindih. Motif-motif disusun secara acak, namun tetap terlihat harmonis. Warna-warna yang digunakan pada kain ini kontras. Kain ini dipakai oleh para ibu saat mengikuti kegiatan adat yang kehadirannya disebut panoropi. Panoropi biasanya adalah tamu undangan biasa yang hadir untuk meramaikan acara.',
    'Piala Kosong': 'Piala Kosong memiliki motif menyerupai belah ketupat dengan ujung tumpul dan garis-garis horizontal yang disusun secara rapat. Pola yang digunakan dalam kain ini tampak berulang di seluruh kain, menciptakan kesan harmoni dan keseimbangan. Kain ini digunakan untuk menggambarkan ciri khas keteguhan suku Batak dalam suatu pendirian yang selalu menurun kepada anak cucunya.',
    'Piala Pull': 'Piala Pull memiliki pola utama lingakaran berulang yang menyerupai bunga. Selain itu, terdapat juga pola segitiga yang terjalin dengan garis-garis horizontal. Segitiga ini membentuk pola yang lebih dinamis dan tegas, memberikan kontras dengan bentuk lingkaran yang lebih halus. Kain ini digunakan sebagai penutup badan yang mengandung makna tetap sehat jasmani dan rohani.',
    'Polos-polos': 'Polos-polos memiliki pola utama berupa garis-garis horizontal yang terbuat dari warna-warna berbeda dan cerah. Di dalam setiap warna terdapat pola berbentuk layang-layang. Kain ini digunakan sebagai selendang dengan cara dililitkan di bahu dalam acara pesta pernikahan dan upacara adat.',
    'Pucca Bunga': 'Pucca bunga memiliki motif yang didominasi oleh bintik-bintik kecil yang menyerupai bunga. Pola geometris garis-garis lurus juga terlihat dalam kain ini. Ulos Pucca sering digunakan dalam berbagai upacara dan ritual, termasuk pernikahan, kematian, penyambutan tamu istimewa, dan upacara keagamaan. Ulos Pucca juga sering diberikan sebagai hadiah di acara penting sebagai tanda rasa hormat.',
    'Sadum': 'Sadum memiliki motif atau pola yang didominasi oleh flora dan fauna, seperti tumbuhan, burung, dan manusia dalam bentuk yang sederhana. Motif ini memberikan kesan natural dan dekat dengan alam. Ulos Sadum pada masyarakat Toba (Tarutung) digunakan sebagai hande-hande atau selendang.',
    'Semi Tumtuman': 'Semi Tumtuman memiliki motif yang didominasi oleh bentuk-bentuk geometris, seperti garis-garis lurus dan zigzag. Ada bagian dengan motif yang lebih rapat dan ada pula bagian dengan motif yang lebih renggang. Kain ini dipakai oleh para ibu saat mengikuti kegiatan adat yang kehadirannya disebut panoropi. Panoropi biasanya merupakan tamu undangan biasa yang hadir untuk meramaikan acara.',
    'Sibolang Rasta': 'Sibolang Rasta memiliki motif dasar dengan pola seperti pagar dengan kedua ujung runcing yang berulang secara teratur dan rapat. Kain ini dikenal sebagai lambang dukacita karena umumnya dipakai dalam acara-acara berkabung. Biasanya, kain ini dipakai jika ada orang dewasa yang meninggal tetapi belum memiliki cucu, dan dapat juga dipakai oleh janda atau duda yang ditinggal mati pasangannya.',
    'Tumtuman': 'Tumtuman memiliki motif yang didominasi oleh bentuk-bentuk geometris, seperti garis-garis di dekat kotak-kotak kecil dengan pola yang berulang. Kain ini biasanya dipakai oleh hasuhutan (tuan rumah dari pihak perempuan) dalam pesta adat pernikahan. Kain ini juga dapat digunakan oleh pengantin perempuan dalam adat pernikahan.'
}

# Data tenun
tenun_data = [
    {'nama': 'Bintang Maratur', 
    'kegunaan': 'Bintang Maratur memiliki motif yang menyerupai bintang, tersusun secara simetris di tengah kain dan diapit oleh garis-garis zigzag di kedua sisinya. Kain ini memiliki makna sebagai perantara ucapan suka cita atau berita gembira yang diberikan kepada orang-orang yang mendapat berkat atau rezeki, misalnya pada acara mambosuri atau tujuh bulanan.',
    'gambar': 'uploads/bintang_maratur.jpg'},
    {'nama': 'Bintik Toraja',
     'kegunaan': 'Bintik Toraja memiliki motif yang cenderung geometris, terdiri dari bentuk-bentuk segi empat, segitiga, dan lingkaran yang saling tumpang tindih. Kain ini memiliki tekstur yang sedikit kasar atau timbul pada bagian motif. Kain ini digunakan sebagai selendang yang dililitkan di bahu dan juga dijadikan sebagai rok untuk memberikan sentuhan elegan dalam berbagai acara, seperti pesta, pernikahan, dan upacara adat.',
     'gambar': 'uploads/bintik_toraja.jpg'},
    {'nama': 'Harungguan',
      'kegunaan': 'Harungguan memiliki motif garis-garis horizontal berwarna-warni yang disusun secara berulang. Garis-garis ini memiliki variasi warna yang cukup banyak dan disusun secara sejajar serta rapat, menciptakan kesan yang dinamis dan berlapis. Makna dari harungguan adalah kumpulan bersatu. Kain harungguan ini biasanya digunakan pada acara adat istiadat Batak dan dikenakan oleh wanita Batak.',
      'gambar': 'uploads/harungguan.jpg'},
    {'nama': 'Iccor Moror',
     'kegunaan': 'Iccor Moror memiliki motif yang terdiri dari garis-garis vertikal berwarna-warni yang membentang dari atas ke bawah kain. Garis-garis vertikal disusun secara paralel dan berulang, menciptakan kesan yang dinamis dan berlapis. Variasi warna pada setiap garis membuat tampilan kain menjadi lebih menarik. Kain songket ini biasanya dipakai dalam upacara adat oleh pengantin wanita atau disebut sebagai hasuhuton.',
     'gambar': 'uploads/iccor_moror.jpg'},
    {'nama': 'Maulana',
     'kegunaan': 'Maulana memiliki motif yang terdiri dari garis-garis horizontal tipis yang diselingi oleh pola-pola kecil berbentuk kotak atau belah ketupat yang disusun secara berulang dan teratur. Pola-pola kecil ini memiliki warna yang kontras dengan warna dasar kain. Kain ini digunakan sebagai selendang oleh para ibu dan dikenakan dalam acara adat ketika kehadirannya hanya sekadar meramaikan.',
     'gambar': 'uploads/maulana.jpg'},
    {'nama': 'Maulana Pull',
     'kegunaan': 'Maulana Pull memiliki motif yang cenderung abstrak, terdiri dari bentuk-bentuk tidak beraturan yang saling tumpang tindih. Motif-motif disusun secara acak, namun tetap terlihat harmonis. Warna-warna yang digunakan pada kain ini kontras. Kain ini dipakai oleh para ibu saat mengikuti kegiatan adat yang kehadirannya disebut panoropi. Panoropi biasanya adalah tamu undangan biasa yang hadir untuk meramaikan acara.',
     'gambar': 'uploads/maulana_pull.jpg'},
    {'nama': 'Piala Kosong',
     'kegunaan': 'Piala Kosong memiliki motif menyerupai belah ketupat dengan ujung tumpul dan garis-garis horizontal yang disusun secara rapat. Pola yang digunakan dalam kain ini tampak berulang di seluruh kain, menciptakan kesan harmoni dan keseimbangan. Kain ini digunakan untuk menggambarkan ciri khas keteguhan suku Batak dalam suatu pendirian yang selalu menurun kepada anak cucunya.',
     'gambar': 'uploads/piala_kosong.jpg'},
    {'nama': 'Piala Pull',
     'kegunaan': 'Piala Pull memiliki pola utama lingakaran berulang yang menyerupai bunga. Selain itu, terdapat juga pola segitiga yang terjalin dengan garis-garis horizontal. Segitiga ini membentuk pola yang lebih dinamis dan tegas, memberikan kontras dengan bentuk lingkaran yang lebih halus. Kain ini digunakan sebagai penutup badan yang mengandung makna tetap sehat jasmani dan rohani.',
     'gambar': 'uploads/piala_pull.jpg'},
    {'nama': 'Polos-polos',
     'kegunaan': 'Polos-polos memiliki pola utama berupa garis-garis horizontal yang terbuat dari warna-warna berbeda dan cerah. Di dalam setiap warna terdapat pola berbentuk layang-layang. Kain ini digunakan sebagai selendang dengan cara dililitkan di bahu dalam acara pesta pernikahan dan upacara adat.',
     'gambar': 'uploads/polos_polos.jpg'},
    {'nama': 'Pucca Bunga',
     'kegunaan': 'Pucca bunga memiliki motif yang didominasi oleh bintik-bintik kecil yang menyerupai bunga. Pola geometris garis-garis lurus juga terlihat dalam kain ini. Ulos Pucca sering digunakan dalam berbagai upacara dan ritual, termasuk pernikahan, kematian, penyambutan tamu istimewa, dan upacara keagamaan. Ulos Pucca juga sering diberikan sebagai hadiah di acara penting sebagai tanda rasa hormat.',
     'gambar': 'uploads/pucca_bunga.jpg'},
     {'nama': 'Sadum',
     'kegunaan': 'Sadum memiliki motif atau pola yang didominasi oleh flora dan fauna, seperti tumbuhan, burung, dan manusia dalam bentuk yang sederhana. Motif ini memberikan kesan natural dan dekat dengan alam. Ulos Sadum pada masyarakat Toba (Tarutung) digunakan sebagai hande-hande atau selendang.',
     'gambar': 'uploads/sadum.jpg'},
     {'nama': 'Semi Tumtuman',
     'kegunaan': 'Semi Tumtuman memiliki motif yang didominasi oleh bentuk-bentuk geometris, seperti garis-garis lurus dan zigzag. Ada bagian dengan motif yang lebih rapat dan ada pula bagian dengan motif yang lebih renggang. Kain ini dipakai oleh para ibu saat mengikuti kegiatan adat yang kehadirannya disebut panoropi. Panoropi biasanya merupakan tamu undangan biasa yang hadir untuk meramaikan acara.',
     'gambar': 'uploads/semi_tumtuman.jpg'},
     {'nama': 'Sibolang Rasta',
     'kegunaan': 'Sibolang Rasta memiliki motif dasar dengan pola seperti pagar dengan kedua ujung runcing yang berulang secara teratur dan rapat. Kain ini dikenal sebagai lambang dukacita karena umumnya dipakai dalam acara-acara berkabung. Biasanya, kain ini dipakai jika ada orang dewasa yang meninggal tetapi belum memiliki cucu, dan dapat juga dipakai oleh janda atau duda yang ditinggal mati pasangannya.',
     'gambar': 'uploads/sibolang_rasta.jpg'},
     {'nama': 'Tumtuman',
     'kegunaan': 'Tumtuman memiliki motif yang didominasi oleh bentuk-bentuk geometris, seperti garis-garis di dekat kotak-kotak kecil dengan pola yang berulang. Kain ini biasanya dipakai oleh hasuhutan (tuan rumah dari pihak perempuan) dalam pesta adat pernikahan. Kain ini juga dapat digunakan oleh pengantin perempuan dalam adat pernikahan.',
     'gambar': 'uploads/tumtuman.jpg'}
]

# Fungsi untuk memproses gambar
def preprocess_image(image_path):
    # Muat gambar
    img = Image.open(image_path)

    # Jika ukuran gambar terlalu besar, ubah ukurannya ke max 1024x1024
    if img.size[0] > 1024 or img.size[1] > 1024:
        img.thumbnail((1024, 1024))  # Thumbnail mengubah ukuran sesuai proporsi asli

    # Ubah ukuran gambar ke 224x224 untuk input ke model
    img = img.resize((224, 224))

    # Konversi gambar ke array
    img_array = img_to_array(img)

    # Normalisasi nilai piksel ke rentang [0, 1]
    img_array = img_array.astype('float32') / 255.0

    # Tambahkan dimensi agar sesuai dengan input model (1, 224, 224, 3)
    img_array = np.expand_dims(img_array, axis=0)

    return img_array

# Fungsi untuk mendapatkan prediksi dari model
def getResult(image_path):
    img_array = preprocess_image(image_path)
    predictions = model.predict(img_array)[0]  # Mengambil hasil prediksi
    return predictions

# Route untuk halaman Home
@app.route('/')
def home():
    return render_template('home.html')

# Route untuk Halaman Klasifikasi dan Deskripsi
@app.route('/classification')
def classification():
    return render_template('classification.html', active_menu='classification')

# Route untuk Halaman Daftar Tenun
@app.route('/daftar_tenun')
def daftar_tenun():
    return render_template('daftar_tenun.html', tenun_data=tenun_data, active_menu='daftar_tenun')

# Route untuk Halaman Pencarian Tenun
@app.route('/pencarian_tenun', methods=['GET', 'POST'])
def pencarian_tenun():
    keyword = request.args.get('keyword', '').lower()
    results = []  # Inisialisasi results sebagai list kosong
    searched = False  # Menandai apakah pencarian telah dilakukan

    if keyword:
        searched = True  # Tandai bahwa pencarian telah dilakukan
        # Cari tenun yang cocok dengan keyword
        results = [tenun for tenun in tenun_data if keyword in tenun['nama'].lower()]

    return render_template('pencarian_tenun.html', keyword=keyword, results=results, searched=searched, active_menu='pencarian_tenun')

# Route untuk Halaman Tentang
@app.route('/tentang')
def tentang():
    return render_template('tentang.html', active_menu='tentang')

# Route untuk Halaman Detail Tenun
@app.route('/detail_tenun/<nama_tenun>')
def detail_tenun(nama_tenun):
    # Mencari tenun berdasarkan nama
    tenun = next((item for item in tenun_data if item['nama'] == nama_tenun), None)
    if tenun is None:
        return "Tenun tidak ditemukan", 404
    return render_template('detail_tenun.html', tenun=tenun)

# Route untuk Prediksi
@app.route('/predict', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']

        # Validasi jika file bukan gambar tenun
        if not is_tenun_image(f):
            return jsonify({"error": "Gambar yang Anda Masukkan Bukan Tenun Tradisional Tarutung"}), 400

        # Simpan file ke dalam direktori 'uploads'
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Dapatkan prediksi dari gambar
        predictions = getResult(file_path)

        # Cari label prediksi yang memiliki probabilitas tertinggi
        predicted_label = labels[np.argmax(predictions)]

        # Cari kegunaan dari prediksi
        kegunaan = kegunaan_labels[predicted_label]

        # Kirim hasil prediksi dan kegunaan ke frontend
        return jsonify({'predicted_label': predicted_label, 'kegunaan': kegunaan})

    return None

def is_tenun_image(file):
    valid_extensions = ['.jpg', '.jpeg', '.png']
    return any(file.filename.endswith(ext) for ext in valid_extensions)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)