1. Generate ArUCo Markers by running "generate_aruco_tags.py" with command:
python generate_aruco_tags.py --id 24 --type DICT_6X6_250 -o tags/

2. Detect ArUCo Markers by running "detect_aruco_video.py" with command:
python detect_aruco_video.py --type DICT_6X6_250 --camera True

3. Calibrate the camera by running "calibration.py" with command below and get "calibration_matrix.npy" and "distortion_coefficients.npy" as output.
python calibration.py --dir calibration_checkerboard/ --square_size 0.024

4. Finally, do pose estimation by running "pose_estimation.py" with command:
python pose_estimation.py --K_Matrix calibration_matrix.npy --D_Coeff distortion_coefficients.npy --type DICT_6X6_250
