from __main__ import vtk, qt, ctk, slicer

import ChangeTrackerWizard

class ChangeTracker:
  def __init__( self, parent ):
    parent.title = """ChangeTracker"""
    parent.categories = ["""Wizards"""]
    parent.contributors = ["""Andrey Fedorov""", """Kilian Pohl""", """Peter Black""", """Ron Kikinis"""]
    parent.helpText = """
    ChangeTracker facilitates estimation of small changes in the anatomy. The change is quantified in mL for growth/shrinkage, and is also visualized with tumor changes color-coded. The module documentation (work in progress) can be found here: <a href="http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.0/Modules/ChangeTracker">http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.0/Modules/ChangeTracker</a><br><br>To use the module, follow the workflow that consists of the 4 steps:<br><br>1. Select baseline and followup image volumes that you want to compare. Note that it is expected that the differences between the two images are not drastic (e.g., the module has not been tested to handle images pre/post resection, or with the large changes due to treatment)<br><br>2. Define the region of interest by placing the ROI widget appropriately.<br><br>3. Segment the structure of interest in the ROI. Currently, this is done using intensity threshold.<br><br>4. Choose the change detection metric and parameters, if necessary.<br><br>5. The results and quantification of changes are displayed.
    """;
    parent.acknowledgementText = """This work is supported by NA-MIC, NAC, NCIGT, and the Slicer Community. See <a href="http://www.slicer.org">http://slicer.org</a> for details.  Module implemented by Andrey Fedorov. This work was partially supported by Brain Science Foundation and NIH U01 CA151261.
    """
    self.parent = parent

class ChangeTrackerWidget:
  def __init__( self, parent=None ):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout( qt.QVBoxLayout() )
      self.parent.setMRMLScene( slicer.mrmlScene )
    else:
      self.parent = parent
    self.layout = self.parent.layout()

    # this flag is 1 if there is an update in progress
    self.__updating = 1

    # the pointer to the logic and the mrmlManager
    self.__mrmlManager = None
    self.__logic = None

    if not parent:
      self.setup()

      # after setup, be ready for events
      self.__updating = 0

      self.parent.show()

    if slicer.mrmlScene.GetTagByClassName( "vtkMRMLScriptedModuleNode" ) != 'ScriptedModule':
      slicer.mrmlScene.RegisterNodeClass(vtkMRMLScriptedModuleNode())


  def setup( self ):
    '''
    Create and start the ChangeTracker workflow.
    '''
    self.workflow = ctk.ctkWorkflow()

    workflowWidget = ctk.ctkWorkflowStackedWidget()
    workflowWidget.setWorkflow( self.workflow )

    workflowWidget.buttonBoxWidget().nextButtonDefaultText = ""
    workflowWidget.buttonBoxWidget().backButtonDefaultText = ""
    
    # create all wizard steps
    self.selectScansStep = ChangeTrackerWizard.ChangeTrackerSelectScansStep( 'SelectScans'  )
    self.defineROIStep = ChangeTrackerWizard.ChangeTrackerDefineROIStep( 'DefineROI'  )
    self.segmentROIStep = ChangeTrackerWizard.ChangeTrackerSegmentROIStep( 'SegmentROI'  )
    self.analyzeROIStep = ChangeTrackerWizard.ChangeTrackerAnalyzeROIStep( 'AnalyzeROI'  )
    self.reportROIStep = ChangeTrackerWizard.ChangeTrackerReportROIStep( 'ReportROI'  )

    # add the wizard steps to an array for convenience
    allSteps = []

    allSteps.append( self.selectScansStep )
    allSteps.append( self.defineROIStep )
    allSteps.append( self.segmentROIStep )
    allSteps.append( self.analyzeROIStep )
    allSteps.append( self.reportROIStep )

    # Add transition for the first step which let's the user choose between simple and advanced mode
    self.workflow.addTransition( self.selectScansStep, self.defineROIStep )
    self.workflow.addTransition( self.defineROIStep, self.segmentROIStep )
    self.workflow.addTransition( self.segmentROIStep, self.analyzeROIStep )
    self.workflow.addTransition( self.analyzeROIStep, self.reportROIStep )

    nNodes = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLScriptedModuleNode')

    self.parameterNode = None
    for n in xrange(nNodes):
      compNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLScriptedModuleNode')
      nodeid = None
      if compNode.GetModuleName() == 'ChangeTracker':
        self.parameterNode = compNode
        print 'Found existing ChangeTracker parameter node'
        break
    if self.parameterNode == None:
      self.parameterNode = slicer.vtkMRMLScriptedModuleNode()
      self.parameterNode.SetModuleName('ChangeTracker')
      slicer.mrmlScene.AddNode(self.parameterNode)
 
    for s in allSteps:
        s.setParameterNode (self.parameterNode)

    # restore workflow step
    currentStep = self.parameterNode.GetParameter('currentStep')
    if currentStep != '':
      print 'Restoring workflow step to ', currentStep
      if currentStep == 'SelectScans':
        self.workflow.setInitialStep(self.selectScansStep)
      if currentStep == 'DefineROI':
        self.workflow.setInitialStep(self.defineROIStep)
      if currentStep == 'SegmentROI':
        self.workflow.setInitialStep(self.segmentROIStep)
      if currentStep == 'AnalyzeROI':
        self.workflow.setInitialStep(self.analyzeROIStep)
      if currentStep == 'ReportROI':
        self.workflow.setInitialStep(self.reportROIStep)
    else:
      print 'currentStep in parameter node is empty!'
        
    # start the workflow and show the widget
    self.workflow.start()
    workflowWidget.visible = True
    self.layout.addWidget( workflowWidget )

    # enable global access to the dynamicFrames on step 2 and step 6
    #slicer.modules.emsegmentSimpleDynamicFrame = defineInputChannelsSimpleStep.dynamicFrame()
    #slicer.modules.emsegmentAdvancedDynamicFrame = definePreprocessingStep.dynamicFrame()

    # compress the layout
      #self.layout.addStretch(1)        
 
  def enter(self):
    print "ChangeTracker: enter() called"
