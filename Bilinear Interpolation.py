import numpy as np
from PIL import Image

base = Image.open("./images/peppersBayer.png") #file imput for bayer image
color = Image.open("./ColorImages/peppers.png") #file input for color image

#function used for finding pixel value of a red or blue pixel located at a green pixel on the mosaic map
#the coefficients used for the pixels in the main and opposite maps are found in the high quality linear interpolatino paper
def red_or_blue_at_green(bi_pixel, rgb, x_pixel, y_pixel, pixel, mappixel, gradient_weight):
    width = rgb.shape[0]
    height = rgb.shape[1]
    main = rgb[:,:, pixel] #main channel is based on channel of provided pixel
    opposite = rgb[:, :, mappixel] #opposite channel is based on mosaic map location of provided pixel
    value = bi_pixel #initial value is the bilinear interpolated pixel
    if x_pixel - 2 >= 0 and x_pixel + 2 < width and y_pixel - 2 >= 0 and y_pixel + 2 < height:
        #horizontal pattern
        if main[x_pixel - 1, y_pixel] != -1 and main[x_pixel + 1, y_pixel] != -1:
            mainchannel = 4 * (main[x_pixel - 1, y_pixel] + main[x_pixel + 1, y_pixel])
            oppositechannel = (5 * opposite[x_pixel, y_pixel] + 0.5 * (opposite[x_pixel, y_pixel - 2] + opposite[x_pixel, y_pixel + 2])
                               - (opposite[x_pixel - 1, y_pixel - 1] + opposite[x_pixel - 1, y_pixel + 1] +
                                  opposite[x_pixel + 1, y_pixel + 1] + opposite[x_pixel + 1, y_pixel - 1] +
                                  opposite[x_pixel - 2, y_pixel] + opposite[x_pixel + 2, y_pixel]))
        #verticle pattern
        elif main[x_pixel, y_pixel - 1] != -1 and main[x_pixel, y_pixel + 1] != -1:
            mainchannel = 4 * (main[x_pixel, y_pixel - 1] + main[x_pixel, y_pixel + 1])
            oppositechannel = (5 * opposite[x_pixel, y_pixel] + 0.5 * (opposite[x_pixel - 2, y_pixel] + opposite[x_pixel - 2, y_pixel])
                               - (opposite[x_pixel - 1, y_pixel - 1] + opposite[x_pixel - 1, y_pixel + 1] +
                                  opposite[x_pixel + 1, y_pixel + 1] + opposite[x_pixel + 1, y_pixel - 1] +
                                  opposite[x_pixel, y_pixel - 2] + opposite[x_pixel, y_pixel + 2]))
        value = (mainchannel + (gradient_weight * oppositechannel)) / 8
    return value

#function used for finding pixel value of a green pixel located at a red or blue pixel on the mosaic map
#the coefficients used for the pixels in the main and opposite maps are found in the high quality linear interpolatino paper
def green_at_red_or_blue(bi_pixel, rgb, x_pixel, y_pixel, pixel, mappixel, gradient_weight):
    width = rgb.shape[0]
    height = rgb.shape[1]
    main = rgb[:, :, pixel] #main channel is based on channel of provided pixel
    opposite = rgb[:, :, mappixel] #opposite channel is based on mosaic map location of provided pixel
    value = bi_pixel #initial value is the bilinear interpolated pixel
    if x_pixel - 2 >= 0 and x_pixel + 2 < width and y_pixel - 2 >= 0 and y_pixel + 2 < height:
        mainchannel = 2 * (main[x_pixel + 1, y_pixel] + main[x_pixel - 1, y_pixel] + main[x_pixel, y_pixel + 1] + main[x_pixel, y_pixel -1])
        oppositechannel = 4 * opposite[x_pixel, y_pixel] - (opposite[x_pixel + 2, y_pixel] + opposite[x_pixel - 2, y_pixel] + opposite[x_pixel, y_pixel + 2] + opposite[x_pixel, y_pixel - 2])
        value = (mainchannel + (gradient_weight * oppositechannel))/8
    return value

#function used for finding the pixel value of a red or blue pixel located at the opposite color on the mosaic map
#the coefficients used for the pixels in the main and opposite maps are found in the high quality linear interpolatino paper
def red_or_blue_at_each_other(bi_pixel, rgb, x_pixel, y_pixel, pixel, mappixel, gradient_weight):
    width = rgb.shape[0]
    height = rgb.shape[1]
    main = rgb[:, :, pixel] #main channel is based on channel of provided pixel
    opposite = rgb[:, :, mappixel] #opposite channel is based on mosaic map location of provided pixel
    value = bi_pixel #initial value is the bilinear interpolated pixel
    if x_pixel - 2 >= 0 and x_pixel + 2 < width and y_pixel - 2 >= 0 and y_pixel + 2 < height:
        mainchannel = 2 * (main[x_pixel + 1, y_pixel + 1] + main[x_pixel + 1, y_pixel - 1] +
                           main[x_pixel - 1, y_pixel - 1] + main[x_pixel - 1, y_pixel + 1])
        oppositechannel = 6 * opposite[x_pixel, y_pixel] - (3/2) * (opposite[x_pixel - 2, y_pixel] + opposite[x_pixel + 2, y_pixel] + opposite[x_pixel, y_pixel + 2] + opposite[x_pixel, y_pixel - 2])
        value = (mainchannel + (gradient_weight * oppositechannel)) / 8

    return value

def bilinear_interpolation(rgb, x_pixel, y_pixel, channel):
    Red = 0
    Green = 1
    Blue = 2

    width = rgb.shape[0]
    height = rgb.shape[1]
    adjacent_pixels = []

    #for green pixels, the directly adjacent pixels are averaged
    if channel == Green:
        if x_pixel - 1 >= 0 and rgb[x_pixel - 1, y_pixel, channel] != -1:
            adjacent_pixels.append(rgb[x_pixel - 1, y_pixel, channel])
        if x_pixel + 1 < width and rgb[x_pixel + 1, y_pixel, channel] != -1:
            adjacent_pixels.append(rgb[x_pixel + 1, y_pixel, channel])
        if y_pixel - 1 >= 0 and rgb[x_pixel, y_pixel - 1, channel] != -1:
            adjacent_pixels.append(rgb[x_pixel, y_pixel - 1, channel])
        if y_pixel + 1 < height and rgb[x_pixel, y_pixel + 1, channel] != -1:
            adjacent_pixels.append(rgb[x_pixel, y_pixel + 1, channel])
        average = sum(adjacent_pixels) / len(adjacent_pixels)

    #for blue or red pixels, the cross diagonol (corner) pixels are also averaged
    elif channel == Blue or channel == Red:

        if x_pixel - 1 >= 0 and y_pixel - 1 >= 0 and rgb[x_pixel - 1, y_pixel - 1, channel] != -1:  # (-1,-1)
            adjacent_pixels.append(rgb[x_pixel - 1, y_pixel - 1, channel])
        if x_pixel - 1 >= 0 and y_pixel + 1 < height and rgb[x_pixel - 1, y_pixel + 1, channel] != -1:  # (-1,+1)
            adjacent_pixels.append(rgb[x_pixel - 1, y_pixel + 1, channel])
        if x_pixel + 1 < width and y_pixel + 1 < height and rgb[x_pixel + 1, y_pixel + 1, channel] != -1:  # (+1,+1)
            adjacent_pixels.append(rgb[x_pixel + 1, y_pixel + 1, channel])
        if x_pixel + 1 < width and y_pixel - 1 >= 0 and rgb[x_pixel + 1, y_pixel - 1, channel] != -1:  # (+1,-1)
            adjacent_pixels.append(rgb[x_pixel + 1, y_pixel - 1, channel])

        if x_pixel - 1 >= 0  and rgb[x_pixel - 1, y_pixel, channel] != -1:
            adjacent_pixels.append(rgb[x_pixel - 1, y_pixel, channel])
        if x_pixel + 1 < width and rgb[x_pixel + 1, y_pixel, channel] != -1:
            adjacent_pixels.append(rgb[x_pixel + 1, y_pixel, channel])
        if y_pixel - 1 >= 0 and rgb[x_pixel, y_pixel - 1, channel] != -1:
            adjacent_pixels.append(rgb[x_pixel, y_pixel - 1, channel])
        if y_pixel + 1 < height and rgb[x_pixel, y_pixel + 1, channel] != -1:
            adjacent_pixels.append(rgb[x_pixel, y_pixel + 1, channel])
        if(len(adjacent_pixels)>0):
            average = sum(adjacent_pixels) // len(adjacent_pixels)
        else:
            average = 0

    else:
        average = 0

    return average

def hqlinearinterpolation(bi_pixel, rgb, x_pixel, y_pixel, channel, rgb_map):
    Red = 0
    Green = 1
    Blue = 2
    weights = [0.5, 0.625, 0.75] #predefined weights from paper
    pixel = channel
    mappixel = int(rgb_map[x_pixel, y_pixel])
    gradient_weight = weights[mappixel] #selects weight based on map pixel
    value = 0
    if pixel == Green and  (mappixel == Blue or mappixel == Red): #if channel is green at a red or blue map pixel
        value = green_at_red_or_blue(bi_pixel, rgb, x_pixel, y_pixel, pixel, mappixel, gradient_weight)
    elif (pixel == Red or pixel == Blue) and mappixel == Green: #if channel is red or blue at green map pixel
        value = red_or_blue_at_green(bi_pixel, rgb, x_pixel, y_pixel, pixel, mappixel, gradient_weight)
    elif (pixel == Red and mappixel == Blue) or (pixel == Blue and mappixel == Red): #if channel is blue or red and map pixel is opposite
        value = red_or_blue_at_each_other(bi_pixel, rgb, x_pixel, y_pixel, pixel, mappixel, gradient_weight)

    #checks and correct for out of bound pixel values
    if value < 0:
        value = 0
    elif value > 255:
        value = 255
    return value

def demosaicing(base):
    base = np.asarray(base) #convert base from png to nparray
    Red = 0
    Green = 1
    Blue = 2
    rgb = np.zeros([base.shape[0], base.shape[1], 3]) - 1 #create array for image with 3 channels for red, green, and blue
    rgb_map = np.zeros([base.shape[0], base.shape[1]]) #create array for rgb mosaic/map
    for x_pixel in (range(0, rgb.shape[0], 2)):
        for y_pixel in (range(0, rgb.shape[1], 2)): #nested for loop responsible for setting up bggr mosaic
            rgb[x_pixel, y_pixel, Blue] = base[x_pixel, y_pixel]
            rgb_map[x_pixel, y_pixel] = Blue

            if x_pixel + 1 < rgb.shape[0]:
                rgb[x_pixel + 1, y_pixel, Green] = base[x_pixel + 1, y_pixel]
                rgb_map[x_pixel + 1, y_pixel] = Green
            if y_pixel + 1 < rgb.shape[1]:
                rgb[x_pixel, y_pixel + 1, Green] = base[x_pixel, y_pixel + 1]
                rgb_map[x_pixel, y_pixel + 1] = Green
            if x_pixel + 1 < rgb.shape[0] and y_pixel + 1 < rgb.shape[1]:
                rgb[x_pixel + 1, y_pixel + 1, Red] = base[x_pixel + 1, y_pixel + 1]
                rgb_map[x_pixel + 1, y_pixel + 1] = Red

    rgb_improved = rgb.copy() #copies of rgb array to be used for high quality interpolation
    rgb_original = rgb.copy()

    for x_pixel in range(rgb.shape[0]): #width
        for y_pixel in range(rgb.shape[1]): #height
            for channel in range(rgb.shape[2]): #channel
                if(rgb[x_pixel, y_pixel, channel] == -1): #only fills in blank pixels
                    bi_pixel = bilinear_interpolation(rgb, x_pixel, y_pixel, channel) #bilinear interpolation performed on pixel
                    rgb[x_pixel, y_pixel, channel] = bi_pixel #pixel value is set to result of bilinear interpolation

                    #result of bilinear interpolation is used for high quality linear interpolation
                    rgb_improved[x_pixel, y_pixel, channel] = hqlinearinterpolation(bi_pixel, rgb_original, x_pixel, y_pixel, channel, rgb_map)

    #Create Images from rgb and rgb_improved arrays
    rgbimg = Image.fromarray(rgb.astype(np.uint8), 'RGB')
    improvedrgbimg = Image.fromarray(rgb_improved.astype(np.uint8), 'RGB')

    #display and save bilinear interpolated image
    rgbimg.show()
    rgbimg.save('Demosaic/Bilinear/PeppersBilinear.png', 'PNG')

    #display and save high quality interpolated image
    improvedrgbimg.show()
    improvedrgbimg.save('Demosaic/HighQuality/PeppersHighQuality.png', 'PNG')
    return rgb, rgb_improved


def error(Bilinear, HighQuality, Color): #error function for demosaicing methods
    Color = np.asarray(Color) #convert color image to nparray

    #calculate Mean Square Error of Bilinear and High Quality Interpolation
    Bilinear_MSE = np.sum(np.square(Color - Bilinear)) / (Color.shape[0] * Color.shape[1])
    HQ_MSE = np.sum(np.square(Color - HighQuality)) / (Color.shape[0] * Color.shape[1])

    #calculate Peak Signal to Noise Ratio of Bilinear and High Quality Interpolation
    Bilinear_PSNR = 10*np.log10(255**2/Bilinear_MSE)
    HQ_PSNR = 10*np.log10(255**2/HQ_MSE)

    #print data
    print('Bilinear Interpolation Data')
    print('MSE:', Bilinear_MSE)
    print('PSNR:', Bilinear_PSNR)
    print('')
    print('High Quality Interpolation Data')
    print('MSE:', HQ_MSE)
    print('PSNR:', HQ_PSNR)

base.show()
Bilinear, HighQuality = demosaicing(base)
error(Bilinear, HighQuality, color)
