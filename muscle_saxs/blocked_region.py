#!/usr/bin/env python
# encoding: utf-8
"""
blocked_region.py - find the blocked region and return its location

Created by CDW on 2015.03.13
"""


# System imports
import warnings
import numpy as np
import cv2
import matplotlib.pyplot as plt


## Contour processing
def find_blocked_region(img, plot=False, min_size=5):
    """Locate the centrally blocked region of the image.
    Given an image, find the center region where the blocker is, defined as
    the inner-most (and roundest) area with pixel values less than two
    standard deviations from the mean pixel value.
    
    Parameters
    ----------
    img : numpy.array 
        greyscale diffraction image
    plot : boolean, optional
        whether to plot outcome, or axis to plot to (false by default)
    min_size : int, optional
        don't accept a blocked region below this size in pixels (5 by default)
    
    Returns
    -------
    center : tuple 
        (x,y) value locations of the center of the blocked region
    radius :
        the radius of the blocked region
    """
    # Segment the image
    bar = img.mean() + 2 * img.std()  # bar to leap
    bin_img = (img<bar).astype(np.uint8)*255  # binary that image
    bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, np.ones(min_size))
    # Process the image into contours
    cont, hier = cv2.findContours(bin_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    if hier is None:
        raise Exception, "No contours found"
    hier = hier[0]
    # Blocked region is lowest contour, create a circle for it
    blocked_region = _lowest_contour_in_hierarchy(cont, hier)
    ((x, y), radius) = cv2.minEnclosingCircle(blocked_region)
    # Plot if option to do so is passed
    if plot is not False:
        if plot is True:
            fig, ax = plt.subplots(figsize=[6,3])
        else:
            ax = plot
        circle = plt.Circle((x,y), radius, facecolor='m', alpha=0.5)
        ax.imshow(img)
        ax.add_patch(circle)
        ax.set_title('Blocked region identification')
        plt.draw()
        plt.tight_layout()
        plt.show()
    return ((x, y), radius)

def _lowest_contour_in_hierarchy(contours, hierarchy):
    """Return the lowest, most junior, node(s) in a contour set.
    
    Parameters
    ----------
    contour : list
        A list of contours found in an image. 
    hierarchy : list
        A contour hierarchy consists of a series of entries such 
        as [a, b, c, d] where:
            a is index of the next contour on the same level
            b is index of the prior contour on the same level
            c is the first child of this contour
            d is the parent of this contour
        and a value of -1 means none-such parent/child/sibling exists.
    
    Returns
    -------
    contour : list
       The innermost contour in a set.
    """
    level_list = _node_levels([[]], hierarchy, 0, 0) # walk tree to find levels
    lowest = level_list[-1]
    if len(lowest) > 1:
        warnings.warn("More than one lowest contour, taking roundest one")
        return _roundest_contour([contours[i] for i in lowest])
    else:
        return contours[lowest[0]]

def _node_levels(tree, hier, level, node):
    """Creates list of which nodes are on which level, by recursively walking 
    the hierarchy tree.
    """
    h = hier[node] # the current node in the hierarchy
    if len(tree) < (level+1):
        tree.append([]) 
    tree[level].append(node) # add our current node to the structure
    if h[0] >= 0: # then keep walking this level
        _node_levels(tree, hier, level, h[0])
    if h[2] >= 0: # then walk the child level
        _node_levels(tree, hier, level+1, h[2])
    return tree

def _roundest_contour(contours):
    """Given a list of contours, return the roundest."""
    ratios = [np.sqrt(cv2.contourArea(c))/cv2.arcLength(c, 1) for c in contours]
    highest_ratio_contour = contours[ratios.index(max(ratios))] 
    return highest_ratio_contour


