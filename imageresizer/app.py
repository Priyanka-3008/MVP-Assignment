from flask import Flask, request
from flask import jsonify
app=Flask(__name__)
tools=[
     {'sampletool':'explanaton','mytools':'tools'}
]
@app.route('/hello/',methods=['GET','POST'])
def welcome():
    return "Hello flask its a task"



@app.route('/getlist',methods=['GET'])
def getlist():
    if not tools:
        return jsonify({"tools":None})
    return jsonify({"tools":tools})



@app.route('/addtool',methods=['POST'])
def addtool():
    data=request.get_json()
    toolname=data.get('toolname')

    if not toolname:
        return jsonify({"Error":"Tool name can not be empty"}),400
    tools.append(toolname)
    return jsonify({"Message":"Updated the tools list"}),201






if __name__=='__main__':
    app.run(debug=True)
