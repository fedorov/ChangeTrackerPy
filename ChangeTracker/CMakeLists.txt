
#-----------------------------------------------------------------------------
set(MODULE_NAME ChangeTracker)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  )

set(MODULE_PYTHON_RESOURCES
  ${MODULE_NAME}Wizard/__init__.py
  ${MODULE_NAME}Wizard/Helper.py
  ${MODULE_NAME}Wizard/${MODULE_NAME}Step.py
  ${MODULE_NAME}Wizard/${MODULE_NAME}SelectScansStep.py
  ${MODULE_NAME}Wizard/${MODULE_NAME}DefineROIStep.py
  ${MODULE_NAME}Wizard/${MODULE_NAME}SegmentROIStep.py
  ${MODULE_NAME}Wizard/${MODULE_NAME}RegistrationStep.py
  ${MODULE_NAME}Wizard/${MODULE_NAME}AnalyzeROIStep.py
  ${MODULE_NAME}Wizard/${MODULE_NAME}ReportROIStep.py
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  )

