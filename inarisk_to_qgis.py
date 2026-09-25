from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

import os.path
from .inarisk_to_qgis_dialog import InaRiskToQgisDialog
from .spatial_planning_dialog import InaRiskSpatialPlanningDialog
from .i18n_manager import tr

class InaRiskToQgis:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = '&InaRISK to QGIS'
        self.first_start = True

    def add_action(self, icon_path, text, callback, enabled_flag=True,
                   add_to_menu=True, add_to_toolbar=True, status_tip=None,
                   whats_this=None, parent=None):
        
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)
        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_earth = os.path.join(self.plugin_dir, 'earth.svg')
        icon_layer = os.path.join(self.plugin_dir, 'layer.svg')
        
        self.add_action(
            icon_earth,
            text=tr('Run InaRISK to QGIS'),
            callback=self.run_server,
            parent=self.iface.mainWindow())

        self.add_action(
            icon_layer,
            text=tr('InaRISK for Spatial Planning'),
            callback=self.run_spatial_planning,
            parent=self.iface.mainWindow())

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu('&InaRISK to QGIS', action)
            self.iface.removeToolBarIcon(action)

    def run_server(self):
        self._launch_dialog()

    def _launch_dialog(self):
        self.dlg = InaRiskToQgisDialog(self.iface)
        self.dlg.exec()

    def run_spatial_planning(self):
        self.dlg_sp = InaRiskSpatialPlanningDialog(self.iface)
        self.dlg_sp.exec()
