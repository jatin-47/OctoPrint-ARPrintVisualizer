from flask import Response
import numpy as np
import cv2

def ar(input):
    """
    Returns the augmented input image
    """
    gray = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
    # aruco_dict_type = ARUCO_DICT["DICT_6X6_250"]
    # calibration_matrix_path = "calibration_matrix.npy"
    # distortion_coefficients_path = "distortion_coefficients.npy"
    
    # matrix_coefficients = np.load(calibration_matrix_path)
    # distortion_coefficients = np.load(distortion_coefficients_path)
    
    # gray = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
    # cv2.aruco_dict = cv2.aruco.Dictionary_get(aruco_dict_type)
    # parameters = cv2.aruco.DetectorParameters_create()

    # corners, ids, rejected_img_points = cv2.aruco.detectMarkers(gray, cv2.aruco_dict,parameters=parameters)

    # # If markers are detected
    # if len(corners) > 0:
    #     for i in range(0, len(ids)):
    #         # Estimate pose of each marker and return the values rvec and tvec---(different from those of camera coefficients)
    #         rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], 0.02, matrix_coefficients, distortion_coefficients)
    #         # Draw a square around the markers
    #         cv2.aruco.drawDetectedMarkers(input, corners) 

    #         # Draw Axis
    #         cv2.drawFrameAxes(input, matrix_coefficients, distortion_coefficients, rvec, tvec, 0.01)  

    return gray

def generate_feed(camera_ip):
    """
    Generates a video feed from the camera at the given index. stops video feed if its cut off/ cant read frame
    """
    cap = cv2.VideoCapture(camera_ip)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = ar(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    cap.release()

def generate_snapshot(camera_ip):
    """
    Generates snapshot from the camera at the given index. if the frame didnt return, return error
    """
    cap = cv2.VideoCapture(camera_ip)
    ret, frame = cap.read()
    if not ret:
        yield Response("error: could not capture frame")
    else:
        frame = ar(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            yield Response("error: could not encode frame")
        else:
            yield Response(buffer.tobytes(), mimetype='image/jpeg')
    cap.release()

def get_centre(corner):
    """
    Returns the centre of a rectangle
    """
    (topLeft, topRight, bottomRight, bottomLeft)  = corner.reshape((4, 2))
    return int((topLeft[0] + bottomRight[0]) / 2.0), int((topLeft[1] + bottomRight[1]) / 2.0)

def get_rec_points(corners):
    """
    Return the four corners of the rectangle that is formed by the centre of the detected four aruco markers
    """
    if len(corners) == 4:
        points = []
        for corner in corners:
            points.append(get_centre(corner))
        #sort based on y value
        points.sort(key=lambda x: x[1])
        #sort based on x value
        points[0:2] = sorted(points[0:2], key=lambda x: x[0])
        points[2:4] = sorted(points[2:4], key=lambda x: x[0], reverse=True)

        points = np.array(points)
        points = np.int32(points)
        return points
    else:
        return None


def aruco_display(corners, ids, rejected, image):
    if len(corners) > 0:
		# flatten the ArUco IDs list
        ids = ids.flatten()
        # loop over the detected ArUCo corners
        for (markerCorner, markerID) in zip(corners, ids):
            # extract the marker corners (which are always returned in
            # top-left, top-right, bottom-right, and bottom-left order)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners
			# convert each of the (x, y)-coordinate pairs to integers
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            cv2.line(image, topLeft, topRight, (255, 0, 0), 2)
            cv2.line(image, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(image, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(image, bottomLeft, topLeft, (0, 255, 0), 2)
			# compute and draw the center (x, y)-coordinates of the ArUco
			# marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(image, (cX, cY), 4, (0, 0, 255), -1)
			# draw the ArUco marker ID on the image
            cv2.putText(image, str(markerID),(topLeft[0], topLeft[1] - 10), cv2.FONT_HERSHEY_SIMPLEX,
				0.5, (0, 255, 0), 2)
            print("[Inference] ArUco marker ID: {}".format(markerID))
			# show the output image
    return image

ARUCO_DICT = {
	"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
	"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
	"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
	"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
	"DICT_5X5_50": cv2.aruco.DICT_5X5_50,
	"DICT_5X5_100": cv2.aruco.DICT_5X5_100,
	"DICT_5X5_250": cv2.aruco.DICT_5X5_250,
	"DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
	"DICT_6X6_50": cv2.aruco.DICT_6X6_50,
	"DICT_6X6_100": cv2.aruco.DICT_6X6_100,
	"DICT_6X6_250": cv2.aruco.DICT_6X6_250,
	"DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
	"DICT_7X7_50": cv2.aruco.DICT_7X7_50,
	"DICT_7X7_100": cv2.aruco.DICT_7X7_100,
	"DICT_7X7_250": cv2.aruco.DICT_7X7_250,
	"DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
	"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
	"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
	"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
	"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

