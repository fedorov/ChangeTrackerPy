from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

class ChangeTrackerSegmentROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '3. Segment the analyzed structure' )
    self.setDescription( 'Segment the structure in the selected ROI.' )

    self.__parent = super( ChangeTrackerSegmentROIStep, self )

  def createUserInterface( self ):
    '''
    '''
#    self.buttonBoxHints = self.ButtonBoxHidden

    self.__layout = self.__parent.createUserInterface()

    roiLabel = qt.QLabel( 'Select segmentation:' )
    self.__roiSelector = slicer.qMRMLNodeComboBox()
#    self.__roiSelector.setNodeTyes('vtkMRMLROIAnnotationNode')
    self.__roiSelector.toolTip = "Choose the ROI segmentation"

    self.__layout.addRow( roiLabel, self.__roiSelector )

  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
    # check here that ROI is not empty and is within the baseline volume
    self.__parent.validationSucceeded(desiredBranchId)

  def onEntry(self, comingFrom, transitionType):
    '''
    Resample the baseline volume using ROI
    '''
    pNode = self.parameterNode()
    baselineVolumeID = pNode.GetParameter('baselineVolumeID')
    baselineVolume = slicer.mrmlScene.GetNodeByID(baselineVolumeID)

    outputVolume = slicer.modules.volumes.logic().CloneVolume(slicer.mrmlScene, baselineVolume, 'baselineROI')
    cropVolumeNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLCropVolumeParametersNode')
    cropVolumeNode.SetScene(slicer.mrmlScene)
    cropVolumeNode.SetName('ChangeTracker_CropVolume_node')
    slicer.mrmlScene.AddNode(cropVolumeNode)

    cropVolumeNode.SetAndObserveInputVolumeNodeID(pNode.GetParameter('baselineVolumeID'))
    cropVolumeNode.SetAndObserveROINodeID(pNode.GetParameter('roiID'))
    # cropVolumeNode.SetAndObserveOutputVolumeNodeID(outputVolume.GetID())

    cropVolumeLogic = slicer.modules.cropvolume.logic()
    cropVolumeLogic.Apply(cropVolumeNode)

    # TODO: initialize volume selectors, fit ROI to slice viewers, create
    # label volume, initialize the threshold, initialize volume rendering ?

    super(ChangeTrackerSegmentROIStep, self).onEntry(comingFrom, transitionType)
