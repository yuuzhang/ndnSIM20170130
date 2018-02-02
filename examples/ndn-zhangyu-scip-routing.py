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
from Carbon.Aliases import false
from compiler.ast import nodes
from MA.MA import floor

# ZhangYu 2018-1-26 添加了traffic split, randomized rounding。因为randomized rounding是需要路由计算的结果来分配的带宽的，一种方法是按照
# NDF Developer Guide的建议保存在PIT中，这里采用了较简单的做法，直接保存在该主程序中，然后传递给自定义的NDF Strategy中
# ZhangYu 2017-9-6 改用Python脚本运行ndnSIM仿真
""" 
    PyBindGen在Ubuntu1204虚拟机中的是可以用的，但是ndnSIM2.0以后无论是1404的GCC4.8还是1604的GCC5.1都不能正常执行--apiscan
    所以放弃了自动生成，而是手工修改modulegen__gcc_ILP32来添加AnnotatedTopologyReader，运行命令如下：
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
parser.add_argument("--routingName", type=str, choices=["Flooding","BestRoute","MultiPathPairFirst","SCIP","debug"], 
                    default="MultiPathPairFirst", 
                    help="could be Flooding, BestRoute, MultiPath, MultiPathPairFirst")
parser.add_argument("--recordsNumber",type=int,default=100,help="total number of records in trace file")
parser.add_argument("--vis",action="store_true",default=False)

args=parser.parse_args()

manualAssign=True

# ----------------仿真拓扑----------------
topoFileName="topo-for-CompareMultiPath.txt"
#topoFileName="22nodes-2.txt"
topologyReader=AnnotatedTopologyReader("",20.0)
topologyReader.SetFileName("src/ndnSIM/examples/topologies/"+topoFileName)
nodes=topologyReader.Read()

# ----------------协议加载----------------
ndnHelper = ndn.StackHelper()
#ndnHelper.SetOldContentStore("ns3::ndn::cs::Lru","MaxSize","100","","","","","","")
ndnHelper.SetOldContentStore("ns3::ndn::cs::Nocache","","","","","","","","")
ndnHelper.InstallAll();
topologyReader.ApplyOspfMetric()
ndnGlobalRoutingHelper = ndn.GlobalRoutingHelper()
ndnGlobalRoutingHelper.InstallAll()

# ----------------业务加载----------------
consumerList=[]
producerList=[]
if(manualAssign):
    consumerList=["Node0","Node0"]
    producerList=["Node4","Node3"]
else:
    K=int(floor(int(nodes.GetN())/2.0))
    for k in range(K):
        consumerList.append(topologyReader.GetNodeName(nodes.Get(k)))
        producerList.append(topologyReader.GetNodeName(nodes.Get(k+K)))

cHelper = ndn.AppHelper("ns3::ndn::ConsumerCbr")
cHelper.SetAttribute("Frequency", StringValue(args.InterestsPerSec))
pHelper = ndn.AppHelper("ns3::ndn::Producer")
pHelper.SetAttribute("PayloadSize", StringValue("1024"));
'''
2017-10-17 ZhangYu 考虑到多播时的FIB，把prefix改为跟producerName相关，而不是consumerName
'''
for i in range(len(producerList)):
    cHelper.SetPrefix("/"+producerList[i])
    App=cHelper.Install(topologyReader.FindNodeFromName(consumerList[i]))
    #App.Start(Seconds(0.01*i));

    pHelper.SetPrefix("/"+producerList[i])
    ndnGlobalRoutingHelper.AddOrigin("/"+producerList[i], topologyReader.FindNodeFromName(producerList[i]))
    pHelper.Install(topologyReader.FindNodeFromName(producerList[i]))

# ----------------路由和转发----------------
# Calculate and install FIBs
if args.routingName=="Flooding":
    ndnGlobalRoutingHelper.CalculateAllPossibleRoutes()
    for i in range(len(producerList)):
        ndn.StrategyChoiceHelper.InstallAll("/"+producerList[i], "/localhost/nfd/strategy/ncc")
elif args.routingName=="BestRoute":
    ndnGlobalRoutingHelper.CalculateRoutes()
    for i in range(len(producerList)):
        ndn.StrategyChoiceHelper.InstallAll("/"+producerList[i], "/localhost/nfd/strategy/ncc")
elif args.routingName=="MultiPathPairFirst":
    ndnGlobalRoutingHelper.CalculateNoCommLinkMultiPathRoutesPairFirst();
    for i in range(len(producerList)):
        ndn.StrategyChoiceHelper.InstallAll("/"+producerList[i], "/localhost/nfd/strategy/randomized-rounding")
elif args.routingName=="SCIP":
    routeList=mintreeMFP.caculatemaxConcurrentMFPRoute("/topologies/"+topoFileName,consumerList,producerList)
    for i in range(len(routeList)):
        ndnGlobalRoutingHelper.addRouteHop(routeList[i]['edgeStart'],routeList[i]['prefix'],routeList[i]['edgeEnd'],1)
        #print(routeList[i]['edgeStart']+','+routeList[i]['prefix']+','+routeList[i]['edgeEnd'])
    for i in range(len(producerList)):
        ndn.StrategyChoiceHelper.InstallAll("/"+producerList[i], "/localhost/nfd/strategy/randomized-rounding")
elif args.routingName=="debug":
    ndnGlobalRoutingHelper.addRouteHop("Node0","/Node4","Node2",1,0.1);
    ndnGlobalRoutingHelper.addRouteHop("Node2","/Node4","Node4",1,0.1);
    ndnGlobalRoutingHelper.addRouteHop("Node0","/Node4","Node1",1,0.9);
    ndnGlobalRoutingHelper.addRouteHop("Node1","/Node4","Node4",1,0.9);
    for i in range(len(producerList)):
        #ndn.StrategyChoiceHelper.InstallAll("/"+producerList[i], "/localhost/nfd/strategy/multicast")
        ndn.StrategyChoiceHelper.Install(topologyReader.FindNodeFromName(consumerList[i]), "/"+producerList[i], "/localhost/nfd/strategy/randomized-rounding")
else:
    print "Unkown routingName, try again..."

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
#filename=".txt"
TracePerSec=args.recordsNumber
#ndn.CsTracer.InstallAll("cs-trace"+filename, Seconds(TracePerSec))
ndn.L3RateTracer.InstallAll("rate-trace"+filename, Seconds(TracePerSec))
#ndn.AppDelayTracer.InstallAll("app-delays-trace"+filename)
L2RateTracer.InstallAll("drop-trace"+filename,Seconds(TracePerSec))
if args.vis:
    visualizer.start()
Simulator.Run()

Simulator.Destroy()

# ----------------结果处理----------------
import subprocess



