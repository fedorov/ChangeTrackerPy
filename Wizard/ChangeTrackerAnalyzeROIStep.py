from __main__ import qt, ctk

from ChangeTrackerStep import *
from Helper import *

import glob
import re
import os
import string

class ChangeTrackerAnalyzeROIStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '4. ROI Analysis' )
    self.setDescription( 'Select the analysis method for the selected ROI.' )

    self.__parent = super( ChangeTrackerAnalyzeROIStep, self )

    qt.QTimer.singleShot(0, self.killButton)

  def killButton(self):
    # hide useless button
    bl = slicer.util.findChildren(text='ReportROI')
    if len(bl):
      bl[0].hide()


  def createUserInterface( self ):
    '''
    '''
#    self.buttonBoxHints = self.ButtonBoxHidden

    self.__layout = self.__parent.createUserInterface()

    # find all metrics in the plugins directory. The assumption is that all
    # metrics are named as ChangeTracker*Metric
    allModules = dir(slicer.moduleNames)
    changeTrackerMetrics = []
    for m in allModules:
      if m.endswith('Metric'):
        changeTrackerMetrics.append(m)

    print 'Metrics discovered: ', changeTrackerMetrics

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

    self.__metricsTabs = qt.QTabWidget()
    metricsFrameLayout.addWidget(self.__metricsTabs)

    # TODO: error checking!
    for m in changeTrackerMetrics:
      pluginName = m
      moduleManager = slicer.app.moduleManager()
      plugin = moduleManager.module(pluginName)
      label = qt.QLabel(plugin.title)
      checkbox = qt.QCheckBox()
      self.__metricCheckboxList[checkbox] = pluginName

      # initialize basic frame
      basicFrameLayout.addRow(label, checkbox)

      # initialize advanced frame
      metricGui = slicer.util.getModuleGui(pluginName)
      parametersWidget = Helper.findChildren(metricGui, text='Parameters')[0]

      if parametersWidget != None:
        metricWidget = qt.QWidget()
        metricLayout = qt.QFormLayout(metricWidget)
        metricLayout.addRow(parametersWidget)
        self.__metricsTabs.addTab(metricWidget, pluginName)
      
    self.__transformSelector = slicer.qMRMLNodeComboBox()
    self.__transformSelector.toolTip = "Transform aligning the follow-up scan with the baseline"
    self.__transformSelector.nodeTypes = ['vtkMRMLLinearTransformNode']
    self.__transformSelector.noneEnabled = 1
    self.__transformSelector.setMRMLScene(slicer.mrmlScene)

    transformSelectorLabel = qt.QLabel('Transform: ')
    registrationFrameLayout.addRow(transformSelectorLabel, self.__transformSelector)

    # TODO (?) query parameters for each metric, and put each metric into a
    # separate frame, with the parameters GUI initialized. Might be a nice
    # feature to have.`

  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
      
    # to proceed to the next step, at least one metric should be selected!
    nSelectedMetrics = 0
    for m in self.__metricCheckboxList:
      if m.isChecked():
        nSelectedMetrics = nSelectedMetrics+1

    if nSelectedMetrics > 0:
    
      # do we have a transform node?
      self.__parent.validationSucceeded(desiredBranchId)

    else:
      self.__parent.validationFailed(desiredBranchId, 'Error', "At least one metric should be selected to proceed to the next step!")



  def onEntry(self, comingFrom, transitionType):
    Helper.Info('Analyze step: on Entry')
    super(ChangeTrackerAnalyzeROIStep, self).onEntry(comingFrom, transitionType)
    self.updateWidgetFromParameters()

    pNode = self.parameterNode()
    pNode.SetParameter('currentStep', self.stepid)
    
    qt.QTimer.singleShot(0, self.killButton)

  def onExit(self, goingTo, transitionType):
    if goingTo.id() != 'SegmentROI' and goingTo.id() != 'ReportROI':
      return
    '''
    Do the processing for this step here
    '''
    Helper.Info('Analyze step: entering onExit()')

    self.updateParametersFromWidget()


    print 'onExit() in Analyze step: goingTo = ',goingTo.id(),', selfId = ',self.id()
    if goingTo.id() == 'ReportROI':
      self.doStepProcessing()

    Helper.Info('Analyze step: leaving onExit()')
    
    super(ChangeTrackerAnalyzeROIStep, self).onExit(goingTo, transitionType)

  def updateWidgetFromParameters(self):
    pNode = self.parameterNode()
    # update widget elements
    metricsList = string.split(pNode.GetParameter('metrics'),',')
    for mc in self.__metricCheckboxList:
      m = self.__metricCheckboxList[mc]
      if m in metricsList:
        mc.setChecked(1)
    
    transformID = pNode.GetParameter('followupTransformID')
    if transformID != '':
      self.__transformSelector.setCurrentNode(Helper.getNodeByID(transformID))
    
  def updateParametersFromWidget(self):
    pNode = self.parameterNode()

    # which metrics have been selected?
    metricsList = ''
    for m in self.__metricCheckboxList:
      if m.isChecked():
        if metricsList != '':
          metricsList = metricsList + ','     
        metricsList = metricsList + self.__metricCheckboxList[m]
    pNode.SetParameter('metrics', metricsList)

    # do we have a transform node?
    followupTransform = self.__transformSelector.currentNode()
    if followupTransform != None:
      pNode.SetParameter('followupTransformID', followupTransform.GetID())
    else:
      pNode.SetParameter('followupTransformID', '')

  '''
  def updateProgress(self):
    print 'updateProgress() !!!'
    slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
    self.progress.repaint()
  '''

  def doStepProcessing(self):
    print 'Step processing'
    
    '''
    timer = qt.QTimer()
    timer.setInterval(1000)
    timer.setSingleShot(0)
    timer.connect('timeout()', self.updateProgress)
    '''

    # pop up progress dialog to prevent user from messing around
    self.progress = qt.QProgressDialog(slicer.util.mainWindow())
    self.progress.minimumDuration = 0
    self.progress.show()
    self.progress.setValue(0)
    self.progress.setMaximum(0)
    self.progress.setCancelButton(0)
    self.progress.setWindowModality(2)
 
    self.progress.setLabelText('Registering followup image to baseline')
    slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
    self.progress.repaint()
    
    # qt.QTimer.singleShot(0, self.updateProgress)

    '''
    Step logic:
      1) register followup to baseline
      2) resample followup to baseline ROI
      3) given baselineROI, followupROI and baseline segmentation, run each of
      the change detection metrics
    '''
    pNode = self.parameterNode()

    # (1) register followup to baseline
    # If the followup transform is initialized, do not register!
    if pNode.GetParameter('followupTransformID') == '':
      baselineVolumeID = pNode.GetParameter('baselineVolumeID')
      followupVolumeID = pNode.GetParameter('followupVolumeID')
      self.__followupTransform = slicer.vtkMRMLLinearTransformNode()
      slicer.mrmlScene.AddNode(self.__followupTransform)

      parameters = {}
      parameters["fixedVolume"] = baselineVolumeID
      parameters["movingVolume"] = followupVolumeID
      parameters["initializeTransformMode"] = "useMomentsAlign"
      parameters["useRigid"] = True
      parameters["useScaleVersor3D"] = False
      parameters["useScaleSkewVersor3D"] = False
      parameters["useAffine"] = True
      parameters["linearTransform"] = self.__followupTransform.GetID()
      # apparently this is needed even if not b-spline (see bug report 1542)
      parameters["forceMINumberOfThreads"] = -1

      # FIXME: make sure brainsfit is available first?
      cliNode = None
      cliNode = slicer.cli.run(slicer.modules.brainsfit, cliNode, parameters, wait_for_completion = True)
      
      status = cliNode.GetStatusString()

      '''
      while status != 'Completed':
      # while status == 'Running' or status == 'Scheduled' or status == 'Idle':
        slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
        self.progress.repaint()
        status = cliNode.GetStatusString()

      print 'Registration completed: status = ', status
      '''

      if status == 'Completed':
        Helper.Info('registration completed OK')
      else:
        Helper.ErrorPopup('Registration step failed. Unable to proceed. Please quit Slicer and report this issue including the output from the error log.')
        return

      pNode.SetParameter('followupTransformID', self.__followupTransform.GetID())

      print 'AnalyzeROIStep: registration completed!'
    else:
      print 'AnalyzeROIStep: registration not required!'

    self.progress.setLabelText('Estimating changes')
    slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
    self.progress.repaint()

    # self.__cliObserverTag = self.__cliNode.AddObserver('ModifiedEvent', self.processRegistrationCompletion)
    # self.__registrationStatus.setText('Wait ...')
    # self.__registrationButton.setEnabled(0)

    # (2) resample followup to baselineROI
    baselineVolumeROI = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('croppedBaselineVolumeID'))
    followupVolume = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('followupVolumeID'))
    followupVolumeROI = slicer.modules.volumes.logic().CloneVolume(slicer.mrmlScene, followupVolume, 'followupROI')

    parameters = {}
    parameters["inputVolume"] = pNode.GetParameter('followupVolumeID')
    parameters["referenceVolume"] = pNode.GetParameter('croppedBaselineVolumeID')
    parameters["outputVolume"] = followupVolumeROI.GetID()
    parameters["transformationFile"] = pNode.GetParameter('followupTransformID')
    parameters["interpolationType"] = "bs"

    cliNode = None
    cliNode = slicer.cli.run(slicer.modules.resamplescalarvectordwivolume, cliNode, parameters, 1)

    status = cliNode.GetStatusString()
    if status == 'Completed':
      Helper.Info('ResampleScalarVectorDWIVolume completed OK')
      pNode.SetParameter('croppedFollowupVolumeID', followupVolumeROI.GetID())
    else:
      Helper.Error('Failed to resample!')

    # (3) calculate each of the metrics
    # most of the parameters will be the same for all metrics
    parameters = {}
    parameters['baselineVolume'] = pNode.GetParameter('croppedBaselineVolumeID')
    parameters['followupVolume'] = pNode.GetParameter('croppedFollowupVolumeID')
    parameters['baselineSegmentationVolume'] = pNode.GetParameter('croppedBaselineVolumeSegmentationID')
    
    baselineVolume = slicer.mrmlScene.GetNodeByID(pNode.GetParameter('croppedBaselineVolumeID'))

    metricsList = pNode.GetParameter('metrics')

    if metricsList == '':
      Helper.Error('doStepProcessing(): metrics list is empty!')
      
    resultVolumesList = ''

    moduleManager = slicer.app.moduleManager()
    for m in string.split(metricsList,','):
      # TODO: processing should be separated from the workflow! need to move
      # this into a different place
      pluginName = m
      # pluginName = pluginName.lower()
        
      vl = slicer.modules.volumes.logic()
      outputVolume = vl.CreateLabelVolume(slicer.mrmlScene, baselineVolume, 'changesVolume_'+m)
      outputReport =  slicer.app.temporaryPath+os.sep+pluginName+'_report.txt'

      parameters["tmpDirectory"] = slicer.app.temporaryPath
      parameters['outputVolume'] = outputVolume.GetID()
      parameters['reportFileName'] = outputReport

      plugin = moduleManager.module(pluginName)
      if plugin != None:
        cliNode = None
        Helper.Info('About to run '+m+' metric!')
        cliNode = slicer.cli.run(plugin, cliNode, parameters, 1)

      '''
      TODO: error checking for CLI!
      '''
      labelsColorNode = slicer.modules.colors.logic().GetColorTableNodeID(10)
      outputVolume.GetDisplayNode().SetAndObserveColorNodeID(labelsColorNode)
        
      if resultVolumesList != '':
          resultVolumesList = resultVolumesList + ','
      resultVolumesList = resultVolumesList + outputVolume.GetID()

      outputVolume.SetDescription(Helper.readFileAsString(outputReport))

    pNode.SetParameter('resultVolumes', resultVolumesList)

    Helper.Info('Selected metrics: '+pNode.GetParameter('metrics'))
    Helper.Info('Metrics processing results:'+pNode.GetParameter('resultVolumes'))

    # close the progress window 
    '''
    timer.stop()
    '''
    self.progress.setValue(2)
    self.progress.repaint()
    slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
    self.progress.close()
    self.progress = None
