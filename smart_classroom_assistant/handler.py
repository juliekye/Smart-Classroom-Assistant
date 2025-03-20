import face_recognition
import pickle
import os
import json
from awss3 import S3, DynamoDB, CloudWatch
import subprocess
import uuid

WORK_DIR = '/home/app/'
ENCODING_PATH = WORK_DIR + 'encoding'
VIDEO_DIR = '/tmp/'
OUTPUT_BUCKET_NAME = 'awsome-people-output'
CW = CloudWatch()
OUTPUT_S3 = S3(OUTPUT_BUCKET_NAME)
DB = DynamoDB('Students')


def compare_encoding(known_encodings, unknown_encoding):
    results = face_recognition.compare_faces(known_encodings, unknown_encoding)
    first_true_index = next(
        (index for index, value in enumerate(results) if value), None)
    return first_true_index


def read_encoding():
    try:
        with open(ENCODING_PATH, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(e)
        return None


def recognize_image(encoding_dict, image_path):
    unknown_image = face_recognition.load_image_file(image_path)
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
    index = compare_encoding(encoding_dict['encoding'], unknown_encoding)
    if index is None:
        return None
    else:
        return encoding_dict['name'][index]


def extract_frames(video_path, output_dir):
    try:
        subprocess.run(
            ["/usr/bin/ffmpeg", "-i", str(video_path), "-r", "1",
             os.path.join(output_dir, "image-%3d.jpeg")],
            text=True,
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError as e:
        CW.log_to_cloudwatch(str(e))
        return False


def process_request(video_path):
    encoding_dict = read_encoding()
    output_dir = '/tmp/output/' + str(uuid.uuid4()) + '/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not extract_frames(video_path, output_dir):
        return None

    output_frames = os.listdir(output_dir)

    for img in output_frames:
        res = recognize_image(encoding_dict, output_dir + img)
        if res is not None:
            return res

    return None


def save_video(binary):
    path = VIDEO_DIR + 'input-' + str(uuid.uuid4()) + '.mp4'
    open(path, 'wb').write(binary)
    return path


def json_to_csv(student_json):
    if student_json is None:
        return ""

    res = []
    for key in ["name", "major", "year"]:
        if key in student_json:
            _, value = list(student_json[key].items())[0]
            res.append(value)
    return ','.join(res)


def face_recognition_handler(event, context):
    try:
        if len(event['Records']) > 0:
            record = event["Records"][0]
            s3_bucket = record["s3"]["bucket"]["name"]
            s3_key = record["s3"]["object"]["key"]
            INPUT_S3 = S3(s3_bucket)
            video = INPUT_S3.get_object(s3_key)
            if video is None:
                msg = s3_key + ' not found in bucket'
                CW.log_to_cloudwatch(msg)
                return msg

            video_path = save_video(video)
            name = process_request(video_path)
            if name is None:
                CW.log_to_cloudwatch(s3_key + ' no face found')
                return str(None)
            else:
                # DynamoDB
                res = DB.search_by_name(name)
                OUTPUT_S3.put_object(s3_key.split(
                    '.')[0] + ".csv", json_to_csv(res))
                return res
        else:
            return {"res": 'empty event'}
    except Exception as e:
        CW.log_to_cloudwatch(str(e))
        return str(e)
