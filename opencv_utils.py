#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

import os
import tempfile

import requests
from opencv.cv import (CV_BGR2GRAY, CV_GAUSSIAN, CV_HAAR_DO_CANNY_PRUNING,
                       cvCreateImage, cvCvtColor, cvSize, cvSmooth,
                       cvCreateMemStorage, cvClearMemStorage,
                       cvEqualizeHist,
                       cvLoadHaarClassifierCascade,
                       cvHaarDetectObjects)
from opencv.highgui import cvLoadImage

HAAR_SCALE = 1.1
HAAR_NEIGHBORS = 2


def download_url(url):
    req = requests.get(url)
    ext = url.rsplit('.')[0]
    f = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    f.write(req.content)
    f.close()
    return f.name


def process_url(url):
    path = download_url(url)
    faces = detect_faces_on(path)
    record_faces(faces)
    delete_path(path)


def detect_faces_on(path):
    faces = []
    image = cvLoadImage(path)
    # convert to grayscale for faster results
    grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
    cvCvtColor(image, grayscale, CV_BGR2GRAY)
    # smooth picture for better results
    cvSmooth(grayscale, grayscale, CV_GAUSSIAN, 3, 3)

    storage = cvCreateMemStorage(0)
    cvClearMemStorage(storage)
    cvEqualizeHist(grayscale, grayscale)

    cascade_files = [
                     # ('/usr/share/opencv/haarcascades/haarcascade_eye_tree_eyeglasses.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_frontalface_alt.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_lowerbody.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_mcs_mouth.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_profileface.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_eye.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_mcs_eyepair_big.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_mcs_nose.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_righteye_2splits.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_frontalface_alt2.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_fullbody.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_mcs_eyepair_small.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_mcs_righteye.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_upperbody.xml', (50, 50)),
                     ('/usr/share/opencv/haarcascades/haarcascade_frontalface_alt_tree.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_lefteye_2splits.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_mcs_lefteye.xml', (50, 50)),
                     # ('/usr/share/opencv/haarcascades/haarcascade_mcs_upperbody.xml', (50, 50)),
                     # ('parojos_22_5.1.xml', (22, 5)),
                     # ('Mouth.xml', (22, 15)),
                    ]

    for cascade_file, cascade_sizes in cascade_files:
        cascade = cvLoadHaarClassifierCascade(os.path.join(cascade_file), cvSize(1, 1))
        faces += cvHaarDetectObjects(grayscale, cascade, storage, HAAR_SCALE, HAAR_NEIGHBORS, CV_HAAR_DO_CANNY_PRUNING, cvSize(*cascade_sizes))

    return [{'x': f.x, 'y': f.y, 'w': f.width, 'h': f.height} for f in faces]


def record_faces(faces):

    return


def delete_path(path):
    try:
        return os.remove(path)
    except OSError:
        return False


if __name__ == '__main__':
    import sys
    from subprocess import call

    infile = sys.argv[1]
    faces = detect_faces_on(infile)
    if not faces:
        sys.exit()

    outfile = "/var/www/yeleman.com/pub/%s_faced.jpg" % infile
    call("cp %s %s" % (infile, outfile), shell=True)
    for face in faces:
        data = {'outfile': outfile,
                'x': face['x'],
                'y': face['y'],
                'xwidth': face['x'] + face['w'],
                'yheight': face['y'] + face['h']
                }
        print(data)
        call('convert %(outfile)s -stroke red -fill none -draw "rectangle %(x)d,%(y)d %(xwidth)d,%(yheight)d" %(outfile)s' % data, shell=True)
