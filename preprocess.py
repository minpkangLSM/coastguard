import os
import pytesseract
import math
import csv
import re
import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from tqdm import tqdm

class meta_info :

    @staticmethod
    def frame_classifier(img_dir, avg_threshold=1.5, std_threshold=0.5):

        frame = cv2.imread(img_dir, cv2.COLOR_RGB2BGR)
        frame_parts = frame[26:666, :, :]

        # # intensity
        # intensity = np.mean(frame_parts)

        # statistics
        b_avg = np.mean(frame_parts[:, :, 0])
        g_avg = np.mean(frame_parts[:, :, 1])
        r_avg = np.mean(frame_parts[:, :, 2])
        avg_std = np.std([b_avg, g_avg, r_avg])

        b_std = np.std(frame_parts[:, :, 0])
        g_std = np.std(frame_parts[:, :, 1])
        r_std = np.std(frame_parts[:, :, 2])
        std_std = np.std([b_std, g_std, r_std])

        if avg_std < avg_threshold:

            if std_std < std_threshold: img = "THR"
            else: img = "RGB"

        else: img = "RGB"

        return img

    def geo_info(self,
                 frame_folder_dir,
                 ) :

        # frame meta dict
        frame_meta_list = []
        meta_list = ["name", "Tlat", "Tlon", "Rng", "Alat", "Alon", "Az", "El", "Date", "Time", "img"]

        # frame folder dir generation
        frame_nm_list = os.listdir(frame_folder_dir)
        for frame_nm in tqdm(frame_nm_list) :

            frame_dir = os.path.join(frame_folder_dir, frame_nm)
            img = meta_info.frame_classifier(img_dir=frame_dir)

            frame = cv2.imread(frame_dir, cv2.IMREAD_GRAYSCALE)
            # frame = np.array(Image.open(frame_dir))

            # cv2 : order of coordinates = [y, x]
            Tlat = frame[668:690, 118:251]
            Tlon = frame[668:690, 331:468]
            Rng = frame[668:690, 537:958]
            Alat = frame[697:716, 75:215]
            Alon = frame[697:716, 341:488]
            Az = frame[697:716, 770:845]
            El = frame[697:716, 918:989]
            Date = frame[697:716, 1010:1160]
            Time = frame[697:716, 1160:1277]

            # save meta info of a frame in dict type
            frame_dict = {}
            frame_dict[meta_list[0]] = frame_nm
            frame_dict[meta_list[10]] = img

            frame_dict[meta_list[1]] = pytesseract.image_to_string(Tlat, lang=None, config='--psm 8')
            if frame_dict[meta_list[1]] == "" :
                frame_dict[meta_list[1]] = "None"
                print("Tlat None")

            frame_dict[meta_list[2]] = pytesseract.image_to_string(Tlon, lang=None, config='--psm 8')
            if frame_dict[meta_list[2]] == "" :
                frame_dict[meta_list[2]] = "None"
                print("Tlon None")

            frame_dict[meta_list[3]] = pytesseract.image_to_string(Rng, lang=None, config='--psm 8')
            if frame_dict[meta_list[3]] == "" :
                frame_dict[meta_list[3]] = "None"
                print("Rng None")

            frame_dict[meta_list[4]] = pytesseract.image_to_string(Alat, lang=None, config='--psm 8')
            if frame_dict[meta_list[4]] == "" :
                frame_dict[meta_list[4]] = "None"
                print("Alat None")

            frame_dict[meta_list[5]] = pytesseract.image_to_string(Alon, lang=None, config='--psm 8')
            if frame_dict[meta_list[5]] == "" :
                frame_dict[meta_list[5]] = "None"
                print("Alon None")

            frame_dict[meta_list[6]] = pytesseract.image_to_string(Az, lang=None, config='--psm 8')
            if frame_dict[meta_list[6]] == "" :
                frame_dict[meta_list[6]] = "None"
                print("Az None")

            frame_dict[meta_list[7]] = pytesseract.image_to_string(El, lang=None, config='--psm 8')
            if frame_dict[meta_list[7]] == "" :
                frame_dict[meta_list[7]] = "None"
                print("El None")

            frame_dict[meta_list[8]] = pytesseract.image_to_string(Date, lang=None, config='--psm 8')
            if frame_dict[meta_list[8]] == "" :
                frame_dict[meta_list[8]] = "None"
                print("Date None")

            frame_dict[meta_list[9]] = pytesseract.image_to_string(Time, lang=None, config='--psm 8')
            if frame_dict[meta_list[9]] == "" :
                frame_dict[meta_list[9]] = "None"
                print("Time None")

            frame_meta_list.append(frame_dict)

        # dict to csv format file
        with open("E:\\2021_coastguard\\frame\\D\\extract_geoinfo_with_img.csv", "w", encoding='UTF-8', newline='', ) as f:
            writer = csv.DictWriter(f, fieldnames=meta_list)
            writer.writeheader()
            for data in frame_meta_list:
                writer.writerow(data)

        return frame_meta_list

    def interpolation(self,
                      input,
                      output,
                      interpolation=False):

        # input
        f = open(input, 'r', encoding='UTF-8', newline="")
        f = csv.reader(f)

        # pattern reg
        Loc_p = re.compile('(\d{1,3})(\D+)(\d{1,3})(\D+)(\d{1,3})')  # Tlat, Tlon, ALat, Alon, Az, El
        Pos_p = re.compile('([+-]?\d{1,2})(\D+)(\d{1,2})')  # Az, El
        Date_p = re.compile('(\d{2})-([a-zA-Z]{3})-(\d{4})')  # Date
        Time_p = re.compile("(\d{2}):(\d{2}):(\d{2})")  # Time

        # geo-data
        meta_list = ["name", "Tlat", "Tlon", "Rng", "Alat", "Alon", "Az", "El", "Date", "Time", "Img"]
        interpolated_meta = [] # 최종결과값 (str 타입으로 변환된 값 - 연산이 불가능한 형태라고 가정)
        temp_meta = [] # 연산이 가능한 형태(튜플)로 저장된 값

        for idx, line in enumerate(f) :
            re_frame_dict = {} # 현재 decoding하고 있는 값
            if idx == 0 : continue # 맨 처음 열은 열 별 이름이므로 패스

            Tlat_re = re.findall(Loc_p, line[1])
            if Tlat_re != []: Tlat = str(Tlat_re[0][0])+'°'+str(Tlat_re[0][2])+"."+str(Tlat_re[0][4])+"'"
            else : Tlat = None # No fitted in the shape of re, considering Error : None
            Tlon_re = re.findall(Loc_p, line[2])
            if Tlon_re != []: Tlon = str(Tlon_re[0][0])+'°'+str(Tlon_re[0][2])+"."+str(Tlon_re[0][4])+"'"
            else : Tlon = None
            Alat_re = re.findall(Loc_p, line[4])
            if Alat_re != []: Alat = str(Alat_re[0][0])+'°'+ str(Alat_re[0][2])+"."+str(Alat_re[0][4])+"'"
            else : Alat = None
            Alon_re = re.findall(Loc_p, line[5])
            if Alon_re != []: Alon = str(Alon_re[0][0])+'°'+str(Alon_re[0][2] +"."+str(Alon_re[0][4]))+"'"
            else : Alon = None
            Az_re = re.findall(Pos_p, line[6])
            if Az_re != []: Az = str(Az_re[0][0]) + "." + str(Az_re[0][2]) + '°'
            else : Az = None
            El_re = re.findall(Pos_p, line[7])
            if El_re != []: El = str(El_re[0][0]) + "." + str(El_re[0][2]) + '°'
            else : El = None
            Date_re = re.findall(Date_p, line[8])
            if Date_re != [] : Date = str(Date_re[0][0])+"-"+str(Date_re[0][1])+"-"+str(Date_re[0][2])
            else : Date = None
            Time_re = re.findall(Time_p, line[9])
            if Time_re != [] : Time = str(Time_re[0][0])+":"+str(Time_re[0][1])+":"+str(Time_re[0][2])
            else : Time = None
            temp_meta.append([line[0], Tlat_re, Tlon_re, line[3], Alat_re, Alon_re, Az_re, El_re, Date_re, Time_re])
        print(temp_meta)
        interval = np.zeros((10))
        for idx in range(len(temp_meta)):
            # Tlat
            if temp_meta[idx][1] == [] and interval[1] == 0:
                interval[1] += 1
                Tlat_head = idx
            elif temp_meta[idx][1] == [] and interval[1] != 0:
                interval[1] += 1
            elif temp_meta[idx][1] != [] and interval[1] != 0:
                front = float(temp_meta[Tlat_head-1][1][0][0])+float(temp_meta[Tlat_head-1][1][0][2]+"."+temp_meta[Tlat_head-1][1][0][4])/60.
                rear = float(temp_meta[idx][1][0][0])+float(temp_meta[idx][1][0][2]+"."+temp_meta[idx][1][0][4])/60.
                gap = rear - front
                interval_gap = gap / interval[1]
                for i in range(int(interval[1])) :
                    value = front+interval_gap*(i+1)
                    first = math.floor(value)
                    second = math.floor((value-first)*60)
                    third = math.floor(((value-first)*60-second)*100)
                    Tlat = [(str(first), '°', str(second), '.', str(third))]
                    temp_meta[Tlat_head+i][1] = Tlat
                interval[1] = 0

            # Tlon
            if temp_meta[idx][2] == [] and interval[2] == 0:
                interval[2] += 1
                Tlon_head = idx
            elif temp_meta[idx][2] == [] and interval[2] != 0:
                interval[2] += 1
            elif temp_meta[idx][2] != [] and interval[2] != 0:
                front = float(temp_meta[Tlon_head - 1][2][0][0]) + \
                        float(temp_meta[Tlon_head - 1][2][0][2] + "." + temp_meta[Tlon_head - 1][2][0][4]) / 60.
                rear = float(temp_meta[idx][2][0][0]) + \
                       float(temp_meta[idx][2][0][2] + "." + temp_meta[idx][2][0][4]) / 60.
                gap = rear - front
                interval_gap = gap / interval[2]
                for i in range(int(interval[2])):
                    value = front + interval_gap * (i + 1)
                    first = math.floor(value)
                    second = math.floor((value - first) * 60)
                    third = math.floor(((value - first) * 60 - second) * 100)
                    Tlat = [(str(first), '°', str(second), '.', str(third))]
                    temp_meta[Tlon_head + i][2] = Tlat
                interval[2] = 0

            # Alon
            if temp_meta[idx][4] == [] and interval[4] == 0:
                interval[4] += 1
                Alon_head = idx
            elif temp_meta[idx][4] == [] and interval[4] != 0:
                interval[4] += 1
            elif temp_meta[idx][4] != [] and interval[4] != 0:
                front = float(temp_meta[Tlon_head - 1][4][0][0]) + \
                        float(temp_meta[Tlon_head - 1][4][0][2] + "." + temp_meta[Tlon_head - 1][4][0][4]) / 60.
                rear = float(temp_meta[idx][4][0][0]) + \
                        float(temp_meta[idx][4][0][2] + "." + temp_meta[idx][4][0][4]) / 60.
                gap = rear - front
                interval_gap = gap / interval[4]
                for i in range(int(interval[4])):
                    value = front + interval_gap * (i + 1)
                    first = math.floor(value)
                    second = math.floor((value - first) * 60)
                    third = math.floor(((value - first) * 60 - second) * 100)
                    Alon = [(str(first), '°', str(second), '.', str(third))]
                    temp_meta[Alon_head + i][4] = Alon
                interval[4] = 0

            # Alat
            if temp_meta[idx][5] == [] and interval[5] == 0:
                interval[5] += 1
                Alat_head = idx
            elif temp_meta[idx][5] == [] and interval[5] != 0:
                interval[5] += 1
            elif temp_meta[idx][5] != [] and interval[5] != 0:
                front = float(temp_meta[Tlon_head - 1][5][0][0]) + \
                        float(temp_meta[Tlon_head - 1][5][0][2] + "." + temp_meta[Tlon_head - 1][5][0][4]) / 60.
                rear = float(temp_meta[idx][5][0][0]) + \
                        float(temp_meta[idx][5][0][2] + "." + temp_meta[idx][5][0][4]) / 60.
                gap = rear - front
                interval_gap = gap / interval[5]
                for i in range(int(interval[5])):
                    value = front + interval_gap * (i + 1)
                    first = math.floor(value)
                    second = math.floor((value - first) * 60)
                    third = math.floor(((value - first) * 60 - second) * 100)
                    Alat = [(str(first), '°', str(second), '.', str(third))]
                    temp_meta[Alat_head + i][5] = Alat
                interval[5] = 0

            # Az
            if temp_meta[idx][6] == [] and interval[6] == 0:
                interval[6] += 1
                Az_head = idx
            elif temp_meta[idx][6] == [] and interval[6] != 0:
                interval[6] += 1
            elif temp_meta[idx][6] != [] and interval[6] != 0:
                front = float(temp_meta[Az_head - 1][6][0][0]) + float(temp_meta[Az_head - 1][6][0][2])/10
                rear = float(temp_meta[idx][6][0][0]) + float(temp_meta[idx][6][0][2])/10
                gap = rear - front
                interval_gap = gap / interval[6]
                for i in range(int(interval[6])):
                    value = str(front + interval_gap * (i + 1)).split(".")
                    first = value[0]
                    second = value[1]
                    Az = [(str(first), '.', str(second))]
                    temp_meta[Az_head + i][6] = Az
                interval[6] = 0
            # El
            if temp_meta[idx][7] == [] and interval[7] == 0:
                interval[7] += 1
                El_head = idx
            elif temp_meta[idx][7] == [] and interval[7] != 0:
                interval[7] += 1
            elif temp_meta[idx][7] != [] and interval[7] != 0:
                front = float(temp_meta[El_head - 1][7][0][0]) + float(temp_meta[El_head - 1][7][0][2]) / 10.
                rear = float(temp_meta[idx][7][0][0]) + float(temp_meta[idx][7][0][2]) / 10.
                gap = rear - front
                interval_gap = gap / interval[7]
                for i in range(int(interval[7])):
                    value = str(front + interval_gap * (i + 1)).split(".")
                    first = value[0]
                    second = value[1]
                    El = [(str(first), '.', str(second))]
                    print("El : ", El)
                    temp_meta[El_head + i][7] = El
                interval[7] = 0

        for inter_idx in range(len(temp_meta)):
            re_frame_dict = {}
            re_frame_dict[meta_list[0]] = temp_meta[inter_idx][0]
            re_frame_dict[meta_list[1]] = str(temp_meta[inter_idx][1][0][0]) + \
                                          "°" + str(temp_meta[inter_idx][1][0][2]) + \
                                          "." + str(temp_meta[inter_idx][1][0][4]) + "'"
            re_frame_dict[meta_list[2]] = str(temp_meta[inter_idx][2][0][0]) + \
                                          "°" + str(temp_meta[inter_idx][2][0][2]) + \
                                          "." + str(temp_meta[inter_idx][2][0][4]) + "'"
            re_frame_dict[meta_list[3]] = temp_meta[inter_idx][3]
            re_frame_dict[meta_list[4]] = str(temp_meta[inter_idx][4][0][0]) + \
                                          "°" + str(temp_meta[inter_idx][4][0][2]) + \
                                          "." + str(temp_meta[inter_idx][4][0][4]) + "'"
            re_frame_dict[meta_list[5]] = str(temp_meta[inter_idx][5][0][0]) + \
                                          "°" + str(temp_meta[inter_idx][5][0][2]) + \
                                          "." + str(temp_meta[inter_idx][5][0][4]) + "'"
            re_frame_dict[meta_list[6]] = str(temp_meta[inter_idx][6][0][0]) + \
                                          "." + str(temp_meta[inter_idx][6][0][2]) + "°"
            print(inter_idx, temp_meta[inter_idx][7])
            re_frame_dict[meta_list[7]] = str(temp_meta[inter_idx][7][0][0]) + \
                                          "." + str(temp_meta[inter_idx][7][0][2]) + "°"
            re_frame_dict[meta_list[8]] = str(temp_meta[inter_idx][8][0][0]) + \
                                          "-" + str(temp_meta[inter_idx][8][0][1]) + \
                                          "-" + str(temp_meta[inter_idx][8][0][2])
            re_frame_dict[meta_list[9]] = str(temp_meta[inter_idx][9][0][0]) + \
                                          ":" + str(temp_meta[inter_idx][9][0][1]) + \
                                          ":" + str(temp_meta[inter_idx][9][0][2])

            interpolated_meta.append(re_frame_dict)
        with open(output, "w", encoding='UTF-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=meta_list)
            writer.writeheader()
            for data in interpolated_meta:
                writer.writerow(data)
            print("FINISHED.")

i = meta_info()
# i.geo_info(frame_folder_dir="E:\\2021_coastguard\\frame\\D_frames")
i.interpolation(input="E:\\2021_coastguard\\coastguard_git\\test_psm8.csv",
                output="E:\\2021_coastguard\\coastguard_git\\test_psm8_interpolated.csv",
                interpolation=True)
