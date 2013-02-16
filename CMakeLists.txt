cmake_minimum_required(VERSION 2.8.9)

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  set(EXTENSION_NAME ChangeTracker)
  set(EXTENSION_HOMEPAGE "http://wiki.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/ChangeTracker")
  set(EXTENSION_CATEGORY "Wizards")
  set(EXTENSION_CONTRIBUTORS "Andrey Fedorov (SPL), Kilian Pohl (SPL), Peter Black (BWH), Jean-Christophe Fillion-Robin (Kitware), Ron Kikinis (SPL)")
  set(EXTENSION_DESCRIPTION "ChangeTracker is a software tool for quantification of the subtle changes in pathology. The module provides a workflow pipeline that combines user input with the medical data. As a result we provide quantitative volumetric measurements of growth/shrinkage together with the volume rendering of the tumor and color-coded visualization of the tumor growth/shrinkage.")
  set(EXTENSION_ICONURL "http://www.slicer.org/slicerWiki/images/b/b9/ChangeTracker_logo.png")
  set(EXTENSION_SCREENSHOTURLS "http://www.slicer.org/slicerWiki/images/8/8e/Slicer4_ChangeTracker_Ad.png")
  set(EXTENSION_STATUS "Work in progress")
endif()

#-----------------------------------------------------------------------------
if(NOT Slicer_SOURCE_DIR)
  find_package(Slicer REQUIRED)
  include(${Slicer_USE_FILE})
endif()

#-----------------------------------------------------------------------------
add_subdirectory(Metrics)

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

if(NOT Slicer_SOURCE_DIR)
  include(${Slicer_EXTENSION_CPACK})
endif()
