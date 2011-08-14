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

    baselineVolumeROI = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('croppedBaselineVolumeID'))
    followupVolume = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('followupVolumeID'))
    followupVolumeROI = slicer.modules.volumes.logic().CloneVolume(slicer.mrmlScene, followupVolume, 'followupROI')

    parameters = {}
    parameters["inputVolume"] = pNode.GetParameter('followupVolumeID')
    parameters["referenceVolume"] = pNode.GetParameter('croppedBaselineVolumeID')
    parameters["outputVolume"] = followupVolumeROI.GetID()
    parameters["transformationFile"] = followupVolume.GetTransformNodeID()
    parameters["interpolationType"] = "bs"

    self.__cliNode = None
    self.__cliNode = slicer.cli.run(slicer.modules.resamplevolume2, self.__cliNode, parameters, 1)

    # TODO: error checking
    pNode.SetParameter('croppedFollowupVolumeID',followupVolumeROI.GetID())

    # cropped volume will inherit the transform node from follow-up volume,
    # unset it
    followupVolumeROI.SetAndObserveTransformNodeID(None)

    Helper.SetBgFgVolumes(pNode.GetParameter('croppedBaselineVolumeID'),pNode.GetParameter('croppedFollowupVolumeID'))
    super(ChangeTrackerAnalyzeROIStep, self).onEntry(comingFrom, transitionType)


