import pytesseract


def run_ocr_tesseract(image):
    return pytesseract.image_to_string(image, lang="vie5")

# def run_ocr_kraken(image_name):
#     shell_script = 'kraken -i ' + image_name + ' /tmp/kraken_result binarize segment ocr -m kraken.mlmodel'
#     subprocess.run([shell_script], shell=True)
#     f = open("/tmp/kraken_result", "r")
#     text = f.read()
#     f.close()
#     return text


def run_ocr_kraken(image):
    return pytesseract.image_to_string(image, lang="eng")


def run_ocr_ocropy(image):
    return pytesseract.image_to_string(image, lang="vie")
