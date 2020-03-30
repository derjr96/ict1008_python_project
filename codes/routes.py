from flask import render_template, request, redirect, make_response
from codes import app, G_bus, G_walk, G_lrt, walkNodeList, walkEdgeList, mrtNodeList, mrtEdgeList, addr
from codes.walk_astaralgo import AstarWalkAlgo
from codes.walk_mrt_algo import AstarWalkMrtAlgo
import codes.PlotShortestWalkBusRoute as DjWalkBus
from codes.walk_lrt_bus_algo import WalkBusLrt
import json


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/", methods=["GET", "POST"])
def home():
    print(request.method)

    # walk
    walkvalue = 0
    walkvalue1 = 0
    walkvalue2 = 0

    # walk and mrt
    walklrtvalue = 0
    walklrtvalue1 = 0
    walklrtvalue2 = 0
    walklrtvalue3 = 0
    walklrtvalue4 = 0
    walklrtvalue5 = 0
    walklrtvalue6 = 0
    walklrtvalue7 = 0

    # walk bus mrt
    allvalue = 0
    allvalue1 = 0
    allvalue2 = 0
    allvalue3 = 0
    allvalue4 = 0
    allvalue5 = 0
    allvalue6 = 0
    allvalue7 = 0

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
            walkvalue = aswa.printout()[0]
            walkvalue1 = aswa.printout()[1]
            walkvalue2 = aswa.printout()[2]
            return render_template("base.html", walkvariable=walkvalue, walkvariable1=walkvalue1,
                                   walkvariable2=walkvalue2, addr=json.dumps(addr))
            # redirect("/walking")
        elif str(request.form["dropdown"]) == "WalkandMRT":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            asawl = AstarWalkMrtAlgo(address_input, address_input1, G_walk, G_lrt, walkNodeList, walkEdgeList,
                                     mrtNodeList, mrtEdgeList)  # astar walk with mrt
            asawl.generate()
            # for walk and lrt output
            walklrtvalue = asawl.printout2()[0]
            walklrtvalue1 = asawl.printout2()[1]
            walklrtvalue2 = asawl.printout2()[2]
            walklrtvalue3 = asawl.printout2()[3]
            walklrtvalue4 = asawl.printout2()[4]
            walklrtvalue5 = asawl.printout2()[5]
            walklrtvalue6 = asawl.printout2()[6]
            walklrtvalue7 = asawl.printout2()[7]
            return render_template("base.html", wlvariable=walklrtvalue, wlvariable1=walklrtvalue1,
                                   wlvariable2=walklrtvalue2, wlvariable3=walklrtvalue3, wlvariable4=walklrtvalue4,
                                   wlvariable5=walklrtvalue5, wlvariable6=walklrtvalue6, wlvariable7=walklrtvalue7,
                                   addr=json.dumps(addr))
            # redirect("/walkinglrt")
        elif str(request.form["dropdown"]) == "WalkandBus":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            result = DjWalkBus.plotShortestWalkBus(G_walk, G_bus, address_input, address_input1)
            return render_template("base.html", wbvariable=result[0], wbvariable1=result[1], wbvariable2=result[2],
                                   wbvariable3=result[3], addr=json.dumps(addr))
            # redirect("/walkingbus")
        elif str(request.form["dropdown"]) == "WalkBusMrt":
            dropdown = str(request.form["dropdown"])  # dropdown value
            print(address_input, "-->", address_input1)
            print(dropdown)
            # will implement it later.
            allthree = WalkBusLrt(address_input, address_input1, G_bus, G_walk, G_lrt, walkNodeList, walkEdgeList,
                                  mrtNodeList, mrtEdgeList)
            allthree.generate()
            allvalue = allthree.printout3()[0]
            allvalue1 = allthree.printout3()[1]
            allvalue2 = allthree.printout3()[2]
            allvalue3 = allthree.printout3()[3]
            allvalue4 = allthree.printout3()[4]
            allvalue5 = allthree.printout3()[5]
            allvalue6 = allthree.printout3()[6]
            allvalue7 = allthree.printout3()[7]
            return render_template("base.html", wlbvariable=allvalue, wlbvariable1=allvalue1, wlbvariable2=allvalue2,
                                   wlbvariable3=allvalue3, wlbvariable4=allvalue4, wlbvariable5=allvalue5,
                                   wlbvariable6=allvalue6, wlbvariable7=allvalue7, addr=json.dumps(addr))

        return render_template("base.html", addr=json.dumps(addr))
    elif request.method == "GET":
        return render_template("home.html", addr=json.dumps(addr))


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
