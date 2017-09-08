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
from ns.topology_read import TopologyReader
#from ns.topology_read import *

# ZhangYu 2017-9-6 改用Python脚本运行ndnSIM仿真
""" 
    PyBindGen在Ubuntu1204虚拟机中的是可以用的，但是ndnSIM2.0以后无论是1404的GCC4.8还是1604的GCC5.1都不能正常执行--apiscan
    所以放弃了自动生成，而是手工修改modulegen__gcc_ILP32来添加AnnotatedTopologyReader
    To run scenario and see what is happening, use the following command:
    NS_LOG=ndn.GlobalRoutingHelper:ndn.Producer ./waf --pyrun=src/ndnSIM/examples/ndn-zhangyu-scip-routing.py
"""

# ----------------命令行参数----------------

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
# Setup argument parser
parser = ArgumentParser(description="./waf --pyrun=ndn-zhangyu-scip-routing.py", formatter_class=RawDescriptionHelpFormatter)
parser.add_argument("--InterestsPerSec", type=int,default=200, help="Interests emit by consumer per second")
parser.add_argument("--simulationSpan", type=int, default=50, help="Simulation span time by seconds");
parser.add_argument("--routingName", type=str, choices=["BestRoute","MultiPathPairFirst"], default="MultiPathPairFirst", help="could be Flooding, BestRoute, MultiPath, MultiPathPairFirst");
args=parser.parse_args()
print args.routingName

#print dir(TopologyReader)
print dir(AnnotatedTopologyReader)

# ----------------仿真拓扑----------------
topologyReader=AnnotatedTopologyReader("",20.0)
#AnnotatedTopologyReader.
print "***********pass"

Config.SetDefault("ns3::PointToPointNetDevice::DataRate", StringValue("10Mbps"))
Config.SetDefault("ns3::PointToPointChannel::Delay", StringValue("10ms"))
Config.SetDefault("ns3::DropTailQueue::MaxPackets", StringValue("20"))



p2p = PointToPointHelper ()
grid = PointToPointGridHelper (3,3,p2p)
grid.BoundingBox(100,100,200,200)
topologyReader.SetFileName("topo-for-CompareMultiPath.txt")

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

