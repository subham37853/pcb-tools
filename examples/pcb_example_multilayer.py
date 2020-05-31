#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 Hamilton Kibbe <ham@hamiltonkib.be>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
This example demonstrates the use of pcb-tools with cairo to render composite
images using the PCB interface
"""

import os
from gerber import PCB
from gerber.render import theme,RenderSettings
from gerber.render.cairo_backend import GerberCairoContext
from gerber import utils, common,layers,excellon
import re


GERBER_FOLDER = os.path.join(os.path.dirname('/home/shubho/Internship/pcb-tools/intern-test/working'),'not-working')
SAVED_PNG_FOLDER = os.path.join(os.path.dirname('/home/shubho/Internship/pcb-tools/intern-test/working'),'notworking_png')
class CustomLayer(layers.PCBLayer):

    def __init__(self, filename=None, layer_class=None, cam_source=None, **kwargs):
        super(CustomLayer, self).__init__(**kwargs)
        self.filename = filename
        self.layer_class = layer_class
        self.cam_source = cam_source
        self.surface = None
        self.primitives = cam_source.primitives if cam_source is not None else []


    @classmethod
    def custom_fileReader(cls, f):
        ext = os.path.splitext(f)
        if ext[len(ext)-1] in ['.gbr','.xln'] :
            print("Reading File ", f)
            camfile = common.read(os.path.join(GERBER_FOLDER, f))
            if 'copper' in ext[0] and 'top' in ext[0]:
                return cls(f, 'top', camfile)

            elif 'copper' in ext[0] and 'inner' in ext[0]:
                    return CustomInternalLayer.from_cam(camfile)

            elif 'copper' in ext[0] and 'bottom' in ext[0]:
                    return cls(f, 'bottom', camfile)

            elif 'silk' in ext[0] and 'top' in ext[0]:
                return cls(f, 'topsilk', camfile)

            elif 'silk' in ext[0] and 'bottom' in ext[0]:
                    return cls(f, 'bottomsilk', camfile)

            elif 'drill' in ext[0]:
                return CustomDrillLayer.from_cam(camfile)

            elif 'mask' in ext[0] and 'top' in ext[0]:
                return cls(f, 'topmask', camfile)

            elif 'mask' in ext[0] and 'bottom' in ext[0]:
                return cls(f, 'bottommask', camfile)

            elif 'paste' in ext[0] and 'top' in ext[0]:
                return cls(f, 'toppaste', camfile)

            elif 'paste' in ext[0] and 'bottom' in ext[0]:
                return cls(f, 'bottompaste', camfile)

            elif 'profile' in ext[0]:
                return cls(f, 'outline', camfile)


class CustomDrillLayer(CustomLayer):
    @classmethod
    def from_cam(cls, camfile):
        return cls(camfile.filename, camfile)

    def __init__(self, filename=None, cam_source=None, layers=None, **kwargs):
        super(CustomDrillLayer, self).__init__(filename, 'drill', cam_source, **kwargs)
        self.layers = layers if layers is not None else ['top', 'bottom']


class CustomInternalLayer(CustomLayer):

    @classmethod
    def from_cam(cls, camfile):
        filename = camfile.filename
        try:
            order = int(re.search(r'\d+', filename).group())
        except AttributeError:
            order = 0
        return cls(filename, camfile, order)

    def __init__(self, filename=None, cam_source=None, order=0, **kwargs):
        super(CustomInternalLayer, self).__init__(filename, 'internal', cam_source, **kwargs)
        self.order = order

    def __eq__(self, other):
        if not hasattr(other, 'order'):
            raise TypeError()
        return (self.order == other.order)

    def __ne__(self, other):
        if not hasattr(other, 'order'):
            raise TypeError()
        return (self.order != other.order)

    def __gt__(self, other):
        if not hasattr(other, 'order'):
            raise TypeError()
        return (self.order > other.order)

    def __lt__(self, other):
        if not hasattr(other, 'order'):
            raise TypeError()
        return (self.order < other.order)

    def __ge__(self, other):
        if not hasattr(other, 'order'):
            raise TypeError()
        return (self.order >= other.order)

    def __le__(self, other):
        if not hasattr(other, 'order'):
            raise TypeError()
        return (self.order <= other.order)






# Create a new drawing context
ctx = GerberCairoContext()

# Create a new PCB instance
#pcb = PCB.from_directory(GERBER_FOLDER, verbose=True)

files = utils.listdir(GERBER_FOLDER, True, True)
pcb = PCB([])
for f in files:
    customLayer = CustomLayer([])
    layer = customLayer.custom_fileReader(f)
    if layer is not None:
        pcb.layers.append(layer)

print("My PCB Layer", pcb.layers)
print("My PBC Top layers ",pcb.top_layers)
# Render PCB top view
val = os.path.join(os.path.dirname(SAVED_PNG_FOLDER), 'pcb_internTest_top.png',)
ctx.render_layers(pcb.top_layers,
                  val,
                  theme.THEMES['OSH Park'])

# Render PCB bottom view
ctx.render_layers(pcb.bottom_layers,
                  os.path.join(os.path.dirname(SAVED_PNG_FOLDER), 'pcb_internTest_bottom.png'),
                  theme.THEMES['OSH Park'], max_width=800, max_height=600)

# Render copper layers only
ctx.render_layers(pcb.copper_layers + pcb.drill_layers,
                  os.path.join(os.path.dirname(SAVED_PNG_FOLDER),
                               'pcb_internTest_transparent.png'),
                  theme.THEMES['Transparent Copper'], max_width=800, max_height=600)

