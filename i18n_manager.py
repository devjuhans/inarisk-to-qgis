from qgis.PyQt.QtCore import QSettings

translations = {
    'Run InaRISK to QGIS': 'Jalankan InaRISK to QGIS',
    'Download from InaRISK Server (GeoServer)': 'Unduh dari Server InaRISK (GeoServer)',
    'Process Local Zip Files': 'Proses File Zip Lokal',
    'InaRISK Downloader - Server Download': 'Pengunduh InaRISK - Unduhan Server',
    'Parameters': 'Parameter',
    'Log': 'Log',
    'Index Options': 'Opsi Indeks',
    'Index Type:': 'Jenis Indeks:',
    'Disaster:': 'Bencana:',
    'Download all types': 'Unduh semua jenis',
    'Area Selection': 'Pemilihan Area',
    'Area Layer:': 'Layer Area:',
    'Browse': 'Cari',
    'Output Options': 'Opsi Output',
    'Save Folder:': 'Folder Penyimpanan:',
    '[Create temporary layer]': '[Buat layer sementara]',
    'Output Type:': 'Jenis Output:',
    'Output as Raster': 'Output sebagai Raster',
    'Output as Vector (Polygons)': 'Output sebagai Vektor (Poligon)',
    'Format:': 'Format:',
    'Classification:': 'Klasifikasi:',
    'Classify': 'Klasifikasikan',
    'Do Not Classify': 'Jangan Klasifikasikan',
    'Smooth Polygons': 'Haluskan Poligon',
    'Run': 'Jalankan',
    'Close': 'Tutup',
    'Select Output Folder': 'Pilih Folder Output',
    'Select AOI Vector File': 'Pilih File Vektor AOI',
    'Vector files (*.shp *.gpkg *.geojson *.kml)': 'File vektor (*.shp *.gpkg *.geojson *.kml)',
    
    # Help text
    'InaRISK to QGIS': 'InaRISK ke QGIS',
    'This algorithm fetches and processes InaRISK raster data directly from BNPB ArcGIS ImageServers.': 'Algoritma ini mengambil dan memproses data raster InaRISK langsung dari BNPB ArcGIS ImageServers.',
    'How to Use': 'Cara Penggunaan',
    'Select the Index Type (Bahaya, Risiko, Kerentanan) and the specific disaster you wish to map.': 'Pilih Jenis Indeks (Bahaya, Risiko, Kerentanan) dan bencana spesifik yang ingin dipetakan.',
    'Choose an active vector layer from your QGIS project or click <b>Browse</b> to load a spatial file (Shapefile, GeoJSON, etc.). The tool will strictly crop the data to this bounding area.': 'Pilih layer vektor aktif dari proyek QGIS Anda atau klik <b>Cari</b> untuk memuat file spasial (Shapefile, GeoJSON, dll). Alat ini akan memotong data sesuai area batas ini.',
    'You can output the raw Raster, or have the plugin automatically convert it into Vector Polygons.': 'Anda dapat menghasilkan output Raster mentah, atau membiarkan plugin mengubahnya menjadi Vektor Poligon secara otomatis.',
    'If selected, the raw float values will be categorized into standard ranges (Tinggi, Sedang, Rendah).': 'Jika dipilih, nilai float mentah akan dikategorikan ke rentang standar (Tinggi, Sedang, Rendah).',
    'Leave as <code>[Create temporary layer]</code> to load the result into memory, or browse to a folder to save it permanently.': 'Biarkan sebagai <code>[Buat layer sementara]</code> untuk memuat hasil ke dalam memori, atau cari folder untuk menyimpannya secara permanen.',
    'Vector polygon outputs will automatically include <b>Classification</b>, <b>Value</b>, and <b>Source</b> attributes.': 'Output vektor poligon akan otomatis menyertakan atribut <b>Klasifikasi</b>, <b>Value</b>, dan <b>Source</b>.',
    'Disclaimer:': 'Penafian:',
    'This is an unofficial tool created by <b>Juhans</b> to assist with disaster spatial analysis, and is not officially affiliated with BNPB. Data is sourced from the public InaRISK server and depends on its server condition; I have no control over its availability.': 'Ini adalah alat tidak resmi yang dibuat oleh <b>Juhans</b> untuk membantu analisis spasial bencana, dan tidak berafiliasi resmi dengan BNPB. Data bersumber dari server InaRISK publik dan bergantung pada kondisi servernya; saya tidak memiliki kendali atas ketersediaannya.',
    'Contact:': 'Kontak:',
    
    # core_logic.py logs
    'Reprojecting AOI from': 'Memproyeksikan ulang AOI dari',
    'Error': 'Kesalahan',
    'Please select a valid output directory.': 'Harap pilih direktori output yang valid.',
    'Downloading from server requires an AOI layer to define the extent.': 'Mengunduh dari server memerlukan layer AOI untuk menentukan batasan luas area.',
    '--- Processing': '--- Memproses',
    'Warning: Processing failed for': 'Peringatan: Pemrosesan gagal untuk',
    'Warning: Connection/Server failed for': 'Peringatan: Koneksi/Server gagal untuk',
    'continuing to next disaster...': 'melanjutkan ke bencana berikutnya...',
    'Successfully finished processing!': 'Pemrosesan berhasil diselesaikan!',
    '--- PROCESSING SUMMARY ---': '--- RINGKASAN PEMROSESAN ---',
    'Successfully Processed': 'Berhasil Diproses',
    'No Data in This Area': 'Tidak Ada Data di Area Ini',
    'Processing Error': 'Gagal Diproses (Terjadi Kesalahan)',
    'Server/Connection Error': 'Kesalahan Server/Koneksi',
    'No layer mapping found for': 'Tidak ada pemetaan layer yang ditemukan untuk',
    'Downloading': 'Mengunduh',
    'from BNPB ArcGIS ImageServer...': 'dari BNPB ArcGIS ImageServer...',
    'Server Error': 'Kesalahan Server',
    'ImageServer failed to provide a valid raster. Check if this specific disaster layer exists.': 'ImageServer gagal menyediakan raster yang valid. Periksa apakah layer bencana ini ada.',
    'Buffering AOI by 0.0005 degrees (~50m)...': 'Membuat buffer AOI sebesar 0.0005 derajat (~50m)...',
    'Clipping raster to AOI...': 'Memotong raster ke AOI...',
    'No Data Found for': 'Tidak Ada Data yang Ditemukan untuk',
    'in selected area.': 'di area yang dipilih.',
    'Classifying raster (0-0.3, 0.3-0.6, 0.6-1.0)...': 'Mengklasifikasikan raster (0-0.3, 0.3-0.6, 0.6-1.0)...',
    'Converting to Vector...': 'Mengonversi ke Vektor...',
    'Smoothing Polygons...': 'Menghaluskan Poligon...',
    'Clipping vector to real AOI...': 'Memotong vektor ke AOI sebenarnya...',
    'Adding fields (Kelas, Value, Source)...': 'Menambahkan bidang (Kelas, Value, Source)...',
    'Saving final raster...': 'Menyimpan raster akhir...',
    'Error processing': 'Kesalahan memproses',
    'Failed': 'Gagal',
    
    # New additions for index/disasters
    'Hazard': 'Bahaya',
    'Risk': 'Risiko',
    'Vulnerability': 'Kerentanan',
    'Flood': 'Banjir',
    'Flash Flood': 'Banjir Bandang',
    'Extreme Weather': 'Cuaca Ekstrim',
    'Extreme Wave and Abrasion': 'Gelombang Ekstrim dan Abrasi',
    'Earthquake': 'Gempa Bumi',
    'Volcano': 'Gunung Api',
    'Drought': 'Kekeringan',
    'Liquefaction': 'Likuefaksi',
    'Landslide': 'Tanah Longsor',
    
    # Classes and Sources
    'Low': 'Rendah',
    'Medium': 'Sedang',
    'High': 'Tinggi',
    'Hazard Index': 'Indeks Bahaya',
    'Risk Index': 'Indeks Risiko',
    'Vulnerability Index': 'Indeks Kerentanan',
    'InaRISK, by National Disaster Management Authority (BNPB) of Indonesia': 'InaRISK, oleh Badan Nasional Penanggulangan Bencana (BNPB)',
    'Classification': 'Klasifikasi',
    'Processing Finished': 'Pemrosesan Selesai'
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
        current_version = "1.2"
        
        if saved_version != current_version:
            self.current_lang = "English"
            settings.setValue("inarisk_to_qgis/language", "English")
            settings.setValue("inarisk_to_qgis/version", current_version)
        else:
            self.current_lang = settings.value("inarisk_to_qgis/language", "English", type=str)
        
    def set_language(self, lang):
        self.current_lang = lang
        settings = QSettings()
        settings.setValue("inarisk_to_qgis/language", lang)
        
    def tr(self, text):
        if self.current_lang == "Bahasa Indonesia" and text in translations:
            return translations[text]
        return text

def tr(text):
    return I18nManager.get_instance().tr(text)
