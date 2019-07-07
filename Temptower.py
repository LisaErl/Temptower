
# Copyright (c) 2019 Lisa Erlingheuser
# This Cura PostProcessing-Script is released under the terms of the AGPLv3 or higher.

# This Cura Postprocessing Script changes the printing temperature step by step in a user selectable interval. 
# The user enters the desired temperature intervals and a height interval. 

# Each time a layer is above the specified interval, the temperature is reduced by the specified value.

import re #To perform the search and replace.
import string
import os
import urllib.request

from UM.Logger import Logger
from UM.Message import Message
from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

from ..Script import Script


class Temptower(Script):

    def getSettingDataString(self):
        return """{
            "name": "Temptower",
            "key": "Temptower",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "tempinter":
                {
                    "label": "Temp-Interval",
                    "description": "The Temp-Interval",
                    "type": "int",
                    "default_value": 5
                },
                "heightinter":
                {
                    "label": "Height-Interval",
                    "description": "The Height-Interval",
                    "type": "int",
                    "default_value": 5
                }
            }
        }"""

    def getVar(self):
        self.tempinter = float(self.getSettingValueByKey("tempinter"))
        self.heightinter = float(self.getSettingValueByKey("heightinter")) 
        
    def getLayerHeight(self, lines):
        for line in lines:
            actZ = Script.getValue(self, line = line, key = 'Z')            
            if actZ != None:                
                return float(actZ)
                
    def getFirstTemp(self, data):
        gesdata = '\n'.join(data)
        lines = gesdata.split("\n")
        for line_number, line in enumerate(lines, 1):
            cmdl = line.split(';')[0]
            cmd = cmdl.split(' ')[0]
            if cmd == 'M104':
                sTemp = Script.getValue(self, line = line, key = 'S')
                iTemp = int(sTemp)
                Logger.log('d',  'Temptower --> getFirstTemp sTemp: ' + str(sTemp))
                return iTemp
        
            

    def execute(self, data):
        _msg = ''
        self.getVar()
        lineNo = 0
        layno = 0
        iNextHeight = self.heightinter
        iNextTemp = self.getFirstTemp(data) - self.tempinter
        Logger.log('d',  'Temptower --> execute iNextHeight: ' + str(iNextHeight))
        Logger.log('d',  'Temptower --> execute iNextTemp: ' + str(iNextTemp))
        for layer_number, layer in enumerate(data):            
            lines = layer.split("\n")
            for line_number, line in enumerate(lines):
                lineNo = lineNo +1
                if line != '':
                    if ';LAYER' in line:
                        layno = int(line.split(':')[1])
                        #Logger.log('d',  'Temptower --> execute layno: ' + str(layno))
                        actZ = self.getLayerHeight(lines)
                        if actZ != None and layno > 0:
                            if actZ > iNextHeight:
                                _msg = 'Temperatures set for Temptower'
                                Logger.log('d',  'Temptower --> execute actZ: ' + str(actZ))
                                lines[line_number+1] = 'M104 S' + str(iNextTemp) + '; --> New Temp for Temptower, Target temperature=' + str(iNextTemp) + ' at height > ' + str(iNextHeight) + ' reached with ' + str(actZ) + '\n' + lines[line_number+1]
                                iNextHeight = iNextHeight + self.heightinter
                                iNextTemp = iNextTemp - self.tempinter
                                Logger.log('d',  'Temptower --> execute iNextHeight: ' + str(iNextHeight))
                                Logger.log('d',  'Temptower --> execute iNextTemp: ' + str(iNextTemp))
                        break
            data[layer_number] = '\n'.join(lines)
        if _msg != None and _msg != '':
            Message("Info Temptower:" + "\n" + _msg, title = catalog.i18nc("@info:title", "Post Processing")).show()
        return data