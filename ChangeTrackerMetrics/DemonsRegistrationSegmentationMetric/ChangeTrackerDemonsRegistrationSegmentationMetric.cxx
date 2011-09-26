/*
#include <BRAINSDemonWarpCommonLibWin32Header.h>
#include <BRAINSCommonLibWin32Header.h>
#include <BRAINSThreadControl.h>
#include <BRAINSDemonWarpTemplates.h>
*/

#include <stdlib.h>
#include <ChangeTrackerDemonsRegistrationSegmentationMetricCLP.h>

#include <itkImage.h>
#include <itkImageFileReader.h>
#include <itkImageFileWriter.h>
#include <itkImageDuplicator.h>
#include <itkImageRegionIteratorWithIndex.h>

#define DEMONS_RESULT "ctdr_registered.nrrd"
#define DEMONS_DF_RESULT "ctdr_registered_DF.nrrd"

#define DEMONS_REVERSE_RESULT "ctdr-seg_reverse_registered.nrrd"
#define DEMONS_REVERSE_DF_RESULT "ctdr-seg_reverse_registered_DF.nrrd"
#define DEMONS_WARPED_SEGMENTATION "ctdr-seg_followup_segmentation.nrrd"
// this will go away once bug #1455 is resolved
#define PLUGINS_PATH "/Users/fedorov/Slicer/Slicer4-Superbuild/Slicer-build/lib/Slicer-4.0/cli-modules/"
#define GROWTH_LABEL 14
#define SHRINK_LABEL 12

int main(int argc, char *argv[])
{

  PARSE_ARGS;

  std::ostringstream cmdLine;
  int ret;

  std::string warpedSegmentationFileName = tmpDirectory+"/"+DEMONS_WARPED_SEGMENTATION;

  // run registration with the followup as fixed image
  cmdLine << PLUGINS_PATH << "/BRAINSDemonWarp " <<
    "--registrationFilterType Demons -n 3 -i 20,20,20 " << // 3 levels, with 20 iterations each
    " --minimumFixedPyramid 2,2,2 --minimumMovingPyramid 2,2,2 " <<
    " --movingVolume " << baselineVolume <<
    " --fixedVolume " << followupVolume <<
    " --outputVolume " << tmpDirectory << "/" << DEMONS_REVERSE_RESULT <<
    " --outputDeformationFieldVolume " << tmpDirectory << "/" << DEMONS_REVERSE_DF_RESULT;
  std::cout << cmdLine.str() << std::endl;
  ret = system(cmdLine.str().c_str());
  if(ret){
    std::cerr << "ERROR during demons registration" << std::endl;
    return -1;
  } else {
    std::cout << "Demons registration completed OK" << std::endl;
  }

  cmdLine.str("");

  // resample the segmentation of the baseline image to the fixed image
  cmdLine << PLUGINS_PATH << "/BRAINSResample " <<
    " --referenceVolume " << followupVolume <<
    " --inputVolume " << baselineSegmentationVolume <<
    " --interpolationMode NearestNeighbor " <<
    " --deformationVolume " << DEMONS_REVERSE_DF_RESULT <<
    " --outputVolume " << warpedSegmentationFileName;
  std::cout << cmdLine.str() << std::endl;
  system(cmdLine.str().c_str());
  if(ret){
    std::cerr << "ERROR during resampling" << std::endl;
    return -1;
  } else {
    std::cout << "Demons registration completed OK" << std::endl;
  }

  // read the warped segmentation, and create the change map
  typedef itk::Image<char, 3> ImageType;
  typedef itk::ImageFileReader<ImageType> ReaderType;
  typedef itk::ImageFileWriter<ImageType> WriterType;
  typedef itk::ImageDuplicator<ImageType> DuplicatorType;
  typedef itk::ImageRegionIteratorWithIndex<ImageType> IteratorType;

  ReaderType::Pointer reader1 = ReaderType::New();
  reader1->SetFileName(warpedSegmentationFileName.c_str());
  reader1->Update();
  
  ReaderType::Pointer reader2 = ReaderType::New();
  reader2->SetFileName(baselineSegmentationVolume.c_str());
  reader2->Update();

  DuplicatorType::Pointer dup = DuplicatorType::New();
  ImageType::Pointer followupSegmentation = reader1->GetOutput(),
    baselineSegmentation = reader2->GetOutput(),
    changesLabel;

  dup->SetInputImage(baselineSegmentation);
  dup->Update();
  changesLabel = dup->GetOutput();
  changesLabel->FillBuffer(0);

  IteratorType bIt(baselineSegmentation, baselineSegmentation->GetBufferedRegion());
  float growthPixels = 0, shrinkPixels = 0;
  for(bIt.GoToBegin();!bIt.IsAtEnd();++bIt){
    ImageType::IndexType idx = bIt.GetIndex();
    ImageType::PixelType bPxl, fPxl;
    bPxl = bIt.Get();
    fPxl = followupSegmentation->GetPixel(idx);

    if(bPxl && !fPxl){
      changesLabel->SetPixel(idx, 12);
      shrinkPixels++;
    } else if(!bPxl && fPxl) {
      changesLabel->SetPixel(idx, 14);
      growthPixels++;
    }
  }
  
  WriterType::Pointer writer = WriterType::New();
  writer->SetInput(changesLabel);
  writer->SetFileName(outputVolume.c_str());
  writer->Update();

  if(reportFileName != ""){
    ImageType::SpacingType s = changesLabel->GetSpacing();
    float sv = s[0]*s[1]*s[2];
    std::ofstream rep(reportFileName.c_str());
    rep << "Growth: " << growthPixels*sv << " mm^3 (" << growthPixels << " pixels) " << std::endl;
    rep << "Shrinkage: " << shrinkPixels*sv << " mm^3 (" << shrinkPixels << " pixels) " << std::endl;
    rep << "Total: " << (growthPixels-shrinkPixels)*sv << " mm^3 (" << growthPixels-shrinkPixels << " pixels) " << std::endl;
  }
  
  return EXIT_SUCCESS;
}
