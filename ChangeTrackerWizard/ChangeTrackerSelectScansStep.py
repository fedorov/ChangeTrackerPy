from __main__ import qt, ctk

from ChangeTrackerStep import *
#from Helper import *

class ChangeTrackerSelectScansStep( ChangeTrackerStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '1. Select input scans' )
    self.setDescription( 'Select the baseline and follow-up scans to be compared.' )

    self.__parent = super( ChangeTrackerSelectScansStep, self )

  def createUserInterface( self ):
    '''
    '''
#    self.buttonBoxHints = self.ButtonBoxHidden

    self.__layout = self.__parent.createUserInterface()

    # let's load all tasks
    """self.loadTasks()

    selectTaskLabel = qt.QLabel( 'Select Task' )
    selectTaskLabel.setFont( self.__parent.getBoldFont() )
    self.__layout.addRow( selectTaskLabel )
"""
    self.__baselineVolumeSelector = qt.QComboBox()
    self.__baselineVolumeSelector.toolTip = "Choose the baseline scan"

    self.__followupVolumeSelector = qt.QComboBox()
    self.__followupVolumeSelector.toolTip = "Choose the followup scan"
"""
    # fill the comboBox with the taskNames
    self.__taskComboBox.addItems( self.getTaskNames() )
    self.__layout.addRow( Helper.CreateSpace( 20 ), self.__taskComboBox )

    # add empty row
    self.__layout.addRow( "", qt.QWidget() )


    chooseModeLabel = qt.QLabel( 'Choose Mode' )
    chooseModeLabel.setFont( self.__parent.getBoldFont() )
    self.__layout.addRow( chooseModeLabel )

    buttonBox = qt.QDialogButtonBox()
    simpleButton = buttonBox.addButton( buttonBox.Discard )
    simpleButton.setIcon( qt.QIcon() )
    simpleButton.text = "Simple"
    simpleButton.toolTip = "Click to use the simple mode."
    advancedButton = buttonBox.addButton( buttonBox.Apply )
    advancedButton.setIcon( qt.QIcon() )
    advancedButton.text = "Advanced"
    advancedButton.toolTip = "Click to use the advanced mode."
    self.__layout.addWidget( buttonBox )

    # connect the simple and advanced buttons
    simpleButton.connect( 'clicked()', self.goSimple )
    advancedButton.connect( 'clicked()', self.goAdvanced )


  def loadTasks( self ):
    '''
    Load all available Tasks and save them to self.__tasksList as key,value pairs of taskName and fileName
    '''
    if not self.logic():
      Helper.Error( "No logic class!" )
      return False

    # we query the logic for a comma-separated string with the following format of each item:
    # tasksName:tasksFile
    tasksList = self.logic().GetTasks().split( ',' )

    self.__tasksList.clear()

    for t in tasksList:
      task = t.split( ':' )
      taskName = task[0]
      taskFile = task[1]

      # add this entry to out tasksList
      self.__tasksList[taskName] = taskFile

    return True

  def loadTask( self ):
    '''
    '''
    index = self.__taskComboBox.currentIndex

    taskName = self.__taskComboBox.currentText
    taskFile = self.__tasksList[taskName]

    if not taskName or not taskFile:
      # error!
      Helper.Error( "Either taskName or taskFile was empty!" )
      return False

    # now get any loaded EMSTemplateNode which could fit our name
    templateNodesPreLoad = slicer.mrmlScene.GetNodesByClassByName( 'vtkMRMLEMSTemplateNode', taskName )
    if templateNodesPreLoad.GetNumberOfItems() > 0:
      # this is strange behavior but we can continue in this case!
      Helper.Warning( "We already have the template node in the scene and do not load it again!" )

    else:

      # there was no relevant template node in the scene, so let's import the mrml file
      # this is the normal behavior!      
      Helper.Debug( "Attempting to load task '" + taskName + "' from file '" + taskFile + "'" )

      # only load if no relevant node exists
      self.mrmlManager().ImportMRMLFile( taskFile )


    # now get the loaded EMSTemplateNode
    templateNodes = slicer.mrmlScene.GetNodesByClassByName( 'vtkMRMLEMSTemplateNode', taskName )

    if not templateNodes:
      # error!
      Helper.Error( "Could not find any template node after trying to load them!" )
      return False

    # we load the last template node which fits the taskname
    templateNode = templateNodes.GetItemAsObject( templateNodes.GetNumberOfItems() - 1 )

    loadResult = self.mrmlManager().SetLoadedParameterSetIndex( templateNode )
    if not loadResult:
      Helper.Info( "EMS node is corrupted - the manager could not be updated with new task: " + taskName )
      #return False

    self.logic().DefineTclTaskFullPathName( self.mrmlManager().GetTclTaskFilename() )

    return True


  def getTaskNames( self ):
    '''
    Get the taskNames of our tasksList
    '''
    return self.__tasksList.keys()

  def goSimple( self ):
    '''
    '''

    workflow = self.workflow()
    if not workflow:
      Helper.Error( "No valid workflow found!" )
      return False

    # we go forward in the simpleMode branch
    workflow.goForward( 'SimpleMode' )


  def goAdvanced( self ):
    '''
    '''

    workflow = self.workflow()
    if not workflow:
      Helper.Error( "No valid workflow found!" )
      return False

    # we go forward in the advancedMode branch
    workflow.goForward( 'AdvancedMode' )

  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )

    # we will try to load the selected task
    if self.loadTask():
      self.__parent.validationSucceeded( desiredBranchId )
    else:
      self.__parent.validationFailed( desiredBranchId, 'Load Task Error', 'There was an error loading the selected task!' )
"""
