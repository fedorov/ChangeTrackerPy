from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

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

    self.__layout = self.__parent.createUserInterface()

    # add radio box group
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
