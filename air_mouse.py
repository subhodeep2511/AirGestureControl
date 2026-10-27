import cv2
import mediapipe as mp
import pyautogui
import math
import time

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

SMOOTHING = 0.22
DEAD_ZONE = 3

PINCH_RATIO = 0.38

CLICK_CONFIRM_FRAMES = 5
RELEASE_CONFIRM_FRAMES = 4
RIGHT_CLICK_CONFIRM_FRAMES = 10

CLICK_COOLDOWN = 0.55
DRAG_HOLD_TIME = 0.45

SWIPE_DISTANCE = 45
SWIPE_TIME = 0.45
SWIPE_COOLDOWN = 0.55
SWIPE_SCROLL_AMOUNT = 7

FRAME_MARGIN = 70

MODEL_PATH = "hand_landmarker.task"

screen_width, screen_height = pyautogui.size()

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.70,
    min_hand_presence_confidence=0.70,
    min_tracking_confidence=0.70
)

landmarker = HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

cursor_x = screen_width / 2
cursor_y = screen_height / 2

previous_camera_x = None
previous_camera_y = None

left_pinch_active = False
left_pinch_frames = 0
left_release_frames = 0
left_pinch_start = 0

right_pinch_active = False
right_pinch_frames = 0
right_pinch_start = 0

dragging = False

right_click_frames = 0
right_click_active = False

swipe_start_y = None
swipe_start_time = None
swipe_last_time = 0
swipe_tracking = False

paused = False
timestamp = 0
gesture = "NONE"

last_click_time = 0


def distance(p1, p2):
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


def finger_up(hand, tip, pip):
    return hand[tip].y < hand[pip].y


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def hand_scale(hand):
    return max(
        distance(hand[0], hand[9]),
        0.001
    )


def pinch_ratio(hand, finger_tip):
    return (
        distance(hand[4], hand[finger_tip])
        / hand_scale(hand)
    )


def fist_pose(hand):
    return (
        not finger_up(hand, 8, 6)
        and not finger_up(hand, 12, 10)
        and not finger_up(hand, 16, 14)
        and not finger_up(hand, 20, 18)
    )


def two_finger_pose(hand):
    return (
        finger_up(hand, 8, 6)
        and finger_up(hand, 12, 10)
        and not finger_up(hand, 16, 14)
        and not finger_up(hand, 20, 18)
    )


def reset_movement():
    global previous_camera_x
    global previous_camera_y

    previous_camera_x = None
    previous_camera_y = None


def reset_swipe():
    global swipe_start_y
    global swipe_start_time
    global swipe_tracking

    swipe_start_y = None
    swipe_start_time = None
    swipe_tracking = False


def move_cursor(hand):
    global cursor_x
    global cursor_y
    global previous_camera_x
    global previous_camera_y

    index = hand[8]

    x = index.x * CAMERA_WIDTH
    y = index.y * CAMERA_HEIGHT

    x = clamp(
        x,
        FRAME_MARGIN,
        CAMERA_WIDTH - FRAME_MARGIN
    )

    y = clamp(
        y,
        FRAME_MARGIN,
        CAMERA_HEIGHT - FRAME_MARGIN
    )

    if previous_camera_x is not None:

        dx = x - previous_camera_x
        dy = y - previous_camera_y

        if abs(dx) < 1.5:
            x = previous_camera_x

        if abs(dy) < 1.5:
            y = previous_camera_y

    previous_camera_x = x
    previous_camera_y = y

    normalized_x = (
        x - FRAME_MARGIN
    ) / (
        CAMERA_WIDTH - 2 * FRAME_MARGIN
    )

    normalized_y = (
        y - FRAME_MARGIN
    ) / (
        CAMERA_HEIGHT - 2 * FRAME_MARGIN
    )

    target_x = normalized_x * screen_width
    target_y = normalized_y * screen_height

    dx = target_x - cursor_x
    dy = target_y - cursor_y

    movement = math.sqrt(
        dx * dx + dy * dy
    )

    if movement < DEAD_ZONE:
        return

    if movement > 300:
        smoothing = 0.32
    elif movement > 150:
        smoothing = 0.27
    else:
        smoothing = SMOOTHING

    cursor_x += dx * smoothing
    cursor_y += dy * smoothing

    cursor_x = clamp(
        cursor_x,
        0,
        screen_width - 1
    )

    cursor_y = clamp(
        cursor_y,
        0,
        screen_height - 1
    )

    pyautogui.moveTo(
        int(cursor_x),
        int(cursor_y)
    )


def start_drag():
    global dragging

    if not dragging:

        pyautogui.mouseDown(
            button="left"
        )

        dragging = True


def stop_drag():
    global dragging

    if dragging:

        pyautogui.mouseUp(
            button="left"
        )

        dragging = False


def detect_swipe(hand):
    global swipe_start_y
    global swipe_start_time
    global swipe_tracking
    global swipe_last_time

    if not two_finger_pose(hand):
        reset_swipe()
        return None

    current_time = time.time()

    current_y = (
        hand[0].y *
        CAMERA_HEIGHT
    )

    if (
        current_time - swipe_last_time
        < SWIPE_COOLDOWN
    ):
        return None

    if not swipe_tracking:

        swipe_tracking = True
        swipe_start_y = current_y
        swipe_start_time = current_time

        return None

    elapsed = (
        current_time -
        swipe_start_time
    )

    movement = (
        swipe_start_y -
        current_y
    )

    if elapsed > SWIPE_TIME:

        reset_swipe()
        return None

    if abs(movement) >= SWIPE_DISTANCE:

        swipe_last_time = current_time

        if movement > 0:

            reset_swipe()

            return "UP"

        else:

            reset_swipe()

            return "DOWN"

    return None


print()
print("============================================")
print("             AIR GESTURE CONTROL")
print("============================================")
print()
print("LEFT HAND")
print("  Index only              = Move cursor")
print("  Thumb + index           = Left click")
print()
print("RIGHT HAND")
print("  Index only              = Move cursor")
print("  Thumb + index HOLD      = Drag / move")
print("  Closed fist             = Right click")
print("  Two fingers SWIPE UP    = Scroll up")
print("  Two fingers SWIPE DOWN  = Scroll down")
print()
print("KEYBOARD")
print("  P                       = Pause / Resume")
print("  Q                       = Quit")
print()
print("============================================")


while True:

    success, frame = cap.read()

    if not success:

        print(
            "Camera could not be accessed."
        )

        break

    frame = cv2.flip(
        frame,
        1
    )

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    timestamp += 1

    result = landmarker.detect_for_video(
        mp_image,
        timestamp
    )

    hands = result.hand_landmarks

    gesture = "NONE"

    left_hand = None
    right_hand = None

    for i, hand in enumerate(hands):

        label = (
            result
            .handedness[i][0]
            .category_name
        )

        if label == "Left":

            left_hand = hand

        elif label == "Right":

            right_hand = hand

    # ==================================================
    # LEFT HAND
    # ==================================================

    if left_hand is not None:

        index_up = finger_up(
            left_hand,
            8,
            6
        )

        middle_up = finger_up(
            left_hand,
            12,
            10
        )

        ring_up = finger_up(
            left_hand,
            16,
            14
        )

        pinky_up = finger_up(
            left_hand,
            20,
            18
        )

        pinch = (
            pinch_ratio(
                left_hand,
                8
            )
            < PINCH_RATIO
        )

        clean_move = (
            index_up
            and not middle_up
            and not ring_up
            and not pinky_up
            and not pinch
        )

        clean_pinch = (
            pinch
            and not middle_up
            and not ring_up
            and not pinky_up
        )

        if (
            clean_move
            and not paused
        ):

            move_cursor(
                left_hand
            )

            gesture = "MOVE"

            left_pinch_active = False
            left_pinch_frames = 0

        elif (
            clean_pinch
            and not paused
        ):

            reset_movement()

            if not left_pinch_active:

                left_pinch_active = True

                left_pinch_start = (
                    time.time()
                )

                left_pinch_frames = 0

            left_pinch_frames += 1

            gesture = "LEFT CLICK"

        else:

            if left_pinch_active:

                left_release_frames += 1

                if (
                    left_release_frames
                    >= RELEASE_CONFIRM_FRAMES
                ):

                    held_time = (
                        time.time()
                        - left_pinch_start
                    )

                    if (
                        held_time
                        < DRAG_HOLD_TIME
                        and left_pinch_frames
                        >= CLICK_CONFIRM_FRAMES
                    ):

                        current_time = (
                            time.time()
                        )

                        if (
                            current_time
                            - last_click_time
                            > CLICK_COOLDOWN
                        ):

                            pyautogui.click()

                            last_click_time = (
                                current_time
                            )

                    left_pinch_active = False
                    left_pinch_frames = 0
                    left_release_frames = 0

    else:

        left_pinch_active = False
        left_pinch_frames = 0
        left_release_frames = 0

    # ==================================================
    # RIGHT HAND
    # ==================================================

    if right_hand is not None:

        index_up = finger_up(
            right_hand,
            8,
            6
        )

        middle_up = finger_up(
            right_hand,
            12,
            10
        )

        ring_up = finger_up(
            right_hand,
            16,
            14
        )

        pinky_up = finger_up(
            right_hand,
            20,
            18
        )

        pinch = (
            pinch_ratio(
                right_hand,
                8
            )
            < PINCH_RATIO
        )

        # ==============================================
        # SWIPE SCROLL
        # ==============================================

        if (
            two_finger_pose(right_hand)
            and not pinch
            and not paused
        ):

            right_click_frames = 0
            right_click_active = False

            swipe = detect_swipe(
                right_hand
            )

            if swipe == "UP":

                pyautogui.scroll(
                    SWIPE_SCROLL_AMOUNT
                )

                gesture = "SWIPE UP"

            elif swipe == "DOWN":

                pyautogui.scroll(
                    -SWIPE_SCROLL_AMOUNT
                )

                gesture = "SWIPE DOWN"

            else:

                gesture = "READY TO SWIPE"

            reset_movement()

        # ==============================================
        # RIGHT HAND DRAG
        # ==============================================

        elif (
            pinch
            and not middle_up
            and not ring_up
            and not pinky_up
            and not paused
        ):

            reset_swipe()

            right_click_frames = 0
            right_click_active = False

            if not right_pinch_active:

                right_pinch_active = True

                right_pinch_start = (
                    time.time()
                )

                right_pinch_frames = 0

            right_pinch_frames += 1

            held_time = (
                time.time()
                - right_pinch_start
            )

            if (
                held_time
                >= DRAG_HOLD_TIME
                and not dragging
            ):

                start_drag()

            if dragging:

                move_cursor(
                    right_hand
                )

                gesture = "DRAGGING"

            else:

                gesture = "HOLD FOR DRAG"

        # ==============================================
        # RIGHT CLICK
        # ==============================================

        elif fist_pose(right_hand):

            reset_swipe()

            right_pinch_active = False
            right_pinch_frames = 0

            right_click_frames += 1

            if (
                right_click_frames
                >= RIGHT_CLICK_CONFIRM_FRAMES
                and not right_click_active
            ):

                current_time = (
                    time.time()
                )

                if (
                    current_time
                    - last_click_time
                    > CLICK_COOLDOWN
                ):

                    pyautogui.rightClick()

                    last_click_time = (
                        current_time
                    )

                right_click_active = True

            gesture = "RIGHT CLICK"

        # ==============================================
        # RIGHT HAND MOVEMENT
        # ==============================================

        elif (
            index_up
            and not middle_up
            and not ring_up
            and not pinky_up
            and not paused
        ):

            reset_swipe()

            right_click_frames = 0
            right_click_active = False

            if dragging:

                move_cursor(
                    right_hand
                )

                gesture = "DRAGGING"

            else:

                move_cursor(
                    right_hand
                )

                gesture = "MOVE"

        # ==============================================
        # RESET
        # ==============================================

        else:

            reset_swipe()

            right_click_frames = 0
            right_click_active = False

            if dragging:

                stop_drag()

            right_pinch_active = False
            right_pinch_frames = 0

    else:

        reset_swipe()

        right_click_frames = 0
        right_click_active = False

        if dragging:

            stop_drag()

        right_pinch_active = False
        right_pinch_frames = 0

    # ==================================================
    # DRAW LANDMARKS
    # ==================================================

    for hand in hands:

        for point in hand:

            px = int(
                point.x
                * CAMERA_WIDTH
            )

            py = int(
                point.y
                * CAMERA_HEIGHT
            )

            cv2.circle(
                frame,
                (px, py),
                3,
                (0, 255, 0),
                -1
            )

    # ==================================================
    # UI
    # ==================================================

    status = (
        "PAUSED"
        if paused
        else "ACTIVE"
    )

    cv2.putText(
        frame,
        f"AIR MOUSE: {status}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"GESTURE: {gesture}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "LEFT: Index=Move | Pinch=Left Click",
        (20, CAMERA_HEIGHT - 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (255, 255, 255),
        1
    )

    cv2.putText(
        frame,
        "RIGHT: Pinch Hold=Drag | Fist=Right Click",
        (20, CAMERA_HEIGHT - 64),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.40,
        (255, 255, 255),
        1
    )

    cv2.putText(
        frame,
        "RIGHT: Two Fingers Swipe UP/DOWN=Scroll",
        (20, CAMERA_HEIGHT - 38),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        (255, 255, 255),
        1
    )

    cv2.putText(
        frame,
        "P=Pause | Q=Quit",
        (20, CAMERA_HEIGHT - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )

    cv2.imshow(
        "Air Gesture Control",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):

        break

    elif key == ord("p"):

        paused = not paused

        if paused:

            stop_drag()
            reset_movement()
            reset_swipe()


stop_drag()

cap.release()

cv2.destroyAllWindows()

landmarker.close()

print(
    "Air Gesture Control stopped."
)