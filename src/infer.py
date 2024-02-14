import cv2
import numpy as np
import math

from PIL import Image

CLASS_ANCHOR = 0
CLASS_DART = 1

# choosen dimensions of dart board plane
MIDDLE_X = 500
MIDDLE_Y = 400
MAX_RADIUS = 290

# proportionate distance on dart board
# source: https://www.dimensions.com/element/dartboard
BULLSEYE = 6.35 / 170
OUTER_BULLSEYE = 16 / 170
CENTER_TO_OUTER_TREBLE = 107 / 170
CENTER_TO_OUTER_DOUBLE = 170 / 170
RINGS = 8 / 170

def to_coordinates(predictions):
    res = []
    for pred in predictions:
        xmin, ymin, xmax, ymax, _, _ = pred
        center_x, center_y = (xmin + xmax) / 2, (ymin + ymax) / 2
        res.append((center_x, center_y))
    return res

def filter(predictions, class_id):
    res = []
    for pred in predictions:
        if pred[-1] == class_id:
            res.append(pred)
    return res

def build_homography_matrix(anchor_candidates):
    if len(anchor_candidates) != 4:
        raise ValueError('Need exactly 4 anchor candidates for now')
    
    # Sort points based on x-coordinate
    sorted_points_x = sorted(anchor_candidates, key=lambda p: p[0])

    # Sort points based on y-coordinate
    sorted_points_y = sorted(anchor_candidates, key=lambda p: p[1])

    # Determine the top, bottom, right, and left points
    top = sorted_points_y[0]
    bottom = sorted_points_y[-1]
    right = sorted_points_x[-1]
    left = sorted_points_x[0]

    # destinations for anchors
    middle_x = (top[0] + bottom[0]) / 2
    middle_y = (left[1] + right[1]) / 2

    height = bottom[1] - top[1]
    width = right[0] - left[0]
    avg_size = (height + width) / 2
    height_offset = height - avg_size
    width_offset = width - avg_size
    print(f'larger side: {"width" if width > height else "height"}')
    print(f'height: {height} width: {width} avg_size: {avg_size}')
    print(f'height_offset: {height_offset} width_offset: {width_offset}')

    top_anchor_dest = (middle_x, top[1] - height_offset)
    bottom_anchor_dest = (middle_x, bottom[1] + height_offset)
    left_anchor_dest = (left[0] - width_offset, middle_y)
    right_anchor_dest = (right[0] + width_offset, middle_y)

    src_points = [top, left, right, bottom]
    dst_points = [top_anchor_dest, left_anchor_dest, right_anchor_dest, bottom_anchor_dest]
    print(src_points)
    print(dst_points)

    H, _ = cv2.findHomography(np.array(src_points), np.array(dst_points))
    return H

def build_homography_matrix_2(anchor_candidates):
    if len(anchor_candidates) != 4:
        raise ValueError('Need exactly 4 anchor candidates for now')
    
    # Sort points based on x-coordinate
    sorted_points_x = sorted(anchor_candidates, key=lambda p: p[0])

    # Sort points based on y-coordinate
    sorted_points_y = sorted(anchor_candidates, key=lambda p: p[1])

    # Determine the top, bottom, right, and left points
    top = sorted_points_y[0]
    bottom = sorted_points_y[-1]
    right = sorted_points_x[-1]
    left = sorted_points_x[0]

    # destinations for anchors
    top_anchor_dest = (MIDDLE_X, MIDDLE_Y - MAX_RADIUS)
    bottom_anchor_dest = (MIDDLE_X, MIDDLE_Y + MAX_RADIUS)
    left_anchor_dest = (MIDDLE_X - MAX_RADIUS, MIDDLE_Y)
    right_anchor_dest = (MIDDLE_X + MAX_RADIUS, MIDDLE_Y)

    src_points = [top, left, right, bottom]
    dst_points = [top_anchor_dest, left_anchor_dest, right_anchor_dest, bottom_anchor_dest]
    print(src_points)
    print(dst_points)

    H, _ = cv2.findHomography(np.array(src_points), np.array(dst_points))
    return H

def translate_position(pos, homography_matrix):
    pos_t = np.array([pos[0], pos[1], 1])
    pos_t = np.matmul(homography_matrix, pos_t)
    pos_t = pos_t / pos_t[-1]
    return pos_t[0], pos_t[1]

def translate_img(img, output_size, homography_matrix):
    input_image_arr = np.array(img)
    output_image_arr = cv2.warpPerspective(input_image_arr, homography_matrix, output_size)
    img_warped = Image.fromarray(output_image_arr)
    return img_warped

def angle_to_base_score(angle):
    """
    Calculates the base score based on the angle of the dart from the center of the board.
    Assumes 0 degrees is 12 o'clock and references the middle ot the 20 field.
    """
    shifted_angle = (angle + 9) % 360
    multiplier = math.floor(shifted_angle / 18) # 360 / 20 => width of a field

    scores = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
    return scores[multiplier % 20]

def build_score_prediction(dart_pos):
    
    #calc vectors from middle to point and to 20 (0 degrees)
    middleToDart = (dart_pos[0]-MIDDLE_X, dart_pos[1]-MIDDLE_Y)
    middleToUpperAnchor = (0, -MAX_RADIUS)
    #calc angle for number
    u = middleToDart[0]*middleToUpperAnchor[0]+middleToDart[1]*middleToUpperAnchor[1]
    v = math.sqrt(middleToDart[0]**2 + middleToDart[1]**2) * math.sqrt(middleToUpperAnchor[0]**2 + middleToUpperAnchor[1]**2) #abs()
    print(f'u: {u} v: {v} ratio: {u/v}')
    middleToDartLength = math.sqrt(middleToDart[0]**2 + middleToDart[1]**2)
    print('middleToTop dis', MAX_RADIUS, 'middleToDart dis', middleToDartLength, 'ratio', middleToDartLength/MAX_RADIUS)
    
    angleOfDart = math.acos(u/v) * (180/math.pi)
    if middleToDart[0] < 0:
        angleOfDart = 360 - angleOfDart

    #calc distance from middle for point multiplication
    dist = math.sqrt(middleToDart[0]**2 + middleToDart[1]**2)
    
    if dist > MAX_RADIUS:
        return 0, '-'
    if dist <= MAX_RADIUS * BULLSEYE:
        return 50, 'd25'
    if dist <= MAX_RADIUS * OUTER_BULLSEYE:
        return 25, '25'
    
    score = angle_to_base_score(angleOfDart)

    
    if dist >= MAX_RADIUS * (CENTER_TO_OUTER_TREBLE - RINGS) and dist <= MAX_RADIUS * CENTER_TO_OUTER_TREBLE:
        return score * 3, 't' + int(score)
    
    if dist >= MAX_RADIUS * (CENTER_TO_OUTER_DOUBLE - RINGS) and dist <= MAX_RADIUS * CENTER_TO_OUTER_DOUBLE:
        return score * 2, 'd' + int(score)
    
    return score

