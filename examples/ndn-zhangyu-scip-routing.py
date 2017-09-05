## -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-
#
# 2017-9-2 ZhangYu-SCIP-Routing.py
#

from ns.core import *
from ns.network import *
from ns.point_to_point import *
from ns.point_to_point_layout import *
from ns.ndnSIM import *
import mintreeMFP

#
# To run scenario and see what is happening, use the following command:
#
#     NS_LOG=ndn.GlobalRoutingHelper:ndn.Producer ./waf --pyrun=src/ndnSIM/examples/ndn-zhangyu-scip-routing.py
#

Config.SetDefault("ns3::PointToPointNetDevice::DataRate", StringValue("10Mbps"))
Config.SetDefault("ns3::PointToPointChannel::Delay", StringValue("10ms"))
Config.SetDefault("ns3::DropTailQueue::MaxPackets", StringValue("20"))

import sys; cmd = CommandLine(); cmd.Parse(sys.argv);

p2p = PointToPointHelper ()
grid = PointToPointGridHelper (3,3,p2p)
grid.BoundingBox(100,100,200,200)
# AnnotatedTopologyReader.SetFileName("")

#######################################################

ndnHelper = ndn.StackHelper()
ndnHelper.InstallAll();


# Getting containers for the consumer/producer
producer = grid.GetNode(2, 2)
consumerNodes = NodeContainer()
consumerNodes.Add(grid.GetNode(0,0))


cHelper = ndn.AppHelper("ns3::ndn::ConsumerCbr")
cHelper.SetPrefix("/prefix")
cHelper.SetAttribute("Frequency", StringValue("10"))
out = cHelper.Install(consumerNodes)

pHelper = ndn.AppHelper("ns3::ndn::Producer")
pHelper.SetPrefix("/prefix")
pHelper.SetAttribute("PayloadSize", StringValue("1024"));
pHelper.Install(producer)

ndnGlobalRoutingHelper = ndn.GlobalRoutingHelper()
ndnGlobalRoutingHelper.InstallAll()

# Add /prefix origins to ndn::GlobalRouter
ndnGlobalRoutingHelper.AddOrigin("/prefix", producer)

# Calculate and install FIBs
ndnGlobalRoutingHelper.CalculateRoutes()
ndnGlobalRoutingHelper.CalculateNoCommLinkMultiPathRoutesPairFirst();
mintreeMFP.caculateRoute()

# #######################################################

Simulator.Stop(Seconds(20.0))
Simulator.Run()

# # To access FIB, PIT, CS, uncomment the following lines

# l3Protocol = ndn.L3Protocol.getL3Protocol(grid.GetNode(0,0))
# forwarder = l3Protocol.getForwarder()

# fib = forwarder.getFib()
# print "Contents of FIB (%d):" % fib.size()
# for i in fib:
#     print " - %s:" % i.getPrefix()
#     for nh in i.getNextHops():
#         print "    - %s%d (cost: %d)" % (nh.getFace(), nh.getFace().getId(), nh.getCost())

# pit = forwarder.getPit()
# print "Contents of PIT (%d):" % pit.size()
# for i in pit:
#     print " - %s" % i.getName()

# cs = forwarder.getCs()
# print "Contents of CS (%d):" % cs.size()
# for i in cs:
#     print " - %s" % i.getName()

Simulator.Destroy()

# # or run using the visualizer
# import visualizer
# visualizer.start()
#import visualizer
#visualizer.start()

