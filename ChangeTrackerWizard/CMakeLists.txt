SET(EMSegmentWizard_PYTHON_SCRIPTS
  __init__.py
  ChangeTrackerStep.py
  ChangeTrackerSelectScansStep.py
 )

SET(ChangeTrackerWizard_PYTHON_RESOURCES
  )
  
ctkMacroCompilePythonScript(
  TARGET_NAME ChangeTrackerPyWizard
  SCRIPTS "${EMSegmentWizard_PYTHON_SCRIPTS}"
  RESOURCES "${EMSegmentWizard_PYTHON_RESOURCES}"
  DESTINATION_DIR ${Slicer_BINARY_DIR}/bin/Python/ChangeTrackerPyWizard
  INSTALL_DIR ${Slicer_INSTALL_BIN_DIR}/Python
  )

#-----------------------------------------------------------------------------
# Testing
#
if(BUILD_TESTING)
endif(BUILD_TESTING)
