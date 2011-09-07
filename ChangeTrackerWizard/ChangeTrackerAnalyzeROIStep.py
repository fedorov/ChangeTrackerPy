from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

import glob
import re
import os

class ChangeTrackerAnalyzeROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '4. ROI Analysis' )
    self.setDescription( 'Select the analysis method for the selected ROI.' )

    self.__parent = super( ChangeTrackerAnalyzeROIStep, self )

  def createUserInterface( self ):
    '''
    '''
#    self.buttonBoxHints = self.ButtonBoxHidden

    self.__layout = self.__parent.createUserInterface()

    # find all metrics in the plugins directory. The assumption is that all
    # metrics are named as ChangeTracker*Metric
    metricsSearchPattern = slicer.app.slicerHome+'/plugins/ChangeTracker*Metric'
    changeTrackerMetrics = glob.glob(metricsSearchPattern)

    # if len(changeTrackerMetrics) == 0:
    #   report error -- should this be done in __init__ ? 
    
    self.__metricCheckboxList = {}

    self.__basicFrame = ctk.ctkCollapsibleButton()
    self.__basicFrame.text = "Basic settings"
    self.__basicFrame.collapsed = 0
    basicFrameLayout = qt.QFormLayout(self.__basicFrame)
    self.__layout.addRow(self.__basicFrame)

    self.__advancedFrame = ctk.ctkCollapsibleButton()
    self.__advancedFrame.text = "Advanced settings"
    self.__advancedFrame.collapsed = 1
    boxLayout = qt.QVBoxLayout(self.__advancedFrame)
    self.__layout.addRow(self.__advancedFrame)

    self.__metricsFrame = ctk.ctkCollapsibleButton()
    self.__metricsFrame.text = "Change Detection Metrics"
    self.__metricsFrame.collapsed = 0
    metricsFrameLayout = qt.QVBoxLayout(self.__metricsFrame)
    boxLayout.addWidget(self.__metricsFrame)

    self.__registrationFrame = ctk.ctkCollapsibleButton()
    self.__registrationFrame.text = "Registration"
    self.__registrationFrame.collapsed = 0
    registrationFrameLayout = qt.QFormLayout(self.__registrationFrame)
    boxLayout.addWidget(self.__registrationFrame)

    metricsTabs = qt.QTabWidget()
    metricsFrameLayout.addWidget(metricsTabs)

    # TODO: error checking!
    for m in changeTrackerMetrics:
      pluginName = os.path.split(m)[1]
      metricName = re.match(r"ChangeTracker(\w+)Metric", pluginName).group(1)
      print "Discovered metric ",metricName
      label = qt.QLabel(metricName)
      checkbox = qt.QCheckBox()
      self.__metricCheckboxList[checkbox] = metricName

      # initialize basic frame
      basicFrameLayout.addRow(label, checkbox)

      # initialize advanced frame
      metricGui = slicer.util.getModuleGui(pluginName)
      parametersWidget = Helper.findChildren(metricGui, text='Parameters')[0]

      if parametersWidget != None:
        metricWidget = qt.QWidget()
        metricLayout = qt.QFormLayout(metricWidget)
        metricLayout.addRow(parametersWidget)
        metricsTabs.addTab(metricWidget, metricName)
      
    self.__transformSelector = slicer.qMRMLNodeComboBox()
    self.__transformSelector.toolTip = "Transform aligning the follow-up scan with the baseline"
    self.__transformSelector.nodeTypes = ['vtkMRMLLinearTransformNode']
    self.__transformSelector.noneEnabled = 1
    self.__transformSelector.setMRMLScene(slicer.mrmlScene)

    transformSelectorLabel = qt.QLabel('Transform: ')
    registrationFrameLayout.addRow(transformSelectorLabel, self.__transformSelector)

    # TODO (?) query parameters for each metric, and put each metric into a
    # separate frame, with the parameters GUI initialized. Might be a nice
    # feature to have.

  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
      
    # to proceed to the next step, at least one metric should be selected!
    nSelectedMetrics = 0
    # parameters will be the same for all metrics
    pNode = self.parameterNode()
    parameters = {}
    parameters['baselineVolume'] = pNode.GetParameter('croppedBaselineVolumeID')
    parameters['followupVolume'] = pNode.GetParameter('croppedFollowupVolumeID')
    parameters['baselineSegmentationVolume'] = pNode.GetParameter('croppedBaselineVolumeSegmentationID')
    
    baselineVolume = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('croppedBaselineVolumeID'))

    moduleManager = slicer.app.moduleManager()
    for m in self.__metricCheckboxList:
      if m.isChecked():
        nSelectedMetrics = nSelectedMetrics+1

        # TODO: processing should be separated from the workflow! need to move
        # this into a different place
        pluginName = 'ChangeTracker'+self.__metricCheckboxList[m]+'Metric'
        pluginName = pluginName.lower()
        
        vl = slicer.modules.volumes.logic()
        outputVolume = vl.CreateLabelVolume(slicer.mrmlScene, baselineVolume, 'changesVolume_'+self.__metricCheckboxList[m])
        parameters['outputVolume'] = outputVolume.GetID()

        plugin = moduleManager.module(pluginName)
        if plugin != None:
          # QUESTION: how can I get the pointer to the module object based on
          # the module name?
          cliNode = None
          cliNode = slicer.cli.run(plugin, cliNode, parameters, 1)

          

    if nSelectedMetrics > 0:
      self.__parent.validationSucceeded(desiredBranchId)
      print 'Validation from Analysis step succeeded!'
    else:
      self.__parent.validationFailed(desiredBranchId, "At least one metric should be selected to proceed to the next step!")

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


