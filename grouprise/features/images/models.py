from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, SmartResize, Transpose


class Image(models.Model):
    file = models.ImageField("Datei")
    creator = models.ForeignKey(
        "gestalten.Gestalt", related_name="images", on_delete=models.PROTECT
    )

    preview_api = ImageSpecField(
        source="file", processors=[Transpose(), SmartResize(250, 250)]
    )
    preview_content = ImageSpecField(
        source="file", processors=[Transpose(), SmartResize(200, 200)]
    )
    preview_gallery = ImageSpecField(
        source="file", processors=[Transpose(), ResizeToFit(250)]
    )
    preview_group = ImageSpecField(
        source="file", processors=[Transpose(), SmartResize(366, 120)]
    )
    intro = ImageSpecField(source="file", processors=[Transpose(), ResizeToFit(554)])
    sidebar = ImageSpecField(source="file", processors=[Transpose(), ResizeToFit(313)])
    facebook_meta = ImageSpecField(
        source="file", processors=[Transpose(), ResizeToFit(800)]
    )
    twitter_meta = ImageSpecField(
        source="file", processors=[Transpose(), SmartResize(600, 300)]
    )

    def __str__(self):
        return "{} ({})".format(self.file, self.creator)[2:]
