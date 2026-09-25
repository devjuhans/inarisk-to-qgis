from qgis.PyQt.QtCore import QSettings

translations = {
    # Actions & Dialog Titles
    'Run InaRISK to QGIS': 'Jalankan InaRISK to QGIS',
    'InaRISK to QGIS': 'InaRISK to QGIS',
    'InaRISK to QGIS - Select Mode': 'InaRISK to QGIS - Pilih Mode',
    'Download from InaRISK Server (GeoServer)': 'Unduh dari Server InaRISK',
    'Process Local Zip Files': 'Proses File Zip Lokal',
    'InaRISK Downloader - Server Download': 'Unduh Data InaRISK',
    'InaRISK for Spatial Planning': 'InaRISK untuk Tata Ruang',
    'InaRISK for Spatial Planning (KRB)': 'InaRISK untuk Tata Ruang',
    'Run InaRISK for Spatial Planning': 'Jalankan InaRISK untuk Tata Ruang',
    
    # Common UI
    'Language:': 'Bahasa:',
    'Parameters': 'Parameter',
    'Log': 'Log',
    'Run': 'Jalankan',
    'Close': 'Tutup',
    'Browse': 'Telusuri',
    
    # Form Group Titles & Labels
    'Index Options': 'Opsi Indeks',
    'Index Type:': 'Jenis Indeks:',
    'Disaster:': 'Bencana:',
    'Disaster Prone Area': 'Kawasan Rawan Bencana',
    'Disaster Prone Area:': 'Kawasan Rawan Bencana',
    'Hazard Disasters:': 'Kawasan Rawan Bencana',
    'Download all types': 'Unduh semua jenis bencana',
    
    'Area Selection': 'Pemilihan Area',
    'Area Layer:': 'Layer Batas Area:',
    'Select AOI Vector File': 'Pilih File Vektor Batas Area',
    'Vector files (*.shp *.gpkg *.geojson *.kml)': 'File vektor (*.shp *.gpkg *.geojson *.kml)',
    
    'Output Options': 'Opsi Output',
    'Save Folder:': 'Folder Penyimpanan:',
    '[Create temporary layer]': '[Buat layer sementara]',
    'Select Output Folder': 'Pilih Folder Penyimpanan',
    'Output Type:': 'Jenis Output:',
    'Output as Raster': 'Output Raster',
    'Output as Vector (Polygons)': 'Output Vektor (Poligon)',
    'Format:': 'Format:',
    'Classification:': 'Klasifikasi:',
    'Classify': 'Klasifikasikan',
    'Do Not Classify': 'Tanpa Klasifikasi',
    'Adjust Gradual Symbology': 'Atur Simbologi Gradual',
    'Apply thematic colors: Green (Low), Yellow (Medium), Red (High).': 'Pewarnaan tematik: Hijau (Rendah), Kuning (Sedang), Merah (Tinggi).',
    'Access Year:': 'Tahun Akses:',
    'Optional': 'Opsional',
    'e.g. 2024 (Optional)': 'Opsional',
    
    # Source Attribution
    'InaRISK, National Disaster Management Authority (BNPB)': 'InaRISK, Badan Nasional Penanggulangan Bencana (BNPB)',
    'InaRISK, National Disaster Management Authority (BNPB), Access Year {year}': 'InaRISK, Badan Nasional Penanggulangan Bencana (BNPB), Tahun Akses {year}',
    
    # Help Panel - Common
    'User Guide': 'Panduan Penggunaan',
    'Vector Attributes': 'Tabel Atribut Vektor',
    'Notice:': 'Catatan:',
    'Requires an active internet connection to access BNPB servers.': 'Memerlukan koneksi internet aktif untuk mengakses server BNPB.',
    'Contact:': 'Kontak:',
    
    # Help Panel - General Dialog
    'Download and process InaRISK disaster layers directly from BNPB servers.': 'Unduh dan proses data spasial bencana InaRISK langsung dari server BNPB.',
    'Select the index type and disaster layers, then specify an Area Layer (AOI) to define the spatial boundary.': 'Pilih jenis indeks dan jenis bencana, lalu tentukan layer batas area (AOI).',
    'Choose Raster (.tif) or Vector Polygons (.shp, .gpkg, .geojson, .kml). Classification categorizes continuous index values into three BNPB tiers: Low (0 - 0.333), Medium (0.333 - 0.667), and High (0.667 - 1.0) with optional gradual symbology. Leave the save folder blank to generate temporary layers.': 'Pilih format Raster (.tif) atau Vektor Poligon (.shp, .gpkg, .geojson, .kml). Klasifikasi membagi nilai indeks ke dalam tiga kelas BNPB: Rendah (0 - 0.333), Sedang (0.333 - 0.667), dan Tinggi (0.667 - 1.0) dengan opsi pewarnaan tematik. Kosongkan folder penyimpanan untuk membuat layer sementara.',
    "Vector outputs include 'Kelas' (index category), 'Value' (index range), and 'Source' (attribution with optional access year).": "Layer vektor memuat atribut 'Kelas' (kategori indeks), 'Value' (rentang nilai), dan 'Source' (sumber data dan tahun akses).",
    
    # Help Panel - Spatial Planning Dialog
    'Extract and format BNPB Hazard data into standardized Kawasan Rawan Bencana (KRB) layers for spatial planning (RTRW/RDTR).': 'Ekstraksi dan standarisasi data Bahaya BNPB menjadi layer Kawasan Rawan Bencana (KRB) untuk rencana tata ruang (RTRW/RDTR).',
    'Select the hazard layers and specify the Area Layer (AOI) boundary.': 'Pilih jenis bencana bahaya dan tentukan layer batas area (AOI).',
    'Outputs use standard KRB naming (e.g. KRB_BANJIR_AR). Classification applies BNPB equal-interval tiers: Low (0 - 0.333), Medium (0.333 - 0.667), and High (0.667 - 1.0) per Perka BNPB No. 2/2012.': 'Output menggunakan penamaan standar KRB (contoh: KRB_BANJIR_AR). Klasifikasi membagi data ke dalam 3 kelas interval sama: Rendah (0 - 0.333), Sedang (0.333 - 0.667), dan Tinggi (0.667 - 1.0) sesuai Perka BNPB No. 2/2012.',
    "Vector polygon layers include attribute fields for 'Kelas' (e.g. Kawasan Rawan Bencana Banjir Tinggi), 'Value' (index range), and 'Source' (attribution with optional access year).": "Layer poligon vektor memuat atribut 'Kelas' (contoh: Kawasan Rawan Bencana Banjir Tinggi), 'Value' (rentang nilai), dan 'Source' (sumber data beserta tahun akses).",
    'Disaster Prone Area': 'Kawasan Rawan Bencana',
    
    # Processing Logs & Messages
    'Reprojecting AOI from': 'Memproyeksikan ulang batas area dari',
    'Error': 'Kesalahan',
    'Please select a valid output directory.': 'Harap pilih folder penyimpanan yang valid.',
    'Downloading from server requires an AOI layer to define the extent.': 'Diperlukan layer batas area untuk mengunduh data.',
    'Please select at least one disaster.': 'Pilih setidaknya satu jenis bencana.',
    'Processing': 'Memproses',
    'Success': 'Berhasil',
    'No data found in selected area': 'Tidak ada data di area yang dipilih',
    'Server/Connection error': 'Koneksi ke server gagal',
    'Processing error': 'Gagal diproses',
    'Warning: Server connection failed for': 'Peringatan: Koneksi server gagal untuk',
    'Warning: Processing failed for': 'Peringatan: Pemrosesan gagal untuk',
    'Proceeding to next item.': 'Melanjutkan ke data berikutnya.',
    'Processing completed.': 'Pemrosesan selesai.',
    'Processing Summary': 'Ringkasan Pemrosesan',
    'Completed': 'Selesai',
    'Processing has completed.': 'Pemrosesan telah selesai.',
    'Summary': 'Ringkasan',
    'Downloading': 'Mengunduh',
    'Server Error': 'Kesalahan Server',
    'ImageServer failed to provide a valid raster. Check if this specific disaster layer exists.': 'Server peta tidak dapat menyediakan raster. Periksa apakah layer bencana ini tersedia.',
    'Buffering AOI...': 'Menyiapkan batas area...',
    'Clipping raster...': 'Memotong raster ke batas area...',
    'No data found for': 'Tidak ada data untuk',
    'Classifying raster...': 'Mengklasifikasikan data...',
    'Filtering raster noise (Sieve)...': 'Menyaring noise piksel raster (Sieve)...',
    'Converting to vector format...': 'Mengonversi ke format vektor...',
    'Clipping vector...': 'Memotong vektor ke batas area...',
    'Adding attribute fields...': 'Menambahkan kolom atribut...',
    'Saving raster output...': 'Menyimpan data raster...',
    'Failed to load output layer:': 'Gagal memuat layer hasil:',
    'Error processing': 'Terjadi kesalahan saat memproses',
    'Failed': 'Gagal',
    'No layer mapping found for': 'Layer tidak ditemukan untuk',
    
    # Index Names
    'Hazard': 'Bahaya',
    'Risk': 'Risiko',
    'Vulnerability': 'Kerentanan',
    'Hazard Index': 'Indeks Bahaya',
    'Risk Index': 'Indeks Risiko',
    'Vulnerability Index': 'Indeks Kerentanan',
    
    # Disaster Types
    'Flood': 'Banjir',
    'Flash Flood': 'Banjir Bandang',
    'Extreme Weather': 'Cuaca Ekstrim',
    'Extreme Wave and Abrasion': 'Gelombang Ekstrim dan Abrasi',
    'Earthquake': 'Gempa Bumi',
    'Volcano': 'Gunung Api',
    'Drought': 'Kekeringan',
    'Liquefaction': 'Likuefaksi',
    'Forest and Land Fire': 'Kebakaran Hutan dan Lahan',
    'Landslide': 'Tanah Longsor',
    'Tsunami': 'Tsunami',
    'Multi': 'Multi',
    
    # Classification Classes
    'Low': 'Rendah',
    'Medium': 'Sedang',
    'High': 'Tinggi',
}

class I18nManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        settings = QSettings()
        saved_version = settings.value("inarisk_to_qgis/version", "", type=str)
        current_version = "3.0"
        
        if saved_version != current_version:
            self.current_lang = "English"
            settings.setValue("inarisk_to_qgis/language", "English")
            settings.setValue("inarisk_to_qgis/version", current_version)
        else:
            self.current_lang = settings.value("inarisk_to_qgis/language", "English")
            
    def set_language(self, lang):
        self.current_lang = lang
        settings = QSettings()
        settings.setValue("inarisk_to_qgis/language", lang)
        
    def tr(self, text):
        if self.current_lang == "Bahasa Indonesia":
            return translations.get(text, text)
        return text

def tr(text):
    return I18nManager.get_instance().tr(text)
