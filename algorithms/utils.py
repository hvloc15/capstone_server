import numpy as np
import cv2
import re
from django.conf import settings
import subprocess


def read_inmemory_image_to_opencv(inmemory_image):
    image_bytestream = inmemory_image.file.read()
    return cv2.imdecode(np.fromstring(image_bytestream, np.uint8), cv2.IMREAD_UNCHANGED)


def read_image(image_name, is_in_media=True):

    if not is_in_media:
        media_dir = '/'.join([settings.BASE_DIR,'media'])
    else:
        media_dir = settings.BASE_DIR

    return cv2.imread(''.join([media_dir, image_name]))


def read_small_part_of_image(image_name, lower, upper):
    image = read_image(image_name)
    return image[upper:lower, :]


def save_image(image, name, is_saved_as_media=False):
    if not is_saved_as_media:
        new_image_name = "/".join(["/media", name + '.png'])
    else:
        new_image_name = name
    cv2.imwrite("/".join([settings.BASE_DIR, new_image_name]), image)
    return new_image_name


def resize_image(image):
    height, width = image.shape[0], image.shape[1]
    factor = min(1, float(1024.0 / width))
    if factor >= 1:
        interpolation = cv2.INTER_AREA
    else:
        interpolation = cv2.INTER_CUBIC
    size = int(factor * width), int(factor * height)
    return cv2.resize(image, size, interpolation=interpolation)


def get_threshold_of_images(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 127, 255,
                           cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return thresh


def text_skew_correction(image, thresh):
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                             flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return rotated


def deshadow(image):
    rgb_planes = cv2.split(image)
    result_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7, 7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        result_planes.append(diff_img)
    result = cv2.merge(result_planes)
    return result


def preprocess_image(image):
    image = deshadow(image)
    image = text_skew_correction(image, get_threshold_of_images(image))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def to_string(arr):
    return " ".join(arr)


def get_lastvalue_newkey(stack, part, is_first):
    if part == "":
        if is_first:
            return "", to_string(stack)
        else:
            new_key = stack.pop()
            return to_string(stack), new_key
    if is_first:
        stack.append(part)
        return "", to_string(stack)
    else:
        return to_string(stack), part


def extract_line(line, separator):
    line = re.sub(r"[\[\(\{\]\)\}]", "", line)
    if line.find(separator) == -1:
        return None
    is_first = True
    dict = {}
    key = None
    stack = []

    line = re.sub(r"(?<![0-9]):", ": ", line)
    line = re.sub(r" +", " ", line)

    substrs = line.split(" ")

    for substr in substrs:
        if substr != "" and substr[-1] == ":":
            substr = substr[:-1]
            lastvalue, newkey = get_lastvalue_newkey(stack, substr, is_first)

            if key is not None:
                dict[key] = lastvalue

            key = newkey
            stack.clear()
            is_first = False
        else:
            stack.append(substr)

    dict[key] = " ".join(stack)
    return dict


def get_text_size(uppers, lowers):
    min_len = min(len(uppers), len(lowers))
    median_text = []
    for i in range(min_len):
        median_text.append(lowers[i] - uppers[i])
    return median_text[min_len // 2]


def filter_lines(uppers, lowers, text_height=40):
    if len(uppers) > len(lowers):
        lowers.append(uppers[-1])
    elif len(uppers) < len(lowers):
        uppers.append(lowers[-1])
    i = 0
    while i < len(lowers) - 1:
        if lowers[i] > uppers[i + 1] and abs(lowers[i] - uppers[i + 1]) < text_height:
            lowers.pop(i)
            uppers.pop(i + 1)
        else:
            i += 1


def get_upper_and_lower_lines(threshed_image, threshold=1, padding_lower=0, padding_upper=0):
    hist = cv2.reduce(threshed_image, 1, cv2.REDUCE_AVG).reshape(-1)
    H, W = threshed_image.shape[:2]
    temp_lowers = [y + padding_lower for y in range(H - 1) if hist[y] > threshold and hist[y + 1] <= threshold]
    temp_uppers = [y + padding_upper for y in range(H - 1) if hist[y] <= threshold and hist[y + 1] > threshold]

    lowers, uppers = [], []
    i = 0
    j = 0

    while i < len(temp_uppers) and j < len(temp_lowers):
        if temp_uppers[i] < temp_lowers[j]:
            uppers.append((temp_uppers[i]))
            lowers.append(temp_lowers[j])
            i += 1
            j += 1
        else:
            j += 1

    while len(uppers) > len(lowers):
        uppers.pop()

    return lowers, uppers


def modify_image_and_detect_bounding_boxes(uploaded_image):
    #image = cv2.cvtColor(uploaded_image, cv2.COLOR_BGR2GRAY)
    image = preprocess_image(uploaded_image)

    ## (2) threshold
    _, threshed_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    threshold = 1

    ## (3) Generated upper and lower lines for the images
    temp_lowers, temp_uppers = get_upper_and_lower_lines(threshed_image)

    ## (4) Try to detect lines again in a region that have multiple lines which are not detected
    min_len = min(len(temp_lowers), len(temp_uppers))

    uppers = []
    lowers = []

    text_height = 40

    for i in range(min_len):
        # if the area contains more than one row, do skew correction in that area and detect lower, upper line again
        if temp_lowers[i] - temp_uppers[i] >= text_height * 2:
            lower, upper = temp_lowers[i] + 5, temp_uppers[i] - 5
            # get the area confined by the upper and lower lines
            portion = threshed_image[upper: lower]
            # do skew correction
            correction = text_skew_correction(portion, portion)
            # do skew correction in real image
            image[upper: lower] = text_skew_correction(image[upper: lower], portion)

            # get new lines
            new_lowers, new_uppers = get_upper_and_lower_lines(correction, threshold, upper + 2, upper - 2)
            lowers += new_lowers
            uppers += new_uppers
        else:
            uppers.append(temp_uppers[i] - 2)
            lowers.append(temp_lowers[i] + 2)

    H, W = image.shape[:2]

    # Because I add some padding to the lines, there may be case when the line at y<0 or y>H
    uppers[0] = max(0, uppers[0])
    lowers[-1] = min(H, lowers[-1])

    # Remove pair of upper and lower lines which are too closed
    filter_lines(uppers, lowers, text_height)

    # Show the result
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # for y in uppers:
    # 	cv2.line(image, (0, y), (W, y), (255, 0, 0), 1)
    #
    # for y in lowers:
    # 	cv2.line(image, (0, y), (W, y), (0, 255, 0), 1)

    return lowers, uppers, image


def perform_imgtxtenh_preprocess(name):
    image_path = ''.join([settings.BASE_DIR, name])
    subprocess.call(' '.join([settings.IMGTXTENH, image_path, image_path]),  shell=True)
