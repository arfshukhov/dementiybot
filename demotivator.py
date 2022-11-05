from PIL import Image, ImageOps, ImageFont, ImageDraw
import sys
import os


class OverLength(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Длина слов не может быть больше 40 символов"


class Demotivator:
    def __init__(self, picture, text1, *text2: str):
        self.main_image = Image.new("RGB", (1024, 1024), "black")
        self.path = picture
        self.picture = Image.open(picture)
        self.prepared_picture: object
        self.frame: object
        self.text1 = text1
        self.text2 = text2
        self.string_offset = 75
        self.processing_picture()
        self.write_text(self.text1, 45, 10, 15, 20)
        if text2:
            self.write_text("".join(self.text2), 30, 6.6, 10, 13)
        else:
            pass
        self.crop_frame()
        self.download_demotivator()

    def processing_picture(self):
        self.picture.thumbnail((683, 683))
        self.prepared_picture = ImageOps.expand(self.picture, border=3, fill="white")
        self.main_image.paste(self.prepared_picture, (512 - int(self.prepared_picture.size[0] / 2), 50))

    def write_text(self, text, size, l_font, h_font, offset):
        draw = ImageDraw.Draw(self.main_image)
        lower = []
        upper = []
        if len(self.text1) <= 40:

            for i in text:
                if i.isupper(): upper.append(i)
                else: lower.append(i)
            draw.text((512-(l_font*len(lower)+h_font*len(upper)), self.prepared_picture.size[1]+self.string_offset),
                                 text, font=ImageFont.truetype("fonts/timesnewromanpsmt.ttf", size=size))
            self.string_offset += 2*h_font+offset
        else:
            elements = text.split(" ")
            prepared_elements = []
            sector = []
            lenght = 0
            for m, k in enumerate(elements):
                # mlen = len(elements)-1
                if len(k) < 40:
                    sector.append(k)
                    lenght += len(k)+1
                    try:
                        if len(elements[m+1]) + 1 + lenght < 40:
                            continue
                        else:
                            prepared_elements.append(" ".join(sector))
                            sector = []
                            lenght = 0
                    except:
                        prepared_elements.append(" ".join(sector))
                        sector = []
                else:
                    raise OverLength
            for b in prepared_elements:
                for i in b:
                    if i.isupper():
                        upper.append(i)
                    else:
                        lower.append(i)
                draw.text((512 - (l_font * len(lower) + h_font * len(upper)),
                           self.prepared_picture.size[1] + self.string_offset),
                          b, font=ImageFont.truetype("arial.ttf", size=size))
                self.string_offset += 1.5* h_font + offset
                upper = []
                lower = []
        self.string_offset+=20
        return

    def crop_frame(self):
        self.frame = self.main_image.crop((0, 0, 1024, self.prepared_picture.size[1] + self.string_offset))

    def download_demotivator(self):
        os.remove(self.path)
        self.frame.save(self.path)
