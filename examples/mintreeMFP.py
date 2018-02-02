# _*_ coding: utf-8 _*_
from pyscipopt import Model, Conshdlr, quicksum , SCIP_RESULT, SCIP_PRESOLTIMING, SCIP_PROPTIMING, SCIP_PARAMSETTING, SCIP_PARAMEMPHASIS
from pyscipopt.scip import Expr, ExprCons, Term
import networkx as nx             #导入networkx包
import re
import numpy as np
import sys

"""
2017-7-26
reference to mfc from PySCIPOpt/examples/finished/atsp.py
The most complex problem based on node flow conservation is Maximum Concurrent Multicommodity Flow Problem (MCFP). I extended the model of MCFP for solving Steiner Tree
the detail see my latex document. 
the if there are only the "C" type Vars, Conshdlr consenfolp don't be called
"""

EPS = 1.e-6

def mintreeMFP(n,e,d):
    """
    mintreeMFP: min Cost Tree based on Flow Conservation 
    Parameters:
        - n: number of nodes
        - e[i,j]['cap','cost']: edges of graph, 'cap': capacity of edge, 'cost': cost for traversing edge (i,j)
        - d[i,j]: demande(data) from node i to j
    Returns a model, ready to be solved.
    """
    print("\n========min Cost Tree based on Flow Conservation======")
    
    model=Model("mintreeMFP")
    x,f,z={},{},{}   # flow variable 
    """
    In our model, f[i,j] is the sum of flow on edge, if f[i,j]>0 then z[i,j]=1 else z[i,j]=0, such that get minTree
    In order to express the logical constraint, define a Big M, and z is Binary, 
    z[i,j]>=f[i,j]/M (gurantee f/M <1) and z[i,j]<=f[i,j]*M (gurantee f[i,j]*M >1)
    """
    M=100000000
    for (i,j) in e.keys():
        f[i,j]=model.addVar(ub=10000,lb=0,vtype="C",name="f[%s,%s]"%(i,j))
        z[i,j]=model.addVar(ub=1,lb=0,vtype="B",name="z[%s,%s]"%(i,j))
        for (s,t) in d.keys():
            x[i,j,s,t]=model.addVar(ub=100,lb=0,vtype="C",name="x[%s,%s,%s,%s]"%(i,j,s,t))
    # node flow conservation
    for (s,t) in d.keys():
        for j in n.keys() :
            # for destination node
            if j==t:
                model.addCons(quicksum(x[i,j,s,t] for i in n.keys() if (i,j) in e.keys()) - 
                              quicksum(x[j,i,s,t] for i in n.keys() if (j,i) in e.keys()) == d[s,t], "DesNode(%s)"%j)
            # for source node
            elif j==s:
                model.addCons(quicksum(x[i,j,s,t] for i in n.keys() if (i,j) in e.keys()) - 
                              quicksum(x[j,i,s,t] for i in n.keys() if (j,i) in e.keys()) == -d[s,t], "SourceNode(%s)"%j)
            else:
                model.addCons(quicksum(x[i,j,s,t] for i in n.keys() if (i,j) in e.keys()) - 
                              quicksum(x[j,i,s,t] for i in n.keys() if (j,i) in e.keys()) == 0, "SourceNode(%s)"%j)
    # constrains for edge capacity, take into consideration of tree optimization, using variable f
    for (i,j) in e.keys():
        f[i,j]=quicksum(x[i,j,s,t] for (s,t) in d.keys())
        model.addCons(f[i,j]<=e[i,j]['cap'],'edge(%s,%s)'%(i,j))
        # logical constraint
        model.addCons(M*z[i,j]>=f[i,j])
        model.addCons(z[i,j]<=f[i,j]*M)

    model.data = x,f
    
    #model.setObjective(quicksum(f[i,j]*e[i,j]['cost'] for (i,j) in e.keys()), "minimize")
    model.setObjective(quicksum(z[i,j] for (i,j) in e.keys()), "minimize")
    return model
            
def maxConcurrentMFP(n,e,d):
    """
    maxConcurrentMFP: max concurrent multi-commodity flow Problem
    Parameters:
        - n: number of nodes
        - e[i,j]['cap','cost']: edges of graph, 'cap': capacity of edge, 'cost': cost for traversing edge (i,j)
        - d[i,j]: demande from node i to j
    Returns a model, ready to be solved.
    """
    print("\n========concurrent multi-commodity flow Problem======")
    model=Model("maxConcurrentMFP")
    x={}  # flow variable 
    lamb=model.addVar(ub=10000,lb=1.0,vtype="C",name="lamb")
    for (i,j) in e.keys():        
        for (s,t) in d.keys():
            x[i,j,s,t]=model.addVar(ub=1000000,lb=0.0,vtype="C",name="x[%s,%s,%s,%s]"%(i,j,s,t))
    # node flow conservation
    for (s,t) in d.keys():
        for j in n.keys():
            # for destination node
            if j==t:
                model.addCons(quicksum(x[i,j,s,t] for i in n.keys() if (i,j) in e.keys()) - 
                              quicksum(x[j,i,s,t] for i in n.keys() if (j,i) in e.keys()) == d[s,t]*lamb, "DesNode(%s)"%j)
            # for source node
            elif j==s:
                model.addCons(quicksum(x[i,j,s,t] for i in n.keys() if (i,j) in e.keys()) - 
                              quicksum(x[j,i,s,t] for i in n.keys() if (j,i) in e.keys()) == -d[s,t]*lamb, "SourceNode(%s)"%j)
            else:
                model.addCons(quicksum(x[i,j,s,t] for i in n.keys() if (i,j) in e.keys()) - 
                              quicksum(x[j,i,s,t] for i in n.keys() if (j,i) in e.keys()) == 0, "SourceNode(%s)"%j)
    # constrains for edge capacity, take into consideration of tree optimization, using variable f
    for (i,j) in e.keys():
        model.addCons(quicksum(x[i,j,s,t] for (s,t) in d.keys())<=e[i,j]['cap'],'edge(%s,%s)'%(i,j))    
    model.data = x
    
    model.setObjective(lamb, "maximize")
    return model

def MaxMFP(n,e,d):
    """
    MaxMFP: Max sum multi-commodity flow Problem
    Parameters:
        - n: number of nodes
        - e[i,j]['cap','cost']: edges of graph, 'cap': capacity of edge, 'cost': cost for traversing edge (i,j)
        - d[i,j]: demande from node i to j
    Returns a model, ready to be solved.
    """
    print("\n========Max multi-commodity flow Problem======")
    model=Model("MaxMFP")
    x,vard={},{}  # flow variable
    for (s,t) in d.keys():
        vard[s,t]=model.addVar(ub=10000,lb=0.0,vtype="C",name="vard[%s,%s]"%(s,t)) 
    for (i,j) in e.keys():        
        for (s,t) in d.keys():
            x[i,j,s,t]=model.addVar(ub=1000,lb=0.0,vtype="C",name="x[%s,%s,%s,%s]"%(i,j,s,t))
    # node flow conservation
    for (s,t) in d.keys():
        for j in n.keys():
            # for destination node
            if j==t:
                model.addCons(quicksum(x[i,j,s,t] for i in n.keys() if (i,j) in e.keys()) - 
                              quicksum(x[j,i,s,t] for i in n.keys() if (j,i) in e.keys()) == vard[s,t], "DesNode(%s)"%j)
            # for source node
            elif j==s:
                model.addCons(quicksum(x[i,j,s,t] for i in n.keys() if (i,j) in e.keys()) - 
                              quicksum(x[j,i,s,t] for i in n.keys() if (j,i) in e.keys()) == -vard[s,t], "SourceNode(%s)"%j)
            else:
                model.addCons(quicksum(x[i,j,s,t] for i in n.keys() if (i,j) in e.keys()) - 
                              quicksum(x[j,i,s,t] for i in n.keys() if (j,i) in e.keys()) == 0, "SourceNode(%s)"%j)
    # constrains for edge capacity, take into consideration of tree optimization, using variable f
    for (i,j) in e.keys():
        model.addCons(quicksum(x[i,j,s,t] for (s,t) in d.keys())<=e[i,j]['cap'],'edge(%s,%s)'%(i,j))    
    model.data = x,vard
    
    model.setObjective(quicksum(vard[s,t] for (s,t) in d.keys()), "maximize")
    return model
def readTopology(filename,cap=None): 
    # ZhangYu 2018-1-28使用SCIP计算时，发现这里没有设置是否无向图， 而Matlab有这个选项
    isUndirectedGraph=True   
    mark=["router\n","link\n"]
    try:
        filehandle = open(sys.path[0]+filename,'r')
    except:
        print("Could not open file " + sys.path[0]+filename)
        quit()
    filelines=filehandle.readlines()
    markPos=[]
    for i in range(len(mark)):
        markPos.append(filelines.index(mark[i]))
    # read edges
    edge,node={},{}
    for aline in filelines[markPos[1]+1:]:
        if str(aline).startswith('#') | str(aline).startswith(' ') | str(aline).startswith('\n'):
            continue
        else:
            alineArray=str(aline).split()
            if cap is None:
                # 这里允许节点是诸如 UCLA-A这样的名字
                edge[str(alineArray[0]),
                     str(alineArray[1])]={'cap':re.findall(
                         "\d+",str(alineArray[2]))[0],'cost':re.findall("\d+",str(alineArray[3]))[0]}
            else:
                edge[str(alineArray[0]),
                     str(alineArray[1])]={'cap':cap,'cost':re.findall("\d+",str(alineArray[3]))[0]}
            if isUndirectedGraph:
                edge[str(alineArray[1]),str(alineArray[0])]=edge[str(alineArray[0]),str(alineArray[1])]
                
    # read nodes. G can be get only by edges, we read nodes here because we need the nodes coordinate for drawing graph
    for aline in filelines[markPos[0]+1:markPos[1]]:
        if str(aline).startswith('#') | str(aline).startswith(' ') | str(aline).startswith('\n'):
            continue
        else:
            alineArray=str(aline).split()
            node[str(alineArray[0])]=np.array(
                [int(re.findall("\d+", str(alineArray[3]))[0]),int(re.findall("\d+", str(alineArray[2]))[0])])
            #pos['1']=np.array([4,5])
    
    if __name__=="__main__":
        import matplotlib.pyplot as plt
        G=nx.DiGraph()
        G.add_nodes_from(node)
        G.add_edges_from(edge.keys())    
        
        # Draw nodes
        nx.draw_networkx_nodes(G, node,node_size=900, node_color='orange')
        nx.draw_networkx_labels(G, node,font_size=10, font_family='sans-serif')
        
        # Draw edges
        nx.draw_networkx_edges(G,node, arrows=True,width=1.5, edge_color='g')
        
        # Draw edge labels
        #edge_labels = dict([((u, v), d['label'])
        #                    for u, v, d in G.edges(data=True)])
        #nx.draw_networkx_edge_labels(G, pos,edge_labels=edge_labels)
        
        plt.axis('off')  # 是否打开坐标系on/off
        #plt.savefig("lyy_graph.eps", format='eps')  # save as eps
        plt.show()
    
    return edge,node
def caculatemaxConcurrentMFPRoute(filename,consumerList,producerList):
    # Traffic Matrix d[1,5] represent interest from node 1 to node 5
    e,n=readTopology(filename)
    d={}
    for i in range(len(consumerList)):
        d[consumerList[i],producerList[i]]=1
    model=maxConcurrentMFP(n, e, d)
    model.hideOutput()
    model.optimize()
    lamb=model.getObjVal()
    print "  ------------variant lambda is:",lamb 
    for v in model.getVars():
        if model.getVal(v)>EPS:
            print('{0}={1}'.format(v.name,model.getVal(v)))
            
    x = model.data
    edgesUsed={}
    for(i,j) in e.keys():
        totalTraffic=0
        for (s,t) in d.keys():
            totalTraffic=totalTraffic+model.getVal(x[i,j,s,t])
        edgesUsed[i,j]={'totalTraffic':totalTraffic}
        
    routeList=[]
    probability=1.0
    for (s,t) in d.keys():
        for (i,j) in e.keys() :
            if(model.getVal(x[i,j,s,t])>EPS):
                r={'edgeStart':i,'edgeEnd':j,'prefix':"/"+t,'cost':1.0, 'probability':
                   (model.getVal(x[i,j,s,t])/edgesUsed[i,j]['totalTraffic'])}
                routeList.append(r)
    return routeList
def caculateMaxMFPRoute(filename,consumerList,producerList):
    # Traffic Matrix d[1,5] represent interest from node 1 to node 5
    e,n=readTopology(filename)
    d={}
    for i in range(len(consumerList)):
        d[consumerList[i],producerList[i]]=1
    model=maxConcurrentMFP(n, e, d)
    model.hideOutput()
    model.optimize()
    lamb=model.getObjVal()
    print "  ------------variant lambda is:",lamb 
    for v in model.getVars():
        if model.getVal(v)>EPS:
            print('{0}={1}'.format(v.name,model.getVal(v)))
            
    x = model.data
    routeList=[]
    for (s,t) in d.keys():
        for (i,j) in e.keys() :
            if(model.getVal(x[i,j,s,t])>EPS):
                d={'edgeStart':i,'prefix':"/"+t,'edgeEnd':j}
                routeList.append(d)
                #print('edgeUsed({0},{1})={2}',format(i,j,z[i,j]))
    return routeList
def TenNodesTopology():
    isUndirectedGraph=True
    n=dict()
    for i in range(1,10):
        n[i]=1
    e,d={},{}
    e[1,2]={'cap':10,'cost':2}
    e[1,3]={'cap':10,'cost':2}
    e[1,4]={'cap':10,'cost':2}
    e[1,5]={'cap':10,'cost':2}
    e[1,6]={'cap':10,'cost':2}
    e[2,3]={'cap':10,'cost':2}
    e[2,6]={'cap':10,'cost':2}
    e[3,4]={'cap':10,'cost':2}
    e[3,6]={'cap':10,'cost':2}
    e[4,5]={'cap':10,'cost':2}
    e[4,6]={'cap':10,'cost':2}
    e[5,6]={'cap':10,'cost':2}
    e[7,1]={'cap':10,'cost':2}
    e[7,3]={'cap':10,'cost':2}
    e[8,1]={'cap':10,'cost':2}
    e[8,5]={'cap':10,'cost':2}
    e[9,2]={'cap':10,'cost':2}
    e[9,3]={'cap':10,'cost':2}
    e[9,4]={'cap':10,'cost':2}
    e[9,5]={'cap':10,'cost':2}
    e[10,9]={'cap':10,'cost':2}
    e[10,6]={'cap':10,'cost':2}
    e[10,1]={'cap':10,'cost':2}    
    d[1,3]=1
    d[1,5]=1
    d[9,6]=1
    d[7,1]=1
    #d[2,6]=1
    #d[4,6]=1
    if isUndirectedGraph:
        for (i,j) in e.keys():
            e[j,i]=e[i,j]
    return n,e,d
def SixNodesTopology():
    n=6
    e,d={},{}
    e[0,1]={'cap':10,'cost':2}
    e[0,2]={'cap':10,'cost':2}
    e[0,5]={'cap':10,'cost':2}
    e[5,3]={'cap':10,'cost':2}
    e[1,4]={'cap':10,'cost':2}
    e[2,4]={'cap':10,'cost':2}
    e[2,3]={'cap':10,'cost':2}
    # Traffic Matrix d[1,5] represent data from node 1 to node 5
    d['Node0','Node4']=1
    #d['Node0','Node3']=1

if __name__ == "__main__":
    '''
    filename="50Nodes-5.txt"
    e,n=readTopology("/topologies/"+filename)
    d={}
 
    d['Node3','Node22']=1
    d['Node5','Node24']=1
    d['Node21','Node6']=1
    d['Node4','Node6']=1
    d['Node3','Node19']=1
    '''
    n,e,d=TenNodesTopology()
    '''
    d['Node4','Node0']=1
    d['Node3','Node0']=1
   '''    
    '''
    model=mintreeMFP(n,e,d)
    model.hideOutput()
    model.optimize()
    maxFlow = model.getObjVal()
    print "  ----------minTreeMFP Optimal value: ",maxFlow

    for v in model.getVars():
        if model.getVal(v)>EPS:
            print('{0}={1}'.format(v.name,model.getVal(v)))
    
    x,f = model.data
    edgeflow={}
    for (i,j) in e.keys() :
        edgeflow[i,j]=0

        for (s,t) in d.keys():
            edgeflow[i,j]=edgeflow[i,j]+ model.getVal(x[i,j,s,t])
        if (edgeflow[i,j]>EPS):
            print('edgeflow({0},{1})={2}'.format(i,j,edgeflow[i,j]))
            #print('edgeUsed({0},{1})={2}',format(i,j,z[i,j]))
    '''
    model=maxConcurrentMFP(n, e, d)
    model.hideOutput()
    model.optimize()
    lamb=model.getObjVal()
    print "  ---------maxConcurrentMFP variant lambda is:",lamb 
    for v in model.getVars():
        if model.getVal(v)>EPS:
            print('{0}={1}'.format(v.name,model.getVal(v)))
    
    model=MaxMFP(n, e, d)
    model.hideOutput()
    model.optimize()
    maxFlow=model.getObjVal()
    print "  ------------MaxMFP Optimal value: ",maxFlow
    x,vard=model.data
    for (s,t) in d.keys():
        if(d[s,t]>EPS):
            print('Flow({0},{1})={2}'.format(s,t,model.getVal(vard[s,t])))
            for (i,j) in e.keys():
                if(model.getVal(x[i,j,s,t])>EPS):
                    print('x[{0},{1},{2},{3}]={4}'.format(i,j,s,t,model.getVal(x[i,j,s,t])))
