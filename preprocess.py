from abc import *
import os
from PIL import Image
import pandas as pd
import glob
import pytesseract
import natsort
import csv
import re
import cv2

class clipper(metaclasss=ABCMeta):

    @abstractmethod
    def frame_clip(self,
                  original_path,
                  cutted_path,
                  areamode):
        """
        Code for dividing frames into 3 parts : 1) HDIR, 2) main frame(scene), 3) Meta parts
        :param original_path
        :param cutted_path : directory to save image
        :param areamode : part what you want clip
        :return:
        """
        img_list = os.listdir(original_path)
        img_list = natsort.natsorted(img_list, reverse=False)

        if areamode == 1:
            area = (0, 0, 1280, 26)
        if areamode == 2:
            area = (0, -26, 1280, 666)
        if areamode == 3:
            area = (0, 666, 1280, 720)

        for i, filename in enumerate(img_list):
            im = Image.open(original_path + '/' + filename)
            crop_image = im.crop(area)
            savename = cutted_path + '/' + 'crop_{0}'.format(i) + '.jpg'
            crop_image.save(savename)

    @abstractmethod
    def meta_clip(self,
                  original_path,
                  cutted_path,
                  areamode):
        """
        Code for dividing 3) Meta parts into 8 parts : 1) TargetN, 2) TargetL, 3) AirN, 4) AirL, 5) Cam Az, 6) Cam El, 7) Date, 8) Time
        This code has to follow <frame_clip>
        :param original_path
        :param cutted_path : directory to save meta image
        :param areamode : part what you want clip
        :return:
        """

        img_list = os.listdir(original_path)
        img_list = natsort.natsorted(img_list, reverse=False)

        if areamode == 1:
            area = (110, 0, 250, 25)
        if areamode == 2:
            area = (327, 0, 475, 25)
        if areamode == 3:
            area = (70, 30, 210, 50)
        if areamode == 4:
            area = (340, 30, 490, 50)
        if areamode == 5:
            area = (760, 30, 850, 50)
        if areamode == 6:
            area = (910, 30, 995, 50)
        if areamode == 7:
            area = (1005, 30, 1160, 50)
        if areamode == 8:
            area = (1165, 28, 1278, 55)

        for i, filename in enumerate(img_list):
            im = Image.open(original_path + '/' + filename)
            crop_image = im.crop(area)
            savename = cutted_path + '/' + 'crop_{0}'.format(i) + '.jpg'
            crop_image.save(savename)

class divider(metaclass=ABCMeta):

    @abstractmethod
    def frame_classifier(self,
                         frame_folder,
                         dst,
                         avg_thr=1.5,
                         std_thr=0.5):
        """
        Code for dividing frames into RGB or THR
        :param frame_folder:
        :param dst:
        :param avg_thr:
        :param std_thr
        :return:
        """
        pass

class ocr(metaclass=ABCMeta):
    @abstractmethod
    def ocr_python_tesseract_path(self,
                                  original_path,
                                  csvfile):

        """
        Code for ocr process image to text
        :param original_path : where the image is stored
        :param csvfile : the csv file name you want to save or path
        :return
        """

        csvfile = open(csvfile, "w", newline="", encoding='UTF-8-sig')
        writer = csv.writer(csvfile)
        img_list = os.listdir(original_path)
        img_list = natsort.natsorted(img_list, reverse=False)

        for i, img_file in enumerate(img_list):
            img_abs_dir = os.path.join(original_path, img_file)
            _, ext = os.path.splitext(img_abs_dir)
            img = cv2.imread(img_abs_dir, cv2.IMREAD_GRAYSCALE)
            filename = "{}.jpg".format(os.getpid())
            cv2.imwrite(filename, img)
            text = pytesseract.image_to_string(Image.open(filename), lang=None, config='--psm 6')
            os.remove(filename)
            csv_list = []
            re.match('[A-Z]+$', text.rstrip())
            csv_list.append(text)
            csv_list = [item.rstrip() for item in csv_list]
            writer.writerow(csv_list)
            print(csv_list)
        csvfile.close()
        print('Fished')

    @abstractmethod
    def interpolation(self,
                 input,
                 pattern,
                 output):

        """
           Code for ocr process image to text
           :param input : what you want interpolation
           :param pattern : area mode
           :param output : directory to save image
           :return
        """
        # input
        f = open(input, 'r', newline="", encoding='UTF-8-sig')
        f = csv.reader(f)

        # output
        csvfile = open(output, "w", newline="", encoding='UTF-8-sig')
        writer = csv.writer(csvfile)

        list_number = []

        # pattern : 정규 표현식
        if pattern == 1 or pattern == 3:
            pattern = re.compile('(\d{2}°)\s(\d{1,2}.\d{3}\')')
        elif pattern == 2 or pattern == 4:
            pattern = re.compile('(\d{3}°)\s(\d{1,2}.\d{3}\')')
        elif pattern == 5:
            pattern = re.compile('([-|+]?\d{1,3}\.\d{1}°)')
        elif pattern == 6:
            pattern = re.compile('[-]\d{1,2}\.\d{1}°')
        elif pattern == 7:
            pattern = re.compile('\d{2}-\D{3}-\d{4}')
        else:
            pattern == re.compile('\d{2}:\d{2}:\d{2}L')

        # 숫자를 리스트로 세파트로 나누어 list_number에 저장
        for idx, row in enumerate(f):
            line_str = "".join(map(str, row))
            number_find = re.findall('(\d{1,3})', line_str)
            list_number.append(number_find)

            # 0,1,2번째가 같다는 가정하에 실험 진행
            if idx < 2:
                all_list_number = []
                all_list_number.append(str(list_number[idx][0]) + '°' + str(list_number[idx][1]) + '.' + str(
                    list_number[idx][2]) + '\'')
                writer.writerow(all_list_number)

            if idx > 2:
                # idx>2 부터 보정 시작
                # before, after 저장
                err_before_str = list_number[idx - 2]
                err_after_str = list_number[idx]

                # 숫자 오류 발생
                # 보통 4개의 넘버 그룹이 생기는 이유는 '를 1로 보았기 때문입으로 3개 미만의 숫자 그룹으로 인식된 오류만 보정
                if len(list_number[idx - 1]) < 3:

                    # idx도 오류일 경우
                    if len(list_number[idx]) < 3:
                        err_after_str = err_before_str

                    print("before", err_before_str)
                    print("after", err_after_str)
                    print("error", list_number[idx - 1])

                    # 숫자 보정 : (idx-2 + idx) / 2 = idx-1
                    current_num_0 = (int(err_before_str[0]) + int(err_after_str[0])) // 2
                    current_num_1 = (int(err_before_str[1]) + int(err_after_str[1])) // 2
                    current_num_2 = (int(err_before_str[2]) + int(err_after_str[2])) // 2
                    list_number[idx - 1] = [str(current_num_0), str(current_num_1), str(current_num_2)]

                    print("current", list_number[idx - 1])
                # 저장
                all_list_number = []
                all_list_number.append(str(list_number[idx - 1][0]) + '°' + str(list_number[idx - 1][1]) + '.' + str(
                    list_number[idx - 1][2]) + '\'')
                writer.writerow(all_list_number)
            # 마지막번째 숫자 보정
            if idx == 2005:
                if len(list_number[2005]) != 3:
                    err_before_str = list_number[idx - 2]
                    err_after_str = list_number[idx - 1]
                    print("2005before", err_before_str)
                    print("2005after", err_after_str)
                    print("2005error", list_number[2005])
                    # 숫자 보정 : (idx-2 + idx) / 2 = idx-1
                    current_num_0 = (int(err_before_str[0]) + int(err_after_str[0])) // 2
                    current_num_1 = (int(err_before_str[1]) + int(err_after_str[1])) // 2
                    current_num_2 = (int(err_before_str[2]) + int(err_after_str[2])) // 2
                    list_number[idx] = [str(current_num_0), str(current_num_1), str(current_num_2)]
                else:
                    list_number[idx] = list_number[idx]
                print("2005 : current", list_number[idx])
                all_list_number = []
                all_list_number.append(
                    str(list_number[idx][0]) + '°' + str(list_number[idx][1]) + '.' + str(list_number[idx][2]) + '\'')
                writer.writerow(all_list_number)

        csvfile.close()
        print('Fished')

    def csv_merge(self,
                  input_file,
                  mode,
                  output_file):

        """
           Code for merge csv
           :param input_file : csv file you want merge
           :param mode : start name of csv file like 'csv_3_*_re.csv'
           :param output_file : directory to save csv
           :return
        """

        allFile_list = glob.glob(os.path.join(input_file, mode))  # glob함수로 sales_로 시작하는 파일들을 모은다
        print(allFile_list)
        allData = []  # 읽어 들인 csv파일 내용을 저장할 빈 리스트를 하나 만든다

        for file in allFile_list:
            df = pd.read_csv(file)  # for구문으로 csv파일들을 읽어 들인다
            allData.append(df)  # 빈 리스트에 읽어 들인 내용을 추가한다
            print(allData)

        dataCombine = pd.concat(allData, axis=1, ignore_index=True)  # concat함수를 이용해서 리스트의 내용을 병합
        # axis=0은 수직으로 병합함. axis=1은 수평. ignore_index=True는 인데스 값이 기존 순서를 무시하고 순서대로 정렬되도록 한다.
        dataCombine.to_csv(output_file, index=False)  # to_csv함수로 저장한다. 인데스를 빼려면 False로 설정

