from flask import render_template, request, redirect
from codes import app, G_walk, G_lrt, walkNodeList, walkEdgeList, mrtNodeList, mrtEdgeList
from codes.walk_astaralgo import AstarWalkAlgo
from codes.walk_mrt_algo import AstarWalkMrtAlgo
import codes.PlotShortestWalkBusRoute as DjWalkBus


@app.route("/", methods=["GET", "POST"])
# @app.route("/home", methods=["GET", "POST"])
def home():
    print(request.method)
    if request.method == "POST":
        address_input = str(request.form["address_input"])  # src
        address_input1 = str(request.form["address_input1"])  # dst
        print(address_input, "-->", address_input1)  #
        print(str(request.form["dropdown"]))
        if str(request.form["dropdown"]) == "Walk":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            aswa = AstarWalkAlgo(address_input, address_input1, G_walk, walkNodeList, walkEdgeList)
            aswa.generate()
            redirect("/walking")
        if str(request.form["dropdown"]) == "WalkandMRT":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            asawl = AstarWalkMrtAlgo(address_input, address_input1, G_walk, G_lrt, walkNodeList, walkEdgeList,
                                     mrtNodeList, mrtEdgeList)  # astar walk with mrt
            asawl.generate()
            redirect("/walkinglrt")
        if str(request.form["dropdown"]) == "WalkandBus":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            DjWalkBus.plotShortestWalkBus(address_input, address_input1)
            redirect("/walkingbus")
        # if request.form["dropdown"] == "walk":
        #     address_input = str(request.form["address_input"])  # src
        #     address_input1 = str(request.form["address_input1"])  # dst
        #     aswa = AstarWalkAlgo(address_input, address_input1)
        #     aswa.generate()
        #     print(address_input, "-->", address_input1)
        #     redirect("/walking")

        return render_template('base.html')

    if request.method == "GET":
        return render_template("home.html")


@app.route("/test", methods=['POST'])
def test():
    print(request.method)
    if request.method == "POST":
        address_input = str(request.form["address_input"])  # src
        address_input1 = str(request.form["address_input1"])  # dst
        print(address_input, "-->", address_input1)


@app.route("/walking")
def walk():
    return render_template("default.html")


@app.route("/default")
def default():
    return render_template("default.html")


@app.route("/punggol")
def punggol():
    return render_template('punggol.html')


@app.route("/walkinglrt")
def walklrt():
    return render_template('default.html')
