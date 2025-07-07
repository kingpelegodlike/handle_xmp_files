import sys
import os
import re
from pathlib import Path
from libxmp import XMPFiles, XMPMeta, XMPError
from libxmp.utils import file_to_dict, object_to_dict
from libxmp.consts import XMP_ITERATOR_OPTIONS, XMP_SKIP_OPTIONS
from libxmp.consts import XMP_NS_XMP as NS_XAP
from libxmp.consts import XMP_NS_CC as NS_CC
from libxmp.consts import XMP_NS_DC as NS_DC
from libxmp.consts import XMP_NS_EXIF as NS_EXIF
from libxmp.consts import XMP_NS_IPTCCore as NS_IPTCCore
from libxmp.consts import XMP_NS_TIFF as NS_TIFF
from libxmp.consts import XMP_NS_CameraRaw as NS_CAMERA_RAW_SETTINGS
from libxmp.consts import XMP_NS_Photoshop as NS_PHOTOSHOP
from libxmp import utils
import xml.etree.ElementTree as ET

if len(sys.argv) < 1:
    print("Usage python <file_path>")
    print("Usage python /mnt/e/Users/Public/Pictures/Perso/file.jpg")
    sys.exit(1)
pattern = '.*(JPG|jpg|JPEG|jpeg)$'
pattern_sample = re.compile(pattern)
file_path = sys.argv[1]
match = pattern_sample.match(str(file_path))
if match:
    print(f"Parse matched picture file '{file_path}'")
    try:
        xmpfile = XMPFiles( file_path=str(file_path), open_forupdate=True )
    except AttributeError:
        print(f"NO 'XMP' data found for file {file_path}!")
        sys.exit(2)
    print(f"Parse XMP picture file '{file_path}'")
    try:
        xmp = xmpfile.get_xmp()
        # print(f"XMP ({type(xmp)})\n{xmp}")
    except XMPError as xmp_error:
        print(f"Can't get XMP from file {file_path}!.\n{xmp_error}")
        sys.exit(3)
    if not xmp:
        print(f"NO 'XMP' data found for file {file_path}!")
        sys.exit(4)
    try:
        date_time_original = xmp.get_property(NS_EXIF, "DateTimeOriginal")
        print(f'DateTimeOriginal: {date_time_original}')
    except XMPError as xmp_error:
        print(f"NO 'DateTimeOriginal' property found for file {file_path}!")
        date_time_original = "NO"
    except AttributeError as attr_error:
        print(f"NO 'DateTimeOriginal' property found for file {file_path}!")
        date_time_original = "NO"
    try:
        rating = xmp.get_property(NS_XAP, "Rating")
        print(f"Rating: {rating}")
    except XMPError as xmp_error:
        print(f"NO 'Rating' property found for file {file_path}!")
        rating = "NO"
    try:
        label = xmp.get_property(NS_XAP, "Label")
        print(f"Label: {label}")
    except XMPError as xmp_error:
        print(f"NO 'Label' property found for file {file_path}!")
    try:
        subjects = xmp.get_property(NS_DC, "subject")
        print(f"Subjects ({type(subjects)}): {subjects}")
    except XMPError as xmp_error:
        print(f"NO 'Subject' property found for file {file_path}!")
    subject_items_nb = xmp.count_array_items('http://purl.org/dc/elements/1.1/', 'subject')
    for idx in range(1, subject_items_nb+1):
        subject_item = xmp.get_array_item('http://purl.org/dc/elements/1.1/', 'subject',idx)
        print(f"XMP subject item number {idx}: {subject_item}({type(subject_item)})")
else:
    print(f"Picture file '{str(file_path)}' does not math pattern '{pattern}'")
    sys.exit(5)