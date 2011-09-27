from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

'''
TODO:
  add advanced option to specify segmentation
'''

class ChangeTrackerSegmentROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '3. Segment the analyzed structure' )
    self.setDescription( 'Segment the structure in the selected ROI.' )

    self.__parent = super( ChangeTrackerSegmentROIStep, self )
    
    self.__vrDisplayNode = None
    self.__threshold = [ -1, -1 ]
       
    # initialize VR stuff
    self.__vrLogic = slicer.modules.volumerendering.logic()
    self.__vrOpacityMap = None

    self.__roiSegmentationNode = None
    self.__roiVolume = None

  def createUserInterface( self ):
    '''
    '''
    print 'SegmentROI create interface'
#    self.buttonBoxHints = self.ButtonBoxHidden

    self.__layout = self.__parent.createUserInterface()

    threshLabel = qt.QLabel('Choose threshold:')
    self.__threshRange = slicer.qMRMLRangeWidget()
    self.__threshRange.decimals = 0
    self.__threshRange.singleStep = 1

    roiLabel = qt.QLabel( 'Select segmentation:' )
    self.__roiLabelSelector = slicer.qMRMLNodeComboBox()
    self.__roiLabelSelector.nodeTypes = ( 'vtkMRMLScalarVolumeNode', '' )
    self.__roiLabelSelector.addAttribute('vtkMRMLScalarVolumeNode','LabelMap','1')
    self.__roiLabelSelector.toolTip = "Choose the ROI segmentation"
    self.__roiLabelSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
    self.__roiLabelSelector.addEnabled = 0
    self.__roiLabelSelector.setMRMLScene(slicer.mrmlScene)

    self.__layout.addRow(threshLabel, self.__threshRange)
    # self.__layout.addRow( roiLabel, self.__roiLabelSelector )

    self.__threshRange.connect('valuesChanged(double,double)', self.onThresholdChanged)

  def onThresholdChanged(self): 
    
    if self.__vrOpacityMap == None:
      return

    range0 = self.__threshRange.minimumValue
    range1 = self.__threshRange.maximumValue

    self.__vrOpacityMap.RemoveAllPoints()
    self.__vrOpacityMap.AddPoint(0,0)
    self.__vrOpacityMap.AddPoint(0,0)
    self.__vrOpacityMap.AddPoint(range0-1,0)
    self.__vrOpacityMap.AddPoint(range0,1)
    self.__vrOpacityMap.AddPoint(range1,1)
    self.__vrOpacityMap.AddPoint(range1+1,0)

    # update the label volume accordingly
    thresh = vtk.vtkImageThreshold()
    thresh.SetInput(self.__roiVolume.GetImageData())
    thresh.ThresholdBetween(range0, range1)
    thresh.SetInValue(10)
    thresh.SetOutValue(0)
    thresh.ReplaceOutOn()
    thresh.ReplaceInOn()
    thresh.Update()

    self.__roiSegmentationNode.SetAndObserveImageData(thresh.GetOutput())

  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
    self.__parent.validationSucceeded(desiredBranchId)

  def onExit(self, goingTo, transitionType):
    self.__vrDisplayNode.VisibilityOff()

    super(ChangeTrackerSegmentROIStep, self).onExit(goingTo, transitionType)

  def onEntry(self, comingFrom, transitionType):
    '''
    Resample the baseline volume using ROI

    TODO: if coming from the next step, do not resample!

    TODO: this should go to onExit() in the previous step!
    '''
    super(ChangeTrackerSegmentROIStep, self).onEntry(comingFrom, transitionType)

    pNode = self.parameterNode()
    Helper.SetBgFgVolumes(pNode.GetParameter('croppedBaselineVolumeID'),'')

    # initilize threshold selector based on the ROI contents
    roiVolume = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('croppedBaselineVolumeID'))
    roiImage = roiVolume.GetImageData()
    roiImageRange = roiImage.GetScalarRange()
    self.__threshRange.minimum =  roiImageRange[0]
    self.__threshRange.maximum = roiImageRange[1]
    # TODO: initialize volume selectors, fit ROI to slice viewers, create
    # label volume, initialize the threshold, initialize volume rendering ?

    if self.__vrDisplayNode == None:
      self.__vrDisplayNode = self.__vrLogic.CreateVolumeRenderingDisplayNode()
      viewNode = slicer.util.getNode('vtkMRMLViewNode1')
      self.__vrDisplayNode.AddViewNodeID(viewNode.GetID())
      print 'SegmentROI step: create VR node ',self.__vrDisplayNode.GetID()
      self.__vrDisplayNode.SetCurrentVolumeMapper(2)

    self.__vrDisplayNode.SetAndObserveVolumeNodeID(roiVolume.GetID())
    self.__vrLogic.UpdateDisplayNodeFromVolumeNode(self.__vrDisplayNode, roiVolume)
    self.__vrOpacityMap = self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
    vrColorMap = self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetRGBTransferFunction()
    
    # setup color transfer function once
    vrColorMap.RemoveAllPoints()
    vrColorMap.AddRGBPoint(0, 0, 0, 0) 
    vrColorMap.AddRGBPoint(roiImageRange[0]-1, 0, 0, 0) 
    vrColorMap.AddRGBPoint(roiImageRange[0], 0.8, 0.8, 0) 
    vrColorMap.AddRGBPoint(roiImageRange[1], 0.8, 0.8, 0) 
    vrColorMap.AddRGBPoint(roiImageRange[1]+1, 0, 0, 0) 

    self.__vrDisplayNode.VisibilityOn()

    self.__vrOpacityMap.RemoveAllPoints()
    self.__vrOpacityMap.AddPoint(0,0)
    self.__vrOpacityMap.AddPoint(0,0)
    self.__vrOpacityMap.AddPoint(roiImageRange[0]-1,0)
    self.__vrOpacityMap.AddPoint(roiImageRange[0],1)
    self.__vrOpacityMap.AddPoint(roiImageRange[1],1)
    self.__vrOpacityMap.AddPoint(roiImageRange[1]+1,0)

    # create a label volume from the ROI
    if self.__roiSegmentationNode == None:
      vl = slicer.modules.volumes.logic()
      self.__roiSegmentationNode = vl.CreateLabelVolume(slicer.mrmlScene, roiVolume, 'baselineROI_segmentation')

      # initialize the color map the same way as in Slicer3
      # don't know how to get that node by some ID, so I had to experiment to
      # get the right one ...
      labelsColorNode = slicer.modules.colors.logic().GetColorTableNodeID(10)
      self.__roiSegmentationNode.GetDisplayNode().SetAndObserveColorNodeID(labelsColorNode)

      self.parameterNode().SetParameter('croppedBaselineVolumeSegmentationID', self.__roiSegmentationNode.GetID())
   
    Helper.SetLabelVolume(self.__roiSegmentationNode.GetID())

    self.__roiVolume = roiVolume

    self.__threshRange.minimumValue = 0.5*(roiImageRange[0]+roiImageRange[1])
    self.__threshRange.maximumValue = roiImageRange[1]

    self.onThresholdChanged()

