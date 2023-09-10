
# @return promo: str
# Устаревший и недоработанный метод. Использовать в КРАЙНЕМ случае.
# Лучше ввод вручную с tg или vk, либо cloud vision.
def get_promo_from_img(self, path):

    def detect_language(text: str):
        english_alphabet = "abcdefghijklmnopqrstuvwxyz"
        russian_alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

        for _ in text.lower():
            if _ in english_alphabet:
                return "eng"
            if _ in russian_alphabet:
                return "rus"

    rs = [i for i in range(201, 231)]
    gs = [i for i in range(241, 256)]
    bs = [i for i in range(255, 256)]

    im = Image.open(path)
    box = (220, 570, 765, 690)
    im = im.crop(box)
    pixels = im.load()
    width, height = im.size
    range_corner = []
    x = 498
    for _ in range(4, 59):
        if _ == 8:
            x = 499
        if _ == 28:
            x = 500
        if _ == 33:
            x = 501
        if _ == 34:
            x = 502
        if _ == 35:
            x = 501
        if _ == 37:
            x = 502
        if _ == 39:
            x = 503
        if _ == 41:
            x = 504
        if _ == 43:
            x = 505
        if _ == 44:
            x = 506
        if _ == 45:
            x = 507
        if _ == 46:
            x = 508
        if _ == 48:
            x = 509
        if _ == 49:
            x = 511
        if _ == 50:
            x = 512
        if _ == 51:
            x = 513
        if _ == 53:
            x = 514
        if _ == 54:
            x = 516
        if _ == 55:
            x = 517
        if _ == 56:
            x = 519
        if _ == 57:
            x = 521
        if _ == 58:
            x = 522
        range_corner.append([x, _, width])

    for x in range(width):
        for y in range(height):
            r, g, b = pixels[x, y]
            if r not in rs and g not in gs and b not in bs:
                pixels[x,y] = (0, 0, 0)
    for x in range(width):
        for y in range(4):
            pixels[x, y] = (0, 0, 0)
    for x in range(6):
        for y in range(height):
            pixels[x, y] = (0, 0, 0)
    for _ in range(len(range_corner)):
        for x in range(range_corner[_][0], width):
            y = range_corner[_][1]
            pixels[x, y] = (0, 0, 0)

    im.save('temp_img.jpg')
    im.show()
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    promo = pytesseract.image_to_string(im, lang=detect_language())
    print(promo)
    return promo
    # sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    # api_key = os.getenv('APIKEY_2CAPTCHA', '91338054e656fd811a92592021cbe6a6')
    # solver = TwoCaptcha('91338054e656fd811a92592021cbe6a6')
    # try:
    #     result = solver.normal(path)
    # except Exception as e:
    #     print(e)
    #     # TODO: tg msg | код не распознан
    #     return False
    # else:
    #     return str(result)