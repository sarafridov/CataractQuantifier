# CataractQuantifier
Quantify the severity and extent of the cataract in a photo of a rat eye.

### Preliminaries
CataractQuantifier provides (nearly identical) versions for Mac and Windows machines (disclaimer: the Windows version is untested). Below is documentation for using CataractQuantifier in either context.

CataractQuantifier is in preparation for publication, along with empirical statistical analysis of its consistency in quantifying rat cataracts. This page will be updated upon publication.

### Taking Photographs
To ensure high-quality, consistent data, all photographs should be taken in the same way. We recommend the following procedure:
- Hold the rat inside a dark box to block extraneous light sources
- Take photos using the same digital camera, with the same settings each time
- Use a fast shutter speed to minimize motion blur
- Use the camera flash to ensure adequate, consistent lighting
- Zoom and focus on the rat's eye, with the same amount of zoom in each photo

### Preparing Photographs for CataractQuantifier
Import all photographs as .png files to a computer, and place them in the same folder. Make a copy of each image with .shaded appended to the end of the filename. The file structure should be as follows, where you can include as many photos as you want in photo_folder:

cataract_quantifier_[mac/windows].py  
photo_folder>  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;photo1.png  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;photo1.shaded.png  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;photo2.png  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;photo2.shaded.png  

The next step is to edit each of the photo.shaded.png files to show CataractQuantifier where the lens and sclera are. The relevant portions of an example photo (without a cataract) are illustrated here: ![alt text](https://github.com/sarafridov/CataractQuantifier/tree/master/images/unshaded_labeled.png).

[This documentation is a work in progress.]