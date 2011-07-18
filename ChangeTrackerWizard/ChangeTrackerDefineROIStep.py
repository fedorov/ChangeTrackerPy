from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

class ChangeTrackerDefineROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '2. Define Region of Interest' )
    self.setDescription( 'Define ROI that covers the object of interest.' )

    self.__parent = super( ChangeTrackerDefineROIStep, self )

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


  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
    roi = self.__roiSelector.currentNode()
    # FIXME: is this a bug that node selector may return either None or
    # NoneType?
    if roi != 'NoneType' and roi != 'None':
      print 'ROI: ',roi
      # print 'ROI ID: ', roi.GetID()
      # TODO: verify that ROI is within the baseline volume?
      self.__parent.validationSucceeded(desiredBranchId)
    else:
      self.__parent.validationFailed(desiredBranchId, 'Error', 'Please define ROI!')
