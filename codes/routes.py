from flask import render_template, request, redirect, make_response
from codes import app, G_bus, G_walk, G_lrt, walkNodeList, walkEdgeList, mrtNodeList, mrtEdgeList
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
    # for walk output
    # anything = 0
    # anything1 = 0
    # anything2 = 0

    # for walk and lrt output
    anything0 = 0
    anything1 = 0
    anything2 = 0
    anything3 = 0
    anything4 = 0
    anything5 = 0
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
            # for walk output
            # anything = aswa.printout()[0]
            # anything1 = aswa.printout()[1]
            # anything2 = aswa.printout()[2]
            # redirect("/walking")
        elif str(request.form["dropdown"]) == "WalkandMRT":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            asawl = AstarWalkMrtAlgo(address_input, address_input1, G_walk, G_lrt, walkNodeList, walkEdgeList,
                                     mrtNodeList, mrtEdgeList)  # astar walk with mrt
            asawl.generate()
            # for walk and lrt output
            anything0 = asawl.printout2()[0]
            anything1 = asawl.printout2()[1]
            anything2 = asawl.printout2()[2]
            anything3 = asawl.printout2()[3]
            anything4 = asawl.printout2()[4]
            anything5 = asawl.printout2()[5]

            # redirect("/walkinglrt")
        elif str(request.form["dropdown"]) == "WalkandBus":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            print(type(address_input))
            DjWalkBus.plotShortestWalkBus(G_walk, G_bus, address_input, address_input1)
            # redirect("/walkingbus")

        # for walk output
        # return render_template("base.html", variable = anything, variable1 = anything1, variable2 = anything2)

        # for walk and lrt output
        return render_template("base.html", variable=anything0, variable1=anything1, variable2=anything2,
                               variable3=anything3, variable4=anything4, variable5=anything5)
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
