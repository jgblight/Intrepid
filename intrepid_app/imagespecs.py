from imagekit import ImageSpec, register
from imagekit.processors import Crop, SmartCrop, ResizeToFill
from imagekit.utils import get_field_info

class Profile_Image(ImageSpec):
    format = 'JPEG'
    options = {'quality': 60}

    @property 
    def processors(self):
        model, field_name = get_field_info(self.source)
        min_dim = min(model.image_file.width,model.image_file.height)
        return [Crop(width=min_dim,
                    height=min_dim,
                    x=int(-1*model.image_x*model.image_file.width),
                    y=int(-1*model.image_y*model.image_file.height))]

register.generator('profile_image', Profile_Image)

class Header_Image(ImageSpec):
    format = 'JPEG'
    options = {'quality': 60}

    @property 
    def processors(self):
        model, field_name = get_field_info(self.source)
        x = int(-1*model.image_x*model.image_file.width)
        y = int(-1*model.image_y*model.image_file.height)
        crop_width = int(model.image_width*model.image_file.width)
        crop_height = model.image_file.height + y
        return [Crop(width=crop_width,
                    height=crop_height,
                    x=x,
                    y=y)]

register.generator('header_image', Header_Image)

class Pin_Display(ImageSpec):
    format = 'JPEG'
    options = {'quality': 60}

    @property 
    def processors(self):
        model, field_name = get_field_info(self.source)
        min_dim = min(model.original.width,model.original.height)
        return [SmartCrop(width=min_dim,
                    height=min_dim),
                ResizeToFill(width=500,height=500)]

register.generator('pin_display', Pin_Display)
