import os
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, 
    QLabel, QComboBox, QLineEdit, QPushButton, QCheckBox, 
    QTextEdit, QProgressBar, QFileDialog, QTabWidget, QWidget,
    QSplitter, QTextBrowser, QListWidget, QListWidgetItem, QSizePolicy
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon, QIntValidator
from qgis.core import QgsProject, QgsMapLayerType
from .i18n_manager import tr, I18nManager

class InaRiskSpatialPlanningDialog(QDialog):
    def __init__(self, iface, parent=None):
        super(InaRiskSpatialPlanningDialog, self).__init__(parent)
        self.iface = iface
        
        self.setWindowTitle(tr("InaRISK for Spatial Planning"))
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), 'layer.svg')))
        self.resize(780, 560)
        self.setMinimumSize(700, 480)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header layout
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        self.lbl_lang = QLabel(tr("Language:"))
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItems(["English", "Bahasa Indonesia"])
        
        current_lang = I18nManager.get_instance().current_lang
        idx = self.cmb_lang.findText(current_lang)
        if idx != -1:
            self.cmb_lang.setCurrentIndex(idx)
        self.cmb_lang.currentIndexChanged.connect(self.change_language)
        
        header_layout.addWidget(self.lbl_lang)
        header_layout.addWidget(self.cmb_lang)
        main_layout.addLayout(header_layout)
        
        # Splitter between Tabs and Help panel
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter, 1)

        # Tabs
        self.tabs = QTabWidget()
        self.splitter.addWidget(self.tabs)
        
        # Help Panel
        self.help_browser = QTextBrowser()
        self.help_browser.setOpenExternalLinks(True)
        self.help_browser.setHtml(self.get_help_html())
        self.splitter.addWidget(self.help_browser)
        
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        
        # 1. Parameters Tab
        self.tab_params = QWidget()
        params_layout = QVBoxLayout(self.tab_params)
        params_layout.setContentsMargins(6, 6, 6, 6)
        
        from qgis.PyQt.QtWidgets import QScrollArea
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(4, 4, 4, 4)

        # Hazard Disasters Selection (Hazard only)
        self.disaster_group = QGroupBox(tr("Disaster Prone Area"))
        disaster_form = QFormLayout(self.disaster_group)
        disaster_form.setVerticalSpacing(4)
        
        self.list_server_disaster = QListWidget()
        self.list_server_disaster.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.list_server_disaster.setMinimumHeight(135)
        self.list_server_disaster.setStyleSheet("""
            QListWidget {
                padding: 1px;
            }
            QListWidget::item {
                padding: 1px 2px;
                margin: 0px;
            }
        """)
        self.populate_hazard_disasters()
        
        self.chk_all_disasters = QCheckBox(tr("Download all types"))
        self.chk_all_disasters.toggled.connect(self.toggle_all_disasters)
        
        disaster_form.addRow(self.list_server_disaster)
        disaster_form.addRow("", self.chk_all_disasters)
        self.scroll_layout.addWidget(self.disaster_group)

        # Area Selection
        self.area_group = QGroupBox(tr("Area Selection"))
        area_form = QFormLayout(self.area_group)
        area_form.setVerticalSpacing(4)
        
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
        out_layout.setVerticalSpacing(4)
        
        self.txt_year = QLineEdit()
        self.txt_year.setPlaceholderText(tr("Optional"))
        self.txt_year.setValidator(QIntValidator(0, 9999, self))
        self.txt_year.setMaxLength(4)
        self.lbl_year = QLabel(tr("Access Year:"))
        out_layout.addRow(self.lbl_year, self.txt_year)
        
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
        self.cmb_out_type.currentIndexChanged.connect(self.toggle_format_options)
        self.cmb_out_type.setCurrentIndex(1) # Default to Vector for Spatial Planning
        self.lbl_out_type = QLabel(tr("Output Type:"))
        out_layout.addRow(self.lbl_out_type, self.cmb_out_type)
        
        self.cmb_format = QComboBox()
        self.lbl_format = QLabel(tr("Format:"))
        out_layout.addRow(self.lbl_format, self.cmb_format)
        self.toggle_format_options()
        
        self.cmb_classify = QComboBox()
        self.cmb_classify.addItems([tr("Classify"), tr("Do Not Classify")])
        self.lbl_classify = QLabel(tr("Classification:"))
        out_layout.addRow(self.lbl_classify, self.cmb_classify)
        
        self.chk_symbolize = QCheckBox(tr("Adjust Gradual Symbology"))
        self.chk_symbolize.setToolTip(tr("Apply thematic colors: Green (Low), Yellow (Medium), Red (High)."))
        self.chk_symbolize.setChecked(True)
        out_layout.addRow("", self.chk_symbolize)
        
        self.cmb_classify.currentIndexChanged.connect(self.toggle_classify_options)
        self.toggle_classify_options()
        
        self.out_group.setLayout(out_layout)
        self.scroll_layout.addWidget(self.out_group)
        
        self.scroll_layout.addStretch()
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
        
        # Bottom controls
        bottom_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        bottom_layout.addWidget(self.progress_bar)
        
        self.btn_run = QPushButton(tr("Run"))
        self.btn_run.clicked.connect(self.run_process)
        self.btn_close = QPushButton(tr("Close"))
        self.btn_close.clicked.connect(self.close)
        
        bottom_layout.addWidget(self.btn_run)
        bottom_layout.addWidget(self.btn_close)
        main_layout.addLayout(bottom_layout)

    def populate_hazard_disasters(self):
        checked_data = []
        for i in range(self.list_server_disaster.count()):
            item = self.list_server_disaster.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked_data.append(item.data(Qt.ItemDataRole.UserRole))
                
        self.list_server_disaster.clear()
        disasters = [
            ('Flood', 'Banjir'), ('Flash Flood', 'Banjir Bandang'), ('Extreme Weather', 'Cuaca Ekstrim'), 
            ('Extreme Wave and Abrasion', 'Gelombang Ekstrim dan Abrasi'), ('Earthquake', 'Gempa Bumi'), 
            ('Volcano', 'Gunung Api'), ('Drought', 'Kekeringan'), ('Liquefaction', 'Likuefaksi'), 
            ('Forest and Land Fire', 'Karhutla'), ('Landslide', 'Tanah Longsor'), ('Tsunami', 'Tsunami'),
            ('Multi', 'Multi')
        ]
        
        for eng, ind in disasters:
            item = QListWidgetItem(tr(eng))
            item.setData(Qt.ItemDataRole.UserRole, ind)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if ind in checked_data:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.list_server_disaster.addItem(item)
            
        if hasattr(self, 'chk_all_disasters') and self.chk_all_disasters.isChecked():
            for i in range(self.list_server_disaster.count()):
                self.list_server_disaster.item(i).setCheckState(Qt.CheckState.Checked)

    def change_language(self, index):
        lang = self.cmb_lang.currentText()
        I18nManager.get_instance().set_language(lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(tr("InaRISK for Spatial Planning"))
        self.lbl_lang.setText(tr("Language:"))
        self.disaster_group.setTitle(tr("Disaster Prone Area"))
        self.populate_hazard_disasters()
        
        self.chk_all_disasters.setText(tr("Download all types"))
        self.area_group.setTitle(tr("Area Selection"))
        self.btn_browse_aoi.setText(tr("Browse"))
        self.lbl_area_layer.setText(tr("Area Layer:"))
        self.out_group.setTitle(tr("Output Options"))
        
        if self.txt_out_dir.text() == "":
            self.txt_out_dir.setPlaceholderText(tr("[Create temporary layer]"))
        
        self.btn_browse_out.setText(tr("Browse"))
        self.lbl_save_folder.setText(tr("Save Folder:"))
        
        self.cmb_out_type.blockSignals(True)
        out_type_idx = self.cmb_out_type.currentIndex()
        self.cmb_out_type.setItemText(0, tr("Output as Raster"))
        self.cmb_out_type.setItemText(1, tr("Output as Vector (Polygons)"))
        self.cmb_out_type.setCurrentIndex(out_type_idx)
        self.cmb_out_type.blockSignals(False)
        
        self.lbl_out_type.setText(tr("Output Type:"))
        self.lbl_format.setText(tr("Format:"))
        
        cur_classify_idx = self.cmb_classify.currentIndex()
        self.cmb_classify.blockSignals(True)
        self.cmb_classify.setItemText(0, tr("Classify"))
        self.cmb_classify.setItemText(1, tr("Do Not Classify"))
        self.cmb_classify.setCurrentIndex(cur_classify_idx)
        self.cmb_classify.blockSignals(False)
        
        self.lbl_classify.setText(tr("Classification:"))
        self.chk_symbolize.setText(tr("Adjust Gradual Symbology"))
        self.chk_symbolize.setToolTip(tr("Apply thematic colors: Green (Low), Yellow (Medium), Red (High)."))
        self.lbl_year.setText(tr("Access Year:"))
        self.txt_year.setPlaceholderText(tr("Optional"))
        self.toggle_classify_options()
        
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
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; font-size: 11px; margin: 8px; color: #2c3e50; line-height: 110%; }}
                h2 {{ color: #2c3e50; font-size: 13px; margin: 0 0 4px 0; font-weight: bold; line-height: 110%; }}
                h3 {{ color: #34495e; font-size: 11px; margin: 8px 0 2px 0; font-weight: bold; line-height: 110%; }}
                p {{ margin: 0 0 5px 0; line-height: 110%; text-align: left; }}
                .footer-box {{ background-color: #f8f9fa; border-left: 3px solid #FE8038; padding: 5px 8px; margin-top: 8px; font-size: 10px; color: #555; line-height: 110%; }}
            </style>
        </head>
        <body>
            <h2>{tr('InaRISK for Spatial Planning')}</h2>
            <p>{tr('Extract and format BNPB Hazard data into standardized Kawasan Rawan Bencana (KRB) layers for spatial planning (RTRW/RDTR).')}</p>
            
            <h3>{tr('User Guide')}</h3>
            <p>{tr('Select the hazard layers and specify the Area Layer (AOI) boundary.')}</p>
            <p>{tr('Outputs use standard KRB naming (e.g. KRB_BANJIR_AR). Classification applies BNPB equal-interval tiers: Low (0 - 0.333), Medium (0.333 - 0.667), and High (0.667 - 1.0) per Perka BNPB No. 2/2012.')}</p>
            
            <h3>{tr('Vector Attributes')}</h3>
            <p>{tr("Vector polygon layers include attribute fields for 'Kelas' (e.g. Kawasan Rawan Bencana Banjir Tinggi), 'Value' (index range), and 'Source' (attribution with optional access year).")}</p>

            <div class="footer-box">
                <b>{tr('Notice:')}</b> {tr('Requires an active internet connection to access BNPB servers.')}<br>
                {tr('Contact:')} <a href="mailto:juhans@karpo.work">juhans@karpo.work</a>
            </div>
        </body>
        </html>
        """

    def run_process(self):
        from .core_logic import InaRiskProcessor
        self.btn_run.setEnabled(False)
        self.tabs.setCurrentIndex(1)
        self.progress_bar.setValue(0)
        self.txt_log.clear()
        
        processor = InaRiskProcessor(self, self.iface, is_spatial_planning=True)
        processor.process()
        
        self.btn_run.setEnabled(True)

    def toggle_format_options(self):
        is_vector = (self.cmb_out_type.currentIndex() == 1)
        self.cmb_format.clear()
        if is_vector:
            self.cmb_format.addItems(['.gpkg', '.shp', '.geojson', '.kml'])
        else:
            self.cmb_format.addItems(['.tif'])

    def toggle_classify_options(self):
        is_classified = (self.cmb_classify.currentIndex() == 0)
        self.chk_symbolize.setEnabled(is_classified)
        if not is_classified:
            self.chk_symbolize.setChecked(False)
        else:
            self.chk_symbolize.setChecked(True)

    def browse_out_dir(self):
        directory = QFileDialog.getExistingDirectory(self, tr("Select Output Folder"))
        if directory:
            self.txt_out_dir.setText(directory)

    def browse_aoi(self):
        fpath, _ = QFileDialog.getOpenFileName(
            self, tr("Select AOI Vector File"), "", tr("Vector files (*.shp *.gpkg *.geojson *.kml)")
        )
        if fpath:
            self.cmb_aoi.setEditText(fpath)

    def toggle_all_disasters(self):
        if hasattr(self, 'chk_all_disasters'):
            is_checked = self.chk_all_disasters.isChecked()
            for i in range(self.list_server_disaster.count()):
                item = self.list_server_disaster.item(i)
                item.setCheckState(Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)
            self.list_server_disaster.setEnabled(not is_checked)

    def refresh_layers(self):
        self.cmb_aoi.clear()
        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == QgsMapLayerType.VectorLayer:
                self.cmb_aoi.addItem(layer.name(), layer.id())
