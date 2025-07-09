import os
import re
from pathlib import Path
import argparse
import json
import logging
import logging.config
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

logger = logging.getLogger("handle_xmp_files")
logger.setLevel(logging.DEBUG)
logger.handlers = []
logger.propagate = False
console_hdlr = logging.StreamHandler()
console_hdlr.setLevel(logging.INFO)
logger.addHandler(console_hdlr)
loghdlr = logging.FileHandler('log/handle_xmp_files.log', mode='w', encoding = "utf-8")
loghdlr.setFormatter(
    logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s'))
loghdlr.setLevel(logging.DEBUG)
logger.addHandler(loghdlr)

base_path = r"/mnt/e/Users/Public/Pictures/Perso"
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder-path", help="Folder path")
parser.add_argument("-r", "--rule", choices=['and', 'or'], help="rule to apply")
parser.add_argument("-c", "--contacts", help="contact list")
parser.add_argument("-e", "--exclude", help="contact list to exclude")
parser.add_argument("--contacts_file", help="contacts list in a file")
parser.add_argument("-o", "--output", help="SlideShow output file")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="increase output verbosity")
args = parser.parse_args()
# if args.verbose:
#     for handler in logger.handlers[:]:
#         handler.setLevel(logging.DEBUG)
if args.folder_path:
    base_path = args.folder_path
if args.rule:
    if not args.contacts and not args.contacts_file:
        parser.error("rule requires --contacts or --contacts_file")
contacts = []
if args.contacts:
    if not args.rule:
        parser.error("rule requires --rule")
    contacts = args.contacts.split(',')
exclude_contacts = []
if args.exclude:
    if not args.rule:
        parser.error("rule requires --rule")
    exclude_contacts = args.exclude.split(',')
if not contacts and not exclude_contacts and args.contacts_file:
    with open(args.contacts_file, 'r', encoding="utf-8") as contacts_file:
        contacts_status = json.load(contacts_file)
    for included_contact in contacts_status["include"]:
        logger.debug("Include contact: '%s'", included_contact)
        contacts.append(included_contact)
    for excluded_contact in contacts_status["exclude"]:
        logger.debug("Exclude contact: '%s'", excluded_contact)
        exclude_contacts.append(excluded_contact)
sld_file_name = os.path.join("output", "star.sld")
sld_all_file_name = os.path.join("output", "all.sld")
if args.output:
    sld_file_name = os.path.join("output", f"{args.output}_star.sld")
    sld_all_file_name = os.path.join("output", f"{args.output}_all.sld")
with open(sld_file_name, 'w', encoding="utf-8") as sld_file:
    sld_file.write("# Slide Show Sequence v2\n")
    sld_file.write(f"# contacts: {contacts}\n")
    sld_file.write(f"# exclude_contacts: {exclude_contacts}\n")
with open(sld_all_file_name, 'w', encoding="utf-8") as sld_all_file:
    sld_all_file.write("# Slide Show Sequence v2\n")
    sld_all_file.write(f"# contacts: {contacts}\n")
    sld_all_file.write(f"# exclude_contacts: {exclude_contacts}\n")
favorite_file_names = []
all_file_names = []
other_label_file_names = []
pattern_sample = re.compile('.*(JPG|jpg|JPEG|jpeg)$')
contacts_set = set(contacts)
exclude_contacts_set = set(exclude_contacts)
for file_path in Path(base_path).rglob('*'):
    if os.path.isdir(file_path):
        logger.debug("Parse pictures in '%s' folder", file_path)
        continue
    match = pattern_sample.match(str(file_path))
    if match:
        is_favorite_label = False
        logger.info(f"Parse matched picture file '{file_path}'")
        try:
            xmpfile = XMPFiles( file_path=str(file_path), open_forupdate=False )
        except AttributeError:
            # logger.info(f"NO 'XMP' data found for file {file_path}!")
            continue
        # print(f"Parse XMP picture file '{file_path}'")
        try:
            xmp = xmpfile.get_xmp()
        except XMPError as xmp_error:
            logger.info(f"Can't get XMP from filefile {file_path}!.\n{xmp_error}")
            continue
        if not xmp:
            # print(f"NO 'XMP' data found for file {file_path}!")
            continue
        try:
            date_time_original = xmp.get_property(NS_EXIF, "DateTimeOriginal")
            # print(f'file: {file_path} DateTimeOriginal: {date_time_original}')
        except XMPError as xmp_error:
            # print(f"NO 'DateTimeOriginal' property found for file {file_path}!")
            date_time_original = "NO"
        except AttributeError as attr_error:
            # print(f"NO 'DateTimeOriginal' property found for file {file_path}!")
            date_time_original = "NO"
        try:
            rating = xmp.get_property(NS_XAP, "Rating")
            # print(f"file: {file_path} Rating: {rating}")
        except XMPError as xmp_error:
            # print(f"NO 'Rating' property found for file {file_path}!")
            rating = "NO"
        file_subjects = []
        try:
            subject_items_nb = xmp.count_array_items('http://purl.org/dc/elements/1.1/', 'subject')
            for idx in range(1, subject_items_nb+1):
                subject_item = xmp.get_array_item('http://purl.org/dc/elements/1.1/', 'subject',idx)
                # print(f"XMP subject item number {idx}: {subject_item}({type(subject_item)})")
                file_subjects.append(subject_item)
        except XMPError as xmp_error:
            # print(f"NO 'subject' property found for file {file_path}!")
            file_subjects = []
        try:
            label = xmp.get_property(NS_XAP, "Label")
            logger.debug(   f"Label: '{label}' - Rating: '{rating}' - DateTimeOriginal: '{date_time_original}' " \
                            f"- Subjects: {file_subjects}")
            if label == "Yellow":
                is_favorite_label = True
                if args.rule == "and":
                    file_subjects_set = set(file_subjects)
                    # contacts_set = set(contacts)
                    if contacts_set.issubset(file_subjects) and not file_subjects_set.intersection(exclude_contacts_set):
                        sld_file_path = str(file_path).replace(str(base_path), "").replace("/", "\\")[1:]
                        logger.info("Add to favorites and all slideshows")
                        favorite_file_names.append(sld_file_path)
                        all_file_names.append(sld_file_path)
                if args.rule == "or":
                    file_subjects_set = set(file_subjects)
                    # contacts_set = set(contacts)
                    if file_subjects_set.intersection(contacts_set) and not file_subjects_set.intersection(exclude_contacts_set):
                        sld_file_path = str(file_path).replace(str(base_path), "").replace("/", "\\")[1:]
                        logger.info("Add to favorites and all slideshows")
                        favorite_file_names.append(sld_file_path)
                        all_file_names.append(sld_file_path)
                if not args.rule:
                    sld_file_path = str(file_path).replace(str(base_path), "").replace("/", "\\")[1:]
                    logger.info("Add to favorites and all slideshows")
                    favorite_file_names.append(sld_file_path)
                    all_file_names.append(sld_file_path)

        except XMPError as xmp_error:
            logger.info("NO 'Label' property found!")
            pass
        xmpfile.close_file()
        if not is_favorite_label:
            if args.rule == "and":
                file_subjects_set = set(file_subjects)
                # contacts_set = set(contacts)
                if contacts_set.issubset(file_subjects) and not file_subjects_set.intersection(exclude_contacts_set):
                    logger.info("Add to all slideshows")
                    sld_file_path = str(file_path).replace(str(base_path), "").replace("/", "\\")[1:]
                    all_file_names.append(sld_file_path)
            if args.rule == "or":
                file_subjects_set = set(file_subjects)
                # contacts_set = set(contacts)
                if file_subjects_set.intersection(contacts_set) and not file_subjects_set.intersection(exclude_contacts_set):
                    logger.info("Add to all slideshows")
                    sld_file_path = str(file_path).replace(str(base_path), "").replace("/", "\\")[1:]
                    all_file_names.append(sld_file_path)
            if not args.rule:
                logger.info("Add to all slideshows")
                sld_file_path = str(file_path).replace(str(base_path), "").replace("/", "\\")[1:]
                all_file_names.append(sld_file_path)
    else:
        logger.debug(f"Picture file '{str(file_path)}' does not math pattern '.*(JPG|jpg|JPEG|jpeg)$'")
with open(sld_file_name, 'a', encoding="utf-8") as sld_file:
    for favorite_file_name in favorite_file_names:
        sld_file.write(f"\"{favorite_file_name}\"\n")
with open(sld_all_file_name, 'a', encoding="utf-8") as sld_all_file:
    for all_file_name in all_file_names:
        sld_all_file.write(f"\"{all_file_name}\"\n")