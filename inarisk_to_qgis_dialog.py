import os
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                                 QRadioButton, QComboBox, QPushButton, QFileDialog, 
                                 QLabel, QCheckBox, QDialogButtonBox, QLineEdit, QFormLayout,
                                 QSplitter, QTabWidget, QScrollArea, QTextEdit, QTextBrowser,
                                 QProgressBar, QWidget, QSizePolicy)
from qgis.core import QgsProject

class ModeSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super(ModeSelectionDialog, self).__init__(parent)
        self.setWindowTitle('InaRISK to QGIS - Select Mode')
        self.resize(300, 100)
        
        layout = QVBoxLayout(self)
        self.btn_server = QPushButton("Download from InaRISK Server (GeoServer)")
        self.btn_local = QPushButton("Process Local Zip Files")
        
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
        
        from qgis.PyQt.QtWidgets import QSplitter, QTabWidget, QScrollArea, QTextEdit, QTextBrowser, QProgressBar, QWidget, QSizePolicy
        from qgis.PyQt.QtCore import Qt

        self.setWindowTitle('InaRISK Downloader - Server Download')
        self.resize(850, 600)
        
        main_layout = QVBoxLayout(self)

        self.splitter = QSplitter(Qt.Horizontal)
        
        # --- LEFT PANE (Tabs) ---
        self.tabs = QTabWidget()
        
        # 1. Parameters Tab
        self.tab_params = QWidget()
        params_layout = QVBoxLayout(self.tab_params)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        
        # Source Settings
        self.server_widget = QGroupBox("Index Options")
        server_form = QFormLayout(self.server_widget)
        self.cmb_server_index = QComboBox()
        self.cmb_server_index.addItems(['Bahaya', 'Risiko', 'Kerentanan'])
        self.cmb_server_disaster = QComboBox()
        
        self.chk_all_disasters = QCheckBox("Download all types")
        self.chk_all_disasters.stateChanged.connect(self.toggle_all_disasters)
        
        self.cmb_server_index.currentIndexChanged.connect(self.update_server_disasters)
        self.update_server_disasters()
        
        server_form.addRow("Index Type:", self.cmb_server_index)
        server_form.addRow("Disaster:", self.cmb_server_disaster)
        server_form.addRow("", self.chk_all_disasters)
        self.scroll_layout.addWidget(self.server_widget)

        # Area Selection
        area_group = QGroupBox("Area Selection")
        area_form = QFormLayout(area_group)
        
        aoi_layout = QHBoxLayout()
        aoi_layout.setContentsMargins(0, 0, 0, 0)
        self.cmb_aoi = QComboBox()
        self.cmb_aoi.setEditable(True)
        self.cmb_aoi.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.refresh_layers()
        
        self.btn_browse_aoi = QPushButton("Browse")
        self.btn_browse_aoi.clicked.connect(self.browse_aoi)
        
        aoi_layout.addWidget(self.cmb_aoi)
        aoi_layout.addWidget(self.btn_browse_aoi)
        
        area_form.addRow("Area Layer:", aoi_layout)
        self.scroll_layout.addWidget(area_group)

        # Output Options
        out_group = QGroupBox("Output Options")
        out_layout = QFormLayout()
        
        out_dir_layout = QHBoxLayout()
        out_dir_layout.setContentsMargins(0, 0, 0, 0)
        self.txt_out_dir = QLineEdit()
        self.txt_out_dir.setPlaceholderText("[Create temporary layer]")
        self.btn_browse_out = QPushButton("Browse")
        self.btn_browse_out.clicked.connect(self.browse_out_dir)
        out_dir_layout.addWidget(self.txt_out_dir)
        out_dir_layout.addWidget(self.btn_browse_out)
        out_layout.addRow("Save Folder:", out_dir_layout)
        
        self.cmb_out_type = QComboBox()
        self.cmb_out_type.addItems(["Output as Raster", "Output as Vector (Polygons)"])
        out_layout.addRow("Output Type:", self.cmb_out_type)
        
        self.cmb_format = QComboBox()
        out_layout.addRow("Format:", self.cmb_format)
        
        self.cmb_classify = QComboBox()
        self.cmb_classify.addItems(["Classify", "Do Not Classify"])
        out_layout.addRow("Classification:", self.cmb_classify)
        
        self.chk_simplify = QCheckBox("Smooth Polygons")
        self.chk_simplify.setEnabled(False)
        out_layout.addRow("", self.chk_simplify)
        
        out_group.setLayout(out_layout)
        self.scroll_layout.addWidget(out_group)
        
        self.scroll_layout.addStretch() # Push everything up
        self.scroll.setWidget(self.scroll_content)
        params_layout.addWidget(self.scroll)
        self.tabs.addTab(self.tab_params, "Parameters")

        # 2. Log Tab
        self.tab_log = QWidget()
        log_layout = QVBoxLayout(self.tab_log)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        log_layout.addWidget(self.txt_log)
        self.tabs.addTab(self.tab_log, "Log")
        
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
        self.btn_run = QPushButton("Run")
        self.btn_close = QPushButton("Close")
        self.buttonBox.addButton(self.btn_run, QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.btn_close, QDialogButtonBox.RejectRole)
        
        self.btn_run.clicked.connect(self.run_process)
        self.btn_close.clicked.connect(self.reject)
        main_layout.addWidget(self.buttonBox)
        
        # Connect format toggle
        self.cmb_out_type.currentIndexChanged.connect(self.toggle_format_options)
        self.toggle_format_options() # Initial setup

    def get_help_html(self):
        desc = "This algorithm fetches and processes InaRISK raster data directly from BNPB ArcGIS ImageServers." 
        
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
            <h2>InaRISK to QGIS</h2>
            <p>{desc}</p>
            
            <h3>How to Use</h3>
            <ul>
                <li><b>Index Options:</b> Select the Index Type (Bahaya, Risiko, Kerentanan) and the specific disaster you wish to map.</li>
                <li><b>Area Selection:</b> Choose an active vector layer from your QGIS project or click <b>Browse</b> to load a spatial file (Shapefile, GeoJSON, etc.). The tool will strictly crop the data to this bounding area.</li>
                <li><b>Output Type:</b> You can output the raw Raster, or have the plugin automatically convert it into Vector Polygons.</li>
                <li><b>Classification:</b> If selected, the raw float values will be categorized into standard ranges (Tinggi, Sedang, Rendah).</li>
                <li><b>Save Folder:</b> Leave as <code>[Create temporary layer]</code> to load the result into memory, or browse to a folder to save it permanently.</li>
            </ul>
            
            <p>Vector polygon outputs will automatically include <b>Kelas</b>, <b>Value</b>, and <b>Source</b> attributes.</p>

            <div class="disclaimer">
                <b>Disclaimer:</b> This is an unofficial tool created by <b>Juhans</b> to assist with disaster spatial analysis, and is not officially affiliated with BNPB. Data is sourced from the public InaRISK server.<br><br>
                Contact: <a href="mailto:juhans@tuta.io">juhans@tuta.io</a>
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
        is_vector = (self.cmb_out_type.currentText() == "Output as Vector (Polygons)")
        self.cmb_format.clear()
        if is_vector:
            self.cmb_format.addItems(['.shp', '.gpkg', '.geojson', '.kml'])
            self.chk_simplify.setEnabled(True)
        else:
            self.cmb_format.addItems(['.tif'])
            self.chk_simplify.setEnabled(False)

    def update_server_disasters(self):
        index_type = self.cmb_server_index.currentText()
        self.cmb_server_disaster.clear()
        
        if index_type == 'Bahaya':
            self.cmb_server_disaster.addItems([
                'Banjir', 'Banjir Bandang', 'Cuaca Ekstrim', 
                'Gelombang Ekstrim dan Abrasi', 'Gempa Bumi', 
                'Gunung Api', 'Kekeringan', 'Likuefaksi', 
                'Tanah Longsor', 'Tsunami'
            ])
        elif index_type == 'Kerentanan':
            self.cmb_server_disaster.addItems([
                'Banjir', 'Banjir Bandang', 'Cuaca Ekstrim', 
                'Gelombang Ekstrim dan Abrasi', 'Gempa Bumi', 
                'Gunung Api', 'Kekeringan', 'Likuefaksi', 
                'Tanah Longsor', 'Tsunami'
            ])
        elif index_type == 'Risiko':
            self.cmb_server_disaster.addItems([
                'Tanah Longsor'
            ])

    def browse_out_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if directory:
            self.txt_out_dir.setText(directory)

    def browse_aoi(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select AOI Vector File", "", "Vector files (*.shp *.gpkg *.geojson *.kml)")
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
