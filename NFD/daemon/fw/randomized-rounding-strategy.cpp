/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/**
 * Copyright (c) 2014,  Regents of the University of California,
 *                      Arizona Board of Regents,
 *                      Colorado State University,
 *                      University Pierre & Marie Curie, Sorbonne University,
 *                      Washington University in St. Louis,
 *                      Beijing Institute of Technology,
 *                      The University of Memphis
 *
 * This file is part of NFD (Named Data Networking Forwarding Daemon).
 * See AUTHORS.md for complete list of NFD authors and contributors.
 *
 * NFD is free software: you can redistribute it and/or modify it under the terms
 * of the GNU General Public License as published by the Free Software Foundation,
 * either version 3 of the License, or (at your option) any later version.
 *
 * NFD is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * NFD, e.g., in COPYING.md file.  If not, see <http://www.gnu.org/licenses/>.
 *
 * 2018-2-2 在random-load-balancer-strategy的基础上修改而成，但如果放在example下，python代码的主程序不能正常工作
 * 所以参考了BestRoute的代码添加了注册，移动到NFD/Daemon/fw下，c++和Python都可以正常运行
 */

#include "randomized-rounding-strategy.hpp"

#include <boost/random/uniform_int_distribution.hpp>

#include <ndn-cxx/util/random.hpp>

#include "core/logger.hpp"

NFD_LOG_INIT("RandomizedRoundingStrategy");

namespace nfd {
namespace fw {

const Name
  RandomizedRoundingStrategy::STRATEGY_NAME("ndn:/localhost/nfd/strategy/randomized-rounding/%FD%01");
// ZhangYu 2018-2-2 看到bestRoute有就加上了，否则不能加载策略
NFD_REGISTER_STRATEGY(RandomizedRoundingStrategy);

RandomizedRoundingStrategy::RandomizedRoundingStrategy(Forwarder& forwarder, const Name& name)
  : Strategy(forwarder, name)
{
}

RandomizedRoundingStrategy::~RandomizedRoundingStrategy()
{
}

static bool
canForwardToNextHop(const Face& inFace, shared_ptr<pit::Entry> pitEntry, const fib::NextHop& nexthop)
{
  return !wouldViolateScope(inFace, pitEntry->getInterest(), nexthop.getFace()) &&
    canForwardToLegacy(*pitEntry, nexthop.getFace());
}

static bool
hasFaceForForwarding(const Face& inFace, const fib::NextHopList& nexthops, const shared_ptr<pit::Entry>& pitEntry)
{
  return std::find_if(nexthops.begin(), nexthops.end(), bind(&canForwardToNextHop, cref(inFace), pitEntry, _1))
         != nexthops.end();
}

void
RandomizedRoundingStrategy::afterReceiveInterest(const Face& inFace, const Interest& interest,
                                                 const shared_ptr<pit::Entry>& pitEntry)
{
  NFD_LOG_TRACE("afterReceiveInterest");

  if (hasPendingOutRecords(*pitEntry)) {
    // not a new Interest, don't forward
    return;
  }

  const fib::Entry& fibEntry = this->lookupFib(*pitEntry);
  const fib::NextHopList& nexthops = fibEntry.getNextHops();	//端口列表

  // Ensure there is at least 1 Face is available for forwarding
  if (!hasFaceForForwarding(inFace, nexthops, pitEntry)) {
    this->rejectPendingInterest(pitEntry);
    return;
  }

  boost::random::uniform_01<boost::random::mt19937&> dist(m_randomGenerator);
  dist.reset();
  //std::cout << "ZhangYu 2018-3-25 randomValue: " << dist() << std::endl;
  const uint64_t randomValue =std::round(dist() *1000000); //和 global-routing-help中的一样
  //std::cout << "ZhangYu 2018-3-25 randomValue: " << randomValue << std::endl;
  uint64_t probabilitySum=0;
  fib::NextHopList::const_iterator selected;	//端口变量
  uint64_t index=0;
  for(selected=nexthops.begin(); selected !=nexthops.end(); ++selected) {
	  index=index+1;
	  if(canForwardToNextHop(inFace, pitEntry, *selected)){
		  probabilitySum+=selected->getProbability();
		  if(randomValue<probabilitySum){
			  this->sendInterest(pitEntry, selected->getFace(), interest);
			  /*
			  std::cout << "      ZhangYu 2018-2-1 afterReceiveInterest-- "
					  << " face: " << selected->getFace()
					  << " cost: " << selected->getCost()
					  << " probability: " << selected->getProbability() << std::endl;

			  //std::cout << "!!ZhangYu 2018-3-25, index:" << index << std::endl;
			  */
			  return;
		  }
  	  }
  }
}

} // namespace fw
} // namespace nfd
