import os
import zipfile
import processing
from qgis.core import (QgsProject, QgsRasterLayer, QgsVectorLayer, QgsMessageLog, Qgis)
from qgis.PyQt.QtWidgets import QApplication
from qgis.PyQt.QtCore import Qt

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
        'Tanah Longsor': 'INDEKS_BAHAYA_TANAHLONGSOR',
        'Tsunami': 'INDEKS_BAHAYA_TSUNAMI'
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
        'Tanah Longsor': 'INDEKS_KERENTANAN_TANAH_LONGSOR',
        'Tsunami': 'INDEKS_KERENTANAN_TSUNAMI'
    },
    'Risiko': {
        'Tanah Longsor': 'INDEKS_RISIKO_TANAH_LONGSOR'
    }
}

class InaRiskProcessor:
    def __init__(self, dlg, iface):
        self.dlg = dlg
        self.iface = iface
        
    def log(self, message):
        from qgis.PyQt.QtCore import QCoreApplication, QEventLoop
        QgsMessageLog.logMessage(message, 'InaRISK to QGIS', Qgis.Info)
        if hasattr(self.dlg, 'txt_log'):
            self.dlg.txt_log.append(message)
            QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

    def set_progress(self, val):
        from qgis.PyQt.QtCore import QCoreApplication, QEventLoop
        if hasattr(self.dlg, 'progress_bar'):
            self.dlg.progress_bar.setValue(int(val))
            QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        
    def process(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.set_progress(5)
        try:
            # 1. Gather Inputs
            out_dir = self.dlg.txt_out_dir.text()
            out_format = self.dlg.cmb_format.currentText()
            aoi_layer_text = self.dlg.cmb_aoi.currentText()
            
            do_classify = self.dlg.cmb_classify.currentText() == "Classify"
            do_vector = (self.dlg.cmb_out_type.currentText() == "Output as Vector (Polygons)")
            do_simplify = self.dlg.chk_simplify.isChecked()
            
            is_temp = not self.dlg.txt_out_dir.text().strip() or self.dlg.txt_out_dir.text() == "[Create temporary layer]"
            if is_temp:
                import tempfile
                out_dir = tempfile.gettempdir()
            elif not out_dir or not os.path.isdir(out_dir):
                self.iface.messageBar().pushMessage("Error", "Please select a valid output directory.", level=Qgis.Warning, duration=5)
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
                    self.log(f"Reprojecting AOI from {aoi_layer.crs().authid()} to EPSG:4326...")
                    reprojected_path = os.path.join(out_dir, "temp_aoi_4326.gpkg")
                    res = processing.run("native:reprojectlayer", {
                        'INPUT': aoi_layer,
                        'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
                        'OUTPUT': reprojected_path
                    })
                    aoi_layer = QgsVectorLayer(res['OUTPUT'], "AOI_4326", "ogr")

            # 2. Iterate and Process
            if not aoi_layer:
                self.iface.messageBar().pushMessage("Error", "Downloading from server requires an AOI layer to define the extent.", level=Qgis.Warning, duration=5)
                return
                
            index_type = self.dlg.cmb_server_index.currentText()
            if hasattr(self.dlg, 'chk_all_disasters') and self.dlg.chk_all_disasters.isChecked():
                disasters = [self.dlg.cmb_server_disaster.itemText(i) for i in range(self.dlg.cmb_server_disaster.count())]
            else:
                disasters = [self.dlg.cmb_server_disaster.currentText()]
            
            total = len(disasters)
            summary_messages = []
            for i, d in enumerate(disasters):
                self.log(f"--- Processing {d} ({i+1}/{total}) ---")
                status = self._process_single(index_type=index_type, disaster_type=d,
                                               out_dir=out_dir, out_format=out_format, aoi_layer=aoi_layer,
                                               do_classify=do_classify, do_vector=do_vector, do_simplify=do_simplify,
                                               is_temp=is_temp, progress_base=10 + (i/total)*80, progress_scale=80/total)
                
                if status == "SUCCESS":
                    summary_messages.append(f"[{d.upper()}] Data Available, Succesfully Processed.")
                elif status == "NO_DATA":
                    summary_messages.append(f"No [{d.upper()}] Data Available on This Area")
                else:
                    self.log(f"Warning: Processing failed for {d}, continuing to next disaster...")
                    summary_messages.append(f"[{d.upper()}] Data Available, Error on Processing.")
            
            QApplication.restoreOverrideCursor()
            self.set_progress(100)
            self.log(f"Successfully finished processing!")
            
            self.log("\n--- PROCESSING SUMMARY ---")
            for i, msg in enumerate(summary_messages, 1):
                self.log(f"{i}. {msg}")
            self.log("--------------------------\n")
        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.iface.messageBar().pushMessage("Error", str(e), level=Qgis.Critical, duration=10)
        finally:
            QApplication.restoreOverrideCursor()

    def _process_single(self, index_type, disaster_type, out_dir, out_format, aoi_layer, do_classify, do_vector, do_simplify, is_temp, progress_base, progress_scale):
        try:
            layer_name = SERVER_MAPPING.get(index_type, {}).get(disaster_type)
            if not layer_name:
                self.iface.messageBar().pushMessage("Error", f"No layer mapping found for {index_type} {disaster_type}", level=Qgis.Warning, duration=5)
                return "ERROR"
                
            dis_str = disaster_type.upper().replace(" ", "_")
            
            self.log(f"Downloading {layer_name} from BNPB ArcGIS ImageServer...")
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
            with urllib.request.urlopen(req) as response:
                content_type = response.headers.get('Content-Type', '')
                if 'json' in content_type or 'html' in content_type:
                    error_msg = response.read().decode('utf-8', errors='ignore')
                    self.iface.messageBar().pushMessage("Server Error", f"ImageServer failed to provide a valid raster. Check if this specific disaster layer exists.", level=Qgis.Critical, duration=10)
                    return "ERROR"
                    
                with open(input_raster_path, 'wb') as out_file:
                    out_file.write(response.read())

            # 3. Processing
            current_layer_path = input_raster_path
            self.set_progress(progress_base + 30 * progress_scale / 80)
            
            buffered_aoi_path = None
            if do_vector and aoi_layer:
                self.log("Buffering AOI by 0.0005 degrees (~50m)...")
                self.set_progress(progress_base + 35 * progress_scale / 80)
                buffered_aoi_path = os.path.join(out_dir, f"temp_buffered_aoi_{disaster_type}.gpkg")
                processing.run("native:buffer", {
                    'INPUT': aoi_layer,
                    'DISTANCE': 0.0005,
                    'SEGMENTS': 5,
                    'OUTPUT': buffered_aoi_path
                })
            
            if aoi_layer:
                self.log("Clipping raster to AOI...")
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
                stats = chk_layer.dataProvider().bandStatistics(1, QgsRasterBandStats.Max)
                if stats.maximumValue < 0:
                    self.log(f"No Data Found for {disaster_type} in selected area.")
                    return "NO_DATA"
                    
            if do_classify:
                self.log("Classifying raster (0-0.3, 0.3-0.6, 0.6-1.0)...")
                self.set_progress(progress_base + 50 * progress_scale / 80)
                classified_path = os.path.join(out_dir, f"temp_classified_{disaster_type}.tif")
                table = [0, 0.3, 1, 0.3, 0.6, 2, 0.6, 1.0, 3]
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

            clean_disaster = disaster_type.upper().replace(" ", "_")
            clean_index = index_type.upper().replace(" ", "_")
            
            if do_vector:
                out_name = f"INDEKS_{clean_index}_{clean_disaster}_AR{out_format}"
                layer_name = f"INDEKS_{clean_index}_{clean_disaster}_AR"
            else:
                out_name = f"INDEKS_{clean_index}_{clean_disaster}{out_format}"
                layer_name = f"INDEKS_{clean_index}_{clean_disaster}"
                
            final_out_path = os.path.join(out_dir, out_name)

            if do_vector:
                self.log("Converting to Vector...")
                self.set_progress(progress_base + 60 * progress_scale / 80)
                
                vector_path = os.path.join(out_dir, f"temp_vectorized_{disaster_type}.gpkg")
                res_poly = processing.run("gdal:polygonize", {
                    'INPUT': current_layer_path,
                    'BAND': 1,
                    'FIELD': 'CLASS',
                    'OUTPUT': vector_path
                })
                current_vector_path = res_poly['OUTPUT']

                if do_simplify:
                    self.log("Smoothing Polygons...")
                    self.set_progress(progress_base + 70 * progress_scale / 80)
                    smoothed_path = os.path.join(out_dir, f"temp_smoothed_{disaster_type}.gpkg")
                    res_smooth = processing.run("native:smoothgeometry", {
                        'INPUT': current_vector_path,
                        'ITERATIONS': 3,
                        'OFFSET': 0.25,
                        'MAX_ANGLE': 180,
                        'OUTPUT': smoothed_path
                    })
                    current_vector_path = res_smooth['OUTPUT']
                    
                if aoi_layer:
                    self.log("Clipping vector to real AOI...")
                    self.set_progress(progress_base + 75 * progress_scale / 80)
                    cropped_path = os.path.join(out_dir, f"temp_cropped_{disaster_type}.gpkg")
                    res_clip = processing.run("native:clip", {
                        'INPUT': current_vector_path,
                        'OVERLAY': aoi_layer,
                        'OUTPUT': cropped_path
                    })
                    current_vector_path = res_clip['OUTPUT']
                    
                if is_temp:
                    temp_layer = QgsVectorLayer(current_vector_path, "temp", "ogr")
                    geom_name = "MultiPolygon"
                    layer = QgsVectorLayer(f"{geom_name}?crs={temp_layer.crs().authid()}", layer_name, "memory")
                    layer.dataProvider().addAttributes(temp_layer.fields())
                    layer.updateFields()
                    
                    from qgis.core import QgsFeature
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
                
                self.log("Adding fields (Kelas, Value, Source)...")
                self.set_progress(progress_base + 78 * progress_scale / 80)
                from qgis.core import QgsField
                from qgis.PyQt.QtCore import QVariant
                layer.startEditing()
                layer.dataProvider().addAttributes([
                    QgsField("Kelas", QVariant.String),
                    QgsField("Value", QVariant.String),
                    QgsField("Source", QVariant.String)
                ])
                layer.updateFields()
                
                idx_kelas = layer.fields().indexOf("Kelas")
                idx_val = layer.fields().indexOf("Value")
                idx_src = layer.fields().indexOf("Source")
                idx_class = layer.fields().indexOf("CLASS")
                
                prefix = f"Indeks {index_type.title()} {disaster_type.title()}"
                
                for feat in layer.getFeatures():
                    cls_val = feat.attribute(idx_class)
                    if cls_val == 1:
                        feat.setAttribute(idx_kelas, f"{prefix} Rendah")
                        feat.setAttribute(idx_val, "0 - 0.3")
                    elif cls_val == 2:
                        feat.setAttribute(idx_kelas, f"{prefix} Sedang")
                        feat.setAttribute(idx_val, "0.3 - 0.6")
                    elif cls_val == 3:
                        feat.setAttribute(idx_kelas, f"{prefix} Tinggi")
                        feat.setAttribute(idx_val, "0.6 - 1.0")
                    
                    feat.setAttribute(idx_src, 'InaRISK, oleh Badan Nasional Penanggulangan Bencana (BNPB)')
                    layer.updateFeature(feat)
                
                layer.commitChanges()
                QgsProject.instance().addMapLayer(layer)
                
            else:
                self.log("Saving final raster...")
                self.set_progress(progress_base + 78 * progress_scale / 80)
                import shutil
                shutil.copy(current_layer_path, final_out_path)
                layer = QgsRasterLayer(final_out_path, layer_name)
                QgsProject.instance().addMapLayer(layer)
            
            return "SUCCESS"
        except Exception as e:
            self.log(f"Error processing {disaster_type}: {str(e)}")
            self.iface.messageBar().pushMessage("Error", f"Failed {disaster_type}: {str(e)}", level=Qgis.Warning, duration=5)
            return "ERROR"
