#!/usr/bin/env python
 
import sys
import pickle # we use pickle to save run information, etc.
import vtk
from PyQt4 import QtCore, QtGui
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
 
class MainWindow(QtGui.QMainWindow):
 
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)

        self.state = {"test", "stuff", "other"}
         
        self.frame = QtGui.QFrame()
        self.resize(1000,600)
        self.setWindowTitle('ProteusCFD')
        self.move(100,100)

        self.vl = QtGui.QGridLayout()
        self.vl.setSpacing(10)

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        #create tabs dialog and add it to the layout
        self.tabs = QtGui.QTabWidget()
        self.vl.addWidget(self.tabs,0,0)

        #Setup our tree view
        self.treeWidget = QtGui.QTreeWidget()
        self.treeWidget.setHeaderHidden(True)
        self.addItems(self.treeWidget.invisibleRootItem())
        self.treeWidget.itemChanged.connect (self.handleChanged)
        self.tabs.addTab(self.treeWidget, "Physics Options")

        #setup solution control tab
        SolutionControlTab = QtGui.QWidget()
        self.tabs.addTab(SolutionControlTab, "Solution Control")

        #setup boundary condition tab
        BCTab = QtGui.QWidget()
        self.tabs.addTab(BCTab, "Boundary Conditions")
        addBCButton = QtGui.QPushButton('Add Boundary Condition', BCTab)
        addBCButton.clicked.connect(self.BoundaryConditionPopup)
        addBCButton.setToolTip('Add a new boundary condition')
        addBCButton.resize(addBCButton.sizeHint())
        addBCButton.move(10, 10)     
        self.bcwindow = None
        
        #draw the tabs
        self.tabs.show()
        
        #Setup our menu and actions
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        saveAction = QtGui.QAction('Save', self)
        saveAction.setShortcut('Ctril+S')
        saveAction.setStatusTip('Save config')
        saveAction.triggered.connect(self.save)

        loadAction = QtGui.QAction('Load', self)
        loadAction.setStatusTip('Load config')
        loadAction.triggered.connect(self.load)
        
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(loadAction)
        
        self.statusBar().showMessage('Waiting...')
        
        #Setup our vtk widget
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget, 0, 300)

        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(.5,.8,.5)       
        self.ren.ResetCamera()

        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        #create the points
        P0 = [0.0, 0.0, 0.0] 
        P1 = [1.0, 0.0, 0.0]
        P2 = [1.0, 1.0, 0.0]
        P3 = [0.0, 1.0, 0.0]
        P4 = [0.0, 0.0, 1.0]
        P5 = [1.0, 0.0, 1.0]
        P6 = [1.0, 1.0, 1.0]
        P7 = [0.0, 1.0, 1.0]

        # Create the points
        points = vtk.vtkPoints()
        points.InsertNextPoint(P0)
        points.InsertNextPoint(P1)
        points.InsertNextPoint(P2)
        points.InsertNextPoint(P3)
        points.InsertNextPoint(P4)
        points.InsertNextPoint(P5)
        points.InsertNextPoint(P6)
        points.InsertNextPoint(P7)
        
        #create a hex
        hex = vtk.vtkHexahedron()
        hex.GetPointIds().SetId(0,0)
        hex.GetPointIds().SetId(1,1)
        hex.GetPointIds().SetId(2,2)
        hex.GetPointIds().SetId(3,3)
        hex.GetPointIds().SetId(4,4)
        hex.GetPointIds().SetId(5,5)
        hex.GetPointIds().SetId(6,6)
        hex.GetPointIds().SetId(7,7)
        
        #create the cells and insert them
        cells = vtk.vtkCellArray()
        cells.InsertNextCell(hex)

        #add the points and cells to unstructured grid
        grid = vtk.vtkUnstructuredGrid()
        grid.SetPoints(points)
        grid.InsertNextCell(hex.GetCellType(), hex.GetPointIds())

        #visualize the grid
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInput(grid)

        self.vtkActorList = []
        
        # Create an actor
        self.vtkActorList.append(vtk.vtkActor())
        self.vtkActorList[0].SetMapper(mapper)

        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(10, 0, 0)
        source.SetRadius(5.0)
 
        # Create a mapper
        mapper2 = vtk.vtkPolyDataMapper()
        mapper2.SetInputConnection(source.GetOutputPort())
 
        # Create an actor
        self.vtkActorList.append(vtk.vtkActor())
        self.vtkActorList[1].SetMapper(mapper2)

        for actor in self.vtkActorList:
            self.ren.AddActor(actor)

        self.show()
        self.iren.Initialize()

    def addItems(self, parent):
        column = 0
        clients_item = self.addParent(parent, column, 'Clients', 'data Clients')
        vendors_item = self.addParent(parent, column, 'Vendors', 'data Vendors')
        time_period_item = self.addParent(parent, column, 'Time Period', 'data Time Period')

        self.addChild(clients_item, column, 'Type A', 'data Type A')
        self.addChild(clients_item, column, 'Type B', 'data Type B')

        self.addChild(vendors_item, column, 'Mary', 'data Mary')
        self.addChild(vendors_item, column, 'Arnold', 'data Arnold')

        self.addChild(time_period_item, column, 'Init', 'data Init')
        self.addChild(time_period_item, column, 'End', 'data End')

    def addParent(self, parent, column, title, data):
        item = QtGui.QTreeWidgetItem(parent, [title])
        item.setData(column, QtCore.Qt.UserRole, data)
        item.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
        item.setExpanded (True)
        return item

    def addChild(self, parent, column, title, data):
        item = QtGui.QTreeWidgetItem(parent, [title])
        item.setData(column, QtCore.Qt.UserRole, data)
        item.setCheckState (column, QtCore.Qt.Unchecked)
        return item

    def handleChanged(self, item, column):
        if item.checkState(column) == QtCore.Qt.Checked:
            print "checked", item, item.text(column)
            self.vtkActorList[0].VisibilityOn()
        if item.checkState(column) == QtCore.Qt.Unchecked:
            print "unchecked", item, item.text(column)
            self.vtkActorList[0].VisibilityOff()

    def save(self):
        filename = "proteusCFD.state"
        pickle.dump(self.state, open(filename, "wb"))
        
    def load(self):
        filename = "proteusCFD.state"
        self.state = pickle.load(open(filename, "rb"))
        print self.state

    def BoundaryConditionPopup(self):
        print "Opening a new BC popup window..."
        self.bcwindow = BCPopup()
        self.bcwindow.setGeometry(QtCore.QRect(100, 100, 400, 200))
        self.bcwindow.show()

class BCPopup(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.bcList = QtGui.QComboBox(self)
        self.bcList.addItems('one two three four'.split())
        self.bcList.move(10,10)
        #call method upon activation
        self.bcList.activated[str].connect(self.bcListActivate)

    def bcListActivate(self, text):
        print 'Combo selection changed to ' + text
        
        
if __name__ == "__main__":
 
    app = QtGui.QApplication(sys.argv)
 
    window = MainWindow()
 
    sys.exit(app.exec_())
