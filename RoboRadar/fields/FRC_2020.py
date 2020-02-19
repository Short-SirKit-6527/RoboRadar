from math import pi

fieldHeight = (52 * 12 + 5.25) / 2
edgeHeight = fieldHeight + (10 * 12 + 9 + 1/8)
fieldWidth = (26 * 12 + 11.25) / 2
edgeWidth = (30 * 12) / 2

Data = {
    "name": "FRC 2020 Field",
    "theme": "Infinite Recharge",
    "file": "FRC_2020",
    "version": "1.0.0",
    "author": "David Johnston",
    "format": "PSF1",  # Python Script Field - Version 1
    "aliases": {
        "FRC 2020 FIELD 1.0.0",
        "FRC 2020 FIELD 1.0",
        "FRC 2020 FIELD 1",
        "FRC 2020 FIELD V1.0.0",
        "FRC 2020 FIELD V1.0",
        "FRC 2020 FIELD V1",
        "FRC_2020_1.0.0",
        "FRC_2020_1.0",
        "FRC_2020_1",
        "FRC_2020_V1.0.0",
        "FRC_2020_V1.0",
        "FRC_2020_V1",
        "FRC_2020V1.0.0",
        "FRC_2020V1.0",
        "FRC_2020V1",
        },
    "date": "2020-02-08T16:19-05:00",  # -05:00 Eastern no DST. DST is -04:00
    "units": "inches",
    "width": edgeWidth * 2,
    "height": edgeHeight * 2,
    "center": (edgeWidth, edgeHeight),
    "orientation": 0,
    "static-shapes": [
        {
            "name": "carpet",
            "type": "polygon",
            "style": ("filled"),
            "color": (43, 43, 43),
            "layer": 0,
            "points": [
                (edgeWidth, edgeHeight),
                (edgeWidth, -edgeHeight),
                (-edgeWidth, -edgeHeight),
                (-edgeWidth, edgeHeight)
                ]
            },
        {
            "name": "red alliance station",
            "type": "polygon",
            "style": ("filled", "aa"),
            "color": (96, 32, 32),
            "layer": 0,
            "points": [
                (edgeWidth, -edgeHeight),
                (edgeWidth, -edgeHeight+12*12+10+7/8),
                (fieldWidth, -edgeHeight+12*12+10+7/8),
                (fieldWidth-94.66+24, -edgeHeight+10*12+9+1/8),
                (-fieldWidth+94.66-24, -edgeHeight+10*12+9+1/8),
                (-fieldWidth, -edgeHeight+12*12+10+7/8),
                (-edgeWidth, -edgeHeight+12*12+10+7/8),
                (-edgeWidth, -edgeHeight)
                ]
            },
        {
            "name": "blue alliance station",
            "type": "polygon",
            "style": ("filled", "aa"),
            "color": (32, 32, 96),
            "layer": 0,
            "points": [
                (edgeWidth, edgeHeight),
                (edgeWidth, edgeHeight-12*12-10-7/8),
                (fieldWidth, edgeHeight-12*12-10-7/8),
                (fieldWidth-94.66+24, edgeHeight-10*12-9-1/8),
                (-fieldWidth+94.66-24, edgeHeight-10*12-9-1/8),
                (-fieldWidth, edgeHeight-12*12-10-7/8),
                (-edgeWidth, edgeHeight-12*12-10-7/8),
                (-edgeWidth, edgeHeight)
                ]
            },
        {
            "name": "field",
            "type": "polygon",
            "style": ("outline", "aa"),
            "color": (128, 128, 128),
            "layer": 0,
            "points": [

                (fieldWidth, -edgeHeight+12*12+10+7/8),
                (fieldWidth-94.66+24, -edgeHeight+10*12+9+1/8),
                (-fieldWidth+94.66-24, -edgeHeight+10*12+9+1/8),
                (-fieldWidth, -edgeHeight+12*12+10+7/8),
                (-fieldWidth, edgeHeight-12*12-10-7/8),
                (-fieldWidth+94.66-24, edgeHeight-10*12-9-1/8),
                (fieldWidth-94.66+24, edgeHeight-10*12-9-1/8),
                (fieldWidth, edgeHeight-12*12-10-7/8),
                ]
            },
        {
            "name": "red initiation line",
            "type": "polygon",
            "style": ("filled", "aa"),
            "color": (255, 255, 255),
            "layer": 0,
            "points": [
                (fieldWidth, fieldHeight-10*12),
                (fieldWidth, fieldHeight-10*12-2),
                (-fieldWidth, fieldHeight-10*12-2),
                (-fieldWidth, fieldHeight-10*12)
                ]
            },
        {
            "name": "blue initiation line",
            "type": "polygon",
            "style": ("filled", "aa"),
            "color": (255, 255, 255),
            "layer": 0,
            "points": [
                ((26 * 12 + 11.25) / 2, -194.625),
                ((26 * 12 + 11.25) / 2, -194.625+2),
                (-(26 * 12 + 11.25) / 2, -194.625+2),
                (-(26 * 12 + 11.25) / 2, -194.625)
                ]
            }
        ]
    }

if __name__ == "__main__":
    print(Data)
