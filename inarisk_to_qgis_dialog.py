import os
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                                 QRadioButton, QComboBox, QPushButton, QFileDialog, 
                                 QLabel, QCheckBox, QDialogButtonBox, QLineEdit, QFormLayout,
                                 QSplitter, QTabWidget, QScrollArea, QTextEdit, QTextBrowser,
                                 QProgressBar, QWidget, QSizePolicy)
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject
from .i18n_manager import tr, I18nManager

class ModeSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super(ModeSelectionDialog, self).__init__(parent)
        self.setWindowTitle('InaRISK to QGIS - Select Mode')
        self.resize(300, 100)
        
        layout = QVBoxLayout(self)
        self.btn_server = QPushButton(tr("Download from InaRISK Server (GeoServer)"))
        self.btn_local = QPushButton(tr("Process Local Zip Files"))
        
        layout.addWidget(self.btn_server)
        layout.addWidget(self.btn_local)
        
        self.mode = None
        self.btn_server.clicked.connect(self.select_server)
        self.btn_local.clicked.connect(self.select_local)
        
    def select_server(self):
        self.mode = 'server'
        self.accept()

class InaRiskToQgisDialog(QDialog):
    def __init__(self, iface, parent=None):
        super(InaRiskToQgisDialog, self).__init__(parent or iface.mainWindow())
        self.iface = iface
        
        self.i18n = I18nManager.get_instance()

        self.setWindowTitle(tr('InaRISK to QGIS'))
        self.resize(850, 600)
        
        main_layout = QVBoxLayout(self)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- LEFT PANE (Tabs) ---
        self.tabs = QTabWidget()
        
        # 1. Parameters Tab
        self.tab_params = QWidget()
        params_layout = QVBoxLayout(self.tab_params)
        
        # Top bar with language selector
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItems(["English", "Bahasa Indonesia"])
        if self.i18n.current_lang == "Bahasa Indonesia":
            self.cmb_lang.setCurrentText("Bahasa Indonesia")
        else:
            self.cmb_lang.setCurrentText("English")
        self.cmb_lang.currentIndexChanged.connect(self.change_language)
        
        self.lbl_language = QLabel("Language:")
        lang_layout.addWidget(self.lbl_language)
        lang_layout.addWidget(self.cmb_lang)
        params_layout.addLayout(lang_layout)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        
        # Source Settings
        self.server_widget = QGroupBox(tr("Index Options"))
        server_form = QFormLayout(self.server_widget)
        self.cmb_server_index = QComboBox()
        self.cmb_server_index.addItem(tr("Hazard"), "Bahaya")
        self.cmb_server_index.addItem(tr("Risk"), "Risiko")
        self.cmb_server_index.addItem(tr("Vulnerability"), "Kerentanan")
        self.cmb_server_disaster = QComboBox()
        
        self.chk_all_disasters = QCheckBox(tr("Download all types"))
        self.chk_all_disasters.stateChanged.connect(self.toggle_all_disasters)
        
        self.cmb_server_index.currentIndexChanged.connect(self.update_server_disasters)
        self.update_server_disasters()
        
        self.lbl_index_type = QLabel(tr("Index Type:"))
        self.lbl_disaster = QLabel(tr("Disaster:"))
        
        server_form.addRow(self.lbl_index_type, self.cmb_server_index)
        server_form.addRow(self.lbl_disaster, self.cmb_server_disaster)
        server_form.addRow("", self.chk_all_disasters)
        self.scroll_layout.addWidget(self.server_widget)

        # Area Selection
        self.area_group = QGroupBox(tr("Area Selection"))
        area_form = QFormLayout(self.area_group)
        
        aoi_layout = QHBoxLayout()
        aoi_layout.setContentsMargins(0, 0, 0, 0)
        self.cmb_aoi = QComboBox()
        self.cmb_aoi.setEditable(True)
        self.cmb_aoi.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.refresh_layers()
        
        self.btn_browse_aoi = QPushButton(tr("Browse"))
        self.btn_browse_aoi.clicked.connect(self.browse_aoi)
        
        aoi_layout.addWidget(self.cmb_aoi)
        aoi_layout.addWidget(self.btn_browse_aoi)
        
        self.lbl_area_layer = QLabel(tr("Area Layer:"))
        
        area_form.addRow(self.lbl_area_layer, aoi_layout)
        self.scroll_layout.addWidget(self.area_group)

        # Output Options
        self.out_group = QGroupBox(tr("Output Options"))
        out_layout = QFormLayout()
        
        out_dir_layout = QHBoxLayout()
        out_dir_layout.setContentsMargins(0, 0, 0, 0)
        self.txt_out_dir = QLineEdit()
        self.txt_out_dir.setPlaceholderText(tr("[Create temporary layer]"))
        self.btn_browse_out = QPushButton(tr("Browse"))
        self.btn_browse_out.clicked.connect(self.browse_out_dir)
        out_dir_layout.addWidget(self.txt_out_dir)
        out_dir_layout.addWidget(self.btn_browse_out)
        
        self.lbl_save_folder = QLabel(tr("Save Folder:"))
        out_layout.addRow(self.lbl_save_folder, out_dir_layout)
        
        self.cmb_out_type = QComboBox()
        self.cmb_out_type.addItems([tr("Output as Raster"), tr("Output as Vector (Polygons)")])
        
        self.lbl_out_type = QLabel(tr("Output Type:"))
        out_layout.addRow(self.lbl_out_type, self.cmb_out_type)
        
        self.cmb_format = QComboBox()
        self.lbl_format = QLabel(tr("Format:"))
        out_layout.addRow(self.lbl_format, self.cmb_format)
        
        self.cmb_classify = QComboBox()
        self.cmb_classify.addItems([tr("Classify"), tr("Do Not Classify")])
        self.lbl_classify = QLabel(tr("Classification:"))
        out_layout.addRow(self.lbl_classify, self.cmb_classify)
        
        self.chk_simplify = QCheckBox(tr("Smooth Polygons"))
        self.chk_simplify.setEnabled(False)
        out_layout.addRow("", self.chk_simplify)
        
        self.out_group.setLayout(out_layout)
        self.scroll_layout.addWidget(self.out_group)
        
        self.scroll_layout.addStretch() # Push everything up
        self.scroll.setWidget(self.scroll_content)
        params_layout.addWidget(self.scroll)
        self.tabs.addTab(self.tab_params, tr("Parameters"))

        # 2. Log Tab
        self.tab_log = QWidget()
        log_layout = QVBoxLayout(self.tab_log)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        log_layout.addWidget(self.txt_log)
        self.tabs.addTab(self.tab_log, tr("Log"))
        
        self.splitter.addWidget(self.tabs)

        # --- RIGHT PANE (Help Browser) ---
        self.help_browser = QTextBrowser()
        self.help_browser.setHtml(self.get_help_html())
        self.splitter.addWidget(self.help_browser)
        
        self.splitter.setSizes([550, 300])
        main_layout.addWidget(self.splitter)

        # --- BOTTOM BAR ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        self.buttonBox = QDialogButtonBox()
        self.btn_run = QPushButton(tr("Run"))
        self.btn_close = QPushButton(tr("Close"))
        self.buttonBox.addButton(self.btn_run, QDialogButtonBox.ButtonRole.ActionRole)
        self.buttonBox.addButton(self.btn_close, QDialogButtonBox.ButtonRole.RejectRole)
        
        self.btn_run.clicked.connect(self.run_process)
        self.btn_close.clicked.connect(self.reject)
        main_layout.addWidget(self.buttonBox)
        
        # Connect format toggle
        self.cmb_out_type.currentIndexChanged.connect(self.toggle_format_options)
        self.toggle_format_options() # Initial setup
        
    def change_language(self, index):
        lang = self.cmb_lang.currentText()
        self.i18n.set_language(lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(tr('InaRISK to QGIS'))
        self.server_widget.setTitle(tr("Index Options"))
        
        # update index types
        idx_idx = self.cmb_server_index.currentIndex()
        self.cmb_server_index.blockSignals(True)
        self.cmb_server_index.setItemText(0, tr("Hazard"))
        self.cmb_server_index.setItemText(1, tr("Risk"))
        self.cmb_server_index.setItemText(2, tr("Vulnerability"))
        self.cmb_server_index.blockSignals(False)
        
        # save selected disaster
        disaster_data = self.cmb_server_disaster.currentData()
        self.update_server_disasters()
        if disaster_data:
            idx = self.cmb_server_disaster.findData(disaster_data)
            if idx >= 0:
                self.cmb_server_disaster.setCurrentIndex(idx)
        
        self.chk_all_disasters.setText(tr("Download all types"))
        self.lbl_index_type.setText(tr("Index Type:"))
        self.lbl_disaster.setText(tr("Disaster:"))
        self.area_group.setTitle(tr("Area Selection"))
        self.btn_browse_aoi.setText(tr("Browse"))
        self.lbl_area_layer.setText(tr("Area Layer:"))
        self.out_group.setTitle(tr("Output Options"))
        
        if self.txt_out_dir.text() == "":
            self.txt_out_dir.setPlaceholderText(tr("[Create temporary layer]"))
        
        self.btn_browse_out.setText(tr("Browse"))
        self.lbl_save_folder.setText(tr("Save Folder:"))
        
        # Update combo box items
        self.cmb_out_type.blockSignals(True)
        out_type_idx = self.cmb_out_type.currentIndex()
        self.cmb_out_type.setItemText(0, tr("Output as Raster"))
        self.cmb_out_type.setItemText(1, tr("Output as Vector (Polygons)"))
        self.cmb_out_type.blockSignals(False)
        
        self.lbl_out_type.setText(tr("Output Type:"))
        self.lbl_format.setText(tr("Format:"))
        
        class_idx = self.cmb_classify.currentIndex()
        self.cmb_classify.setItemText(0, tr("Classify"))
        self.cmb_classify.setItemText(1, tr("Do Not Classify"))
        
        self.lbl_classify.setText(tr("Classification:"))
        self.chk_simplify.setText(tr("Smooth Polygons"))
        
        self.tabs.setTabText(0, tr("Parameters"))
        self.tabs.setTabText(1, tr("Log"))
        
        self.help_browser.setHtml(self.get_help_html())
        
        self.btn_run.setText(tr("Run"))
        self.btn_close.setText(tr("Close"))

    def get_help_html(self):
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; font-size: 12px; margin: 10px; color: #333; }}
                h2 {{ color: #2c3e50; font-size: 16px; margin-bottom: 5px; }}
                h3 {{ color: #34495e; font-size: 13px; margin-top: 15px; margin-bottom: 5px; }}
                p {{ margin-bottom: 10px; line-height: 1.4; }}
                ul {{ margin-top: 5px; margin-bottom: 10px; padding-left: 20px; }}
                .disclaimer {{ background-color: #f8f9fa; border-left: 4px solid #e74c3c; padding: 8px; margin-top: 20px; font-style: italic; }}
            </style>
        </head>
        <body>
            <h2>{tr('InaRISK to QGIS')}</h2>
            <p>{tr('This algorithm fetches and processes InaRISK raster data directly from BNPB ArcGIS ImageServers.')}</p>
            
            <h3>{tr('How to Use')}</h3>
            <ul>
                <li><b>{tr('Index Options')}:</b> {tr('Select the Index Type (Bahaya, Risiko, Kerentanan) and the specific disaster you wish to map.')}</li>
                <li><b>{tr('Area Selection')}:</b> {tr('Choose an active vector layer from your QGIS project or click <b>Browse</b> to load a spatial file (Shapefile, GeoJSON, etc.). The tool will strictly crop the data to this bounding area.')}</li>
                <li><b>{tr('Output Type')}:</b> {tr('You can output the raw Raster, or have the plugin automatically convert it into Vector Polygons.')}</li>
                <li><b>{tr('Classification')}:</b> {tr('If selected, the raw float values will be categorized into standard ranges (Tinggi, Sedang, Rendah).')}</li>
                <li><b>{tr('Save Folder')}:</b> {tr('Leave as <code>[Create temporary layer]</code> to load the result into memory, or browse to a folder to save it permanently.')}</li>
            </ul>
            
            <p>{tr('Vector polygon outputs will automatically include <b>Classification</b>, <b>Value</b>, and <b>Source</b> attributes.')}</p>

            <div class="disclaimer">
                <b>{tr('Disclaimer:')}</b> {tr('This is an unofficial tool created by <b>Juhans</b> to assist with disaster spatial analysis, and is not officially affiliated with BNPB. Data is sourced from the public InaRISK server and depends on its server condition; I have no control over its availability.')}<br><br>
                {tr('Contact:')} <a href="mailto:juhans@tuta.io">juhans@tuta.io</a>
            </div>
        </body>
        </html>
        """

    def run_process(self):
        from .core_logic import InaRiskProcessor
        self.btn_run.setEnabled(False)
        self.tabs.setCurrentIndex(1) # Switch to Log tab
        self.progress_bar.setValue(0)
        self.txt_log.clear()
        
        processor = InaRiskProcessor(self, self.iface)
        processor.process()
        
        self.btn_run.setEnabled(True)

    def toggle_format_options(self):
        is_vector = (self.cmb_out_type.currentIndex() == 1)
        self.cmb_format.clear()
        if is_vector:
            self.cmb_format.addItems(['.shp', '.gpkg', '.geojson', '.kml'])
            self.chk_simplify.setEnabled(True)
        else:
            self.cmb_format.addItems(['.tif'])
            self.chk_simplify.setEnabled(False)

    def update_server_disasters(self):
        index_type = self.cmb_server_index.currentData()
        self.cmb_server_disaster.clear()
        
        if index_type == 'Bahaya':
            disasters = [
                ('Flood', 'Banjir'), ('Flash Flood', 'Banjir Bandang'), ('Extreme Weather', 'Cuaca Ekstrim'), 
                ('Extreme Wave and Abrasion', 'Gelombang Ekstrim dan Abrasi'), ('Earthquake', 'Gempa Bumi'), 
                ('Volcano', 'Gunung Api'), ('Drought', 'Kekeringan'), ('Liquefaction', 'Likuefaksi'), 
                ('Landslide', 'Tanah Longsor'), ('Tsunami', 'Tsunami')
            ]
        elif index_type == 'Kerentanan':
            disasters = [
                ('Flood', 'Banjir'), ('Flash Flood', 'Banjir Bandang'), ('Extreme Weather', 'Cuaca Ekstrim'), 
                ('Extreme Wave and Abrasion', 'Gelombang Ekstrim dan Abrasi'), ('Earthquake', 'Gempa Bumi'), 
                ('Volcano', 'Gunung Api'), ('Drought', 'Kekeringan'), ('Liquefaction', 'Likuefaksi'), 
                ('Landslide', 'Tanah Longsor'), ('Tsunami', 'Tsunami')
            ]
        elif index_type == 'Risiko':
            disasters = [
                ('Landslide', 'Tanah Longsor')
            ]
        else:
            disasters = []
            
        for eng, ind in disasters:
            self.cmb_server_disaster.addItem(tr(eng), ind)

    def browse_out_dir(self):
        directory = QFileDialog.getExistingDirectory(self, tr("Select Output Folder"))
        if directory:
            self.txt_out_dir.setText(directory)

    def browse_aoi(self):
        file_path, _ = QFileDialog.getOpenFileName(self, tr("Select AOI Vector File"), "", tr("Vector files (*.shp *.gpkg *.geojson *.kml)"))
        if file_path:
            self.cmb_aoi.setCurrentText(file_path)

    def toggle_all_disasters(self):
        if hasattr(self, 'chk_all_disasters'):
            self.cmb_server_disaster.setEnabled(not self.chk_all_disasters.isChecked())

    def refresh_layers(self):
        self.cmb_aoi.clear()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == layer.VectorLayer:
                self.cmb_aoi.addItem(layer.name(), layer.id())
