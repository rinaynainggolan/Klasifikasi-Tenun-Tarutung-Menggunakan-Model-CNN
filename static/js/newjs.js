$(document).ready(function () {
    // Inisialisasi
    $('.image-section').hide();
    $('.loader').hide();
    $('#result').hide();
    $('#btn-kegunaan').hide();
    $('#kegunaan').hide();

    // Fungsi untuk pratinjau gambar yang diunggah
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').attr('src', e.target.result);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }

    // Ketika gambar diunggah, tampilkan pratinjau dan reset hasil prediksi
    $("#imageUpload").change(function () {
        $('.image-section').show();
        $('#btn-predict').show();
        $('#result').text('');
        $('#result').hide();
        $('#btn-kegunaan').hide();
        $('#kegunaan').hide();
        readURL(this);
    });

    // Ketika tombol Predict diklik, lakukan prediksi
    $('#btn-predict').click(function () {
        var form_data = new FormData($('#upload-file')[0]);

        // Tampilkan animasi loading
        $(this).hide();
        $('.loader').show();

        // Lakukan prediksi melalui API /predict
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (response) {
                // Sembunyikan animasi loading dan tampilkan hasil prediksi
                $('.loader').hide();
                $('#result').fadeIn(600);
                $('#result').text('Prediction: ' + response.predicted_label);
                $('#btn-predict').show();

                // Tampilkan tombol "Lihat Kegunaan"
                $('#btn-kegunaan').show();

                // Simpan kegunaan di elemen #kegunaan-text untuk nanti
                $('#kegunaan-text').html(response.kegunaan);

                console.log('Success!');
            },
        });
    });

    // Ketika tombol "Lihat Kegunaan" diklik, tampilkan kegunaan
    $('#btn-kegunaan').click(function () {
        $('#kegunaan').show();
    });
});
