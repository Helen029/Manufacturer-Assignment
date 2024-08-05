# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 14:54:29 2024

@author: Helen Ma
"""

class TransportationOptimizer():
    
    def __init__(self,
                 bom_df,
                 suppliers,
                 distances,
                 weights,
                 min_supply = 0):
        '''
        Inputs:
        - bom: dataframe with every part that must be allocated
        - suppliers: all suppliers that supply each part
        - dist: distance matrix between each manufacturer pair
        = weights:
        - min_supply: minimum percent of a part to allocate to a supplier
        '''
        self.bom_df = bom_df
        self.suppliers = suppliers
        self.dist = distances
        self.weights = weights
        self.min_supply = min_supply

        self.parts = self.bom_df['Final Part Number'].tolist()
        self.manufs = self.dist.index.tolist() #all manufacturers
        self.M = 101

    def build_model(self):
        '''
        Creates the LP Model
        '''
        self.model = Model('IP')
        #self.model.setParam('MIPGap', .05)
        
        #initialize decision vars
        self.init_dv()
        self.model.update()
        #Add constraints
        self.add_constraints()
        self.model.update()
        #Set objective
        self.set_objective()
        self.model.update()
                 
    def init_dv(self):
        '''
        Defines decision vars
        '''
        # Define x(i,j, k) indicating the allocation of part i from manuf j to k
        self.x = {}
        for i in self.parts:
            for j in self.suppliers.loc[self.suppliers['Final Part Number'] == i, 'Manufacturer']:
                for k in self.suppliers.loc[
                    self.suppliers['Final Part Number'] 
                    == self.bom_df.loc[self.bom_df['Final Part Number'] == i, 'Parent'].values[0], 
                    'Manufacturer'].to_list():
                    
                    self.x[i,j,k] = self.model.addVar(lb = 0, ub = 100, vtype = GRB.INTEGER, name = 'x' + str([i,j,k]))
        
        # Define y(i,j,k) indicating if allocation of part i is nonzero from manuf j to k
        self.y = {}
        for i in self.parts:
            for j in self.suppliers.loc[self.suppliers['Final Part Number'] == i, 'Manufacturer']:
                for k in self.suppliers.loc[
                    self.suppliers['Final Part Number'] 
                    == self.bom_df.loc[self.bom_df['Final Part Number'] == i, 'Parent'].values[0], 
                    'Manufacturer'].to_list():
                    
                    self.y[i,j,k] = self.model.addVar(lb = 0,ub = 1, vtype = GRB.BINARY, name = 'y' + str([i,j,k]))
                 
    def add_constraints(self):
        '''
        Adds all constraints
        '''
        self.add_whole_constraint()
        self.add_y_constraint()
        #self.add_min_constraint()
    
                 
    def add_whole_constraint(self):
        '''
        Add constraint to ensure that allocation across manufacturers for each part sums to 100
        '''
        for i in self.parts:
            self.model.addConstr(quicksum(self.x[i,j,k] 
                                          for j in self.suppliers.loc[self.suppliers['Final Part Number'] == i, 'Manufacturer'] 
                                          for k in self.suppliers.loc[
                    self.suppliers['Final Part Number'] 
                    == self.bom_df.loc[self.bom_df['Final Part Number'] == i, 'Parent'].values[0], 
                    'Manufacturer'].to_list()) == 100 )
    
    def add_y_constraint(self):
        '''
        Add constraint that defines binary y in relation to x
        '''
        for i in self.parts:
            for j in self.suppliers.loc[self.suppliers['Final Part Number'] == i, 'Manufacturer']:
                for k in self.suppliers.loc[
                    self.suppliers['Final Part Number'] 
                    == self.bom_df.loc[self.bom_df['Final Part Number'] == i, 'Parent'].values[0], 
                    'Manufacturer'].to_list():
                    
                    self.model.addConstr(self.x[i,j,k] >= self.y[i,j,k])
        
        for i in self.parts:
            for j in self.suppliers.loc[self.suppliers['Final Part Number'] == i, 'Manufacturer']:
                for k in self.suppliers.loc[
                    self.suppliers['Final Part Number'] 
                    == self.bom_df.loc[bom_df['Final Part Number'] == i, 'Parent'].values[0], 
                    'Manufacturer'].to_list():
                    
                    self.model.addConstr(self.x[i,j,k] <= self.M*self.y[i,j,k])
    
    def add_min_constraint(self):
        '''
        add constraint that enforces minimum for select manufacturers
        '''
        for i in self.parts:
            for j in self.suppliers.loc[self.suppliers['Final Part Number'] == i, 'Manufacturer']:
                for k in self.suppliers.loc[
                    self.suppliers['Final Part Number'] 
                    == self.bom_df.loc[bom_df['Final Part Number'] == i, 'Parent'].values[0], 
                    'Manufacturer'].to_list():
                    self.model.addConstr(self.x[i,j,k] >= min_supply)
                
    def add_flow_constraint(self):
        '''
        add constraint that maintains flow balance; i.e. parts can only be sent out of a supplier with supply for it
        '''
        #for j in manufs:
            #for k in manufs:
    
    
    def set_objective(self):
        '''
        Sets objective for LP
        '''
        self.model.setObjective(sum(self.dist.loc[j,k] * 
            self.x[i,j,k] + self.y[i,j,k]
                                    for i in self.parts
                                    for j in self.suppliers.loc[self.suppliers['Final Part Number'] == i, 'Manufacturer'] 
                                    for k in self.suppliers.loc[
                    self.suppliers['Final Part Number'] 
                    == self.bom_df.loc[self.bom_df['Final Part Number'] == i, 'Parent'].values[0], 
                    'Manufacturer'].to_list()), 
            GRB.MINIMIZE)
        
        self.model.update()
    
    def solve(self):
        '''
        Function to solve the LP
        '''
        self.model.params.outputFlag = 0
        self.model.optimize()
        print('Objective Value: ', self.model.ObjVal)
        
        return
    