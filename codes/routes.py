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

    #walk
    walkvalue = 0
    walkvalue1 = 0
    walkvalue2 = 0

    #walk and mrt
    walklrtvalue = 0
    walklrtvalue1 = 0
    walklrtvalue2 = 0
    walklrtvalue3 = 0
    walklrtvalue4 = 0
    walklrtvalue5 = 0
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
            #for walk output
            walkvalue  = aswa.printout()[0]
            walkvalue1 = aswa.printout()[1]
            walkvalue2 = aswa.printout()[2]
            return render_template("base.html", walkvariable = walkvalue, walkvariable1 = walkvalue1, walkvariable2 = walkvalue2)
            # redirect("/walking")
        elif str(request.form["dropdown"]) == "WalkandMRT":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            asawl = AstarWalkMrtAlgo(address_input, address_input1, G_walk, G_lrt, walkNodeList, walkEdgeList,
                                     mrtNodeList, mrtEdgeList)  # astar walk with mrt
            asawl.generate()
            #for walk and lrt output
            walklrtvalue = asawl.printout2()[0]
            walklrtvalue1 = asawl.printout2()[1]
            walklrtvalue2 = asawl.printout2()[2]
            walklrtvalue3 = asawl.printout2()[3]
            walklrtvalue4 = asawl.printout2()[4]
            walklrtvalue5 = asawl.printout2()[5]
            return render_template("base.html", wlvariable = walklrtvalue, wlvariable1 = walklrtvalue1, wlvariable2 = walklrtvalue2, wlvariable3 = walklrtvalue3, wlvariable4= walklrtvalue4, wlvariable5 = walklrtvalue5)
            # redirect("/walkinglrt")
        elif str(request.form["dropdown"]) == "WalkandBus":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            algoTime = DjWalkBus.plotShortestWalkBus(G_walk, G_bus, address_input, address_input1)
            return render_template("base.html", wlvariable = algoTime[0])
            # redirect("/walkingbus")


        return render_template("base.html")
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
