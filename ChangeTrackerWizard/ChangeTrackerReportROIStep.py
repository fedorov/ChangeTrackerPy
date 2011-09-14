from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

import string

class ChangeTrackerReportROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '5. ROI Analysis Results' )
    self.setDescription( '' )

    self.__parent = super( ChangeTrackerReportROIStep, self )

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
    print 'Total metrics: ',len(metricsList)

    print 'Metrics volumes ids = ', metricsVolumesIDs
    print 'Metrics = ', metricsList

    if len(metricsVolumesIDs) != len(metricsList):
      Helper.Error('Missing metric processing results!')

    for m in metricsList:
      print 'Adding tab for metric ',m
      metricWidget = qt.QWidget()
      metricLayout = qt.QFormLayout(metricWidget)
      textWidget = qt.QTextEdit()
      textWidget.setPlainText(1)
      textWidget.setReadOnly(1)

      self.__metricsVolumes[m] = slicer.mrmlScene.GetNodeByID(metricsVolumesIDs[i])
      reportFileName = metricsReports[i]

      reportText = ''
      with open(reportFileName,'r') as f:
        reportText = f.read()
      f.closed

      textWidget.setText(reportText)
      metricLayout.addRow(textWidget)
      self.__metricsTabs.addTab(metricWidget, m)
      self.__metricTabsList[m] = textWidget
      print 'Finished preparing for ', m
      i = i+1

    self.__metricsTabs.connect("currentChanged(int)", self.onTabChanged)
    print 'Creating user interface for last step -- DONE!'


    # change the layout to Compare
    lm = slicer.app.layoutManager()
    lm.setLayout(12)

    pNode = self.parameterNode()

    # find the compare nodes and initialize them as we wish
    sliceNodesCollection = slicer.mrmlScene.GetNodesByClass('vtkMRMLSliceNode')
    sliceCompositeNodesCollection = slicer.mrmlScene.GetNodesByClass('vtkMRMLSliceCompositeNode')
    for s in range(0,sliceNodesCollection.GetNumberOfItems()):
      sNode = sliceNodesCollection.GetItemAsObject(s)
      thisLayoutName = sNode.GetLayoutName()
      # TODO: check they should have the same layout name!
      if thisLayoutName.find('Compare1') == 0:
        sNode.SetLayoutGrid(1,6)
        scNode = sliceCompositeNodesCollection.GetItemAsObject(s)
        scNode.SetBackgroundVolumeID(pNode.GetParameter('croppedBaselineVolumeID'))
        scNode.SetForegroundVolumeID('')
        scNode.SetLabelVolumeID('')
        scNode.SetLinkedControl(1)

      # TODO: save ROI segmentation in pNode, set here for baseline as
      # outline?
      if thisLayoutName.find('Compare2') == 0:
        sNode.SetLayoutGrid(1,6)
        scNode = sliceCompositeNodesCollection.GetItemAsObject(s)
        scNode.SetBackgroundVolumeID(pNode.GetParameter('croppedFollowupVolumeID'))
        scNode.SetForegroundVolumeID('')
        scNode.SetLabelVolumeID('')
        scNode.SetLinkedControl(1)

    # link views
    for s in range(0,sliceNodesCollection.GetNumberOfItems()):
      sNode = sliceNodesCollection.GetItemAsObject(s)
      thisLayoutName = sNode.GetLayoutName()
      if thisLayoutName.find('Compare') == 0:
        scNode = sliceCompositeNodesCollection.GetItemAsObject(s)
        scNode.SetLinkedControl(1)

      appLogic = slicer.app.mrmlApplicationLogic()
      appLogic.PropagateVolumeSelection()

    Helper.Info('Report step: leaving onEntry()')

  def onTabChanged(self, index):
    print 'Tab changed! Current tab title: ', self.__metricsTabs.tabText(index)

