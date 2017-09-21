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
import visualizer

# ZhangYu 2017-9-6 改用Python脚本运行ndnSIM仿真
""" 
    PyBindGen在Ubuntu1204虚拟机中的是可以用的，但是ndnSIM2.0以后无论是1404的GCC4.8还是1604的GCC5.1都不能正常执行--apiscan
    所以放弃了自动生成，而是手工修改modulegen__gcc_ILP32来添加AnnotatedTopologyReader
    To run scenario and see what is happening, use the following command:
    NS_LOG=ndn.GlobalRoutingHelper:ndn.Producer ./waf --pyrun="src/ndnSIM/examples/ndn-zhangyu-scip-routing.py --routingName='Flooding'"
"""
# ----------------命令行参数----------------
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
# Setup argument parser
parser = ArgumentParser(description="./waf --pyrun=ndn-zhangyu-scip-routing.py", formatter_class=RawDescriptionHelpFormatter)
parser.add_argument("--InterestsPerSec", type=str,
                    default="300", help="Interests emit by consumer per second")
parser.add_argument("--simulationSpan", type=int, 
                    default=200, help="Simulation span time by seconds")
parser.add_argument("--routingName", type=str, choices=["Flooding","BestRoute","MultiPathPairFirst"], 
                    default="MultiPathPairFirst", 
                    help="could be Flooding, BestRoute, MultiPath, MultiPathPairFirst")
parser.add_argument("--TracePerSec",type=float,default=5.0,help="All the Tracer Record Interval")
parser.add_argument("--vis",action="store_true",default=False)

args=parser.parse_args()

# ----------------仿真拓扑----------------
topoFileName="topo-for-CompareMultiPath.txt"
topoFileName="src/ndnSIM/examples/topologies/"+topoFileName
topologyReader=AnnotatedTopologyReader("",20.0)
topologyReader.SetFileName(topoFileName)
nodes=topologyReader.Read()


# ----------------协议加载----------------
ndnHelper = ndn.StackHelper()
ndnHelper.SetOldContentStore("ns3::ndn::cs::Lru","MaxSize","100","","","","","","")
ndnHelper.InstallAll();
topologyReader.ApplyOspfMetric()
ndnGlobalRoutingHelper = ndn.GlobalRoutingHelper()
ndnGlobalRoutingHelper.InstallAll()


# ----------------业务加载----------------
consumerList=["Node0","Node2"]
producerList=["Node4","Node3"]

cHelper = ndn.AppHelper("ns3::ndn::ConsumerCbr")
cHelper.SetAttribute("Frequency", StringValue(args.InterestsPerSec))
pHelper = ndn.AppHelper("ns3::ndn::Producer")
pHelper.SetAttribute("PayloadSize", StringValue("1024"));
for i in range(len(producerList)):
    cHelper.SetPrefix("/prefix"+str(i))
    App=cHelper.Install(topologyReader.FindNodeFromName(consumerList[i]))
    App.Start(Seconds(0.01*i));

    pHelper.SetPrefix("/prefix"+str(i))
    ndnGlobalRoutingHelper.AddOrigin("/prefix"+str(i), topologyReader.FindNodeFromName(producerList[i]))
    pHelper.Install(topologyReader.FindNodeFromName(producerList[i]))

# ----------------路由和转发----------------
# Calculate and install FIBs
if args.routingName=="Flooding":
    for i in range(len(producerList)):
        ndn.StrategyChoiceHelper.InstallAll("/prefix"+str(i), "/localhost/nfd/strategy/ncc")
    ndnGlobalRoutingHelper.CalculateAllPossibleRoutes()
elif args.routingName=="BestRoute":
    for i in range(len(producerList)):
        ndn.StrategyChoiceHelper.InstallAll("/prefix"+str(i), "/localhost/nfd/strategy/ncc")
    ndnGlobalRoutingHelper.CalculateRoutes()
elif args.routingName=="MultiPathPairFirst":
    for i in range(len(producerList)):
        ndn.StrategyChoiceHelper.InstallAll("/prefix"+str(i), "/localhost/nfd/strategy/ncc")
    ndnGlobalRoutingHelper.CalculateNoCommLinkMultiPathRoutesPairFirst();
else:
    mintreeMFP.caculateRoute(topoFileName)


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
# ----------------------------------------

Simulator.Stop(Seconds(args.simulationSpan))
#print dir(L2RateTracer)

# ----------------结果记录----------------
filename="-"+args.routingName.lower()+"-"+str(args.InterestsPerSec)+".txt"
filename=".txt"
ndn.CsTracer.InstallAll("cs-trace"+filename, Seconds(args.TracePerSec))
ndn.L3RateTracer.InstallAll("rate-trace"+filename, Seconds(args.TracePerSec))
ndn.AppDelayTracer.InstallAll("app-delays-trace"+filename)
L2RateTracer.InstallAll("drop-trace"+filename,Seconds(args.TracePerSec))
if args.vis:
    visualizer.start()
Simulator.Run()

Simulator.Destroy()


