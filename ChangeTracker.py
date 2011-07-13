from __main__ import vtk, qt, ctk, slicer

# import EMSegmentWizard
# from EMSegmentWizard import Helper
import ChangeTrackerPyWizard

class ChangeTrackerPy:
  def __init__( self, parent ):
    parent.title = "ChangeTracker"
    parent.category = ""
    parent.contributor = "Andrey Fedorov"
    parent.helpText = """Help text"""
    parent.acknowledgementText = """Ack text"""
    self.parent = parent

class ChangeTrackerPyWidget:
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

    # register default slots
    #self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)', self.onMRMLSceneChanged)      


  #def logic( self ):
    #if not self.__logic:
    #    self.__logic = slicer.modulelogic.vtkChangeTrackerLogic()
    #    self.__logic.SetModuleName( "ChangeTracker" )
    #    self.__logic.SetMRMLScene( slicer.mrmlScene )
    #    self.__logic.RegisterNodes()
    #    self.__logic.InitializeEventListeners()

    #return self.__logic

  #def mrmlManager( self ):
  #  if not self.__mrmlManager:
  #      self.__mrmlManager = self.logic().GetMRMLManager()
  #      self.__mrmlManager.SetMRMLScene( slicer.mrmlScene )
  #
  #  return self.__mrmlManager


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
    selectScansStep = ChangeTrackerPyWizard.ChangeTrackerSelectScansStep( 'SelectScans'  )

    selectROIStep = ChangeTrackerPyWizard.ChangeTrackerSelectScansStep( 'SelectROI'  )

    '''
    defineInputChannelsSimpleStep = ChangeTrackerWizard.ChangeTrackerDefineInputChannelsStep( Helper.GetNthStepId( 2 ) + 'Simple' ) # simple branch
    defineInputChannelsAdvancedStep = ChangeTrackerWizard.ChangeTrackerDefineInputChannelsStep( Helper.GetNthStepId( 2 ) + 'Advanced' ) # advanced branch
    defineAnatomicalTreeStep = ChangeTrackerWizard.ChangeTrackerDefineAnatomicalTreeStep( Helper.GetNthStepId( 3 ) )
    defineAtlasStep = ChangeTrackerWizard.ChangeTrackerDefineAtlasStep( Helper.GetNthStepId( 4 ) )
    editRegistrationParametersStep = ChangeTrackerWizard.ChangeTrackerEditRegistrationParametersStep( Helper.GetNthStepId( 5 ) )
    definePreprocessingStep = ChangeTrackerWizard.ChangeTrackerDefinePreprocessingStep( Helper.GetNthStepId( 6 ) )
    specifyIntensityDistributionStep = ChangeTrackerWizard.ChangeTrackerSpecifyIntensityDistributionStep( Helper.GetNthStepId( 7 ) )
    editNodeBasedParametersStep = ChangeTrackerWizard.ChangeTrackerEditNodeBasedParametersStep( Helper.GetNthStepId( 8 ) )
    miscStep = ChangeTrackerWizard.ChangeTrackerDefineMiscParametersStep( Helper.GetNthStepId( 9 ) )
    segmentStep = ChangeTrackerWizard.ChangeTrackerDummyStep( Helper.GetNthStepId( 10 ) )

    '''

    # add the wizard steps to an array for convenience
    allSteps = []

    allSteps.append( selectScansStep )
    allSteps.append( selectROIStep )
    '''
    allSteps.append( defineInputChannelsSimpleStep )
    allSteps.append( defineInputChannelsAdvancedStep )
    allSteps.append( defineAnatomicalTreeStep )
    allSteps.append( defineAtlasStep )
    allSteps.append( editRegistrationParametersStep )
    allSteps.append( definePreprocessingStep )
    allSteps.append( specifyIntensityDistributionStep )
    allSteps.append( editNodeBasedParametersStep )
    allSteps.append( miscStep )
    allSteps.append( segmentStep )
    '''

    # Add transition for the first step which let's the user choose between simple and advanced mode
    self.workflow.addTransition( selectScansStep, selectROIStep )

    '''
    self.workflow.addTransition( selectTaskStep, defineInputChannelsAdvancedStep, 'AdvancedMode' )

    # Add transitions associated to the simple mode
    self.workflow.addTransition( defineInputChannelsSimpleStep, segmentStep )

    # Add transitions associated to the advanced mode
    self.workflow.addTransition( defineInputChannelsAdvancedStep, defineAnatomicalTreeStep )

    # .. add transitions for the rest of the advanced mode steps
    for i in range( 3, len( allSteps ) - 1 ):
      self.workflow.addTransition( allSteps[i], allSteps[i + 1] )

    # Propagate the workflow, the logic and the MRML Manager to the steps
    for s in allSteps:
        s.setWorkflow( self.workflow )
        s.setLogic( self.logic() )
        s.setMRMLManager( self.mrmlManager() )
    '''

    # start the workflow and show the widget
    self.workflow.start()
    workflowWidget.visible = True
    self.layout.addWidget( workflowWidget )

    # enable global access to the dynamicFrames on step 2 and step 6
    #slicer.modules.emsegmentSimpleDynamicFrame = defineInputChannelsSimpleStep.dynamicFrame()
    #slicer.modules.emsegmentAdvancedDynamicFrame = definePreprocessingStep.dynamicFrame()

    # compress the layout
      #self.layout.addStretch(1)        
