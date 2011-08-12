from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

class ChangeTrackerAnalyzeROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '5. ROI Analysis' )
    self.setDescription( 'Select the analysis method for the selected ROI.' )

    self.__parent = super( ChangeTrackerAnalyzeROIStep, self )

  def createUserInterface( self ):
    '''
    '''
#    self.buttonBoxHints = self.ButtonBoxHidden

    self.__layout = self.__parent.createUserInterface()

    # add radio box group
    self.__roiDeformableMetricCheck = qt.QCheckBox()
    self.__roiSurfaceMetricCheck = qt.QCheckBox()
    self.__roiIntensityMetricCheck = qt.QCheckBox()

    label1 = qt.QLabel( 'Deformable metric' )
    label2 = qt.QLabel( 'Intensity metric' )
    label3 = qt.QLabel( 'Surface metric' )

    self.__layout.addRow( label1, self.__roiDeformableMetricCheck )
    self.__layout.addRow( label2, self.__roiIntensityMetricCheck )
    self.__layout.addRow( label3, self.__roiSurfaceMetricCheck )

  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
    # check here that ROI is not empty and is within the baseline volume
    self.__parent.validationSucceeded(desiredBranchId)

  def onEntry(self, comingFrom, transitionType):
    # resample the ROI from the follow-up volume, taking into account the
    # transform
    
    pNode = self.parameterNode()
    followupVolumeID = pNode.GetParameter('followupVolumeID')
    followupVolume = slicer.mrmlScene.GetNodeByID(followupVolumeID)

    outputVolume = slicer.modules.volumes.logic().CloneVolume(slicer.mrmlScene, followupVolume, 'followupROI')
    cropVolumeNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLCropVolumeParametersNode')
    cropVolumeNode.SetScene(slicer.mrmlScene)
    cropVolumeNode.SetName('ChangeTracker_CropVolume_node2')
    slicer.mrmlScene.AddNode(cropVolumeNode)

    cropVolumeNode.SetAndObserveInputVolumeNodeID(pNode.GetParameter('followupVolumeID'))
    cropVolumeNode.SetAndObserveROINodeID(pNode.GetParameter('roiID'))
    # cropVolumeNode.SetAndObserveOutputVolumeNodeID(outputVolume.GetID())

    cropVolumeLogic = slicer.modules.cropvolume.logic()
    cropVolumeLogic.Apply(cropVolumeNode)

    # TODO: cropvolume error checking
    pNode.SetParameter('croppedFollowupVolumeID',cropVolumeNode.GetOutputVolumeNodeID())

    # cropped volume will inherit the transform node from follow-up volume,
    # unset it
    cropVolumeNode.SetAndObserveTransformNodeID(None)

    Helper.SetBgFgVolumes(pNode.GetParameter('croppedBaselineVolumeID'),pNode.GetParameter('croppedFollowupVolumeID'))
    super(ChangeTrackerAnalyzeROIStep, self).onEntry(comingFrom, transitionType)


