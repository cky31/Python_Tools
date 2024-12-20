from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFrame,
    QHBoxLayout, QWidget, QMessageBox, QProgressBar, QDialog, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
import paramiko
import re
import os
import sys

program_version = '1.1' # 프로그램 버전 기록용
user_info = {"id": "", "pw": "", "ip": ""} # 사용자의 정보 저장
check_runlevel_count = 20 # 런레벨 변경 후 재시도 체크 카운트 횟수

# MAC OS에서 tkinter는 버튼 클릭 히트박스 이슈 / message(info/error/stop 등..)박스 아이콘 고정 이슈가 있음
# PyQt6 모듈로 GUI모듈을 교체

# SSH 접속 함수
class SSHThread(QThread):
    result_signal = pyqtSignal(str) 
    def __init__(self, ip, username, password, timeout=10):
        super().__init__()
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout

    def run(self): # 접속 시도 후 콜백 변수에 성공 유무를 반환 받음
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, username=self.username, password=self.password, timeout=self.timeout)
            ssh.close()
            self.result_signal.emit("success")
        except Exception as e:
            self.result_signal.emit(f"failure: {str(e)}")

# 로그인창 GUI 구성 클래스 + 로그인창에서 수행될 기능 함수들
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 타이틀명 / 창 사이즈 / 레이아웃 구성 / 간격, 위치 등을 선언
        self.setWindowTitle("Login")
        self.setFixedSize(310, 190)
        # 응용프로그램 기본 아이콘 변경을 위한 아이콘 경로 설정
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'ico.ico')
        else:
            icon_path = 'ico.ico'
        self.setWindowIcon(QIcon(icon_path))

        # ID 입력칸 위젯 속성 정의
        self.label_id = QLabel("ID : ")
        self.label_id.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.input_id = QLineEdit()
        self.input_id.setFixedHeight(25)
        self.input_id.setFixedWidth(200)
        self.input_id.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # PW 입력칸 위젯 속성 정의
        self.label_pw = QLabel("PW : ")
        self.label_pw.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.input_pw = QLineEdit()
        self.input_pw.setFixedHeight(25)
        self.input_pw.setFixedWidth(200)
        self.input_pw.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pw.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # IP 입력칸 위젯 속성 정의
        self.label_ip = QLabel("DCV 접속 IP : ")
        self.label_ip.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.input_ip = QLineEdit()
        self.input_ip.setFixedHeight(25)
        self.input_ip.setFixedWidth(200)
        self.input_ip.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # 에러메세지 출력을 위한 위젯 속성 정의
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 구분선 추가를 위한 구분선 위젯 속성 정의
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator.setFixedHeight(1)
        self.separator.setStyleSheet("background-color: #ccc;")

        # 로그인 버튼 위젯 속성 정의
        self.login_button = QPushButton("로그인")
        self.login_button.setFixedHeight(30)
        self.login_button.clicked.connect(self.handle_login)

        # 하단 카피라이트 위젯 속성 정의
        self.copyright_label = QLabel("ⓒ2024 TheSsenVisualCraft Corp. All right reserved.")
        self.copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.copyright_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.copyright_label.setObjectName("copyrightLabel")

        # 위에서 만든 아이템(위젯)을 서브레이아웃 생성 후 배치
        id_layout = QHBoxLayout()
        id_layout.addWidget(self.label_id)
        id_layout.addWidget(self.input_id)
        id_layout.setSpacing(0)
        pw_layout = QHBoxLayout()
        pw_layout.addWidget(self.label_pw)
        pw_layout.addWidget(self.input_pw)
        pw_layout.setSpacing(0)
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(self.label_ip)
        ip_layout.addWidget(self.input_ip)
        ip_layout.setSpacing(0) 
        label_layout = QVBoxLayout()
        label_layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignCenter)
        label_layout.addWidget(self.separator)
        label_layout.setSpacing(5)
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.setSpacing(10)
        copyright_layout = QVBoxLayout()
        copyright_layout.addWidget(self.copyright_label)
        copyright_layout.setSpacing(0)

        # 로그인 버튼의 입체감을 위한 그림자 속성 정의
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(5)
        shadow_effect.setOffset(1, 1)
        shadow_effect.setColor(QColor(0, 0, 0, 255)) 
        self.login_button.setGraphicsEffect(shadow_effect)

        # 위에서 만든 서브 레이아웃을 메인레이아웃 생성 후 배치
        main_layout = QVBoxLayout()
        main_layout.addLayout(id_layout)
        main_layout.addSpacing(3)
        main_layout.addLayout(pw_layout)
        main_layout.addSpacing(3)
        main_layout.addLayout(ip_layout)
        main_layout.addSpacing(3)
        main_layout.addLayout(label_layout)
        main_layout.setSpacing(5)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(15) 
        main_layout.addLayout(copyright_layout)

        # 중앙 정렬
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 각 아이템(위젯)에 대한 기본 스타일시트 정의 
        self.setStyleSheet("""
            QLabel {
                font-weight : bold;
                color : #000000;
            }
            #copyrightLabel {
                font: 8pt Arial;
                color : #c4c4c4;
            }
            QWidget {
                background-color: #f0f0f0;
                border-radius: 10px;
            }
            QLineEdit {
                border: 1px solid #ccc;
                padding: 3px;
                border-radius: 5px;
                background-color: white;
                color : #000000;
            }
            QPushButton {
                background-color: #1e73be;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #115b9c;
            }
            QPushButton:disabled {
                background-color: #a9a9a9;
                color: #ffffff;
            }
            QLabel {
                font-size: 14px;
            }
            QMessageBox {
                border-radius: 10px;
            }
        """)

    # 엔터키 입력 시 액션에 대한 정의 (로그인 버튼 기능 수행)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.handle_login()

    # 로그인 버튼이 눌렸을때 발생하는 이벤트
    def handle_login(self):
        self.login_button.setEnabled(False)
        self.error_label.setStyleSheet("color: green;")
        self.error_label.setText("로그인 시도 중...")

        ip_text = self.input_ip.text()
        id_text = self.input_id.text()
        pw_text = self.input_pw.text()
         # IP주소 형식이 맞는지 확인
        ipv4_pattern = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
        if not ipv4_pattern.match(ip_text) or not all(0 <= int(octet) <= 255 for octet in ip_text.split('.')):
            self.error_label.setText("*입력하신 정보가 옳바르지 않습니다.")
            self.error_label.setStyleSheet("color: red;")
            self.login_button.setEnabled(True)
            return
        # SSH 접속 기능 병렬 스레드로 수행 (그냥 실행시 로그인 시도 중에 로그인창 GUI가 멈추기에 병렬 수행 처리)
        self.ssh_thread = SSHThread(ip_text, id_text, pw_text)
        self.ssh_thread.result_signal.connect(self.on_ssh_result)
        self.ssh_thread.start()

    # 로그인 접속 결과 처리 함수
    def on_ssh_result(self, result):
        # 성공 시 성공한 ID/PW/IP 전역변수에 저장
        if result == "success":
            user_info["id"] = self.input_id.text()
            user_info["pw"] = self.input_pw.text()
            user_info["ip"] = self.input_ip.text()
            self.error_label.setText("로그인 성공!")
            self.open_main_window() # 로그인 성공 후 메인 윈도우 호출
        else: # 실패 시 실패 문구로 사용자에게 알림
            self.error_label.setText(f"*입력하신 정보가 옳바르지 않습니다.")
            self.error_label.setStyleSheet("color: red;")
            self.login_button.setEnabled(True)

    # 로그인창을 닫고 메인창(기능창)을 호출하는 함수
    def open_main_window(self):
        self.main_window = MainWindow()
        self.main_window.show() # 메인 윈도우 호출
        self.close() # 로그인창 닫기


# 메인창 GUI 화면에 대한 정의 클래스 + 메인창에서 수행할 기능 함수들
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"DCV Tools Ver:{program_version}")
        self.setFixedSize(300, 230)
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, 'ico.ico')
        else:
            icon_path = 'ico.ico'
        self.setWindowIcon(QIcon(icon_path))

        self.service_name = "dcvserver"

        # 구현한 기능을 수행할 라벨 위젯과 버튼 위젯 속성 정의
        self.function_label = QLabel()
        self.function_label.setText(
            '<span sytyle="font-weight: bold">· </span><span style="color: #0d7c14; font-weight: bold;">CASE 1</span><span style="font-weight: bold"> : DCV 사용 중 튕김</span>'
        )
        self.function_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.restart_button = QPushButton("CASE 1 조치 진행")
        self.restart_button.setFixedHeight(35)
        self.restart_button.clicked.connect(self.restart_service)

        self.function_label2 = QLabel()
        self.function_label2.setText(
            '<span sytyle="font-weight: bold">· </span><span style="color: #0d7c14; font-weight: bold;">CASE 2</span><span style="font-weight: bold"> : DCV 처음 접속 시 검은 화면</span>'
        )
        self.function_label2.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.runlevel_button = QPushButton("CASE 2 조치 진행")
        self.runlevel_button.setFixedHeight(35)
        self.runlevel_button.clicked.connect(self.change_runlevel)

        # 진행 상황을 시각적인 효과로 전달하기 위한 프로그레스바 위젯 속성 정의
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 프로그램 자동 종료까지 남은 시간을 표시하기 위하 위젯 속성 정의
        self.timer_label = QLabel("프로그램 자동 종료까지 : 60초 남음")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        # 기능 실행 버튼에 입체감 추가를 위한 그림자 속성 정의
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(5)
        shadow_effect.setOffset(1, 1)
        shadow_effect.setColor(QColor(0, 0, 0, 255)) 
        self.restart_button.setGraphicsEffect(shadow_effect)
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(5)
        shadow_effect.setOffset(1, 1)
        shadow_effect.setColor(QColor(0, 0, 0, 255)) 
        self.runlevel_button.setGraphicsEffect(shadow_effect)

        # 레이아웃 구분을 위한 구분선 속성 정의
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator.setFixedHeight(1)
        self.separator.setStyleSheet("background-color: #ccc;")

        # 수직 메인 레이아웃 생성 후 위에서 생성한 위젯을 배치
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.function_label)
        main_layout.addWidget(self.restart_button)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.function_label2)
        main_layout.addWidget(self.runlevel_button)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.separator)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.timer_label)

        # 중앙 정렬
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 자동 종료 시간 설정 
        self.remaining_time = 60
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # 기능 수행 창에 위젯들에 대한 기본 스타일시트 정의
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-radius: 10px;
                color : #000000
            }
            QLineEdit {
                border: 1px solid #ccc;
                padding: 3px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #1e73be;
                color: white;
                border: none;
                padding: 2px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #115b9c;
            }
            QPushButton:disabled {
                background-color: #a9a9a9;
                color: #ffffff;
            }
            QLabel {
                font-size: 14px;
            }
            QMessageBox {
                border-radius: 10px;
            }
        """)

    # 서비스 재시작 기능 함수 (dcvserver)
    def restart_service(self):
        ip = user_info["ip"]
        username = user_info["id"]
        password = user_info["pw"]
        self.restart_button.setEnabled(False)
        self.runlevel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.update_progress_bar(0)

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password)

            stdin, stdout, stderr = ssh.exec_command("whoami")
            current_user = stdout.read().decode('utf-8').strip()
            # 사용자를 구분하고 사용자에 맞는 명령어 송신
            if current_user != "root":
                command = f"sudo systemctl restart {self.service_name}"
                stdin, stdout, stderr = ssh.exec_command(command)
            else:
                command = f"systemctl restart {self.service_name}"
                stdin, stdout, stderr = ssh.exec_command(command)

            self.update_progress_bar(20)
            # 서비스 재시작 명령어 송신 후 5초 뒤 서비스 상태를 체크하는 함수 호출
            QTimer.singleShot(5000, lambda: self.check_service_status(ssh))
        except Exception as e:
            self.update_progress_bar(0)
            self.show_error_message(f"오류 발생: {str(e)}")
            QTimer.singleShot(5000, lambda: self.restart_button.setEnabled(True))
            QTimer.singleShot(5000, lambda: self.runlevel_button.setEnabled(True))

    # 서비스 상태 확인을 위한 기능 함수
    def check_service_status(self, ssh, retry_count=1):
        stdin, stdout, stderr = ssh.exec_command(f"systemctl is-active {self.service_name}")
        status = stdout.read().decode('utf-8').strip()
        stdin, stdout, stderr = ssh.exec_command(f"systemctl show {self.service_name} --property=ActiveEnterTimestamp") 
        # 타겟이 되는 서비스의 액티브된 시간을 확인하는 명령어 (sudo권한 불필요)
        timestamp_output = stdout.read().decode('utf-8').strip()
        active_timestamp = timestamp_output.split('=')[1] if '=' in timestamp_output else None
        self.update_progress_bar(50)

        stdin, stdout, stderr = ssh.exec_command("date +'%s'")
        current_time = int(stdout.read().decode('utf-8').strip())
        # 확인한 서비스 active 시간과 현재 시간을 비교하여 10초 미만일 경우 재시작에 성공한걸로 구분
        if active_timestamp:
            stdin, stdout, stderr = ssh.exec_command(f"date -d '{active_timestamp}' +'%s'") 
            service_start_time = int(stdout.read().decode('utf-8').strip())
            recently_restarted = (current_time - service_start_time) <= 10
        else:
            recently_restarted = False
        # 다음으로 현재 dcvserver 서비스 상태가 Active 상태가 맞는지 확인
        if status == 'active' and recently_restarted:
            self.update_progress_bar(100)
            QTimer.singleShot(1000, lambda: self.restart_button.setEnabled(True))
            QTimer.singleShot(1000, lambda: self.runlevel_button.setEnabled(True))
            ssh.close()
            QMessageBox.information(self, "작업 성공", "CASE 1 조치 완료") 
            # 모든 확인에 통과할 경우 정상적인 서비스 재시작 확인으로 구분
        else:
            if retry_count < 2:
                QTimer.singleShot(5000, lambda: self.check_service_status(ssh, retry_count + 1)) 
                # 서비스가 active가 아닌 activing 혹은 failed 일 경우 5초간 대기 후 추가 재확인(1회)
            else:
                self.update_progress_bar(0)
                self.restart_button.setEnabled(True)
                self.runlevel_button.setEnabled(True)
                ssh.close()
                QMessageBox.critical(self, "작업 실패", "CASE 1 조치 실패\nIT팀에 문의하세요.") 
                # 재확인 이후 여전히 active가 아닐 경우 최종 실패로 구분
    
    # 런레벨 변경 기능 함수 (블랙스크린 조치)
    def change_runlevel(self):
        ip = user_info["ip"]
        username = user_info["id"]
        self.restart_button.setEnabled(False)
        self.runlevel_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.update_progress_bar(0)

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=user_info['pw'])

            stdin, stdout, stderr = ssh.exec_command("whoami")
            current_user = stdout.read().decode('utf-8').strip()

            if current_user == "root":
                command_3 = "systemctl isolate multi-user.target"
            else:
                command_3 = "sudo systemctl isolate multi-user.target"

            stdin, stdout, stderr = ssh.exec_command(command_3)
            # 런레벨 3로 변경하는 명령어 송신 후 2초 뒤 현재 런레벨 확인을 진행하는 함수 호출
            QTimer.singleShot(2000, lambda: self.check_runlevel(ssh, current_user, check_runlevel_count))
            self.update_progress_bar(20)
        except Exception as e:
            self.update_progress_bar(0)
            self.show_error_message(f"오류 발생: {str(e)}")
            self.restore_buttons()

    # 런레벨 체크 기능 함수 
    def check_runlevel(self, ssh, current_user, remaining_time):
        # 재확인 횟수를 모두 소모 후 최종 실패처리에 대한 액션 정의
        if remaining_time <= 0:
            self.update_progress_bar(0)
            self.restore_buttons()
            QMessageBox.critical(self, "작업 실패", "CASE 2 조치 실패\nIT팀에 문의해주세요.")
            ssh.close()
            return

        try:
            stdin, stdout, stderr = ssh.exec_command("runlevel")
            output = stdout.read().decode('utf-8').strip()
            current_runlevel = output.split()[1] if output else "unknown"

            self.update_progress_bar(50)
            # 런레벨 3로 변경 후 현재상태가 런레벨 3일 경우 런레벨 5로 다시 변경하는 명령어 송신
            if current_runlevel == "3":
                if current_user == "root":
                    command_5 = "systemctl isolate graphical.target"
                else:
                    command_5 = "sudo systemctl isolate graphical.target"

                stdin, stdout, stderr = ssh.exec_command(command_5)
                QTimer.singleShot(3000, lambda: self.check_final_runlevel(ssh, current_user, 5, 3))  # 3초 후 최종 런레벨 체크
            else:
                # 런레벨 확인 후 3으로 변경이 안되었을 경우 1초뒤 런레벨 체크 재수행 (카운트는 20에서 -1씩 1초마다 재수행하니 20초 동안 20회 재확인)
                QTimer.singleShot(1000, lambda: self.check_runlevel(ssh, current_user, remaining_time - 1))
        except Exception as e:
            self.show_error_message(f"상태 확인 중 오류 발생: {str(e)}")
            self.restore_buttons()
            ssh.close()

    # 최총 런레벨 체크 기능 함수 
    def check_final_runlevel(self, ssh, current_user, target_runlevel, remaining_checks):
        if remaining_checks <= 0:
            self.update_progress_bar(0)
            self.restore_buttons()
            QMessageBox.critical(self, "작업 실패", f"CASE 2 조치 실패\nIT팀에 문의해주세요.")
            ssh.close()
            return
        # 현재 런레벨 상태가 다시 5로 변경되었는지 확인하는 함수
        try:
            stdin, stdout, stderr = ssh.exec_command("runlevel")
            output = stdout.read().decode('utf-8').strip()
            current_runlevel = output.split()[1] if output else "unknown"

            if current_runlevel == str(target_runlevel):
                self.update_progress_bar(100)
                QMessageBox.information(self, "작업 성공", f"CASE 2 조치 완료")
                ssh.close()
                self.restore_buttons()
            else:
                QTimer.singleShot(1000, lambda: self.check_final_runlevel(ssh, current_user, target_runlevel, remaining_checks - 1))
        except Exception as e:
            self.show_error_message(f"상태 확인 중 오류 발생: {str(e)}")
            self.update_progress_bar(0)
            self.restore_buttons()
            ssh.close()

    # 사용자에게 직관적으로 진행상황을 알리고자 구현한 게이지바(프로세스바)
    def update_progress_bar(self, target_value):
        current_value = self.progress_bar.value()
        if current_value < target_value:
            increment = min(target_value - current_value, 1)
            self.progress_bar.setValue(current_value + increment)
            QTimer.singleShot(10, lambda: self.update_progress_bar(target_value))

    # 기능 수행중 비활성화 된 버튼을 3초 후 다시 활성화 시키는 기능 함수
    def restore_buttons(self):
        QTimer.singleShot(3000, lambda: self.restart_button.setEnabled(True))
        QTimer.singleShot(3000, lambda: self.runlevel_button.setEnabled(True))

    # 예외처리 외의 기능문제 발생시 에러코드 확인을 위한 에러창 함수 (개발자 에러내용 확인용)
    def show_error_message(self, message="오류 발생"):
        QMessageBox.critical(self, "Error", message)

    # 프로그램 자동 종료까지의 시간을 사용자에게 알리기 위한 기능 함수 
    def update_time(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.close()
            sys.exit()
        else:
            self.timer_label.setText(f"프로그램 자동 종료까지 : {self.remaining_time}초 남음")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(sys.executable), "ico.ico") if getattr(sys, 'frozen', False) else "ico.ico"
    app.setWindowIcon(QIcon(icon_path))
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())