# first
최초 flask app 소스 관리

배포 관련 사항
deploy.json : 도메인, 아이피 등 정보
              형식이 JSON이라서 주석 불가 (key를 쓸 때 명확하게 쓰는)
fabfile.py : 페브릭 작업 내용 기술
fabfile_comment.py : 주석 버전
wsgi.py : entry 파일 (서버구동 시 시작점)
requirements.txt : 서버구동 시 필요한 모듈을 기술 (버전 포함) 개발할 때 사용했던 서드파트 모듈 정보를 기술

# 서버 로그 확인
접속로그
> tail -f /var/log/apache2/access.log
에러로그
> tail -f /var/log/apache2/error.log