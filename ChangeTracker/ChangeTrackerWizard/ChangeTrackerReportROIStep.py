from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

import string

class ChangeTrackerReportROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '5. ROI Analysis Results' )
    self.setDescription( '' )

    self.__vrDisplayNode = None
    self.__vrOpacityMap = None
    self.__vrLogic = slicer.modules.volumerendering.logic()

    self.__xnode = None

    self.__parent = super( ChangeTrackerReportROIStep, self )
    qt.QTimer.singleShot(0, self.killButton)

  def killButton(self):
    # hide useless button
    bl = slicer.util.findChildren(text='ReportROI')
    if len(bl):
      bl[0].hide()


  def createUserInterface( self ):
    '''
    '''
#    self.buttonBoxHints = self.ButtonBoxHidden

    print 'Creating user interface for last step!'
    self.__layout = self.__parent.createUserInterface()

    self.__metricsTabs = qt.QTabWidget()
    self.__layout.addRow(self.__metricsTabs)
    
  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
    # check here that ROI is not empty and is within the baseline volume
    self.__parent.validationSucceeded(desiredBranchId)

  def fitSlices(self):
    slicer.modules.volumes.logic().GetApplicationLogic().FitSliceToAll()

  def onEntry(self, comingFrom, transitionType):
    Helper.Info('Report step: entering onEntry()')
    super(ChangeTrackerReportROIStep, self).onEntry(comingFrom, transitionType)

    pNode = self.parameterNode()
    Helper.Info('Report step: onEntry')
    # create the tabs
    self.__metricsTabs.clear()
    metrics = pNode.GetParameter('metrics')
    self.__metricTabsList = {}
    self.__metricsVolumes = {}

    print 'Metrics list: ', metrics
    metricsReports = string.split(pNode.GetParameter('resultReports'),',')
    metricsVolumesIDs = string.split(pNode.GetParameter('resultVolumes'),',')

    i = 0

    metricsList = string.split(metrics,',')

    if len(metricsVolumesIDs) != len(metricsList):
      Helper.Error('Missing metric processing results!')

    for m in metricsList:
      metricWidget = qt.QWidget()
      metricLayout = qt.QFormLayout(metricWidget)
      textWidget = qt.QTextEdit()
      textWidget.setReadOnly(1)

      self.__metricsVolumes[m] = metricsVolumesIDs[i]
      currentVolume = Helper.getNodeByID(metricsVolumesIDs[i])

      textWidget.setText(currentVolume.GetDescription())
      metricLayout.addRow(textWidget)
      self.__metricsTabs.addTab(metricWidget, m)
      self.__metricTabsList[m] = textWidget
      i = i+1

    self.__metricsTabs.connect("currentChanged(int)", self.onTabChanged)

    # change the layout to Compare
    lm = slicer.app.layoutManager()
    lm.setLayout(12)
    lm.setLayoutNumberOfCompareViewRows(2)

    pNode = self.parameterNode()

    # use GetLayoutName() to identify the corresponding slice node and slice
    # composite node

    # find the compare nodes and initialize them as we wish
    sliceNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLSliceNode')
    sliceNodes.SetReferenceCount(sliceNodes.GetReferenceCount()-1)
    sliceCompositeNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLSliceCompositeNode')
    sliceCompositeNodes.SetReferenceCount(sliceCompositeNodes.GetReferenceCount()-1)

    # setup slice nodes
    for s in range(0,sliceNodes.GetNumberOfItems()):
      sNode = sliceNodes.GetItemAsObject(s)
      thisLayoutName = sNode.GetLayoutName()
      # TODO: check they should have the same layout name!
      if thisLayoutName.find('Compare') == 0:
        sNode.SetLayoutGrid(1,6)

    # setup slice composite nodes
    for s in range(0,sliceCompositeNodes.GetNumberOfItems()):
      scNode = sliceCompositeNodes.GetItemAsObject(s)
      thisLayoutName = scNode.GetLayoutName()
      if thisLayoutName == 'Compare1':
        scNode.SetBackgroundVolumeID(pNode.GetParameter('croppedBaselineVolumeID'))
        scNode.SetForegroundVolumeID('')
        scNode.SetLabelVolumeID('')
        scNode.SetLinkedControl(1)
      if thisLayoutName == 'Compare2':
        scNode.SetBackgroundVolumeID(pNode.GetParameter('croppedFollowupVolumeID'))
        scNode.SetForegroundVolumeID('')
        scNode.SetLabelVolumeID('')
        scNode.SetLinkedControl(1)

    qt.QTimer.singleShot(0, self.fitSlices)


    # Enable crosshairs
    # Is there only one crosshair node?
    xnodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLCrosshairNode')
    xnodes.SetReferenceCount(xnodes.GetReferenceCount()-1)
    self.__xnode = xnodes.GetItemAsObject(0)
    if self.__xnode != None:
      self.__xnode.SetCrosshairMode(5)
    else:
      print 'Failed to find crosshair node!'


    '''
    setup for volume rendering
    '''
    if self.__vrDisplayNode == None:
      # self.__vrDisplayNode = self.__vrLogic.CreateVolumeRenderingDisplayNode()
      # reuse existing node
      vrDisplayNodeID = pNode.GetParameter('vrDisplayNodeID')
      self.__vrDisplayNode = slicer.mrmlScene.GetNodeByID(vrDisplayNodeID)
      #viewNode = slicer.util.getNode('vtkMRMLViewNode1')
      #self.__vrDisplayNode.SetCurrentVolumeMapper(0)
      #self.__vrDisplayNode.AddViewNodeID(viewNode.GetID())

    '''
    trigger volume rendering and label update
    '''
    self.onTabChanged(0)

    pNode.SetParameter('currentStep', self.stepid)

    Helper.Info('Report step: leaving onEntry()')
    
    qt.QTimer.singleShot(0, self.killButton)

  def onExit(self, goingTo, transitionType):
    '''
    Reset crosshairs and turn off volume rendering
    '''
    if self.__xnode != None:
      self.__xnode.SetCrosshairMode(0)

    if self.__vrDisplayNode != None:
      self.__vrDisplayNode.VisibilityOff()

    super(ChangeTrackerReportROIStep, self).onExit(goingTo, transitionType)


  def onTabChanged(self, index):

    metricName = self.__metricsTabs.tabText(index)
    sliceCompositeNodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLSliceCompositeNode')
    sliceCompositeNodes.SetReferenceCount(sliceCompositeNodes.GetReferenceCount()-1)

    for s in range(0,sliceCompositeNodes.GetNumberOfItems()):
      scNode = sliceCompositeNodes.GetItemAsObject(s)
      thisLayoutName = scNode.GetLayoutName()
      # TODO: check they should have the same layout name!
      if thisLayoutName == 'Compare1':
        scNode.SetLinkedControl(0)
        scNode.SetLabelVolumeID(self.__metricsVolumes[metricName])
        scNode.SetLinkedControl(1)
      if thisLayoutName == 'Compare2':
        scNode.SetLinkedControl(0)
        scNode.SetLabelVolumeID(self.__metricsVolumes[metricName])
        scNode.SetLinkedControl(1)
    
    slicer.modules.volumes.logic().GetApplicationLogic().FitSliceToAll()
    
    self.showChangeMapVolumeRendering(self.__metricsVolumes[metricName])

  def showChangeMapVolumeRendering(self, labelID):
    '''
    volume render change detection results
    '''
    labelVolume = slicer.mrmlScene.GetNodeByID(labelID)

    pNode = self.parameterNode()
    roiNodeID = pNode.GetParameter('roiNodeID')
    Helper.InitVRDisplayNode(self.__vrDisplayNode, labelVolume.GetID(), roiNodeID)

    newROI = self.__vrDisplayNode.GetROINode()
    newROI.SetDisplayVisibility(0)

    vrOpacityMap = self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
    vrColorMap = self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetRGBTransferFunction()
    roiNodeID = self.parameterNode().GetParameter('roiNodeID')
    if roiNodeID != '':
      self.__vrDisplayNode.SetAndObserveROINodeID(roiNodeID)
      self.__vrDisplayNode.SetCroppingEnabled(0);

    # label map rendering looks better with shading
    self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().SetShade(1)

    self.__vrDisplayNode.VisibilityOn()
