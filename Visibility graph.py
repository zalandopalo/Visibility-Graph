import sympy


def line_outfig(line_from_to: sympy.geometry.Segment, lines_in_figs: list, x_max_from_figs):
    """
    for segment check ( in or out)
    :param line_from_to: sympy.geometry.Segment
    :param lines_in_figs: collided contours
    :param x_max_from_figs:  for left fast check - inside fig or not
    :return: True if outside
    """

    from sympy.geometry import Point, Segment

    mid_point = line_from_to.midpoint
    y_mid_point = mid_point.y
    l_control = 0
    control_point = Point(x_max_from_figs, y_mid_point)
    control_seg = Segment(mid_point, control_point)
    try:
        for fig in lines_in_figs:
            for line in fig:
                control = control_seg.intersection(line)
                if control != []:
                    for c in control:
                        if type(c) == type(control_point):
                            l_control += 1
                else:
                    continue
    except:
        for line in lines_in_figs:
            control = control_seg.intersection(line)
            if control != []:
                for c in control:
                    if type(c) == type(control_point):
                        l_control += 1
            else:
                continue

    if l_control // 2 == 0 or l_control == 0:
        return True
    else:
        return False


def min_max_contour_points(figs_nods_cords):
    import math
    x_max = - math.inf
    x_min = math.inf
    y_max = - math.inf
    y_min = math.inf
    try:
        for figure in figs_nods_cords:
            for elem in figure:
                x0 = elem[0][0]
                y0 = elem[0][1]
                if x0 > x_max:
                    x_max = x0
                if x0 < x_min:
                    x_min = x0
                if y0 > y_max:
                    y_max = y0
                if y0 < y_min:
                    y_min = y0
    except:
        for figure in figs_nods_cords:
            x0 = figure[0]
            y0 = figure[1]
            if x0 > x_max:
                x_max = x0
            if x0 < x_min:
                x_min = x0
            if y0 > y_max:
                y_max = y0
            if y0 < y_min:
                y_min = y0
    return [x_max, y_max, x_min, y_min]


def image_preparation(path_to_img):
    import cv2
    import math as m
    path_to_img = cv2.imread(img_path)
    path_to_img = cv2.medianBlur(path_to_img, 7)
    # prepare img
    img_gray = cv2.cvtColor(path_to_img, cv2.COLOR_BGR2GRAY)
    thresh = 100

    ret, img_thresh = cv2.threshold(img_gray, thresh, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(img_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # find minimum and maximum size contour
    min_val = m.inf
    max_val = 0
    for contour in contours:
        if contour.shape[0] < min_val:
            min_val = contour.shape[0]
        if contour.shape[0] > max_val:
            max_val = contour.shape[0]

    # make nods
    approx_contours = []
    for contour in contours:
        esp = 0.02 / (contour.shape[0] / min_val)
        arclen = cv2.arcLength(contour, True)
        epsilon = arclen * esp
        approx_contours.append(cv2.approxPolyDP(contour, epsilon, True))

    return approx_contours


img_path = "Picture1.png"
approx_img = image_preparation(img_path)
minmax = min_max_contour_points(approx_img)


def build_graph(points_in_all_contours, contour_lines):
    from sympy.geometry import Point, Segment

    pts = [Point(point[0], point[1]) for point in points_in_all_contours]
    all_lines = []
    for fig in contour_lines:
        for line in fig:
            all_lines.append(line)

    graph_moves = dict
    lens = dict
    for i in range(len(pts)):
        point_from = pts[i]
        print(f"point from: {point_from}")
        avalible_moves = []
        lenths = []

        for j in range(len(pts)):
            if i == j:
                continue
            point_to = pts[j]
            print(f"point to: {point_to}")
            seg_from_to = Segment(point_from, point_to)
            if seg_from_to in all_lines:
                avalible_moves.append(point_to)
                lenths.append(seg_from_to.length)
                continue

            potentual_moves = []
            try:
                figs_in_time = []
                point_to_time = point_from
                inters = []
                for fig in contour_lines:
                    try:
                        for line in fig:
                            try:
                                intersection = seg_from_to.intersection(line)[0]
                            except:
                                intersection = seg_from_to.intersection(line)
                            match type(intersection):
                                case sympy.geometry.Segment2D:
                                    print(f"line on graph:[{line}] is on line from_to: [{seg_from_to}]")
                                    point_to_time = intersection.points[1]
                                    if point_to_time not in inters:
                                        inters.append(point_to_time)
                                    if fig not in figs_in_time:
                                        figs_in_time.append(fig)
                                    continue

                                case sympy.geometry.Point2D:
                                    if intersection not in pts:
                                        print(f"interseption not in points = {intersection}")
                                        raise StopIteration

                                    elif (intersection in pts) and (intersection != point_from):
                                        # cv2.line(img, [int(pts[i].x), int(pts[i].y)], [int(pts[j].x), int(pts[j].y)],
                                        #         (5, 2, 107), 2)
                                        print(f"potential move = {intersection}")
                                        if line_outfig(Segment(point_to_time, intersection), fig, minmax[0]):
                                            if intersection not in inters:
                                                inters.append(intersection)
                                            if fig not in figs_in_time:
                                                figs_in_time.append(fig)
                                            continue
                                        else:
                                            raise StopIteration

                                    elif intersection == point_from:
                                        print(f"point from {point_from} = {intersection}")
                                        continue
                                case _:
                                    continue
                        continue
                    except StopIteration:
                        raise StopIteration
                # проверку на ынутренность линии
                avalible_moves.append(point_to)
                lenths.append(seg_from_to.length)
                lens.update({f"{seg_from_to}": seg_from_to.length})
            except StopIteration:
                continue
        graph_moves.update({f"{point_from}": avalible_moves})
    return graph_moves, lens
