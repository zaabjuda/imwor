Imwor
=====

Setup
=====

Dependencies
------------


Install
-------


To see a list of all available options, run

::

    $ python -m imwor.app --help
    Usage: imwor/app.py [OPTIONS]



Calling
=======

To use the image processing service, include the application url as you would any other image. E.g. this image url

::

    <img src="http://pbs.twimg.com/media/CUUkKBDXIAAUm5X.jpg" />

Would be replaced with this image url

::

    <img src="http://localhost:9999/?url=http://pbs.twimg.com/media/CUUkKBDXIAAUm5X.jpg&w=300&h=300&mode=crop" />

This will request the image served at the supplied url and resize it to ``300x300`` using the ``crop`` mode.
The below is the list of parameters that can be supplied to the service.

General Parameters
------------------

-  *url*: The url of the image to be resized
-  *op*: The operation to perform: noop, region, resize (default), rotate

   -  *noop*: No operation is performed, image is returned as it is received
   -  *region*: Select a sub-region from the image
   -  *resize*: Resize the image
   -  *rotate*: Rotate the image

-  *fmt*: The output format to save as, defaults to the source format

   -  *gif*: Save as GIF
   -  *jpeg*: Save as JPEG
   -  *png*: Save as PNG
   -  *webp*: Save as WebP

-  *opt*: The output should be optimized, only relevant to JPEGs and PNGs
-  *exif*: Keep original `Exif <http://en.wikipedia.org/wiki/Exchangeable_image_file_format>`_ data in the processed
           image, only relevant for JPEG
-  *prog*: Enable progressive output, only relevant to JPEGs
-  *q*: The quality, (1-99) or keep, used to save the image, only relevant to JPEGs

Resize Parameters
-----------------

-  *w*: The desired width of the image
-  *h*: The desired height of the image
-  *mode*: The resizing method: adapt, clip, crop (default), fill and scale

   -  *adapt*: Resize using crop if the resized image retains a supplied percentage of the original image; otherwise
               fill
   -  *clip*: Resize to fit within the desired region, keeping aspect ratio
   -  *crop*: Resize so one dimension fits within region, center, cut remaining
   -  *fill*: Fills the clipped space with a background color
   -  *scale*: Resize to fit within the desired region, ignoring aspect ratio

-  *bg*: Background color used with fill mode (RGB or ARGB)

   -  *RGB*: 3- or 6-digit hexadecimal number
   -  *ARGB*: 4- or 8-digit hexadecimal number, only relevant for PNG images

-  *filter*: The filtering algorithm used for resizing

   -  *nearest*: Fastest, but often images appear pixelated
   -  *bilinear*: Faster, can produce acceptable results
   -  *bicubic*: Fast, can produce acceptable results
   -  *antialias*: Slower, produces the best results

-  *pos*: The crop position

   -  *top-left*: Crop from the top left
   -  *top*: Crop from the top center
   -  *top-right*: Crop from the top right
   -  *left*: Crop from the center left
   -  *center*: Crop from the center
   -  *right*: Crop from the center right
   -  *bottom-left*: Crop from the bottom left
   -  *bottom*: Crop from the bottom center
   -  *bottom-right*: Crop from the bottom right
   -  *face*: Identify faces and crop from the midpoint of their position(s)
   -  *x,y*: Custom center point position ratio, e.g. 0.0,0.75

-  *retain*: The minimum percentage (1-99) of the original image that must still be visible in the resized image in
             order to use crop mode


Region Parameters
-----------------

-  *rect*: The region as x,y,w,h; x,y: top-left position, w,h: width/height of region

Rotate Parameters
-----------------

-  *deg*: The desired rotation angle degrees

   - *0-359*: The number of degrees to rotate (clockwise)
   - *auto*: Auto rotation based on Exif orientation, only relevant to JPEGs

-  *expand*: Expand the size to include the full rotated image


Examples
========

The following images show the various resizing modes in action for original image size of ``640x428`` that is being
resized to ``500x400``.

Adapt
-----

The adaptive resize mode combines both `crop`_ and `fill`_ resize modes to ensure that the image always matches the
requested size and a minimum percentage of the image is always visible. Adaptive resizing will first calculate how much
of the image will be retained if crop is used. Then, if that percentage is equal to or above the requested minimum
retained percentage, crop mode will be used. If it is not, fill will be used. The first figure uses a ``retain``
value of ``80`` to illustrate the adaptve crop behavior.

Clip
----

Crop
----

The image is resized so that one dimension fits within the ``500x400`` box. It is then centered and the excess is cut
from the image. Cropping is useful when the position of the subject is known and the image must be exactly the supplied
size.


Fill
----

Similar to clip, fill resizes the image to fit within a ``500x400`` box. Once clipped, the image is centered within the
box and all left over space is filled with the supplied background color. Filling is useful when no portion of the
image can be lost and it must be exactly the supplied size.


Scale
-----

The image is clipped to fit within the ``500x400`` box and then stretched to fill the excess space. Scaling is often
not useful in production environments as it generally produces poor quality images. This mode is largely included for
completeness.


Testing
=======

To run all tests, issue the following command

::

    $ py.test



Configuration
=============

All options that can be supplied to the application via the command line, can also be specified in the configuration
file. Configuration files are simply python files that define the options as variables. The below is an example
configuration.

::

    # General settings
    port = 8888

    # Set the allowed hosts as an alternative to signed requests. Only those
    # images which are served from the following hosts will be requested.
    allowed_hosts = ["localhost"]

    # Request-related settings
    max_requests = 50
    timeout = 7.5

    # Set default resizing options
    background = "ccc"
    filter = "bilinear"
    mode = "crop"
    position = "top"

    # Set default rotating options
    expand = False

    # Set default saving options
    format = None
    optimize = 1
    quality = "90"


If a new mode is added or a modification was made to the libraries that would change the current expected output for
tests, run the generate test command to regenerate the expected output for the test cases.

::

    $ python -m imwor.test.genexpected

Deploying
=========

The application itself does not include any caching. It is recommended that the application run behind a CDN for
larger applications.

Defaults for the application have been optimized for quality rather than performance. If you wish to get higher
performance out of the application, it is recommended you use a less computationally expensive filtering algorithm and
a lower JPEG quality. For example, add the following to the configuration.

::

    # Set default resizing options
    filter = "bicubic"
    quality = 75


