slicer_add_python_unittest(
  SCRIPT ChangeTrackerSelfTest.py
  SLICER_ARGS --additional-module-path
  "${CMAKE_BINARY_DIR}/${Slicer_QTLOADABLEMODULES_LIB_DIR}"
  )

ctkMacroCompilePythonScript(
  TARGET_NAME ChangeTrackerSelfTest
  SCRIPTS "ChangeTrackerSelfTest.py"
  RESOURCES ""
  DESTINATION_DIR ${CMAKE_BINARY_DIR}/${Slicer_QTSCRIPTEDMODULES_LIB_DIR}
  INSTALL_DIR ${Slicer_INSTALL_QTSCRIPTEDMODULES_LIB_DIR}
  NO_INSTALL_SUBDIR
  )
