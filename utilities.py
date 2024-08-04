# pip install inference, supervision

import cv2
from inference.core.interfaces.camera.entities import VideoFrame
from inference import InferencePipeline
import supervision as sv
from datetime import datetime, timedelta

COLOR_ANNOTATOR = sv.ColorAnnotator()
LABEL_ANNOTATOR = sv.LabelAnnotator()

# Use a different name to avoid confusion with the function
start_time = None

recognized = []
def on_prediction(res: dict, frame: VideoFrame) -> None:
    global start_time, pipeline
    image = frame.image
    annotated_frame = image.copy()

    detections = res["predictions"]["predictions"]

    if len(detections.xyxy) > 0:

        annotated_frame = COLOR_ANNOTATOR.annotate(
            scene=annotated_frame, detections=detections
        )
        annotated_frame = LABEL_ANNOTATOR.annotate(
            scene=annotated_frame,
            detections=detections,
        )
        class_name = (detections.data)["class_name"][0]
        recognized.append(class_name)
        print(class_name)

    # Print the time difference correctly
    print(datetime.now() - start_time)

    if datetime.now() - start_time > timedelta(seconds=5):
        # convert recognized into a set
        recognized_set = set(recognized)
        # convert recognized_set into list
        recognized_list = list(recognized_set)
        print(recognized_list)
        cv2.imshow("frame", annotated_frame)
        pipeline.terminate()
        pipeline.join()
        cv2.destroyAllWindows()
        print("closed")
        return recognized_list

    cv2.imshow("frame", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        return


def start_pipeline():
    global start_time, pipeline
    start_time = datetime.now()
    pipeline = InferencePipeline.init_with_workflow(
        video_reference=0,
        workspace_name="nathan-yan",
        workflow_id="custom-workflow-9",
        max_fps=60,
        api_key="Zw9s4qJmfSsVpb4IerO9",
        on_prediction=on_prediction,
    )

    pipeline.start()


if __name__ == '__main__':
    start_pipeline()
