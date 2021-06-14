from abc import *

class clipper(metaclasss=ABCMeta):

    @abstractmethod
    def frame_clip(self,
                   A,
                   B,
                   C):
        """
        Code for dividing frames into 3 parts : 1) HDIR, 2) main frame(scene), 3) Meta parts
        :param A :
        :param B :
        :param C :
        :return:
        """
        pass

    @abstractmethod
    def meta_clip(self,
                  A,
                  B,
                  C):
        """
        Code for dividing 3) Meta parts into 8 parts : 1) TargetN, 2) TargetL, 3) AirN, 4) AirL, 5) Cam Az, 6) Cam El, 7) Date, 8) Time
        This code has to follow <frame_clip>
        :param A:
        :param B:
        :param C:
        :return:
        """
        pass

    @abstractmethod
    def save_img(self):
        """
        save clipped images
        :return:
        """
        pass

class divider(metaclass=ABCMeta):

    # @abstractmethod
    # def file_list(self,
    #               A,
    #               B,
    #               C):
    #     pass

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
        :param std_thr:
        :return:
        """
        pass

@abstractmethod
def tesseract():
    pass

@abstractmethod
def interpolation():
    pass
