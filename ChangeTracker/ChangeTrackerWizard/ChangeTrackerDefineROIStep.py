from __main__ import qt, ctk, slicer

from .ChangeTrackerStep import *
from .Helper import *
import PythonQt

class ChangeTrackerDefineROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '2. Define Region of Interest' )
    self.setDescription( 'Define ROI that covers the object of interest.' )

    self.__parent = super( ChangeTrackerDefineROIStep, self )

    self.__vrDisplayNode = None

    self.__roiTransformNode = None
    self.__baselineVolume = None

    self.__roi = None
    self.__roiObserverTag = None

    qt.QTimer.singleShot(0, self.killButton)

  def killButton(self):
    # hide useless button
    bl = slicer.util.findChildren(text='ReportROI')
    if len(bl):
      bl[0].hide()

  def createUserInterface( self ):
    '''
    '''
    self.__layout = self.__parent.createUserInterface()

    roiLabel = qt.QLabel( 'Select ROI:' )
    self.__roiSelector = slicer.qMRMLNodeComboBox()
    self.__roiSelector.nodeTypes = ['vtkMRMLMarkupsROINode']
    self.__roiSelector.toolTip = "ROI defining the structure of interest"
    self.__roiSelector.setMRMLScene(slicer.mrmlScene)
    self.__roiSelector.addEnabled = 1

    self.__layout.addRow( roiLabel, self.__roiSelector )

    self.__roiSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onROIChanged)

    # the ROI parameters
    voiGroupBox = qt.QGroupBox()
    voiGroupBox.setTitle( 'Define VOI' )
    self.__layout.addRow( voiGroupBox )

    voiGroupBoxLayout = qt.QFormLayout( voiGroupBox )

    self.__roiWidget = slicer.qMRMLMarkupsROIWidget()
    voiGroupBoxLayout.addRow( self.__roiWidget )

    # initialize VR stuff
    self.__vrLogic = slicer.modules.volumerendering.logic()

    # self.updateWidgetFromParameters(self.parameterNode())
    qt.QTimer.singleShot(0, self.killButton)

  def onROIChanged(self):

    roi = self.__roiSelector.currentNode()

    if roi != None:
      self.__roi = roi

      pNode = self.parameterNode()
      # create VR node first time a valid ROI is selected
      self.InitVRDisplayNode()

      # update VR settings each time ROI changes
      v = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('baselineVolumeID'))
      self.__vrDisplayNode.SetAndObserveROINodeID(roi.GetID())
      self.__vrDisplayNode.SetCroppingEnabled(1)
      self.__vrDisplayNode.VisibilityOn()

      roi.SetAndObserveTransformNodeID(self.__roiTransformNode.GetID())

      # TODO: update opacity function based on ROI content
      # self.__vrOpacityMap.RemoveAllPoints()

      if self.__roiObserverTag != None:
        self.__roi.RemoveObserver(self.__roiObserverTag)

      self.__roiObserverTag = self.__roi.AddObserver('ModifiedEvent', self.processROIEvents)

      roi.SetLocked(False)

      self.__roiWidget.setMRMLMarkupsNode(roi)
      self.__roi.GetDisplayNode().SetVisibility(True)

  def processROIEvents(self,node,event):
    # get the range of intensities inside the ROI

    # get the IJK bounding box of the voxels inside ROI
    roiCenter = [0,0,0]
    roiRadius = [0,0,0]
    self.__roi.GetXYZ(roiCenter)
    self.__roi.GetRadiusXYZ(roiRadius)

    roiCorner1 = [roiCenter[0]+roiRadius[0],roiCenter[1]+roiRadius[1],roiCenter[2]+roiRadius[2],1]
    roiCorner2 = [roiCenter[0]+roiRadius[0],roiCenter[1]+roiRadius[1],roiCenter[2]-roiRadius[2],1]
    roiCorner3 = [roiCenter[0]+roiRadius[0],roiCenter[1]-roiRadius[1],roiCenter[2]+roiRadius[2],1]
    roiCorner4 = [roiCenter[0]+roiRadius[0],roiCenter[1]-roiRadius[1],roiCenter[2]-roiRadius[2],1]
    roiCorner5 = [roiCenter[0]-roiRadius[0],roiCenter[1]+roiRadius[1],roiCenter[2]+roiRadius[2],1]
    roiCorner6 = [roiCenter[0]-roiRadius[0],roiCenter[1]+roiRadius[1],roiCenter[2]-roiRadius[2],1]
    roiCorner7 = [roiCenter[0]-roiRadius[0],roiCenter[1]-roiRadius[1],roiCenter[2]+roiRadius[2],1]
    roiCorner8 = [roiCenter[0]-roiRadius[0],roiCenter[1]-roiRadius[1],roiCenter[2]-roiRadius[2],1]

    ras2ijk = vtk.vtkMatrix4x4()
    self.__baselineVolume.GetRASToIJKMatrix(ras2ijk)

    roiCorner1ijk = ras2ijk.MultiplyPoint(roiCorner1)
    roiCorner2ijk = ras2ijk.MultiplyPoint(roiCorner2)
    roiCorner3ijk = ras2ijk.MultiplyPoint(roiCorner3)
    roiCorner4ijk = ras2ijk.MultiplyPoint(roiCorner4)
    roiCorner5ijk = ras2ijk.MultiplyPoint(roiCorner5)
    roiCorner6ijk = ras2ijk.MultiplyPoint(roiCorner6)
    roiCorner7ijk = ras2ijk.MultiplyPoint(roiCorner7)
    roiCorner8ijk = ras2ijk.MultiplyPoint(roiCorner8)

    lowerIJK = [0, 0, 0]
    upperIJK = [0, 0, 0]

    lowerIJK[0] = min(roiCorner1ijk[0],roiCorner2ijk[0],roiCorner3ijk[0],roiCorner4ijk[0],roiCorner5ijk[0],roiCorner6ijk[0],roiCorner7ijk[0],roiCorner8ijk[0])
    lowerIJK[1] = min(roiCorner1ijk[1],roiCorner2ijk[1],roiCorner3ijk[1],roiCorner4ijk[1],roiCorner5ijk[1],roiCorner6ijk[1],roiCorner7ijk[1],roiCorner8ijk[1])
    lowerIJK[2] = min(roiCorner1ijk[2],roiCorner2ijk[2],roiCorner3ijk[2],roiCorner4ijk[2],roiCorner5ijk[2],roiCorner6ijk[2],roiCorner7ijk[2],roiCorner8ijk[2])

    upperIJK[0] = max(roiCorner1ijk[0],roiCorner2ijk[0],roiCorner3ijk[0],roiCorner4ijk[0],roiCorner5ijk[0],roiCorner6ijk[0],roiCorner7ijk[0],roiCorner8ijk[0])
    upperIJK[1] = max(roiCorner1ijk[1],roiCorner2ijk[1],roiCorner3ijk[1],roiCorner4ijk[1],roiCorner5ijk[1],roiCorner6ijk[1],roiCorner7ijk[1],roiCorner8ijk[1])
    upperIJK[2] = max(roiCorner1ijk[2],roiCorner2ijk[2],roiCorner3ijk[2],roiCorner4ijk[2],roiCorner5ijk[2],roiCorner6ijk[2],roiCorner7ijk[2],roiCorner8ijk[2])

    image = self.__baselineVolume.GetImageData()
    clipper = vtk.vtkImageClip()
    clipper.ClipDataOn()
    clipper.SetOutputWholeExtent(int(lowerIJK[0]),int(upperIJK[0]),int(lowerIJK[1]),int(upperIJK[1]),int(lowerIJK[2]),int(upperIJK[2]))
    clipper.SetInputData(image)
    clipper.Update()

    roiImageRegion = clipper.GetOutput()
    intRange = roiImageRegion.GetScalarRange()
    lThresh = 0.4*(intRange[0]+intRange[1])
    uThresh = intRange[1]

    self.__vrOpacityMap.RemoveAllPoints()
    self.__vrOpacityMap.AddPoint(0,0)
    self.__vrOpacityMap.AddPoint(lThresh-1,0)
    self.__vrOpacityMap.AddPoint(lThresh,1)
    self.__vrOpacityMap.AddPoint(uThresh,1)
    self.__vrOpacityMap.AddPoint(uThresh+1,0)

    # finally, update the focal point to be the center of ROI
    # Don't do this actually -- this breaks volume rendering
    camera = slicer.mrmlScene.GetNodeByID('vtkMRMLCameraNode1')
    camera.SetFocalPoint(roiCenter)

  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
    roi = self.__roiSelector.currentNode()
    if roi == None:
      self.__parent.validationFailed(desiredBranchId, 'Error', 'Please define ROI!')

    self.__parent.validationSucceeded(desiredBranchId)

  def onEntry(self,comingFrom,transitionType):
    super(ChangeTrackerDefineROIStep, self).onEntry(comingFrom, transitionType)

    # setup the interface
    lm = slicer.app.layoutManager()
    lm.setLayout(3)
    pNode = self.parameterNode()
    Helper.SetBgFgVolumes(pNode.GetParameter('baselineVolumeID'),pNode.GetParameter('followupVolumeID'))
    Helper.SetLabelVolume(None)

    # use this transform node to align ROI with the axes of the baseline
    # volume
    roiTfmNodeID = pNode.GetParameter('roiTransformID')
    if roiTfmNodeID != '':
      self.__roiTransformNode = Helper.getNodeByID(roiTfmNodeID)
    else:
      Helper.Error('Internal error! Error code CT-S2-NRT, please report!')

    baselineVolume = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('baselineVolumeID'))
    self.__baselineVolume = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('baselineVolumeID'))

    # get the roiNode from parameters node, if it exists, and initialize the
    # GUI
    self.updateWidgetFromParameterNode(pNode)

    if self.__roi != None:
      self.__roi.GetDisplayNode().SetVisibility(True)

      self.InitVRDisplayNode()

    pNode.SetParameter('currentStep', self.stepid)

    qt.QTimer.singleShot(0, self.killButton)

  def onExit(self, goingTo, transitionType):
    if goingTo.id() != 'SegmentROI' and goingTo.id() != 'SelectScans':
      return
    # TODO: add storeWidgetStateToParameterNode() -- move all pNode-related stuff
    # there?
    if self.__roi != None:
      self.__roi.RemoveObserver(self.__roiObserverTag)
      self.__roi.GetDisplayNode().SetVisibility(False)

    pNode = self.parameterNode()
    if self.__vrDisplayNode != None:
      self.__vrDisplayNode.VisibilityOff()
      pNode.SetParameter('vrDisplayNodeID', self.__vrDisplayNode.GetID())

    pNode.SetParameter('roiNodeID', self.__roiSelector.currentNode().GetID())

    if goingTo.id() == 'SegmentROI':
      self.doStepProcessing()

    super(ChangeTrackerDefineROIStep, self).onExit(goingTo, transitionType)

  def updateWidgetFromParameterNode(self, parameterNode):
    roiNodeID = parameterNode.GetParameter('roiNodeID')

    if roiNodeID != '':
      self.__roi = slicer.mrmlScene.GetNodeByID(roiNodeID)
      self.__roiSelector.setCurrentNode(Helper.getNodeByID(self.__roi.GetID()))
    else:
      roi = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode")
      parameterNode.SetParameter('roiNodeID', roi.GetID())
      self.__roiSelector.setCurrentNode(roi)

    self.onROIChanged()


  def doStepProcessing(self):
    '''
    prepare roi image for the next step
    '''
    pNode = self.parameterNode()
    cropVolumeNode = slicer.vtkMRMLCropVolumeParametersNode()
    cropVolumeNode.SetScene(slicer.mrmlScene)
    cropVolumeNode.SetName('ChangeTracker_CropVolume_node')
    cropVolumeNode.SetIsotropicResampling(True)
    cropVolumeNode.SetSpacingScalingConst(0.5)
    slicer.mrmlScene.AddNode(cropVolumeNode)
    # TODO hide from MRML tree

    cropVolumeNode.SetInputVolumeNodeID(pNode.GetParameter('baselineVolumeID'))
    cropVolumeNode.SetROINodeID(pNode.GetParameter('roiNodeID'))
    # cropVolumeNode.SetAndObserveOutputVolumeNodeID(outputVolume.GetID())

    cropVolumeLogic = slicer.modules.cropvolume.logic()
    cropVolumeLogic.Apply(cropVolumeNode)

    # TODO: cropvolume error checking
    outputVolume = slicer.mrmlScene.GetNodeByID(cropVolumeNode.GetOutputVolumeNodeID())
    outputVolume.SetName("baselineROI")
    pNode.SetParameter('croppedBaselineVolumeID',cropVolumeNode.GetOutputVolumeNodeID())

    roiSegmentationID = pNode.GetParameter('croppedBaselineVolumeSegmentationID')
    if roiSegmentationID == '':
      roiRange = outputVolume.GetImageData().GetScalarRange()

      # default threshold is half-way of the range
      thresholdParameter = str(0.5*(roiRange[0]+roiRange[1]))+','+str(roiRange[1])
      pNode.SetParameter('thresholdRange', thresholdParameter)
      pNode.SetParameter('useSegmentationThresholds', 'True')

    # even if the seg. volume exists, it needs to be updated, because ROI
    # could have changed
    vl = slicer.modules.volumes.logic()
    roiSegmentation = vl.CreateLabelVolume(slicer.mrmlScene, outputVolume, 'baselineROI_segmentation')
    pNode.SetParameter('croppedBaselineVolumeSegmentationID', roiSegmentation.GetID())

  def InitVRDisplayNode(self):
    if self.__vrDisplayNode == None:
      pNode = self.parameterNode()
      vrNodeID = pNode.GetParameter('vrDisplayNodeID')
      if vrNodeID == '':
        self.__vrDisplayNode = slicer.modules.volumerendering.logic().CreateVolumeRenderingDisplayNode()
        v = slicer.mrmlScene.GetNodeByID(self.parameterNode().GetParameter('baselineVolumeID'))
        self.__vrDisplayNode = Helper.InitVRDisplayNode(v.GetID(), self.__roi.GetID())
      else:
        self.__vrDisplayNode = slicer.mrmlScene.GetNodeByID(vrNodeID)

    slicer.modules.volumerendering.logic().CopyDisplayToVolumeRenderingDisplayNode(self.__vrDisplayNode)

    self.__vrOpacityMap = self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
    self.__vrColorMap = self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetRGBTransferFunction()

    # setup color transfer function once
    self.__vrColorMap.RemoveAllPoints()
    self.__vrColorMap.AddRGBPoint(0, 0.8, 0.8, 0)
    self.__vrColorMap.AddRGBPoint(500, 0.8, 0.8, 0)
