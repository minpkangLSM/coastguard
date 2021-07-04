import os
import pytesseract
import math
import csv
import re
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm

class meta_info :

    def geo_info(self,
                 frame_folder_dir,
                 ) :

        # frame meta dict
        frame_meta_list = []
        meta_list = ["name", "Tlat", "Tlon", "Rng", "Alat", "Alon", "Az", "El", "Date", "Time"]

        # frame folder dir generation
        frame_nm_list = os.listdir(frame_folder_dir)
        for frame_nm in tqdm(frame_nm_list) :

            frame_dir = os.path.join(frame_folder_dir, frame_nm)

            frame = cv2.imread(frame_dir, cv2.IMREAD_GRAYSCALE)
            # frame = np.array(Image.open(frame_dir))

            # cv2 : order of coordinates = [y, x]
            Tlat = frame[668:690, 118:251]
            Tlon = frame[668:690, 331:468]
            Rng = frame[668:690, 537:958]
            Alat = frame[697:716, 75:215]
            Alon = frame[697:716, 341:488]
            Az = frame[697:716, 750:860]
            El = frame[697:716, 910:990]
            Date = frame[697:716, 1010:1160]
            Time = frame[697:716, 1160:1277]

            # save meta info of a frame in dict type
            frame_dict = {}
            frame_dict[meta_list[0]] = frame_nm

            frame_dict[meta_list[1]] = pytesseract.image_to_string(Tlat, lang=None, config='--psm 6')
            if frame_dict[meta_list[1]] == "" :
                frame_dict[meta_list[1]] = "None"
                print("Tlat None")

            frame_dict[meta_list[2]] = pytesseract.image_to_string(Tlon, lang=None, config='--psm 6')
            if frame_dict[meta_list[2]] == "" :
                frame_dict[meta_list[2]] = "None"
                print("Tlon None")

            frame_dict[meta_list[3]] = pytesseract.image_to_string(Rng, lang=None, config='--psm 6')
            if frame_dict[meta_list[3]] == "" :
                frame_dict[meta_list[3]] = "None"
                print("Rng None")
            frame_dict[meta_list[4]] = pytesseract.image_to_string(Alat, lang=None, config='--psm 6')
            if frame_dict[meta_list[4]] == "" :
                frame_dict[meta_list[4]] = "None"
                print("Alat None")

            frame_dict[meta_list[5]] = pytesseract.image_to_string(Alon, lang=None, config='--psm 6')
            if frame_dict[meta_list[5]] == "" :
                frame_dict[meta_list[5]] = "None"
                print("Alon None")

            frame_dict[meta_list[6]] = pytesseract.image_to_string(Az, lang=None, config='--psm 6')
            if frame_dict[meta_list[6]] == "" :
                frame_dict[meta_list[6]] = "None"
                print("Az None")

            frame_dict[meta_list[7]] = pytesseract.image_to_string(El, lang=None, config='--psm 6')
            if frame_dict[meta_list[7]] == "" :
                frame_dict[meta_list[7]] = "None"
                print("El None")

            frame_dict[meta_list[8]] = pytesseract.image_to_string(Date, lang=None, config='--psm 6')
            if frame_dict[meta_list[8]] == "" :
                frame_dict[meta_list[8]] = "None"
                print("Date None")

            frame_dict[meta_list[9]] = pytesseract.image_to_string(Time, lang=None, config='--psm 6')
            if frame_dict[meta_list[9]] == "" :
                frame_dict[meta_list[9]] = "None"
                print("Time None")

            frame_meta_list.append(frame_dict)

        # dict to csv format file
        with open("test.csv", "w", encoding='UTF-8', newline='', ) as f:
            writer = csv.DictWriter(f, fieldnames=meta_list)
            writer.writeheader()
            for data in frame_meta_list:
                writer.writerow(data)

        return frame_meta_list

    def interpolation(self,
                      input,
                      output):

        # input
        f = open(input, 'r', encoding='UTF-8', newline="")
        f = csv.reader(f)

        # pattern reg.
        Loc_p = re.compile('(\d{2,3})(\D+)(\d{2,3})(\D+)(\d{2,3})')  # Tlat, Tlon, ALat, Alon, Az, El
        Pos_p = re.compile('([+-]?\d{1,3})(\D*)(\d{1,3})')  # Az, El
        Date_p = re.compile('(\d{2})-([a-zA-Z]{3})-(\d{4})')  # Date
        Time_p = re.compile("(\d{2}):(\d{2}):(\d{2})")  # Time

        # geo-data
        meta_list = ["name", "Tlat", "Tlon", "Rng", "Alat", "Alon", "Az", "El", "Date", "Time"]
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

            temp_meta.append([None, Tlon_re, Tlat_re, None, Alat_re, Alon_re, Az_re, El_re, Date_re, Time_re])
            re_frame_dict[meta_list[0]] = line[0] # Not interpolation target
            re_frame_dict[meta_list[1]] = Tlat
            re_frame_dict[meta_list[2]] = Tlon
            re_frame_dict[meta_list[3]] = line[3] # Not interpolation target
            re_frame_dict[meta_list[4]] = Alat
            re_frame_dict[meta_list[5]] = Alon
            re_frame_dict[meta_list[6]] = Az
            re_frame_dict[meta_list[7]] = El
            re_frame_dict[meta_list[8]] = Date
            re_frame_dict[meta_list[9]] = Time

            if idx == 1 :
                first_err_keys = [key for key, value in re_frame_dict.items() if value == None]
                if first_err_keys == [] : first_err_keys == None
                interpolated_meta.append(re_frame_dict)
                before_meta_info = re_frame_dict

            elif idx == 2 :
                # idx1 값은 idx2 값으로 보정
                for f_err_key in first_err_keys :
                    if re_frame_dict[f_err_key] != None :
                        interpolated_meta[0][f_err_key] = re_frame_dict[f_err_key]
                    else : pass
                interpolated_meta.append(re_frame_dict)
                before_meta_info = re_frame_dict

            # # temp
            # elif idx == len(f):
            #     interpolated_meta.append(re_frame_dict)

            elif idx > 2 :
                print("IDX : ", idx)
                interpolated_meta.append(re_frame_dict)
                Err_idxs = []
                Err_keys = []
                temp_idx = 0
                for key, value in before_meta_info.items() :
                    if value == None :
                        Err_idxs.append(temp_idx)
                        Err_keys.append(key)
                    temp_idx += 1
                if len(Err_idxs) == 8 : break

                for e_idx, e_key in zip(Err_idxs, Err_keys) :
                    current_value = temp_meta[-1][e_idx]
                    before_before_value = temp_meta[idx-3][e_idx]

                    if e_idx == 1 or e_idx == 2 or e_idx == 4 or e_idx == 5 or e_idx == 9 :
                        switch = False
                        if current_value != [] and before_before_value != [] :
                            switch = True
                            first = (int(current_value[0][0]) + int(before_before_value[0][0]))//2
                            second = (int(current_value[0][2]) + int(before_before_value[0][2]))//2
                            third = (int(current_value[0][4]) + int(before_before_value[0][4]))//2

                        elif current_value == [] and before_before_value != []:
                            switch = True
                            first = int(before_before_value[0][0])
                            second = int(before_before_value[0][2])
                            third = int(before_before_value[0][4])

                        elif current_value != [] and before_before_value == []:
                            switch = True
                            first = int(current_value[0][0])
                            second = int(current_value[0][2])
                            third = int(current_value[0][4])

                        if switch :
                            if e_idx == 1 or e_idx == 2 or e_idx == 4 or e_idx == 5:
                                interpolated_meta[idx - 2][e_key] = str(first) + '°' + str(second) + '.' + str(third) + "'"
                                # temp 보정
                                temp_meta[idx - 2][e_idx] = [(str(first)), '°', str(second), '.', str(third)]
                            if e_idx == 9:
                                interpolated_meta[idx - 2][e_key] = str(first) + ':' + str(second) + ':' + str(third) + "'"
                                # temp 보정
                                temp_meta[idx - 2][e_idx] = [(str(first)), str(second), str(third)]

                    if e_idx == 8 :
                        switch = False
                        if current_value != [] and before_before_value != []:
                            switch = True
                            first = (int(current_value[0][0]) + int(before_before_value[0][0])) // 2
                            second = current_value[0][1]
                            third = (int(current_value[0][2]) + int(before_before_value[0][2])) // 2

                        elif current_value == [] and before_before_value != []:
                            switch = True
                            first = int(before_before_value[0][0])
                            second = before_before_value[0][1]
                            third = int(before_before_value[0][2])

                        elif current_value != [] and before_before_value == []:
                            switch = True
                            first = int(current_value[0][0])
                            second = current_value[0][1]
                            third = int(current_value[0][2])
                        if switch :
                            interpolated_meta[idx-2][e_key] = str(first)+'-'+str(second)+'-'+str(third)
                            # temp 보정
                            temp_meta[idx-2][e_idx] = [(str(first)), str(second), str(third)]

                    if e_idx == 9 :
                        switch = False
                        if current_value != [] and before_before_value != []:
                            switch = True
                            first = (int(current_value[0][0]) + int(before_before_value[0][0])) // 2
                            second = (int(current_value[0][1]) + int(before_before_value[0][1])) // 2
                            third = (int(current_value[0][2]) + int(before_before_value[0][2])) // 2

                        elif current_value == [] and before_before_value != []:
                            switch = True
                            first = int(before_before_value[0][0])
                            second = int(before_before_value[0][2])
                            third = int(before_before_value[0][4])

                        elif current_value != [] and before_before_value == []:
                            switch = True
                            first = int(current_value[0][0])
                            second = int(current_value[0][2])
                            third = int(current_value[0][4])
                        if switch :
                            interpolated_meta[idx-2][e_key] = str(first)+':'+str(second)+':'+str(third)
                            # temp 보정
                            temp_meta[idx-2][e_idx] = [(str(first)), str(second), str(third)]

                    if e_idx == 6 or e_idx == 7 :

                        switch = False
                        if current_value != [] and before_before_value != []:
                            switch = True
                            first = (int(current_value[0][0]) + int(before_before_value[0][0]))/2
                            second = (int(current_value[0][2]) + int(before_before_value[0][2]))//2
                            if first < 0 :
                                first = math.ceil(first)
                                first = int(first)
                            else :
                                first = int(first)


                        elif current_value == [] and before_before_value != []:
                            switch = True
                            first = int(before_before_value[0][0])
                            second = int(before_before_value[0][2])

                        elif current_value != [] and before_before_value == []:
                            switch = True
                            first = int(current_value[0][0])
                            second = int(current_value[0][2])

                        if switch :
                            # temp 보정
                            interpolated_meta[idx - 2][e_key] = str(first) + "." + str(second) + '°'
                            temp_meta[idx-2][e_idx] = [(str(first), '.', str(second))]
                before_meta_info = re_frame_dict

        with open(output, "w", encoding='UTF-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=meta_list)
            writer.writeheader()
            for data in interpolated_meta:
                writer.writerow(data)
            print("FINISHED.")

dict = "E:\\2021_coastguard\\coastguard_git\\test.csv"
i = meta_info()
# i.geo_info(frame_folder_dir="E:\\2021_coastguard\\frame\\test")
i.interpolation(input=dict,
                output="E:\\2021_coastguard\\coastguard_git\\test_interpolated.csv")
