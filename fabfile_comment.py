'''
로컬 개발 PC에서 원격 서버의 환경부터 운용까지 모든 세팅을 진행한다
'''
from fabric.contrib.files import append, exists, sed, put
from fabric.api import local, run, sudo, env
import os
import json

# 1. 프로젝트 디렉토리
# print(__file__)
# print(os.path.abspath(__file__)) # c:/Users/paran/Desktop/BJM2019/mcampus/py_project/first/fabfile.py
# print(os.path.dirname(os.path.abspath(__file__))) # c:\Users\paran\Desktop\BJM2019\mcampus\py_project\first\fabfile.py
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) # c:\Users\paran\Desktop\BJM2019\mcampus\py_project\first
print(PROJECT_DIR)
# c:\Users\paran\Desktop\BJM2019\mcampus\py_project\first

# 2. 환경변수 로드
# json.load() : json파일을 읽어서 그 구조를 유지하여 리턴 (피클로드랑 같은 맥락)
envs = json.load( open(os.path.join(PROJECT_DIR,'deploy.json') ) )
print(envs)
''' 
{'REPO_URL': 'https://github.com/wjdalsbjm/first', 
'PROJECT_NAME': 'first', 
'REMOTE_HOST': 'ec2-54-180-89-42.ap-northeast-2.compute.amazonaws.com', 
'REMOTE_HOST_SSH': '54.180.89.42', 
'REMOTE_USER': 'ubuntu'}
json을 읽어서 파이썬 딕셔너리 구조로 갖고옴
'''
# 3. 로드한 환경변수(읽어온 json)를 상수(변하지 않는)의미로 설정
REPO_URL = envs['REPO_URL']
PROJECT_NAME = envs['PROJECT_NAME']
REMOTE_HOST = envs['REMOTE_HOST']
REMOTE_HOST_SSH = envs['REMOTE_HOST_SSH']
REMOTE_USER = envs['REMOTE_USER']

# 4. 환경변수(fabric.api에 있는 환경변수 env)에 필요한 부분 추가
env.user = REMOTE_USER
env.hosts = [
    REMOTE_HOST_SSH,
]
# 4-1. pem 파일로 로그인을 하기 위해
env.use_ssh_config = True
env.key_filename = 'bjm.pem' # AWS 폴더에서 옮겨왔음 -> 동일폴더에 위치

# 5. 원격지에 세팅될 디렉토리 지정
project_folder = '/home/{}/{}'.format(env.user, PROJECT_NAME) # REMOTE_USER 
# ubuntu@ip-172-31-25-136:~$ cd ..
# ubuntu@ip-172-31-25-136:/home$ ls
# ubuntu
# root/home/ubuntu/first 사용자명 프로젝트명 바뀔 수 있으니 동적으로
print(project_folder) # /home/ubuntu/first

# 6. 리눅스에 설치될 기본 패키지 목록
apt_requirements = [
    'curl', # get post?
    'git', # 소스 받아야
    'python3-pip',
    'python3-dev',
    'build-essential',
    'apache2',
    'libapache2-mod-wsgi-py3', # 아파치와 python3를
    'python3-setuptools', # 설치되는 모듈 중 셋업이 필요한 게 있음
    'libssl-dev',
    'libffi-dev'
]

# 패브릭 구동 시 fab 함수명
# 이중에서 _함수명은 구동 불가

'''
작성이 모두 끝난 후
fab new_initServer
소스가 변경된 후
fab update
'''
# 7. 기본 신규 서버 세팅 함수
def new_initServer():
    _setup() # 최초에
    update()

# 7-1. 리눅스 셋업
def _setup(): # _를 쓴다? direct로 안 부르겠다는 의미 : 내부에서만 쓸 거다
    # 리눅스 패키지 업데이트 주소 or 패키지 목록 세팅
    _init_apt()
    # 필요한 패키지 설치
    _install_apt_pacakges(apt_requirements)
    # 가상환경 구축 (pip install virtualenv)
    # 목표 : 운영체계에는 가장 기본만 설치, 프로젝트별로 필요한 패키지를 설치하여 상호 프로젝트 간 영향을 받지 않게 만드는 방식 
    # 가상환경 위치로 이동 virtualenv env, cd env/Scripts
    # activate or . activate (리눅스, 맥) - 프롬프트가 새로 열림
    # (env) > pip list
    # (env) > pip install flask

    # PS C:\Users\paran\Desktop\BJM2019\mcampus\py_project\first> cd ..
    # PS C:\Users\paran\Desktop\BJM2019\mcampus\py_project> virtualenv env
    # Using base prefix 'c:\\users\\paran\\appdata\\local\\programs\\python\\python36'
    # New python executable in C:\Users\paran\Desktop\BJM2019\mcampus\py_project\env\Scripts\python.exe
    # Installing setuptools, pip, wheel...
    # done.

    # (env) C:\Users\paran\Desktop\BJM2019\mcampus\py_project\env\Scripts>pip list # 안 되면 cmd에서 해봐
    # Package    Version
    # ---------- -------
    # pip        19.0.1
    # setuptools 40.8.0
    # wheel      0.32.3
    # 가상환경으로 따로 빼야 패키지들의 업데이트에 따른 이전 프로젝트의 영향을 없앨 수 있음
    # 구동 : C:\~\py_project\env\Scripts\python run.py
    _making_virtualenv()

# 7-2. apt(우분트상) 패키지를 업데이트 여부 확인 및 업데이트
def _init_apt():
    yn = input('ubuntu linux update ok?: [y/n]')
    if yn == 'y': # 사용자가 업데이트를 원한 경우
        # sudo => root 권한으로 실행할 때
        # sudo apt-get update
        # sudo apt-get upgrade
        sudo('apt-get update && apt-get -y upgrade')

# 7-3. 리눅스 상에 필요한 패키지 설치
def _install_apt_pacakges(requires):
    # 설치할 패키지 목록을 나열
    reqs = ''
    for req in requires:
        reqs += ' ' + req
    # reqs => curl git python3-pip ...
    # 수행
    # sudo apt-get install curl
    sudo('apt-get -y install '+reqs)

# 7-4. 가상환경 구축
def _making_virtualenv():
    # 설치여부 확인 => 파일여부 체크
    if not exists('~/.virtualenvs'): # 폴더 만들고
        # 가상환경 폴더
        # run으로 구동하면 ubuntu 소유(퍼미션), sudo로 구동하면 root 소유
        run('mkdir ~/.virtualenvs')
        # 패키지 설치
        sudo('pip3 install virtualenv virtualenvwrapper') # 이제부터 pip 쓸 수 있음
        # 환경변수 반영 및 쉘(윈도우에서 배치) 구동 가상환경 구축
        cmd = """
            '# python virtualenv global setting
            export WORKON_HOME=~/.virtualenvs
            # python location
            export VIRTUALENVWRAPPER_PYTHON="$(command \which python3)"
            # shell 실행
            source /usr/local/bin/virtualenvwrapper.sh'
        """
        run('echo {} >> ~/.bashrc'.format(cmd)) # 시스템 - 설정 - 고급 - 환경변수 를 linux는 저 안에다가 쓰는 것으로 됨

# 8. 소스 수정 후 서버에 반영할 때 사용하는 함수 # git하고
def update():
    # 8-1. 소스를 최신으로 github를 통해서 받는다
    _git_update()
    # 8-2. 가상환경에 필요한 패키지 설치 (1회만 수행)
    _virtualenv_update()
    # 8-3. 아파치에 가상 호스트를 세팅 (1회만)
    _virtualhost_make()
    # 8-4. 아파치가 프로젝트를 access할 수 있게 권한 처리 (1회만)
    # 신규 파일에 대한 검토 필요 -> 그냥 매번 수행
    _grant_apache()
    # 8-5. 서버 재가동(아파치와 관련)
    _restart_apache()

# 8-1. 저장소에서 최신 소스로 반영
def _git_update():
    if exists(project_folder + '/.git'): # 프로젝트 폴더 안에 .git이 존재하는가?
        # first 폴더(프로젝트 폴더)로 이동하고 &&(계속해서 명령어) 저장소로부터 데이터를 fetch를 해서 최신 정보 가져옴
        run('cd %s && git fetch' % (project_folder,))
    else: # 없으면 -> 저장소로부터 최초로 프로젝트를 받아온다
        run('git clone %s %s' % (REPO_URL, project_folder))
    # git의 커밋된 로그를 최신으로 한 개 가져온다 그것의 번호를 리턴
    # local:git log -n 1 --format=%H => 123456789 어떤 숫자로 나옴 (커밋번호?)
    current_commit = local("git log -n 1 --format=%H", capture=True)
    # first 폴더로 이동 (현재 first라도) 그리고 git reset --hard 123456789
    # 최신 커밋사항으로 소스 반영
    run('cd %s && git reset --hard %s' % (project_folder, current_commit))
    #run('cd %s && git reset --hard' % (project_folder, ))

# 8-2. 본 프로젝트에 해당되는 가상환경을 구축하고 그 환경에 그 프로젝트에서 사용하는 모듈 설치
def _virtualenv_update():
    # /home/ubuntu/.virtualenvs/first 라는 가상환경 위치
    virtualenv_folder = project_folder + '/../.virtualenvs/{}'.format(PROJECT_NAME) # 점 두개 : 위로 한 번 올라옴
    # /home/ubuntu/.virtualenvs/first/bin/pip 가 존재하지 않으면
    if not exists(virtualenv_folder + '/bin/pip'):
        # /home/ubuntu/.virtualenvs로 이동하고 그리고 virtualenv first 가상환경을 생성하라 (프로젝트 이름을 따라서) (1회 수행)
        run('cd /home/%s/.virtualenvs && virtualenv %s' % (env.user, PROJECT_NAME))
    # 상관없이 수행 => 필요한 파이썬 모듈을 설치한다 (이 가상환경에만 적용)
    # /home/ubunt/.virtualenvs/first/bin/pip install
    # -r /home/ubunt/first/requirements.txt
    run('%s/bin/pip install -r %s/requirements.txt' % (
        virtualenv_folder, project_folder
    ))

# 여기서는 생략
def _ufw_allow():
    # ufw에서 80 포트를 오픈하는 과정, 리로드
    sudo("ufw allow 'Apache Full'")
    sudo("ufw reload")

# 8-3. 아파치 서버와 flask로 구성된 파이썬 서버간의 연결파트(핵심)
# 아파치는 setup의  _install_apt_pacakges()에서 설치됨
def _virtualhost_make(): # XML?
    script = """
    '<VirtualHost *:80>
    ServerName {servername}
    <Directory /home/{username}/{project_name}>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
    WSGIDaemonProcess {project_name} python-home=/home/{username}/.virtualenvs/{project_name} python-path=/home/{username}/{project_name}
    WSGIProcessGroup {project_name}
    WSGIScriptAlias / /home/{username}/{project_name}/wsgi.py
    
    ErrorLog ${{APACHE_LOG_DIR}}/error.log
    CustomLog ${{APACHE_LOG_DIR}}/access.log combined
    
    </VirtualHost>'""".format(
        username=REMOTE_USER, # ubuntu
        project_name=PROJECT_NAME, # first
        servername=REMOTE_HOST, # 도메인
    )
    # 아파치 사이트 목록 설정 파일에 first.conf 파일을 하나 생성해서 둔다
    sudo('echo {} > /etc/apache2/sites-available/{}.conf'.format(script, PROJECT_NAME))
    # 반영
    sudo('a2ensite {}.conf'.format(PROJECT_NAME))

# 아파치 서버가 파이썬 웹을 엑세스 할 수 있게 처리
def _grant_apache():
    # 파일의 소유주나 소유그룹을 변경하기 위한 리눅스 명령어
    # 아파치쪽 웹의 소유주와 프로젝트 소유주를 일치시킴
    sudo('chown -R :www-data ~/{}'.format(PROJECT_NAME))
    # 프로젝트 폴더의 권한을 775로 변경
    # 권한(쓰기w, 읽기r, 실행x)
    # 775는 루트, 소유주는 다 사용 가능, 누구나 경우는 읽기만 가능 (777은 아무나 파일을 변경할 수 있음)
    sudo('chmod -R 775 ~/{}'.format(PROJECT_NAME))

# 8-5. 아파치 서버 재가동 (아파치가 flask를 물고 있다 virtual host에서 wsgi파일을 물게 해놨다)
def _restart_apache():
    sudo('service apache2 restart')