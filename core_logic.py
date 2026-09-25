import os
import zipfile
import processing
from qgis.core import (QgsProject, QgsRasterLayer, QgsVectorLayer, QgsMessageLog, Qgis, QgsGeometry, QgsFeature, QgsField, QgsSpatialIndex)
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtCore import Qt, QVariant
from .i18n_manager import tr

SERVER_MAPPING = {
    'Bahaya': {
        'Banjir': 'INDEKS_BAHAYA_BANJIR',
        'Banjir Bandang': 'INDEKS_BAHAYA_BANJIRBANDANG',
        'Cuaca Ekstrim': 'INDEKS_BAHAYA_CUACAEKSTRIM',
        'Gelombang Ekstrim dan Abrasi': 'INDEKS_BAHAYA_GEA',
        'Gempa Bumi': 'INDEKS_BAHAYA_GEMPABUMI',
        'Gunung Api': 'INDEKS_BAHAYA_GUNUNGAPI',
        'Kekeringan': 'INDEKS_BAHAYA_KEKERINGAN',
        'Likuefaksi': 'INDEKS_BAHAYA_LIKUEFAKSI',
        'Karhutla': 'INDEKS_BAHAYA_KARHUTLA',
        'Tanah Longsor': 'INDEKS_BAHAYA_TANAHLONGSOR',
        'Tsunami': 'INDEKS_BAHAYA_TSUNAMI',
        'Multi': 'INDEKS_MULTI_BAHAYA'
    },
    'Kerentanan': {
        'Banjir': 'INDEKS_KERENTANAN_BANJIR',
        'Banjir Bandang': 'INDEKS_KERENTANAN_BANJIR_BANDANG',
        'Cuaca Ekstrim': 'INDEKS_KERENTANAN_CUACA_EKSTRIM',
        'Gelombang Ekstrim dan Abrasi': 'INDEKS_KERENTANAN_GELOMBANG_EKSTRIM_ABRASI',
        'Gempa Bumi': 'INDEKS_KERENTANAN_GEMPABUMI',
        'Gunung Api': 'INDEKS_KERENTANAN_LETUSAN_GUNUNGAPI',
        'Kekeringan': 'INDEKS_KERENTANAN_KEKERINGAN',
        'Likuefaksi': 'INDEKS_KERENTANAN_LIKUEFAKSI',
        'Karhutla': 'INDEKS_KERENTANAN_KEBAKARAN_HUTAN_LAHAN',
        'Tanah Longsor': 'INDEKS_KERENTANAN_TANAH_LONGSOR',
        'Tsunami': 'INDEKS_KERENTANAN_TSUNAMI',
        'Multi': 'INDEKS_KERENTANAN_MULTI_BAHAYA'
    },
    'Risiko': {
        'Banjir': 'layer_risiko_banjir',
        'Banjir Bandang': 'layer_risiko_banjir_bandang',
        'Cuaca Ekstrim': 'layer_risiko_cuaca_ekstrim',
        'Gelombang Ekstrim dan Abrasi': 'layer_risiko_gelombang_ekstrim_dan_abrasi',
        'Gempa Bumi': 'layer_risiko_gempabumi',
        'Gunung Api': 'layer_risiko_letusan_gunungapi',
        'Kekeringan': 'layer_risiko_kekeringan',
        'Likuefaksi': 'layer_risiko_likuefaksi',
        'Karhutla': 'layer_risiko_kebakaran_hutan_dan_lahan',
        'Tanah Longsor': 'INDEKS_RISIKO_TANAH_LONGSOR',
        'Tsunami': 'layer_risiko_tsunami',
        'Multi': 'layer_risiko_multi'
    }
}

class InaRiskProcessor:
    def __init__(self, dlg, iface, is_spatial_planning=False):
        self.dlg = dlg
        self.iface = iface
        self.is_spatial_planning = is_spatial_planning
        
    def log(self, message):
        from qgis.PyQt.QtCore import QCoreApplication, QEventLoop
        QgsMessageLog.logMessage(message, 'InaRISK to QGIS', Qgis.MessageLevel.Info)
        if hasattr(self.dlg, 'txt_log'):
            self.dlg.txt_log.append(message)
            QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)

    def set_progress(self, val):
        from qgis.PyQt.QtCore import QCoreApplication, QEventLoop
        if hasattr(self.dlg, 'progress_bar'):
            self.dlg.progress_bar.setValue(int(val))
            QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
        
    def process(self):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.set_progress(5)
        try:
            # 1. Gather Inputs
            out_dir = self.dlg.txt_out_dir.text()
            out_format = self.dlg.cmb_format.currentText()
            aoi_layer_text = self.dlg.cmb_aoi.currentText()
            year = self.dlg.txt_year.text().strip() if hasattr(self.dlg, 'txt_year') else ""
            
            do_classify = (self.dlg.cmb_classify.currentIndex() == 0)
            do_vector = (self.dlg.cmb_out_type.currentIndex() == 1)
            do_symbolize = self.dlg.chk_symbolize.isChecked() and do_classify
            
            is_temp = not self.dlg.txt_out_dir.text().strip() or self.dlg.txt_out_dir.text() == tr("[Create temporary layer]")
            if is_temp:
                import tempfile
                out_dir = tempfile.gettempdir()
            elif not out_dir or not os.path.isdir(out_dir):
                self.iface.messageBar().pushMessage(tr("Error"), tr("Please select a valid output directory."), level=Qgis.MessageLevel.Warning, duration=5)
                return
                
            aoi_layer = None
            layers = QgsProject.instance().mapLayersByName(aoi_layer_text)
            if layers:
                aoi_layer = layers[0]
            elif aoi_layer_text and os.path.isfile(aoi_layer_text):
                aoi_layer = QgsVectorLayer(aoi_layer_text, "AOI", "ogr")
                if not aoi_layer.isValid():
                    aoi_layer = None
                    
            if aoi_layer:
                from qgis.core import QgsCoordinateReferenceSystem
                if aoi_layer.crs().authid() != "EPSG:4326":
                    self.log(f"{tr('Reprojecting AOI from')} {aoi_layer.crs().authid()} to EPSG:4326...")
                    reprojected_path = os.path.join(out_dir, "temp_aoi_4326.gpkg")
                    res = processing.run("native:reprojectlayer", {
                        'INPUT': aoi_layer,
                        'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
                        'OUTPUT': reprojected_path
                    })
                    aoi_layer = QgsVectorLayer(res['OUTPUT'], "AOI_4326", "ogr")

            # 2. Iterate and Process
            if not aoi_layer:
                self.iface.messageBar().pushMessage(tr("Error"), tr("Downloading from server requires an AOI layer to define the extent."), level=Qgis.MessageLevel.Warning, duration=5)
                return
                
            if self.is_spatial_planning:
                index_type = 'Bahaya'
            else:
                index_type = self.dlg.cmb_server_index.currentData()

            disasters = []
            if hasattr(self.dlg, 'chk_all_disasters') and self.dlg.chk_all_disasters.isChecked():
                disasters = [self.dlg.list_server_disaster.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.dlg.list_server_disaster.count())]
            else:
                for i in range(self.dlg.list_server_disaster.count()):
                    item = self.dlg.list_server_disaster.item(i)
                    if item.checkState() == Qt.CheckState.Checked:
                        disasters.append(item.data(Qt.ItemDataRole.UserRole))
                        
            if not disasters:
                self.iface.messageBar().pushMessage(tr("Error"), tr("Please select at least one disaster."), level=Qgis.MessageLevel.Warning, duration=5)
                return
            
            total = len(disasters)
            summary_messages = []
            for i, d in enumerate(disasters):
                self.log(f"{tr('Processing')}: {d} ({i+1}/{total})")
                status = self._process_single(index_type=index_type, disaster_type=d,
                                               out_dir=out_dir, out_format=out_format, aoi_layer=aoi_layer,
                                               do_classify=do_classify, do_vector=do_vector,
                                               do_symbolize=do_symbolize, is_temp=is_temp, year=year,
                                               progress_base=10 + (i/total)*80, progress_scale=80/total)
                
                if status == "SUCCESS":
                    summary_messages.append(f"- {d}: {tr('Success')}")
                elif status == "NO_DATA":
                    summary_messages.append(f"- {d}: {tr('No data found in selected area')}")
                elif status == "SERVER_ERROR":
                    self.log(f"{tr('Warning: Server connection failed for')} {d}. {tr('Proceeding to next item.')}")
                    summary_messages.append(f"- {d}: {tr('Server/Connection error')}")
                else:
                    self.log(f"{tr('Warning: Processing failed for')} {d}. {tr('Proceeding to next item.')}")
                    summary_messages.append(f"- {d}: {tr('Processing error')}")
            
            QApplication.restoreOverrideCursor()
            self.set_progress(100)
            self.log(f"{tr('Processing completed.')}")
            
            self.log(f"\n{tr('Processing Summary')}:")
            for msg in summary_messages:
                self.log(msg)
            self.log("--------------------------\n")
            
            from qgis.PyQt.QtWidgets import QMessageBox
            summary_text = "\n".join(summary_messages)
            QMessageBox.information(self.dlg, tr("Completed"), f"{tr('Processing has completed.')}\n\n{tr('Summary')}:\n{summary_text}")
        except Exception as e:
            self.log(f"{tr('Error')}: {str(e)}")
            self.iface.messageBar().pushMessage(tr("Error"), str(e), level=Qgis.MessageLevel.Critical, duration=10)
        finally:
            QApplication.restoreOverrideCursor()

    def _process_single(self, index_type, disaster_type, out_dir, out_format, aoi_layer, do_classify, do_vector, do_symbolize, is_temp, year, progress_base, progress_scale):
        try:
            layer_name = SERVER_MAPPING.get(index_type, {}).get(disaster_type)
            if not layer_name:
                self.iface.messageBar().pushMessage(tr("Error"), f"{tr('No layer mapping found for')} {index_type} {disaster_type}", level=Qgis.MessageLevel.Warning, duration=5)
                return "ERROR"
                
            dis_str = disaster_type.upper().replace(" ", "_")
            
            self.log(f"{tr('Downloading')} {layer_name}...")
            self.set_progress(progress_base + 10 * progress_scale / 80)
            
            extent = aoi_layer.extent()
            minx, miny, maxx, maxy = extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()
            
            minx -= 0.005
            miny -= 0.005
            maxx += 0.005
            maxy += 0.005
            bbox = f"{minx},{miny},{maxx},{maxy}"
            
            import math
            width = min(int(math.ceil((maxx - minx) / 0.00027)), 4000)
            height = min(int(math.ceil((maxy - miny) / 0.00027)), 4000)
            
            arcgis_url = (f"https://gis.bnpb.go.id/server/rest/services/inarisk/{layer_name}/ImageServer/exportImage"
                          f"?bbox={bbox}&bboxSR=4326&imageSR=4326"
                          f"&size={width},{height}&format=tiff&f=image")
                       
            input_raster_path = os.path.join(out_dir, f"temp_{dis_str}.tif")
            import urllib.request
            req = urllib.request.Request(arcgis_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:  # nosec
                content_type = response.headers.get('Content-Type', '')
                if 'json' in content_type or 'html' in content_type:
                    error_msg = response.read().decode('utf-8', errors='ignore')
                    self.iface.messageBar().pushMessage(tr("Server Error"), tr("ImageServer failed to provide a valid raster. Check if this specific disaster layer exists."), level=Qgis.MessageLevel.Critical, duration=10)
                    return "ERROR"
                    
                with open(input_raster_path, 'wb') as out_file:
                    out_file.write(response.read())

            # 3. Processing
            current_layer_path = input_raster_path
            self.set_progress(progress_base + 30 * progress_scale / 80)
            
            buffered_aoi_path = None
            if do_vector and aoi_layer:
                self.log(tr("Buffering AOI..."))
                self.set_progress(progress_base + 35 * progress_scale / 80)
                buffered_aoi_path = os.path.join(out_dir, f"temp_buffered_aoi_{disaster_type}.gpkg")
                processing.run("native:buffer", {
                    'INPUT': aoi_layer,
                    'DISTANCE': 0.0005,
                    'SEGMENTS': 5,
                    'OUTPUT': buffered_aoi_path
                })
            
            if aoi_layer:
                self.log(tr("Clipping raster..."))
                self.set_progress(progress_base + 40 * progress_scale / 80)
                clipped_path = os.path.join(out_dir, f"temp_clipped_{disaster_type}.tif")
                clip_mask = buffered_aoi_path if do_vector else aoi_layer
                processing.run("gdal:cliprasterbymasklayer", {
                    'INPUT': current_layer_path,
                    'MASK': clip_mask,
                    'OUTPUT': clipped_path
                })
                current_layer_path = clipped_path
                
            from qgis.core import QgsRasterBandStats
            chk_layer = QgsRasterLayer(current_layer_path, "chk")
            if chk_layer.isValid():
                stats = chk_layer.dataProvider().bandStatistics(1, QgsRasterBandStats.Stats.All)
                has_data = True
                if stats.elementCount == 0:
                    has_data = False
                elif stats.maximumValue <= 0:
                    has_data = False
                elif stats.minimumValue == 255 and stats.maximumValue == 255:
                    has_data = False
                elif stats.minimumValue == -9999 and stats.maximumValue == -9999:
                    has_data = False
                    
                if not has_data:
                    self.log(f"{tr('No data found for')} {disaster_type}.")
                    return "NO_DATA"
                    
            if do_classify:
                self.log(tr("Classifying raster..."))
                self.set_progress(progress_base + 50 * progress_scale / 80)
                classified_path = os.path.join(out_dir, f"temp_classified_{disaster_type}.tif")
                table = [0, 0.333, 1, 0.333, 0.667, 2, 0.667, 1.0, 3]
                processing.run("native:reclassifybytable", {
                    'INPUT_RASTER': current_layer_path,
                    'RASTER_BAND': 1,
                    'TABLE': table,
                    'NO_DATA': -9999,
                    'RANGE_BOUNDARIES': 0,
                    'NODATA_FOR_MISSING': True,
                    'DATA_TYPE': 5,
                    'OUTPUT': classified_path
                })
                current_layer_path = classified_path

            idx_eng = {'Bahaya': 'Hazard', 'Kerentanan': 'Vulnerability', 'Risiko': 'Risk'}.get(index_type, index_type)
            dis_eng = {'Banjir': 'Flood', 'Banjir Bandang': 'Flash Flood', 'Cuaca Ekstrim': 'Extreme Weather',
                       'Gelombang Ekstrim dan Abrasi': 'Extreme Wave and Abrasion', 'Gempa Bumi': 'Earthquake',
                       'Gunung Api': 'Volcano', 'Kekeringan': 'Drought', 'Likuefaksi': 'Liquefaction',
                       'Karhutla': 'Forest and Land Fire', 'Tanah Longsor': 'Landslide', 'Tsunami': 'Tsunami',
                       'Multi': 'Multi'}.get(disaster_type, disaster_type)
                       
            clean_disaster = tr(dis_eng).upper().replace(" ", "_")
            if self.is_spatial_planning:
                prefix = f"{tr('Disaster Prone Area')} {tr(dis_eng)}"
                prefix_layer = f"KRB_{clean_disaster}"
            else:
                prefix = f"{tr(idx_eng + ' Index')} {tr(dis_eng)}"
                prefix_layer = f"{tr(idx_eng + ' Index').upper().replace(' ', '_')}_{clean_disaster}"
            
            if do_vector:
                out_name = f"{prefix_layer}_AR{out_format}"
                layer_name = f"{prefix_layer}_AR"
            else:
                out_name = f"{prefix_layer}{out_format}"
                layer_name = f"{prefix_layer}"
                
            final_out_path = os.path.join(out_dir, out_name)
            
            if do_vector:
                self.log(tr("Filtering raster noise (Sieve)..."))
                self.set_progress(progress_base + 35 * progress_scale / 80)
                sieved_path = os.path.join(out_dir, f"temp_sieved_{disaster_type}.tif")
                res_sieve = processing.run("gdal:sieve", {
                    'INPUT': current_layer_path,
                    'THRESHOLD': 8,
                    'EIGHT_CONNECTEDNESS': True,
                    'OUTPUT': sieved_path
                })
                current_layer_path = res_sieve['OUTPUT']

                self.log(tr("Converting to vector format..."))
                self.set_progress(progress_base + 55 * progress_scale / 80)
                
                vector_path = os.path.join(out_dir, f"temp_vectorized_{disaster_type}.gpkg")
                res_poly = processing.run("gdal:polygonize", {
                    'INPUT': current_layer_path,
                    'BAND': 1,
                    'FIELD': 'CLASS',
                    'OUTPUT': vector_path
                })
                current_vector_path = res_poly['OUTPUT']
                

                if aoi_layer:
                    self.log(tr("Clipping vector..."))
                    self.set_progress(progress_base + 75 * progress_scale / 80)
                    cropped_path = os.path.join(out_dir, f"temp_cropped_{disaster_type}.gpkg")
                    res_clip = processing.run("native:clip", {
                        'INPUT': current_vector_path,
                        'OVERLAY': aoi_layer,
                        'OUTPUT': cropped_path
                    })
                    current_vector_path = res_clip['OUTPUT']
                    
                vec_temp = QgsVectorLayer(current_vector_path, "temp_vec", "ogr")
                if not vec_temp.isValid() or vec_temp.featureCount() == 0:
                    self.log(f"{tr('No data found for')} {disaster_type}.")
                    return "NO_DATA"

                self.log(tr("Adding attribute fields..."))
                self.set_progress(progress_base + 78 * progress_scale / 80)
                field_class_name = "Kelas"
                vec_temp.startEditing()
                vec_temp.dataProvider().addAttributes([
                    QgsField(field_class_name, QVariant.String),
                    QgsField("Value", QVariant.String),
                    QgsField("Source", QVariant.String)
                ])
                vec_temp.updateFields()
                
                idx_kelas = vec_temp.fields().indexOf(field_class_name)
                idx_val = vec_temp.fields().indexOf("Value")
                idx_src = vec_temp.fields().indexOf("Source")
                idx_class = vec_temp.fields().indexOf("CLASS")
                
                labels = {
                    1: f"{prefix} {tr('Low')}",
                    2: f"{prefix} {tr('Medium')}",
                    3: f"{prefix} {tr('High')}"
                }
                
                for feat in vec_temp.getFeatures():
                    cls_val = feat.attribute(idx_class)
                    if do_classify and cls_val in labels:
                        feat.setAttribute(idx_kelas, labels[cls_val])
                    else:
                        feat.setAttribute(idx_kelas, str(cls_val) if cls_val is not None else "")
                    
                    if do_classify:
                        if cls_val == 1:
                            feat.setAttribute(idx_val, "0 - 0.333")
                        elif cls_val == 2:
                            feat.setAttribute(idx_val, "0.333 - 0.667")
                        elif cls_val == 3:
                            feat.setAttribute(idx_val, "0.667 - 1.0")
                    else:
                        feat.setAttribute(idx_val, str(cls_val) if cls_val is not None else "")
                    
                    if year:
                        source_str = tr("InaRISK, National Disaster Management Authority (BNPB), Access Year {year}").format(year=year)
                    else:
                        source_str = tr("InaRISK, National Disaster Management Authority (BNPB)")
                    feat.setAttribute(idx_src, source_str)
                    vec_temp.updateFeature(feat)
                
                vec_temp.commitChanges()
                del vec_temp
                    
                if is_temp:
                    temp_layer = QgsVectorLayer(current_vector_path, "temp", "ogr")
                    geom_name = "MultiPolygon"
                    layer = QgsVectorLayer(f"{geom_name}?crs={temp_layer.crs().authid()}", layer_name, "memory")
                    layer.dataProvider().addAttributes(temp_layer.fields())
                    layer.updateFields()
                    
                    features = []
                    for f in temp_layer.getFeatures():
                        new_f = QgsFeature(layer.fields())
                        new_f.setGeometry(f.geometry())
                        new_f.setAttributes(f.attributes())
                        features.append(new_f)
                    layer.dataProvider().addFeatures(features)
                else:
                    res_final = processing.run("native:savefeatures", {
                        'INPUT': current_vector_path,
                        'OUTPUT': final_out_path
                    })
                    layer = QgsVectorLayer(res_final['OUTPUT'], layer_name, "ogr")
                
                if not layer.isValid():
                    self.log(f"{tr('Failed to load output layer:')} {final_out_path}")
                    return "ERROR"
                
                if do_classify and do_symbolize:
                    from qgis.core import QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsSymbol
                    from qgis.PyQt.QtGui import QColor
                    categories = []
                    colors = {1: QColor("green"), 2: QColor("yellow"), 3: QColor("red")}
                    no_pen = getattr(Qt.PenStyle, 'NoPen', getattr(Qt, 'NoPen', None))
                    for val in [1, 2, 3]:
                        lbl = labels[val]
                        symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                        symbol.setColor(colors[val])
                        symbol.setOpacity(0.7)
                        if symbol.symbolLayerCount() > 0:
                            sym_layer = symbol.symbolLayer(0)
                            if hasattr(sym_layer, 'setStrokeStyle') and no_pen is not None:
                                sym_layer.setStrokeStyle(no_pen)
                            if hasattr(sym_layer, 'setStrokeColor'):
                                sym_layer.setStrokeColor(QColor(0, 0, 0, 0))
                        category = QgsRendererCategory(lbl, symbol, lbl)
                        categories.append(category)
                    renderer = QgsCategorizedSymbolRenderer(field_class_name, categories)
                    layer.setRenderer(renderer)
                    layer.triggerRepaint()
                    
                QgsProject.instance().addMapLayer(layer)
                
            else:
                self.log(tr("Saving raster output..."))
                self.set_progress(progress_base + 78 * progress_scale / 80)
                import shutil
                shutil.copy(current_layer_path, final_out_path)
                layer = QgsRasterLayer(final_out_path, layer_name)
                
                if do_classify and do_symbolize:
                    from qgis.core import QgsPalettedRasterRenderer, QgsColorRampShader
                    from qgis.PyQt.QtGui import QColor
                    classes = [
                        QgsPalettedRasterRenderer.Class(1, QColor("green"), f"{prefix} {tr('Low')}"),
                        QgsPalettedRasterRenderer.Class(2, QColor("yellow"), f"{prefix} {tr('Medium')}"),
                        QgsPalettedRasterRenderer.Class(3, QColor("red"), f"{prefix} {tr('High')}"),
                    ]
                    renderer = QgsPalettedRasterRenderer(layer.dataProvider(), 1, classes)
                    layer.setRenderer(renderer)
                    layer.triggerRepaint()
                    
                QgsProject.instance().addMapLayer(layer)
            
            return "SUCCESS"
        except Exception as e:
            error_str = str(e)
            self.log(f"{tr('Error processing')} {disaster_type}: {error_str}")
            self.iface.messageBar().pushMessage(tr("Error"), f"{tr('Failed')} {disaster_type}: {error_str}", level=Qgis.MessageLevel.Warning, duration=5)
            if "HTTP Error" in error_str or "URLError" in error_str or "Timeout" in error_str or "Connection" in error_str or "WinError" in error_str:
                return "SERVER_ERROR"
            return "ERROR"
