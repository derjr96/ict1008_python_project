from flask import render_template, request, redirect, make_response
from codes import app, G_walk, G_lrt, walkNodeList, walkEdgeList, mrtNodeList, mrtEdgeList
from codes.walk_astaralgo import AstarWalkAlgo
from codes.walk_mrt_algo import AstarWalkMrtAlgo
import codes.PlotShortestWalkBusRoute as DjWalkBus
from flask_caching import Cache

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/", methods=["GET", "POST"])
def home():
    print(request.method)
    anything = 0
    anything1 = 0
    anything2 = 0
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
            anything = aswa.printout()[0]
            anything1 = aswa.printout()[1]
            anything2 = aswa.printout()[2]
            # redirect("/walking")
        elif str(request.form["dropdown"]) == "WalkandMRT":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            asawl = AstarWalkMrtAlgo(address_input, address_input1, G_walk, G_lrt, walkNodeList, walkEdgeList,
                                     mrtNodeList, mrtEdgeList)  # astar walk with mrt
            asawl.generate()
            # redirect("/walkinglrt")
        elif str(request.form["dropdown"]) == "WalkandBus":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            print(type(address_input))
            DjWalkBus.plotShortestWalkBus(address_input, address_input1)
            # redirect("/walkingbus")

        return render_template("base.html", variable = anything, variable1 = anything1, variable2 = anything2)
    elif request.method == "GET":
        return render_template("home.html")


@app.route("/test", methods=['POST'])
def test():
    print(request.method)
    if request.method == "POST":
        address_input = str(request.form["address_input"])  # src
        address_input1 = str(request.form["address_input1"])  # dst
        print(address_input, "-->", address_input1)


@app.route("/default")
def default():
    return render_template("default.html")


@app.route("/punggol")
def punggol():
    return render_template('punggol.html')

