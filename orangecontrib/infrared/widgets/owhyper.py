from itertools import chain
import sys
from collections import defaultdict
import gc
import random
import warnings
import math

from AnyQt.QtWidgets import QWidget, QGraphicsItem, QPushButton, QMenu, \
    QGridLayout, QAction, QVBoxLayout, QApplication, QWidgetAction, QLabel, QGraphicsView, QGraphicsScene
from AnyQt.QtGui import QColor, QPixmapCache, QPen, QKeySequence
from AnyQt.QtCore import Qt, QRectF

import numpy as np
import pyqtgraph as pg
from pyqtgraph.graphicsItems.ViewBox import ViewBox
from pyqtgraph import Point, GraphicsObject

from Orange.canvas.registry.description import Default
import Orange.data
from Orange.widgets.widget import OWWidget, Msg, OWComponent
from Orange.widgets import gui
from Orange.widgets.visualize.owheatmap import GraphicsHeatmapWidget, GraphicsWidget
from Orange.widgets.settings import \
    Setting, ContextSetting, DomainContextHandler, SettingProvider
from Orange.widgets.utils.itemmodels import VariableListModel
from Orange.widgets.utils.colorpalette import ColorPaletteGenerator
from Orange.widgets.utils.plot import \
    SELECT, PANNING, ZOOMING

from orangecontrib.infrared.data import getx
from orangecontrib.infrared.widgets.line_geometry import \
    distance_curves, intersect_curves_chunked
from orangecontrib.infrared.widgets.gui import lineEditFloatOrNone
from orangecontrib.infrared.widgets.owcurves import InteractiveViewBox


class ImagePlot(QWidget, OWComponent):

    def __init__(self, parent):
        QWidget.__init__(self)
        OWComponent.__init__(self, parent)

        self.parent = parent

        self.selection_enabled = False

        self.plotview = pg.PlotWidget(background="w", viewBox=InteractiveViewBox(self))
        self.plot = self.plotview.getPlotItem()

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.plotview)
        self.img = pg.ImageItem()
        self.img.setOpts(axisOrder='row-major')
        self.plot.addItem(self.img)
        self.plot.vb.setAspectLocked()

    def set_data(self, data):
        # temporary implementation that works just with one dataset
        self.img.clear()
        if data is not None:
            #TODO create image coordinates from the domain
            xat = data.domain["x"]
            yat = data.domain["y"]
            ndom = Orange.data.Domain([yat, xat])
            datam = Orange.data.Table(ndom, data)
            coordinates = datam.X
            imdata = np.ones((int(max(coordinates[:, 0]+1)), int(max(coordinates[:, 1]+1))))
            #TODO cumpute integrals for showing
            d = data.X.sum(axis=1)
            #TODO Set data - this has to be fast
            for c,v in zip(coordinates, d):
                imdata[int(c[0]), int(c[1])] = v
            self.img.setImage(imdata)


class OWHyper(OWWidget):
    name = "Hyperspectra"
    inputs = [("Data", Orange.data.Table, 'set_data', Default),
              ("Data subset", Orange.data.Table, 'set_subset', Default)]
    outputs = [("Selection", Orange.data.Table)]
    icon = "icons/curves.svg"

    settingsHandler = DomainContextHandler()

    def __init__(self):
        super().__init__()
        self.controlArea.hide()
        self.imageplot = ImagePlot(self)
        self.mainArea.layout().addWidget(self.imageplot)
        self.resize(900, 700)
        self.graph_name = "imageplot.plotview"

    def set_data(self, data):
        self.closeContext()
        self.imageplot.set_data(data)
        self.openContext(data)

    def set_subset(self, data):
        pass


def main(argv=None):
    if argv is None:
        argv = sys.argv
    argv = list(argv)
    app = QApplication(argv)
    w = OWHyper()
    w.show()
    data = Orange.data.Table("whitelight.gsf")
    w.set_data(data)
    w.handleNewSignals()
    rval = app.exec_()
    w.set_data(None)
    w.handleNewSignals()
    w.deleteLater()
    del w
    app.processEvents()
    gc.collect()
    return rval

if __name__ == "__main__":
    sys.exit(main())
