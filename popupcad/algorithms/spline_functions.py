# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>asu.edu.
Please see LICENSE for full license.
"""

import numpy
import matplotlib.pyplot as plt

def N0(i,knots):
    if i==numpy.array(knots).argmax()-1:
        def f(q):
            return (q>=knots[i])*(q<=knots[i+1])*1
    else:
        def f(q):
            return (q>=knots[i])*(q<knots[i+1])*1
    return f

def Nip(i,p,knots,N,calculated):
    def f(q):
        calc = calculated[p][i]
        if calc is None:
            r1 = (knots[i+p]-knots[i])
            r2 = (knots[i+p+1]-knots[i+1])
            if r1==0:
                c=q*0
            else:
                c = (q-knots[i])/r1
    
            if r2==0:
                d = q*0
            else:
                d = (knots[i+p+1]-q)/r2
    
            A = c*N[p-1][i](q)
            B = d*N[p-1][i+1](q)
            
            calculated[p][i] = A+B
    
            return A + B
        else:
            return calc
    return f

def calc_spline(knots,n,w,domain):
    m = len(knots)-1

    p = m-n-1
    
    if len(w)!=n+1:
        w = [1]*(n+1)
        
    N=[]
    calculated = []
    for ii in range(p+1):
        N.append([0]*(m-ii))
        calculated.append([None]*(m-ii))
        
    for ii in range(m):
        N[0][ii]=N0(ii,knots)
    
    for jj in range(m)[1:p+1]:
        for ii in range(m-jj):
            N[jj][ii]=Nip(ii,jj,knots,N,calculated)  
    
    calculated_spline = numpy.array([n(domain)*weight for n,weight in zip(N[p],w)]).T
    return calculated_spline

def interpolated_points(points,knots,w,domain):
    n = len(points)-1
    y = calc_spline(knots,n,w,domain)
    points = numpy.array(points)
    weights = y.sum(1)
    interpolated_points = y.dot(points)
    interpolated_points = (interpolated_points.T/weights).T
    return interpolated_points
    
def make_domain(knots,num_segments):
    domain = numpy.r_[min(knots):max(knots):(num_segments+1)*1j]    
    return domain

def plot_labeled_points(cp):
    labels = ['cp{0}'.format(i) for i in range(len(cp))]
    plt.plot(*cp.T,marker = 'o', linestyle = '')
    bbox1 = {'boxstyle':'round,pad=0.5', 'fc':'yellow', 'alpha':1}
    for label, (x,y) in zip(labels,cp):
        plt.annotate(label, xy = (x, y), xytext = (-20, 20), textcoords = 'offset points', ha = 'right', va = 'bottom', bbox = bbox1, arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

def control_from_fit_points(fp,p,plot = True):
    import scipy.linalg
    
    r = len(fp)-1
    middle = numpy.r_[1:r]
    knots = numpy.r_[[0]*(p+1),middle,[r]*(p+1)]
    m = len(knots)-1
    n = m-p-1
    w = [1]*(n+1)
    
    domain = numpy.r_[0:r+1]
    y = calc_spline(knots,n,w,domain)
    yi = scipy.linalg.pinv(y)
    
    fp = numpy.array(fp)
    
    cp2 = yi.dot(fp)
    if plot:
        plt.plot(domain,y)
    
    return cp2,knots

if __name__=='__main__':
    cp = [[0.0, 0.0], [0.3333333333333333, 0.0], [1.423076923076923, -0.4230769230769232], [0.5192307692307694, 1.480769230769231], [2.5, 0.4999999999999999], [1.480769230769231, 2.519230769230769], [3.576923076923078, 1.423076923076924], [2.666666666666667, 3.0], [3.0, 3.0]]
    fp = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [2.0, 1.0], [2.0, 2.0], [3.0, 2.0], [3.0, 3.0]]
    knots = [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 6.0, 6.0, 6.0]

    w = [1]*len(cp)
#    w[4]=3
    points = cp
    n = len(points)-1
    
    domain = make_domain(knots,600)
    y = calc_spline(knots,n,w,domain)
    plt.plot(domain,y)
    plt.figure()
    plot_labeled_points(numpy.array(cp))
    points = interpolated_points(points,knots,w,domain)
    plt.plot(*points.T)
