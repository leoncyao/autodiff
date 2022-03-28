import sys
import os
from astvisualizer import main
import parser


symbols = {'add' : "+", 'subtract': "-", "mult": "*", "div": "/"}

str_reps = {}

def dict_to_str(expr):

    expr_type = expr['node_type']

    if expr_type == 'name':
        var = expr['id']
        if var in str_reps:
            return str_reps[var]
        else:
            return expr['id']
    elif expr_type == 'constant':
        return expr['value']
    elif expr_type == 'num':
        return expr['n']
    elif expr_type == 'call':
        # Assume all elemetary functions take one derivative
        func_type = expr['func']['id']
        inner_expr_str = dict_to_str(expr['args'][0])
        return '{}({})'.format(func_type, inner_expr_str)
    elif expr_type == 'bin_op':
        # print("trying to convert ", expr)
        left_str= dict_to_str(expr['left'])
        right_str = dict_to_str(expr['right'])

        return '({}{}{})'.format(left_str, symbols[expr['op']['node_type']], right_str)

# memoization
derivatives = {}

def derive(expr, input_var, output_var=None):
    #     '''
    #     Returns string containg symbolic derivative of expr with respect to input_var
    #             Parameters:
    #                     arg1 (int): A decimal integer
    #                     arg2 (int): Another decimal integer
    #                     input_var :
    #                     op :

    #             Returns:
    #                     d/dx (arg1 <op> arg2 ): derivative of 
    #     '''
    
    # if output_var:
    #     if output_var in derivatives:
    #         return derivatives[output_var]
    
    expr_type = expr['node_type']

    if expr_type == 'name':
        var = expr['id']
        if expr['id'] == input_var:
            return '1'
        elif var in derivatives:
            return derivatives[var]
    elif expr_type == 'constant' or expr_type == 'num':
        return '0'
    elif expr_type == 'call':
        # Assume all elemetary functions take one derivative
        inner_expr = expr['args'][0]
        inner_derivative = derive(inner_expr, input_var)

        func_type = expr['func']['id']
        # support only elementary functions
        outside_func = ''
        if func_type == 'cos':
            outside_func = '-sin'
        if func_type == 'sin':
            outside_func = 'cos'
        if func_type == 'exp':
            outside_func = 'exp'

        return '{}({})*({})'.format(outside_func, dict_to_str(inner_expr), inner_derivative)
    elif expr_type == 'bin_op':
        bin_op_type = expr['op']
        left_derivative = derive(expr['left'], input_var)
        right_derivative = derive(expr['right'], input_var)
        
        left_expr = dict_to_str(expr['left'])
        right_expr = dict_to_str(expr['right'])

        # print(left_expr)
        # print(right_expr)
        # print("op type is ", bin_op_type)

        if bin_op_type['node_type'] == 'add':
            return '({}+{})'.format(left_derivative, right_derivative)
        elif bin_op_type['node_type'] == 'subtract':
            return '({}-{})'.format(left_derivative, right_derivative)
        elif bin_op_type['node_type'] == 'mult':
            return '(({})*({}) + ({})*({}))'.format(left_derivative, right_expr, left_expr, right_derivative)
        elif bin_op_type['node_type'] == 'div':
            return '((({})*({}) - ({})*({}))/({})**2)'.format(left_derivative, right_expr, left_expr, right_derivative, right_expr)
    
tree = main(sys.argv)
script_body = tree['body']

# first find function f, assume f is the first function in the script
i = 0
for line in script_body:
    if line['node_type'] == 'function_def':
        break
    i += 1

function_body = tree['body'][i]['body']

# assume only 1 argument
# assume powers of x are constant with respect to x cause i don't remember
# how to differentiate x^x
x = tree['body'][i]['args']['args'][0]['arg']


for i in range(len(function_body)):
    line = function_body[i]
    if line['node_type'] == 'assign':
        var_name = line['targets'][0]['id']
        str_reps[var_name] = dict_to_str(line['value'])
        derivatives[var_name] = derive(line['value'], x, var_name)

input_point = 1

#  need to find the output variable
# for var in derivatives:


# assume final return variable is named 'y'

with open('output.py', 'w') as f:
    f.write("from math import *\n")
    f.write("x = {}\n".format(input_point))
    f.write("print({})".format(derivatives['y']))
    f.close()
    
os.system('python3 output.py')