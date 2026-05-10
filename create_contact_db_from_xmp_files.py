'''
Create a database with files names and their contact extracted from their XMP data
'''

import argparse
import os
import logging
from pathlib import Path
import re
from tinydb import TinyDB, Query
from libxmp import XMPFiles, XMPMeta, XMPError
from libxmp.utils import file_to_dict, object_to_dict
from libxmp.consts import XMP_ITERATOR_OPTIONS, XMP_SKIP_OPTIONS
from libxmp.consts import XMP_NS_XMP as NS_XAP
from libxmp.consts import XMP_NS_CC as NS_CC
from libxmp.consts import XMP_NS_DC as NS_DC
from libxmp.consts import XMP_NS_EXIF as NS_EXIF
from libxmp.consts import XMP_NS_TIFF as NS_TIFF
from libxmp.consts import XMP_NS_CameraRaw as NS_CAMERA_RAW_SETTINGS
from libxmp.consts import XMP_NS_Photoshop as NS_PHOTOSHOP
from libxmp import utils

os.makedirs("log", exist_ok=True)
os.makedirs("output", exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--images-path", help="Images base path", required=True)
parser.add_argument("-d", "--database-name", help="Database file name", required=True)
parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
args = parser.parse_args()

logger = logging.getLogger("create_contact_db_from_xmp_files")
logger.setLevel(logging.DEBUG)
logger.handlers = []
logger.propagate = False
console_hdlr = logging.StreamHandler()
console_hdlr.setLevel(logging.WARNING)
if args.verbose:
    console_hdlr.setLevel(logging.INFO)
logger.addHandler(console_hdlr)
loghdlr = logging.FileHandler('log/create_contact_db_from_xmp_files.log', mode='w', encoding = "utf-8")
loghdlr.setFormatter(
    logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s'))
loghdlr.setLevel(logging.INFO)
if args.verbose:
    loghdlr.setLevel(logging.DEBUG)
logger.addHandler(loghdlr)


base_path = args.images_path
bd_file_name = os.path.join("output", f"{args.database_name}.json")
if os.path.exists(bd_file_name):
  os.remove(bd_file_name)
bd_stars_file_name = os.path.join("output", f"{args.database_name}_stars.json")
if os.path.exists(bd_stars_file_name):
  os.remove(bd_stars_file_name)
db = TinyDB(bd_file_name, indent=4, encoding='utf-8', ensure_ascii=False)
table = db.table('files')
db_stars = TinyDB(bd_stars_file_name, indent=4)
table_stars = db_stars.table('files')
pattern_sample = re.compile('.*(JPG|jpg|JPEG|jpeg)$')
XMPMeta.register_namespace("http://ns.adobe.com/lightroom/1.0/", "lr")
for file_path in Path(base_path).rglob('*'):
    if os.path.isdir(file_path):
        logger.info("Parse pictures in '%s' folder", file_path)
        continue
    match = pattern_sample.match(str(file_path))
    if match:
        is_favorite_label = False
        logger.info("Parse matched picture file '%s'", file_path)
        try:
            xmpfile = XMPFiles( file_path=str(file_path), open_forupdate=False )
        except AttributeError as attrib_err:
            logger.debug("NO 'XMP' data found}!\n%s", attrib_err)
            continue
        try:
            xmp = xmpfile.get_xmp()
        except XMPError as xmp_error:
            logger.debug("Can't get XMP data!\n%s", xmp_error)
            continue
        if not xmp:
            logger.info("NO 'XMP' data found!")
            continue
        try:
            date_time_original = xmp.get_property(NS_EXIF, "DateTimeOriginal")
            logger.debug('DateTimeOriginal: %s', date_time_original)
        except XMPError as xmp_error:
            logger.debug("NO 'DateTimeOriginal' property found!")
            date_time_original = "NO"
        except AttributeError as attr_error:
            logger.debug("NO 'DateTimeOriginal' property found!")
            date_time_original = "NO"
        try:
            rating = xmp.get_property(NS_XAP, "Rating")
            logger.debug("Rating: %s", rating)
        except XMPError as xmp_error:
            logger.debug("NO 'Rating' property found!")
            rating = "NO"
        file_subjects = []
        try:
            subject_items_nb = xmp.count_array_items('http://purl.org/dc/elements/1.1/', 'subject')
            for idx in range(1, subject_items_nb+1):
                subject_item = xmp.get_array_item('http://purl.org/dc/elements/1.1/', 'subject',idx)
                logger.debug("XMP subject item number %s: %s(%s)", idx, subject_item, type(subject_item))
                file_subjects.append(subject_item)
        except XMPError as xmp_error:
            logger.debug("NO 'subject' property found!")
            file_subjects = []
        file_hiera_subjects = []
        try:
            hiera_subject_items_nb = xmp.count_array_items('http://ns.adobe.com/lightroom/1.0/', 'hierarchicalSubject')
            for idx in range(1, hiera_subject_items_nb+1):
                hiera_subject_item = xmp.get_array_item('http://ns.adobe.com/lightroom/1.0/', 'hierarchicalSubject', idx)
                logger.debug("XMP hierarchy subject item number %s: hierarchy %s(%s)", idx, hiera_subject_item, type(hiera_subject_item))
                file_hiera_subjects.append(subject_item)
        except XMPError as xmp_error:
            logger.debug("NO 'hierarchy subject' property found!")
            file_hiera_subjects = []
        try:
            label = xmp.get_property(NS_XAP, "Label")
            logger.debug("Label: '%s'", label)
            if label == "Yellow":
                is_favorite_label = True
        except XMPError as xmp_error:
            logger.debug("NO 'Label' property found!")
            pass
        xmpfile.close_file()
        # db.insert({'file_name': str(file_path), 'rating': rating, 'contacts': file_subjects, 'contacts hierarchy': file_hiera_subjects })
        table.insert({'file_name': str(file_path), 'rating': rating, 'contacts': file_subjects, 'contacts hierarchy': file_hiera_subjects })
        if is_favorite_label:
            # db_stars.insert({'file_name': str(file_path), 'rating': rating, 'contacts': file_subjects, 'contacts hierarchy': file_hiera_subjects })
            table_stars.insert({'file_name': str(file_path), 'rating': rating, 'contacts': file_subjects, 'contacts hierarchy': file_hiera_subjects })