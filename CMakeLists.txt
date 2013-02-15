
if(BUILD_TESTING)
  set(Launcher_Command ${Slicer_LAUNCH_COMMAND})
endif()

add_subdirectory(Wizard)
add_subdirectory(Metrics)

set(CT_PYTHON_SCRIPTS
  ChangeTracker.py
  )
  
set(CT_PYTHON_RESOURCES
  )
  
ctkMacroCompilePythonScript(
  TARGET_NAME ChangeTracker
  SCRIPTS "${CT_PYTHON_SCRIPTS}"
  RESOURCES "${CT_PYTHON_RESOURCES}"
  DESTINATION_DIR ${CMAKE_BINARY_DIR}/${Slicer_QTSCRIPTEDMODULES_LIB_DIR}
  INSTALL_DIR ${Slicer_INSTALL_QTSCRIPTEDMODULES_LIB_DIR}
  NO_INSTALL_SUBDIR
  )

