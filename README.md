This program implements 2 methods of interpolation to be used for demosaicing a bayer image. First, the image is imported into the program as a png. it is then converted into a numpy array in order to be useful for image processing. the mosaic being used for these images in bggr format. this mosaic is created using a nested for loop which iterates through all of the pixels in the image. This Mosaic can be seen in the following image.
![image](https://github.com/EricJ48/CompVisionDemosaicing/assets/130092346/57e87974-6513-4897-991f-c5d874d9d981)
For bilinear interpolation, the value of a single channel of an unknown pixel is determined by taking the average of the pixels immediate neighbors of the same channel. Since green pixels are twice as common as red or blue pixels in the bggr mosaic, finding the value of the green channel involves taking the average of the four immediately adjacent pixels. For red and blue, the cross diagonal (corner) pixels are also taken into account. By determining the value of each channel for the missing pixels and replacing the missing pixels with the new average pixels, a color image is created

![peppersBayer](https://github.com/EricJ48/CompVisionDemosaicing/assets/130092346/3c648156-f170-45b9-bd2f-0fb31dc958f1)
The image above is a bayer image of some peppers. When zooming in close, it is obvious that not all of the pixels are accounted for. The image below shows the same image after demosaicing is performed on the bayer image using bilinear interpolation

![PeppersBilinear](https://github.com/EricJ48/CompVisionDemosaicing/assets/130092346/79eccc15-884a-4391-8737-3492938f21ac)
The performance of bilinear interpolation is already quite good given its simplicity. However, the image is not very sharp and some quality is lost in the process. This is where high quality linear interpolation comes into play. The following paper outlines a improvment on bilinear interpolation which addresses some of the shortcomings of bilinear interpolation: https://stanford.edu/class/ee367/reading/Demosaicing_ICASSP04.pdf



