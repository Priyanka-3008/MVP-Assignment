from flask import Flask,request,jsonify
from PIL import Image
import os
import uuid

app=Flask(__name__)

@app.route('/welcome',methods=['GET','POST'])
def welcome():
    return "A image resizer & image convertor website"


@app.route('/resizeandconvert',methods=['POST'])
def resizeandconvert():
    tar_width=request.form.get('width',type=int)
    tar_height=request.form.get('height',type=int)
    tar_format=request.form.get('format')
    input_path=request.form.get('path')

    if not input_path or not os.path.exists(input_path):
        return jsonify({"error":"No valid image path is provided"})
    
    if tar_width is None or tar_height is None or tar_format is None:
        return jsonify({"error":"width,height and format are required to perform image resizing"}),400
    
    outputfiles=[]

    if os.path.isdir(input_path):
        for filename in os.listdir(input_path):
            file_path=os.path.join(input_path,filename)
            if os.path.isfile(file_path) and is_image_file(file_path):
                outputfiles.extend(process_image(file_path,tar_width,tar_height,tar_format))
    
    elif os.path.isfile(input_path) and is_image_file(input_path):
        outputfiles.extend(process_image(file_path,tar_width,tar_height,tar_format))   
    else:
        return jsonify({"Error":"Provided path is not a directory please check and upload the path again"}),400
    return jsonify({"Message":"Images are resized and converted","Files":outputfiles}),200




def is_image_file(file_path):
    valid_extensions={'.jpg','.png','.bmp','.gif','.tiff'}
    ext=os.path.splitext(file_path)[1].lower()
    return ext in valid_extensions



def process_image(image_path,width,height,img_format):
    img=Image.open(image_path)
    img=img.resize((width,height))
    output_filename=f"{uuid.uuid4()}.{img_format}"
    output_path=os.path.join('output',output_filename)
    img.save(output_path,img_format.upper())
    return [output_path]






    



if __name__=="__main__":
    if not os.path.exists('output'):
        os.makedirs('output')
    app.run(debug=True)
