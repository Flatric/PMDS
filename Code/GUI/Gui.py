# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 12:38:33 2022

@author: Cedric Jung, Mike Sickmüller, Christian Singer.
"""
# Relevant imports to make the GUI work.
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import seaborn as sns
import matplotlib.pyplot as plt
# Figure Canvas makes matplotlib plots renderable in Qt.
from matplotlib.backends.backend_qt5agg import FigureCanvas
# Import data and functions for analyzing death causes in Germany.
from Analytics import causes_of_death, total_deaths 

class MyGUI(QMainWindow):
    
    def __init__(self):
        super(MyGUI, self).__init__()
        # Gui appearance has been designed outside of python.
        uic.loadUi("GUI\plot_deaths.ui", self)
        
        # Buttons for plotting and saving graphs.
        self.plotGraph.clicked.connect(self.plot_graph)
        self.saveGraph.clicked.connect(self.save_graph)
        # Enable selection of multiple items for plotting.
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # Add names of death causes as items to selection menu.
        self.listWidget.addItems(causes_of_death) 
        # How to react to selecting and double clicking items.
        self.listWidget.itemSelectionChanged.connect(self.selection)
        self.listWidget.itemDoubleClicked.connect(self.double_clicked)
        
        self.checkStandardize.stateChanged.connect(self.selection)
        
        # Make sure that an item is selected before .plot_graph() can be executed.
        self.item_selected = False
        self.standardize=None
        self.setWindowTitle("POMEDOS")
        self.setWindowIcon(QIcon('GUI\icon.png'))
        self.show()
        
    def plot_graph(self):
        # Initiate object that will contain the plot.
        scene = QGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        # Check whether user has selected any item before plotting.
        if self.item_selected:
            # Make figure carrying the plot
            fig, ax = plt.subplots(dpi=100)
            fig.set_size_inches(7.25, 5)
            self.figure = fig
            # Create plot.
            sns.set_style("darkgrid")
            self.deaths = total_deaths(1998, 2020, self.causes, self.standardize)
            sns.lineplot(data=self.deaths, x="year", y="deaths",
                 marker="o", color="#03499a", label=self.label).set_title('Annual Standardized Deaths in Germany 1998-2020')
            sns.despine()
            # Show plot in GUI.
            canvas = FigureCanvas(self.figure)
            scene = QGraphicsScene()
            scene.addWidget(canvas)
            self.graphicsView.setScene(scene)
        else:
            pass
        
    def save_graph(self):
        if self.deaths == None:
            pass
        suffix = ""
        if self.standardize:
            suffix = "standardize"
        self.figure.savefig(f"images\{self.label} {suffix}.png")
        
    def selection(self):
        self.item_selected = True
        # transform selected items into input for data query.
        self.causes = self.listWidget.selectedItems()
        self.causes = [item.text() for item in self.causes]
        # If only one item has been choosen display its name as legend in the plot.
        if len(self.causes) == 1:
            self.label = self.causes[0]
        else:
            self.label = None
        # Check whether deaths should be standardized.
        if self.checkStandardize.isChecked():
            self.standardize = True
        else:
            self.standardize = False
        
    def double_clicked(self,item):
        # Double click displays full name of death cause in separate window.
        QMessageBox.information(self, "Info", item.text())

        
def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()
        
if __name__ == "__main__":
    main()
