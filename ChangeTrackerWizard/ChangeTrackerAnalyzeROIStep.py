from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

class ChangeTrackerAnalyzeROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '4. ROI Analysis' )
    self.setDescription( 'Select the analysis method for the selected ROI.' )

    self.__parent = super( ChangeTrackerAnalyzeROIStep, self )

    self.__followupTransform = None

  def createUserInterface( self ):
    '''
    '''
#    self.buttonBoxHints = self.ButtonBoxHidden

    self.__layout = self.__parent.createUserInterface()

    # add registration button
    self.__registrationButton = qt.QPushButton('Run registration')
    self.__registrationStatus = qt.QLabel('Register scans')

    # add radio box group
    self.__roiDeformableMetricCheck = qt.QCheckBox()
    self.__roiSurfaceMetricCheck = qt.QCheckBox()
    self.__roiIntensityMetricCheck = qt.QCheckBox()

    label1 = qt.QLabel( 'Deformable metric' )
    label2 = qt.QLabel( 'Intensity metric' )
    label3 = qt.QLabel( 'Surface metric' )

    self.__layout.addRow(self.__registrationStatus, self.__registrationButton)
    self.__layout.addRow( label1, self.__roiDeformableMetricCheck )
    self.__layout.addRow( label2, self.__roiIntensityMetricCheck )
    self.__layout.addRow( label3, self.__roiSurfaceMetricCheck )

    self.__registrationButton.connect('clicked()', self.onRegistrationRequest)

  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
    # check here that ROI is not empty and is within the baseline volume
    self.__parent.validationSucceeded(desiredBranchId)

  # def onEntry(self, comingFrom, transitionType):

  def onRegistrationRequest(self):

    # rigidly register followup to baseline
    # TODO: do this in a separate step and allow manual adjustment?
    # TODO: add progress reporting (BRAINSfit does not report progress though)
    pNode = self.parameterNode()
    baselineVolumeID = pNode.GetParameter('baselineVolumeID')
    followupVolumeID = pNode.GetParameter('followupVolumeID')
    self.__followupTransform = slicer.mrmlScene.CreateNodeByClass('vtkMRMLLinearTransformNode')
    slicer.mrmlScene.AddNode(self.__followupTransform)

    parameters = {}
    parameters["fixedVolume"] = baselineVolumeID
    parameters["movingVolume"] = followupVolumeID
    parameters["initializeTransformMode"] = "useMomentsAlign"
    parameters["useRigid"] = True
    parameters["useScaleVersor3D"] = True
    parameters["useScaleSkewVersor3D"] = True
    parameters["useAffine"] = True
    parameters["linearTransform"] = self.__followupTransform.GetID()

    self.__cliNode = None
    self.__cliNode = slicer.cli.run(slicer.modules.brainsfit, self.__cliNode, parameters)

    self.__cliObserverTag = self.__cliNode.AddObserver('ModifiedEvent', self.processRegistrationCompletion)
    self.__registrationStatus.setText('Wait ...')
    self.__registrationButton.setEnabled(0)


  def processRegistrationCompletion(self, node, event):
    status = node.GetStatusString()
    self.__registrationStatus.setText('Registration '+status)
    if status == 'Completed':
      self.__registrationButton.setEnabled(1)
  
      pNode = self.parameterNode()
      followupNode = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('followupVolumeID'))
      followupNode.SetAndObserveTransformNodeID(self.__followupTransform.GetID())
      
      Helper.SetBgFgVolumes(pNode.GetParameter('baselineVolumeID'),pNode.GetParameter('followupVolumeID'))

      pNode.SetParameter('followupTransformID', self.__followupTransform.GetID())
