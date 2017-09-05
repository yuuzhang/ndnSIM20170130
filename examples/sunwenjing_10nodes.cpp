/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/**
 * Copyright (c) 2011-2015  Regents of the University of California.
 *
 * This file is part of ndnSIM. See AUTHORS for complete list of ndnSIM authors and
 * contributors.
 *
 * ndnSIM is free software: you can redistribute it and/or modify it under the terms
 * of the GNU General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 *
 * ndnSIM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * ndnSIM, e.g., in COPYING.md file.  If not, see <http://www.gnu.org/licenses/>.
 **/

// ndn-multiple-strategies.cpp

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/point-to-point-layout-module.h"
#include "ns3/ndnSIM-module.h"

namespace ns3{


/**
 * This scenario simulates a grid topology (using PointToPointGrid module)
 *
 * In this scenario, thanks to NFD, we can choose a different forwarding
 * strategy for each prefix in each node.
 *
 * (consumer1) -- ( ) -- (producer2)
 *     |          |         |
 *    ( ) ------ ( ) ----- ( )
 *     |          |         |
 * (consumer2) -- ( ) -- (producer1)
 *
 * All links are 1Mbps with propagation 10ms delay.
 *
 * FIB is populated using NdnGlobalRoutingHelper.
 *
 * Consumer requests data from producer with frequency 100 interests per second
 * (interests contain constantly increasing sequence number).
 *
 * For every received interest, producer replies with a data packet, containing
 * 1024 bytes of virtual payload.
 *
 * To run scenario and see what is happening, use the following command:
 *
 *     NS_LOG=ndn.Consumer:ndn.Producer ./waf --run=ndn-different-strategy-per-prefix
 */

int
main(int argc, char* argv[])
{
  CommandLine cmd;
  cmd.Parse(argc, argv);

  AnnotatedTopologyReader topologyReader("", 20);
  topologyReader.SetFileName("src/ndnSIM/examples/topologies/4node-2path.txt");
  topologyReader.Read();

  // Install NDN stack on all nodes
  ndn::StackHelper ndnHelper;
ndnHelper.SetOldContentStore("ns3::ndn::cs::Lru", "MaxSize", "50");
  ndnHelper.InstallAll();

  // Installing global routing interface on all nodes
  ndn::GlobalRoutingHelper ndnGlobalRoutingHelper;
  ndnGlobalRoutingHelper.InstallAll();

 // Getting containers for the consumer/producer
 
Ptr<Node> consumer1 = Names::Find<Node>("Node1");
//Ptr<Node> consumer2 = Names::Find<Node>("Node2");
//Ptr<Node> consumer3 = Names::Find<Node>("Node4");
//Ptr<Node> consumer4 = Names::Find<Node>("Node5");

 Ptr<Node> producer1 = Names::Find<Node>("Node3");
// Ptr<Node> producer2 = Names::Find<Node>("Node0");
// Ptr<Node> producer3 = Names::Find<Node>("Node7");
// Ptr<Node> producer4 = Names::Find<Node>("Node8");

  //NodeContainer consumerNodes;
  //consumerNodes.Add(Names::Find<Node>("Node0"));
// consumerNodes.Add(Names::Find<Node>("Node8"));



  // Define two name prefixes
  std::string prefix1 = "/prefix1";
//  std::string prefix2 = "/prefix2";
//  std::string prefix3 = "/prefix3";
//  std::string prefix4 = "/prefix4";

  // Install different forwarding strategies for prefix1, prefix2
  ndn::StrategyChoiceHelper::InstallAll(prefix1, "/localhost/nfd/strategy/multicast");
//  ndn::StrategyChoiceHelper::InstallAll(prefix2, "/localhost/nfd/strategy/best-route");
//  ndn::StrategyChoiceHelper::InstallAll(prefix3, "/localhost/nfd/strategy/multicast");
//  ndn::StrategyChoiceHelper::InstallAll(prefix4, "/localhost/nfd/strategy/best-route");

  // Install NDN applications
ndn::AppHelper consumerHelper("ns3::ndn::ConsumerZipfMandelbrot");
  consumerHelper.SetAttribute("q", StringValue("0"));
  consumerHelper.SetAttribute("s", StringValue("1.0"));
  consumerHelper.SetAttribute("NumberOfContents", StringValue("500"));

  consumerHelper.SetPrefix(prefix1);
consumerHelper.SetAttribute("Frequency", StringValue("450")); // 100 interests a second
  consumerHelper.Install(consumer1);

//  consumerHelper.SetPrefix(prefix2);
//consumerHelper.SetAttribute("Frequency", StringValue("450")); // 100 interests a second
//  consumerHelper.Install(consumer2);
//
// consumerHelper.SetPrefix(prefix3);
//consumerHelper.SetAttribute("Frequency", StringValue("450")); // 100 interests a second
//  consumerHelper.Install(consumer3);
//
//  consumerHelper.SetPrefix(prefix4);
//consumerHelper.SetAttribute("Frequency", StringValue("450")); // 100 interests a second
//  consumerHelper.Install(consumer4);

  ndn::AppHelper producerHelper("ns3::ndn::Producer");
  producerHelper.SetAttribute("PayloadSize", StringValue("1024"));
  producerHelper.SetPrefix(prefix1);
  producerHelper.Install(producer1);

//  producerHelper.SetPrefix(prefix2);
//  producerHelper.Install(producer2);
//
//  producerHelper.SetPrefix(prefix3);
//  producerHelper.Install(producer3);
//
//  producerHelper.SetPrefix(prefix4);
//  producerHelper.Install(producer4);

  // Add /prefix1 and /prefix2 origins to ndn::GlobalRouter
  ndnGlobalRoutingHelper.AddOrigins(prefix1, producer1);
//  ndnGlobalRoutingHelper.AddOrigins(prefix2, producer2);
//  ndnGlobalRoutingHelper.AddOrigins(prefix3, producer3);
//  ndnGlobalRoutingHelper.AddOrigins(prefix4, producer4);

  // Calculate and install FIBs
  ndn::GlobalRoutingHelper::CalculateAllPossibleRoutes();

  Simulator::Stop(Seconds(60.0));


 ndn::L3RateTracer::InstallAll("9nodes-450-rate-trace.txt", Seconds(1));
 
ndn::CsTracer::InstallAll("9nodes-450-cs-trace.txt", Seconds(1));
  
 ndn::AppDelayTracer::InstallAll("9nodes-450-app-delays-trace.txt");


  Simulator::Run();
  Simulator::Destroy();

  return 0;
}

} // namespace ns3

int
main(int argc, char* argv[])
{
  return ns3::main(argc, argv);
}

