

import argparse
import base64
import json
import os
import os.path as osp

import imgviz
import PIL.Image

from labelme.logger import logger
from labelme import utils


def main(json_file):


    parser = argparse.ArgumentParser()
    # parser.add_argument("json_file")
    parser.add_argument("-o", "--out", default='./')
    args = parser.parse_args()

    # json_file = args.json_file
    # json_file = '/Users/viatorsun/Desktop/Demo/Tomato/TomatoJSON/HIMG_20211108_144919_1.json'

    if args.out is None:
        out_dir = osp.basename(json_file).replace(".", "_")
        out_dir = osp.join(osp.dirname(json_file), out_dir)
    else:
        out_dir = args.out
        out_dir = osp.join(osp.dirname(json_file), out_dir)
    if not osp.exists(out_dir):
        os.mkdir(out_dir)

    img_name = osp.basename(json_file)[:-5]

    data = json.load(open(json_file))
    imageData = data.get("imageData")

    if not imageData:
        imagePath = os.path.join(os.path.dirname(json_file), data["imagePath"])
        with open(imagePath, "rb", encoding='utf-8') as f:
            imageData = f.read()
            imageData = base64.b64encode(imageData).decode("utf-8")
    img = utils.img_b64_to_arr(imageData)

    label_name_to_value = {"_background_": 0, "femuro": 1, "femur":2,"tibia":3, "tibiao":4}
    for shape in sorted(data["shapes"], key=lambda x: x["label"]):
        label_name = shape["label"]
        if label_name in label_name_to_value:
            label_value = label_name_to_value[label_name]
        else:
            label_value = len(label_name_to_value)
            label_name_to_value[label_name] = label_value
    lbl, _ = utils.shapes_to_label( img.shape, data["shapes"], label_name_to_value )

    label_names = [None] * (max(label_name_to_value.values()) + 1)
    for name, value in label_name_to_value.items():
        label_names[value] = name

    lbl_viz = imgviz.label2rgb( lbl, imgviz.asgray(img), label_names=label_names, loc="rb" )

    # 原图保存
    Images = osp.join(out_dir, 'PNGImages')
    if not osp.exists(Images):
        os.mkdir(Images)
    PIL.Image.fromarray(img).save(osp.join(Images ,img_name + ".png"))

    # 标签保存
    Labels = osp.join(out_dir,'SegmentLabels')
    if not osp.exists(Labels):
        os.mkdir(Labels)
    utils.lblsave(osp.join(Labels, img_name + ".png" ), lbl)

    #with open(osp.join(out_dir, 'SegmentLabels', img_name + ".txt"), "w",encoding='utf-8') as f:
     #   for lbl_name in label_names:
     #       f.write(lbl_name + "\n")


    # 合成图保存
    Label_viz = osp.join(out_dir, "Label_viz")
    if not osp.exists(Label_viz):
        os.mkdir(Label_viz)
    PIL.Image.fromarray(lbl_viz).save(osp.join(Label_viz, img_name + ".png"))

    logger.info("Saved to: {}".format(out_dir))


if __name__ == "__main__":

    json_path = './'

    for root , dirs , files in os.walk(json_path):
        for file in files:
            if file == '.DS_Store':
                continue
            json_path = os.path.join(root ,file)
            print(json_path)
            main(json_path)

