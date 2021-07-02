import os
from PIL import Image
import numpy as np
import pandas as pd
import glob
import pytesseract
import natsort
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
        with open("test.csv", "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=meta_list)
            writer.writeheader()
            for data in frame_meta_list:
                writer.writerow(data)

        return frame_meta_list

    def interpolation(self,
                      input,
                      output):

        # input
        f = open(input, 'r', newline="")
        f = csv.reader(f)

        # pattern reg.
        Loc_p = re.compile('(\d{2,3})(\D*)(\d{2,3})(\D*)(\d{2,3})')  # Tlat, Tlon, ALat, Alon, Az, El
        Pos_p = re.compile('([+-]?\d{1,3})(\D*)(\d{1,3})')  # Az, El
        Date_p = re.compile('(\d{2})-([a-zA-Z]{3})-(\d{4})')  # Date
        Time_p = re.compile("(\d{2}):(\d{2}):(\d{2})")  # Time

        # geo-data
        meta_list = ["name", "Tlat", "Tlon", "Rng", "Alat", "Alon", "Az", "El", "Date", "Time"]
        interpolated_meta = []
        temp_meta = []

        for idx, line in enumerate(f) :
            re_frame_dict = {}

            if idx == 0 : continue

            Tlat_re = re.findall(Loc_p, line[1])
            if Tlat_re != []: Tlat = str(Tlat_re[0][0])+'°'+str(Tlat_re[0][2])+"."+str(Tlat_re[0][4])
            else : Tlat = None
            Tlon_re = re.findall(Loc_p, line[2])
            if Tlon_re != []: Tlon = str(Tlon_re[0][0])+'°'+str(Tlon_re[0][2])+"."+str(Tlon_re[0][4])
            else : Tlon = None
            Alat_re = re.findall(Loc_p, line[4])
            if Alat_re != []: Alat = str(Alat_re[0][0])+'°'+ str(Alat_re[0][2])+"."+str(Alat_re[0][4])
            else : Alat = None
            Alon_re = re.findall(Loc_p, line[5])
            if Alon_re != []: Alon = str(Alon_re[0][0])+'°'+str(Alon_re[0][2] +"."+str(Alon_re[0][4]))
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

            if idx == 1 : # 첫번째 메타는 None이 없다고 가정한다.
                interpolated_meta.append(re_frame_dict)
                before_meta_info = re_frame_dict
            elif idx == 2 :
                Err_key = [key for key, value in re_frame_dict.items() if value == None]
                for key in Err_key :
                    re_frame_dict[key] = before_meta_info[key]
                    t_idx = meta_list.index(key)
                    temp_meta[1][t_idx] = temp_meta[0][t_idx]
                interpolated_meta.append(re_frame_dict)
                before_meta_info = re_frame_dict
            else :
                Err_idx = [eidx for eidx, value in enumerate(before_meta_info.values()) if value == None]
                for e_idx in Err_idx :
                    current_value = temp_meta[-1][e_idx]
                    before_before_value = temp_meta[idx-3][e_idx]
                    if e_idx == 1 or e_idx == 2 or e_idx == 4 or e_idx == 5:
                        first = (int(current_value[0][0]) + int(before_before_value[0][0]))/2
                        second = (int(current_value[0][2]) + int(before_before_value[0][2]))/2
                        third = (int(current_value[0][4]) + int(before_before_value[0][4]))/2
                        # temp meta / re_frame_dict 모두 갱신해야함
                    if e_idx == 6 or e_idx == 7 :
                        first = (int(current_value[0][0]) + int(before_before_value[0][0]))/2
                        second = (int(current_value[0][2]) + int(before_before_value[0][2]))/2


                before_meta_info = re_frame_dict


            #
            # else :
            #     print("IDX : ", idx)
            #     Err_index = [idx for idx, value in enumerate(before_meta_info) if value==None]
            #     before_before_meta = temp_meta[idx-2]
            #     print("Err index : ", Err_index)
            #     if len(Err_index) != 0 :
            #         for idx in Err_index :
            #             print("before meta : ", before_before_meta)
            #             print("before : ", before_before_meta[idx])
            #             print("current meta : ", temp_meta[-1][idx])

                # print(len(list(re_frame_dict.values())))
                # current_meta = list(re_frame_dict.values())[Err_index]
                #
                # print("BB_meta : ", before_before_meta)
                # print("C_meta : ", current_meta)








        # 숫자를 리스트로 세파트로 나누어 list_number에 저장
        # for idx, row in enumerate(f):
        #     line_str = str(row)
        #     print(line_str)
        #     number_find = re.findall('(\d{1,3})', line_str)
        #     list_number.append(number_find)
        #     print("line_str : ", line_str)
        #     print("list number : ", list_number)
        #     # 0,1,2번째가 같다는 가정하에 실험 진행
        #     if idx < 2:
        #         all_list_number = []
        #         all_list_number.append(str(list_number[idx][0]) + '°' + str(list_number[idx][1]) + '.' + str(
        #             list_number[idx][2]) + '\'')
        #         writer.writerow(all_list_number)
        #
        #     if idx > 2:
        #         # idx>2 부터 보정 시작
        #         # before, after 저장
        #         err_before_str = list_number[idx - 2]
        #         err_after_str = list_number[idx]
        #
        #         # 숫자 오류 발생
        #         # 보통 4개의 넘버 그룹이 생기는 이유는 '를 1로 보았기 때문입으로 3개 미만의 숫자 그룹으로 인식된 오류만 보정
        #         if len(list_number[idx - 1]) < 3:
        #
        #             # idx도 오류일 경우
        #             if len(list_number[idx]) < 3:
        #                 err_after_str = err_before_str
        #
        #             print("before", err_before_str)
        #             print("after", err_after_str)
        #             print("error", list_number[idx - 1])
        #
        #             # 숫자 보정 : (idx-2 + idx) / 2 = idx-1
        #             current_num_0 = (int(err_before_str[0]) + int(err_after_str[0])) // 2
        #             current_num_1 = (int(err_before_str[1]) + int(err_after_str[1])) // 2
        #             current_num_2 = (int(err_before_str[2]) + int(err_after_str[2])) // 2
        #             list_number[idx - 1] = [str(current_num_0), str(current_num_1), str(current_num_2)]
        #
        #             print("current", list_number[idx - 1])
        #         # 저장
        #         all_list_number = []
        #         all_list_number.append(str(list_number[idx - 1][0]) + '°' + str(list_number[idx - 1][1]) + '.' + str(
        #             list_number[idx - 1][2]) + '\'')
        #         writer.writerow(all_list_number)
        #     # 마지막번째 숫자 보정
        #     if idx == 2005:
        #         if len(list_number[2005]) != 3:
        #             err_before_str = list_number[idx - 2]
        #             err_after_str = list_number[idx - 1]
        #             print("2005before", err_before_str)
        #             print("2005after", err_after_str)
        #             print("2005error", list_number[2005])
        #             # 숫자 보정 : (idx-2 + idx) / 2 = idx-1
        #             current_num_0 = (int(err_before_str[0]) + int(err_after_str[0])) // 2
        #             current_num_1 = (int(err_before_str[1]) + int(err_after_str[1])) // 2
        #             current_num_2 = (int(err_before_str[2]) + int(err_after_str[2])) // 2
        #             list_number[idx] = [str(current_num_0), str(current_num_1), str(current_num_2)]
        #         else:
        #             list_number[idx] = list_number[idx]
        #         print("2005 : current", list_number[idx])
        #         all_list_number = []
        #         all_list_number.append(
        #             str(list_number[idx][0]) + '°' + str(list_number[idx][1]) + '.' + str(list_number[idx][2]) + '\'')
        #         writer.writerow(all_list_number)
        #
        # csvfile.close()
        # print('Fished')

# mi = meta_info()
# meta_dict = mi.geo_info("E:\\2021_coastguard\\frame\\test")

dict = "E:\\2021_coastguard\\coastguard_git\\test.csv"#"csv_3_1 (1).csv"
i = meta_info()
i.interpolation(input=dict,
                output="E:\\2021_coastguard\\coastguard_git\\csv_3_2 (1)_inter.csv")

# class clipper:
#
#     def frame_index(self):
#         """
#         frame index : file name or order or ...
#         :return:
#         """
#         pass
#     # 클립 후 삭제하는 파트를 수정 -> 바로 인식하는 단계로 넘어갈 것
#     def frame_clip(self,
#                   original_path,
#                   cutted_path,
#                   areamode):
#         """
#         Code for dividing frames into 3 parts : 1) HDIR, 2) main frame(scene), 3) Meta parts
#         :param original_path
#         :param cutted_path : directory to save image
#         :param areamode : part what you want clip
#         :return:
#         """
#         img_list = os.listdir(original_path)
#         img_list = natsort.natsorted(img_list, reverse=False)
#
#         if areamode == 1:
#             area = (0, 0, 1280, 26) # Image Part1 : "HDIR WF0V Enh2 Mod Wht DDE CENT- GeoPnt R"
#         if areamode == 2:
#             area = (0, -26, 1280, 666) # -26??
#         if areamode == 3:
#             area = (0, 666, 1280, 720) # Image Part3 : Geo-Info part
#
#         for i, filename in enumerate(img_list):
#             im = Image.open(original_path + '/' + filename)
#             crop_image = im.crop(area)
#             savename = cutted_path + '/' + 'crop_{0}'.format(i) + '.jpg'
#             crop_image.save(savename)
#
#     def meta_clip(self,
#                   original_path,
#                   cutted_path,
#                   areamode):
#         """
#         Code for dividing 3) Meta parts into 8 parts : 1) TargetN, 2) TargetL, 3) AirN, 4) AirL, 5) Cam Az, 6) Cam El, 7) Date, 8) Time
#         This code has to follow <frame_clip>
#         :param original_path
#         :param cutted_path : directory to save meta image
#         :param areamode : part what you want clip
#         :return:
#         """
#         img_list = os.listdir(original_path)
#         img_list = natsort.natsorted(img_list, reverse=False)
#
#         if areamode == 1:
#             area = (110, 0, 250, 25) # TLat
#         if areamode == 2:
#             area = (327, 0, 475, 25) # TLon
#         if areamode == 3:
#             area = (70, 30, 210, 50) # ALat
#         if areamode == 4:
#             area = (340, 30, 490, 50) # ALon
#         if areamode == 5:
#             area = (760, 30, 850, 50) # Az
#         if areamode == 6:
#             area = (910, 30, 995, 50) # EL
#         if areamode == 7:
#             area = (1005, 30, 1160, 50) # Date
#         if areamode == 8:
#             area = (1165, 28, 1278, 55) # Time
#
#         for i, filename in enumerate(img_list):
#             im = Image.open(original_path + '/' + filename)
#             crop_image = im.crop(area)
#             savename = cutted_path + '/' + 'crop_{0}'.format(i) + '.jpg'
#             crop_image.save(savename)
#
#
# class divider(metaclass=ABCMeta):
#
#     def frame_classifier(self,
#                          frame_folder,
#                          dst,
#                          avg_thr=1.5,
#                          std_thr=0.5):
#         """
#         Code for dividing frames into RGB or THR
#         :param frame_folder:
#         :param dst:
#         :param avg_thr:
#         :param std_thr
#         :return:
#         """
#         pass
#
# class ocr(metaclass=ABCMeta):
#
#     def ocr_python_tesseract_path(self,
#                                   original_path,
#                                   csvfile):
#
#         """
#         Code for ocr process image to text
#         :param original_path : where the image is stored
#         :param csvfile : the csv file name you want to save or path
#         :return
#         """
#
#         csvfile = open(csvfile, "w", newline="", encoding='UTF-8-sig')
#         writer = csv.writer(csvfile)
#         img_list = os.listdir(original_path)
#         img_list = natsort.natsorted(img_list, reverse=False)
#
#         for i, img_file in enumerate(img_list):
#             img_abs_dir = os.path.join(original_path, img_file)
#             _, ext = os.path.splitext(img_abs_dir)
#             img = cv2.imread(img_abs_dir, cv2.IMREAD_GRAYSCALE)
#             filename = "{}.jpg".format(os.getpid())
#             cv2.imwrite(filename, img)
#             text = pytesseract.image_to_string(Image.open(filename), lang=None, config='--psm 6')
#             os.remove(filename)
#             csv_list = []
#             re.match('[A-Z]+$', text.rstrip())
#             csv_list.append(text)
#             csv_list = [item.rstrip() for item in csv_list]
#             writer.writerow(csv_list)
#             print(csv_list)
#         csvfile.close()
#         print('Fished')
#
    # def interpolation(self,
    #              input,
    #              pattern,
    #              output):
    #
    #     """
    #        Code for ocr process image to text
    #        :param input : what you want interpolation
    #        :param pattern : area mode
    #        :param output : directory to save image
    #        :return
    #     """
    #     # input
    #     f = open(input, 'r', newline="", encoding='UTF-8-sig')
    #     f = csv.reader(f)
    #
    #     # output
    #     csvfile = open(output, "w", newline="", encoding='UTF-8-sig')
    #     writer = csv.writer(csvfile)
    #
    #     list_number = []
    #
    #     # pattern : 정규 표현식
    #     if pattern == 1 or pattern == 3:
    #         pattern = re.compile('(\d{2}°)\s(\d{1,2}.\d{3}\')')
    #     elif pattern == 2 or pattern == 4:
    #         pattern = re.compile('(\d{3}°)\s(\d{1,2}.\d{3}\')')
    #     elif pattern == 5:
    #         pattern = re.compile('([-|+]?\d{1,3}\.\d{1}°)')
    #     elif pattern == 6:
    #         pattern = re.compile('[-]\d{1,2}\.\d{1}°')
    #     elif pattern == 7:
    #         pattern = re.compile('\d{2}-\D{3}-\d{4}')
    #     else:
    #         pattern == re.compile('\d{2}:\d{2}:\d{2}L')
    #
    #     # 숫자를 리스트로 세파트로 나누어 list_number에 저장
    #     for idx, row in enumerate(f):
    #         line_str = "".join(map(str, row))
    #         number_find = re.findall('(\d{1,3})', line_str)
    #         list_number.append(number_find)
    #
    #         # 0,1,2번째가 같다는 가정하에 실험 진행
    #         if idx < 2:
    #             all_list_number = []
    #             all_list_number.append(str(list_number[idx][0]) + '°' + str(list_number[idx][1]) + '.' + str(
    #                 list_number[idx][2]) + '\'')
    #             writer.writerow(all_list_number)
    #
    #         if idx > 2:
    #             # idx>2 부터 보정 시작
    #             # before, after 저장
    #             err_before_str = list_number[idx - 2]
    #             err_after_str = list_number[idx]
    #
    #             # 숫자 오류 발생
    #             # 보통 4개의 넘버 그룹이 생기는 이유는 '를 1로 보았기 때문입으로 3개 미만의 숫자 그룹으로 인식된 오류만 보정
    #             if len(list_number[idx - 1]) < 3:
    #
    #                 # idx도 오류일 경우
    #                 if len(list_number[idx]) < 3:
    #                     err_after_str = err_before_str
    #
    #                 print("before", err_before_str)
    #                 print("after", err_after_str)
    #                 print("error", list_number[idx - 1])
    #
    #                 # 숫자 보정 : (idx-2 + idx) / 2 = idx-1
    #                 current_num_0 = (int(err_before_str[0]) + int(err_after_str[0])) // 2
    #                 current_num_1 = (int(err_before_str[1]) + int(err_after_str[1])) // 2
    #                 current_num_2 = (int(err_before_str[2]) + int(err_after_str[2])) // 2
    #                 list_number[idx - 1] = [str(current_num_0), str(current_num_1), str(current_num_2)]
    #
    #                 print("current", list_number[idx - 1])
    #             # 저장
    #             all_list_number = []
    #             all_list_number.append(str(list_number[idx - 1][0]) + '°' + str(list_number[idx - 1][1]) + '.' + str(
    #                 list_number[idx - 1][2]) + '\'')
    #             writer.writerow(all_list_number)
    #         # 마지막번째 숫자 보정
    #         if idx == 2005:
    #             if len(list_number[2005]) != 3:
    #                 err_before_str = list_number[idx - 2]
    #                 err_after_str = list_number[idx - 1]
    #                 print("2005before", err_before_str)
    #                 print("2005after", err_after_str)
    #                 print("2005error", list_number[2005])
    #                 # 숫자 보정 : (idx-2 + idx) / 2 = idx-1
    #                 current_num_0 = (int(err_before_str[0]) + int(err_after_str[0])) // 2
    #                 current_num_1 = (int(err_before_str[1]) + int(err_after_str[1])) // 2
    #                 current_num_2 = (int(err_before_str[2]) + int(err_after_str[2])) // 2
    #                 list_number[idx] = [str(current_num_0), str(current_num_1), str(current_num_2)]
    #             else:
    #                 list_number[idx] = list_number[idx]
    #             print("2005 : current", list_number[idx])
    #             all_list_number = []
    #             all_list_number.append(
    #                 str(list_number[idx][0]) + '°' + str(list_number[idx][1]) + '.' + str(list_number[idx][2]) + '\'')
    #             writer.writerow(all_list_number)
    #
    #     csvfile.close()
    #     print('Fished')

#     def csv_merge(self,
#                   input_file,
#                   mode,
#                   output_file):
#
#         """
#            Code for merge csv
#            :param input_file : csv file you want merge
#            :param mode : start name of csv file like 'csv_3_*_re.csv'
#            :param output_file : directory to save csv
#            :return
#         """
#
#         allFile_list = glob.glob(os.path.join(input_file, mode))  # glob함수로 sales_로 시작하는 파일들을 모은다
#         print(allFile_list)
#         allData = []  # 읽어 들인 csv파일 내용을 저장할 빈 리스트를 하나 만든다
#
#         for file in allFile_list:
#             df = pd.read_csv(file)  # for구문으로 csv파일들을 읽어 들인다
#             allData.append(df)  # 빈 리스트에 읽어 들인 내용을 추가한다
#             print(allData)
#
#         dataCombine = pd.concat(allData, axis=1, ignore_index=True)  # concat함수를 이용해서 리스트의 내용을 병합
#         # axis=0은 수직으로 병합함. axis=1은 수평. ignore_index=True는 인데스 값이 기존 순서를 무시하고 순서대로 정렬되도록 한다.
#         dataCombine.to_csv(output_file, index=False)  # to_csv함수로 저장한다. 인데스를 빼려면 False로 설정
