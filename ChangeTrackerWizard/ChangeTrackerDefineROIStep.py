from __main__ import qt, ctk, slicer

from ChangeTrackerStep import *
from Helper import *

class ChangeTrackerDefineROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '2. Define Region of Interest' )
    self.setDescription( 'Define ROI that covers the object of interest.' )

    self.__parent = super( ChangeTrackerDefineROIStep, self )

    self.__vrDisplayNode = 'None'

  def createUserInterface( self ):
    '''
    '''
    self.__layout = self.__parent.createUserInterface()

    roiLabel = qt.QLabel( 'Select ROI:' )
    self.__roiSelector = slicer.qMRMLNodeComboBox()
    self.__roiSelector.nodeTypes = ['vtkMRMLAnnotationROINode']
    self.__roiSelector.toolTip = "ROI defining the structure of interest"
    self.__roiSelector.setMRMLScene(slicer.mrmlScene)
    self.__roiSelector.addEnabled = 1

    self.__layout.addRow( roiLabel, self.__roiSelector )

    self.__roiSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onROIChanged)

  def onROIChanged(self):
    roi = self.__roiSelector.currentNode()
    # TODO: update ROI in the MRML node, remove observer, add new observer
    # observe modifications of the ROI, change view origin as the ROI is
    # changing
    # In that same handler, call some logic function to recalculate ROI
    # min/max, and update the transfer function accordingly
    if roi != None:
    
      pNode = self.parameterNode()
      # initialize VR stuff
      self.__vrLogic = slicer.modules.volumerendering.logic()
      if self.__vrDisplayNode == 'None':
        print 'DEBUG: ChangeTracker DefineROI step: Creating VR node!'
        self.__vrDisplayNode = self.__vrLogic.CreateVolumeRenderingDisplayNode()
        viewNode = slicer.util.getNode('ViewNode')
        self.__vrDisplayNode.AddViewNodeID(viewNode.GetID())

        v = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('baselineVolumeID'))
        self.__vrLogic.UpdateDisplayNodeFromVolumeNode(self.__vrDisplayNode, v)

      v = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('baselineVolumeID'))
      self.__vrDisplayNode.SetAndObserveROINodeID(roi.GetID())
      self.__vrDisplayNode.SetAndObserveVolumeNodeID(v.GetID())
      self.__vrDisplayNode.SetCroppingEnabled(1)
      self.__vrDisplayNode.VisibilityOn()
     
  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
    roi = self.__roiSelector.currentNode()
    if roi != 'None':
      print 'ROI: ',roi
      pNode = self.parameterNode()
      pNode.SetParameter('roiID',roi.GetID())
      # print 'ROI ID: ', roi.GetID()
      # TODO: verify that ROI is within the baseline volume?
      self.__parent.validationSucceeded(desiredBranchId)
    else:
      self.__parent.validationFailed(desiredBranchId, 'Error', 'Please define ROI!')

  def onEntry(self,comingFrom,transitionType):
    pNode = self.parameterNode()
    Helper.SetBgFgVolumes(pNode.GetParameter('baselineVolumeID'),pNode.GetParameter('followupVolumeID'))

    super(ChangeTrackerDefineROIStep, self).onEntry(comingFrom, transitionType)

  def onExit(self, goingTo, transitionType):
    self.__vrDisplayNode.VisibilityOff()
    super(ChangeTrackerDefineROIStep, self).onExit(goingTo, transitionType)
