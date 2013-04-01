slicer_add_python_unittest(
  SCRIPT ChangeTrackerSelfTest.py
  SLICER_ARGS --additional-module-path
  "${CMAKE_BINARY_DIR}/${Slicer_QTLOADABLEMODULES_LIB_DIR}"
  )

slicerMacroBuildScriptedModule(
  NAME ChangeTrackerSelfTest
  SCRIPTS "ChangeTrackerSelfTest.py"
  RESOURCES ""
  )
