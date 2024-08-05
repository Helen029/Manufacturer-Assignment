# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 15:40:56 2024

@author: Helen Ma
"""

assign = TransportationOptimizer(bom_df, suppliers, distances, weights)
assign.build_model()
assign.solve()
for v in assign.model.getVars():
    #print(v)
    if v.getAttr('x') > 0:
        print(v.getAttr('Varname')[2:-1], v.getAttr('x'), '% allocation')