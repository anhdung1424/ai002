# main.py
import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime

# Import các module đã xây dựng từ các bước trước
from src.p1_acquisition.data_reader import DataAcquisition
from src.p2_recognition.detector import ObjectDetector
from src.p3_context.rule_engine import RuleEngine
from src.p4_action.alert_manager import AlertManager

# Cấu hình trang Dashboard Streamlit
st.set_page_config(page_title="Smart Home Safety Monitor", layout="wide")

def main():
    st.title("🛡️ Hệ thống Phát hiện & Cảnh báo Đồ vật Đặt sai vị trí")
    st.sidebar.header("Cấu hình hệ thống")
    
    # Lựa chọn nguồn đầu vào
    input_source = st.sidebar.selectbox("Chọn nguồn Video", ("Webcam", "File Video"))
    source = 0 if input_source == "Webcam" else "data/input_videos/test_sample.mp4"
    camera_id = st.sidebar.text_input("Mã Camera", "CAM_001")

    # Khởi tạo các Module (Step 12: Generalization)
    if 'pipeline' not in st.session_state:
        st.session_state.acquisition = DataAcquisition(source=source, camera_id=camera_id)
        st.session_state.detector = ObjectDetector()
        st.session_state.rule_engine = RuleEngine()
        st.session_state.alert_manager = AlertManager()
        st.session_state.alert_logs = [] # Lưu trữ log cảnh báo để hiển thị trên bảng

    # Bố cục giao diện: Cột trái (Video) - Cột phải (Log)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📺 Camera Live Stream")
        video_placeholder = st.empty() # Placeholder để cập nhật frame liên tục

    with col2:
        st.subheader("⚠️ Danh sách Cảnh báo")
        log_placeholder = st.empty()

    # Nút bắt đầu/dừng hệ thống
    start_btn = st.sidebar.button("Bắt đầu giám sát")
    
    if start_btn:
        # --- BẮT ĐẦU END-TO-END PIPELINE ---
        # P1: Data Acquisition (Generator)
        for packet in st.session_state.acquisition.get_stream():
            raw_frame = packet["raw_frame"]
            
            # P2: Object Recognition & Position Classification
            # Nhận diện vật thể và xác định floor/low/mid/high
            detections = st.session_state.detector.detect_objects(packet)
            
            current_alerts_in_frame = []
            
            for det in detections:
                # P3: Context Analysis
                # Đối soát với Safety Rules trong config.py
                is_violation, v_type, severity, msg = st.session_state.rule_engine.validate_detection(det)
                
                # Xác định màu sắc Bounding Box (Yêu cầu: ĐỎ cho vi phạm, XANH cho an toàn)
                color = (0, 0, 255) if is_violation else (0, 255, 0) # BGR
                label = f"{det.class_name} ({det.position})"
                
                # Vẽ lên Frame gốc (Visualization)
                x1, y1, x2, y2 = det.bbox
                cv2.rectangle(raw_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(raw_frame, label, (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # P4: Action Triggering
                # Nếu vi phạm, thực hiện lọc trùng và ghi log
                if is_violation:
                    triggered = st.session_state.alert_manager.trigger(det, (is_violation, v_type, severity, msg))
                    if triggered:
                        new_log = {
                            "Thời gian": det.metadata['timestamp'].strftime("%H:%M:%S"),
                            "Vị trí": det.metadata['room_name'],
                            "Vật thể": det.class_name,
                            "Mức độ": severity,
                            "Nội dung": msg
                        }
                        st.session_state.alert_logs.insert(0, new_log) # Đưa log mới lên đầu

            # --- CẬP NHẬT GIAO DIỆN STREAMLIT ---
            # Chuyển đổi BGR (OpenCV) sang RGB (Streamlit)
            frame_rgb = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
            
            # Cập nhật bảng Log cảnh báo (P4.3)
            if st.session_state.alert_logs:
                df_logs = pd.DataFrame(st.session_state.alert_logs).head(10) # Hiển thị 10 log mới nhất
                log_placeholder.table(df_logs)

if __name__ == "__main__":
    main()