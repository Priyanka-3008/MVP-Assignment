from flask import Flask,request,jsonify
from PIL import Image
import os
import uuid
app=Flask(__name__)
@app.route('/resizeandconvert',methods=['POST'])
def resizeandconvert():
    tar_width=request.form.get('width',type=int)
    tar_height=request.form.get('height',type=int)
    tar_format=request.form.get('format')
    uploaded_files=request.files.getlist('images')

    if not uploaded_files:
        return jsonify({"error":"No image is detected"})
    if tar_width is None or tar_height is None or tar_format is None:
        return jsonify({"error":"width,height and format are required to perform image resizing"}),400
    
    outputfiles=[]
    for i in uploaded_files:
        if i and i.filename:
            img=Image.open(i)
            img=img.resize((tar_width,tar_height))
            output_filename=f"{uuid.uuid4()}.{tar_format}"
            output_path=os.path.join('output',output_filename)
            img.save(output_path,tar_format.upper())
            outputfiles.append(output_path)
    return jsonify({"message":"Images resized and converted","files":outputfiles}),200




if __name__=="__main__":
    if not os.path.exists('output'):
        os.makedirs('output')
    app.run(debug=True)
