import os, operator, sys
from pathlib import Path
from termcolor import colored
import pandas as pd

videos_dir = Path('../videos')
sorted_videos_list = []
csv_path = Path("../to-be-sorted.csv")

if sys.argv[1] == "fastai":
    from fastai.vision import *
    models_path = Path("../../Models/slide-classifier/saved-models/")
    learn = load_learner(models_path)
else:
    import inspect
    sys.path.insert(1, os.path.join(sys.path[0], '../../Models/slide-classifier'))
    from custom_nnmodules import *
    from inference import *

def model_predict_fastai(img_path):
    img = open_image(img_path)
    pred_class,pred_idx,outputs = learn.predict(img)
    model_results = outputs.numpy().tolist()
    #model_results_percent = [i * 100 for i in model_results]
    classes = learn.data.classes
    probs = dict(zip(classes, model_results))
    return pred_class, pred_idx, probs

if csv_path.is_file():
    df = pd.read_csv(csv_path, index_col=0)
else:
    df = pd.DataFrame(columns=["video_id","frame","best_guess","probability"])

for item in os.listdir(videos_dir):
    current_dir = videos_dir / item
    frames_dir = current_dir / "frames"
    frames_sorted_dir = current_dir / "frames_sorted"
    if os.path.isdir(current_dir) and os.path.exists(frames_dir) and not os.path.exists(frames_sorted_dir):
        print("Video Folder " + item + " with Frames Directory Found!")
        num_incorrect = 0
        sorted_videos_list.append(item)
        frames = os.listdir(frames_dir)
        num_frames = len(frames)
        for idx, frame in enumerate(frames):
            print("Progress: " + str(idx+1) + "/" + str(num_frames))
            current_frame_path = os.path.join(frames_dir, frame)
            # run classification
            if sys.argv[1] == "fastai":
                best_guess, best_guess_idx, probs = model_predict(current_frame_path)
            else:
                best_guess, best_guess_idx, probs = get_prediction(Image.open(current_frame_path))
            prob_max_correct = list(probs.values())[best_guess_idx]
            print("AI Predicts: " + best_guess)
            print("Probabilities: " + str(probs))
            if prob_max_correct < 0.60:
                num_incorrect = num_incorrect + 1
                print(colored(str(prob_max_correct) + " Likely Incorrect", 'red'))
                df.loc[len(df.index)]=[item,frame,best_guess,prob_max_correct]
            else:
                print(colored(str(prob_max_correct) + " Likely Correct", 'green'))

            classified_image_dir = frames_sorted_dir / best_guess
            if not os.path.exists(classified_image_dir):
                os.makedirs(classified_image_dir)
            os.system('mv ' + str(current_frame_path) + ' ' + str(classified_image_dir))
        if num_incorrect == 0:
            df.loc[len(df.index)]=[item,frame,best_guess,prob_max_correct]
        df.to_csv(csv_path)
print("The Following Videos Need Manual Sorting:\n" + str(sorted_videos_list))