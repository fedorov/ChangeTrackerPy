from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

class ChangeTrackerSelectScansStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '1. Select input scans' )
    self.setDescription( 'Select the baseline and follow-up scans to be compared.' )

    self.__parent = super( ChangeTrackerSelectScansStep, self )

  def createUserInterface( self ):
    '''
    '''
    # TODO: might make sense to hide the button for the last step at this
    # point, but the widget does not have such option
    self.__layout = self.__parent.createUserInterface()
   
    baselineScanLabel = qt.QLabel( 'Select baseline scan:' )
    self.__baselineVolumeSelector = slicer.qMRMLNodeComboBox()
    self.__baselineVolumeSelector.toolTip = "Choose the baseline scan"
    self.__baselineVolumeSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
    self.__baselineVolumeSelector.setMRMLScene(slicer.mrmlScene)
    self.__baselineVolumeSelector.addEnabled = 0

    followupScanLabel = qt.QLabel( 'Select followup scan:' )
    self.__followupVolumeSelector = slicer.qMRMLNodeComboBox()
    self.__followupVolumeSelector.toolTip = "Choose the followup scan"
    self.__followupVolumeSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
    self.__followupVolumeSelector.setMRMLScene(slicer.mrmlScene)
    self.__followupVolumeSelector.addEnabled = 0
   
    self.__layout.addRow( baselineScanLabel, self.__baselineVolumeSelector )
    self.__layout.addRow( followupScanLabel, self.__followupVolumeSelector )

  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
    # check here that the selectors are not empty

    baseline = self.__baselineVolumeSelector.currentNode()
    followup = self.__followupVolumeSelector.currentNode()

    if baseline != 'NoneType' and followup != 'NoneType':
      baselineID = baseline.GetID()
      followupID = followup.GetID()
      if baselineID != '' and followupID != '' and baselineID != followupID:
        lm = slicer.app.layoutManager()
        lm.setLayout(3)
        # TODO: initialize Bg/Fg, fit volumes to slice viewer
        self.__parent.validationSucceeded(desiredBranchId)
      else:
        self.__parent.validationFailed(desiredBranchId, 'Error','Please select distinctive baseline and followup volumes!')
    else:
      self.__parent.validationFailed(desiredBranchId, 'Error','Please select both baseline and followup volumes!')
