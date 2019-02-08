'''
아파치 서버가 이 파일을 구동하여 flask 가동시킴
여기서는 Flask 객체를 가져와서 참조
'''
import sys
import os

# 경로 설정
CUR_DIR = os.getcwd()
# 에러의 출력 방향과 동일하게 일반 출력 방향 설정
sys.stdout = sys.stderr
# path 추가

sys.path.insert(0, CUR_DIR)

# 서버 가져오기
from run import app as application # from 출처는 모듈 or 패키지
# app은 Flask 객체 -> if __name__=='__main__': 부분 빼고는 메모리로 올라옴